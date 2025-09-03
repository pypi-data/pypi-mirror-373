from os import makedirs
import tempfile
from typing import Union, Optional, List, Dict, Callable
import optuna
from .http_client import ConnectRPCClient
from .serializer import serialize, build_requirements, object_to_json
from ._config import AIAUTO_API_TARGET


class AIAutoController:
    _instances = {}

    def __new__(cls, token: str):
        if token not in cls._instances:
            cls._instances[token] = super().__new__(cls)
        return cls._instances[token]

    def __init__(self, token: str):
        if hasattr(self, 'token') and self.token == token:
            return

        self.token = token
        self.client = ConnectRPCClient(token)

        # EnsureWorkspace 호출해서 journal_grpc_storage_proxy_host_external 받아와서 storage 초기화
        try:
            response = self.client.call_rpc("EnsureWorkspace", {})

            # 받아온 journal_grpc_storage_proxy_host_external로 storage 초기화
            host_external = response.get('journalGrpcStorageProxyHostExternal', '')
            if not host_external:
                raise RuntimeError("No storage host returned from EnsureWorkspace")

            host, port = host_external.split(':')
            self.storage = optuna.storages.GrpcStorageProxy(host=host, port=int(port))

            # Store the internal host for CRD usage (if needed later)
            self.storage_host_internal = response.get('journalGrpcStorageProxyHostInternal', '')
            self.dashboard_url = response.get('dashboardUrl', '')

        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize workspace: {e}\n"
                "Please delete and reissue your token from the web dashboard at https://dashboard.common.aiauto.pangyo.ainode.ai"
            ) from e

        # artifact storage
        makedirs('./artifacts', exist_ok=True)
        self.artifact_store = optuna.artifacts.FileSystemArtifactStore('./artifacts')
        self.tmp_dir = tempfile.mkdtemp(prefix=f'ai_auto_tmp_')

    def get_storage(self):
        return self.storage

    def get_artifact_store(self) -> Union[
        optuna.artifacts.FileSystemArtifactStore,
        optuna.artifacts.Boto3ArtifactStore,
        optuna.artifacts.GCSArtifactStore,
    ]:
        return self.artifact_store

    def get_artifact_tmp_dir(self):
        return self.tmp_dir

    def create_study(
        self,
        study_name: str,
        direction: Optional[str] = 'minimize',
        directions: Optional[List[str]] = None,
        sampler: Union[object, dict, None] = None,
        pruner: Union[object, dict, None] = None
    ) -> 'StudyWrapper':
        """Create a new study using the controller's token."""
        if not direction and not directions:
            raise ValueError("Either 'direction' or 'directions' must be specified")

        if direction and directions:
            raise ValueError("Cannot specify both 'direction' and 'directions'")

        try:
            # Prepare request data for CreateStudy
            request_data = {
                "spec": {
                    "studyName": study_name,
                    "direction": direction or "",
                    "directions": directions or [],
                    "samplerJson": object_to_json(sampler),
                    "prunerJson": object_to_json(pruner)
                }
            }

            # Call CreateStudy RPC
            response = self.client.call_rpc("CreateStudy", request_data)

            # Return StudyWrapper
            return StudyWrapper(
                study_name=response.get("studyName", study_name),
                storage=self.storage,
                controller=self
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create study: {e}") from e


class TrialController:
    def __init__(self, trial: optuna.trial.Trial):
        self.trial = trial
        self.logger = optuna.logging.get_logger("optuna")
        self.logs = []

    def get_trial(self) -> optuna.trial.Trial:
        return self.trial

    def log(self, value: str):
        # optuna dashboard 에 log 를 확인하는 기능이 없어서 user_attribute 에 log를 확인할 수 있게 추가
        self.logs.append(value)
        self.trial.set_user_attr('logs', ' '.join([f"[{i+1:05d}] {log}" for i, log in enumerate(self.logs)]))
        # 실제 log 를 trial_number 랑 같이 확인할 수 있게
        self.logger.info(f'\ntrial_number: {self.trial.number}, {value}')


# 용량 제한으로 상위 N개의 trial artifact 만 유지
class CallbackTopNArtifact:
    def __init__(
        self,
        artifact_store: Union[
            optuna.artifacts.FileSystemArtifactStore,
            optuna.artifacts.Boto3ArtifactStore,
            optuna.artifacts.GCSArtifactStore,
        ],
        artifact_attr_name: str = 'artifact_id',
        n_keep: int = 5,
    ):
        self.artifact_store = artifact_store
        self.check_attr_name = artifact_attr_name
        self.n_keep = n_keep

    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial):
        # COMPLETE 상태이고 artifact를 가진 trial들만 정렬
        finished_with_artifacts = [
            t for t in study.trials
            if t.state == optuna.trial.TrialState.COMPLETE and self.check_attr_name in t.user_attrs
        ]

        # 방향에 따라 정렬 (maximize면 내림차순, minimize면 오름차순)
        reverse_sort = study.direction == optuna.study.StudyDirection.MAXIMIZE
        finished_with_artifacts.sort(key=lambda t: t.value, reverse=reverse_sort)

        # 상위 n_keep개 초과하는 trial들의 artifact 삭제
        for old_trial in finished_with_artifacts[self.n_keep:]:
            artifact_id = old_trial.user_attrs.get(self.check_attr_name)
            if artifact_id:
                try:
                    self.artifact_store.remove(artifact_id)
                    # user_attr에서도 제거
                    study._storage.set_trial_user_attr(old_trial._trial_id, self.check_attr_name, None)
                except Exception as e:
                    print(f"Warning: Failed to remove artifact {artifact_id}: {e}")


class StudyWrapper:
    def __init__(self, study_name: str, storage, controller: AIAutoController):
        self.study_name = study_name
        self._storage = storage
        self._controller = controller
        self._study = None

    def get_study(self) -> optuna.Study:
        if self._study is None:
            try:
                self._study = optuna.create_study(
                    study_name=self.study_name,
                    storage=self._storage,
                    load_if_exists=True,
                )
            except Exception as e:
                raise RuntimeError(
                    "Failed to get study. If this persists, please delete and reissue your token "
                    "from the web dashboard at https://dashboard.common.aiauto.pangyo.ainode.ai"
                ) from e
        return self._study

    def optimize(
        self,
        objective: Callable,
        n_trials: int = 10,
        parallelism: int = 2,
        requirements_file: Optional[str] = None,
        requirements_list: Optional[List[str]] = None,
        resources_requests: Optional[Dict[str, str]] = {"cpu": "256m", "memory": "256Mi"},
        resources_limits: Optional[Dict[str, str]] = {"cpu": "256m", "memory": "256Mi"},
        runtime_image: Optional[str] = 'ghcr.io/astral-sh/uv:python3.8-bookworm-slim',
        use_gpu: bool = False
    ) -> None:
        if runtime_image is None or runtime_image == "":
            if use_gpu:
                runtime_image = "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime"
            else:
                runtime_image = "ghcr.io/astral-sh/uv:python3.8-bookworm-slim"
        try:
            request_data = {
                "objective": {
                    "sourceCode": serialize(objective),
                    "requirementsTxt": build_requirements(requirements_file, requirements_list),
                    "objectiveName": objective.__name__  # 함수명 추출하여 전달
                },
                "batch": {
                    "studyName": self.study_name,
                    "nTrials": n_trials,
                    "parallelism": parallelism,
                    "runtimeImage": runtime_image or "",
                    "resourcesRequests": resources_requests or {},
                    "resourcesLimits": resources_limits or {},
                    "useGpu": use_gpu
                }
            }

            self._controller.client.call_rpc("Optimize", request_data)

        except Exception as e:
            raise RuntimeError(f"Failed to start optimization: {e}") from e

    def get_status(self) -> dict:
        try:
            response = self._controller.client.call_rpc(
                "GetStatus",
                {"studyName": self.study_name}
            )

            # Convert camelCase to snake_case for backward compatibility
            return {
                "study_name": response.get("studyName", ""),
                "count_active": response.get("countActive", 0),
                "count_succeeded": response.get("countSucceeded", 0),
                "count_pruned": response.get("countPruned", 0),
                "count_failed": response.get("countFailed", 0),
                "count_total": response.get("countTotal", 0),
                "count_completed": response.get("countCompleted", 0),
                "dashboard_url": response.get("dashboardUrl", ""),
                "last_error": response.get("lastError", ""),
                "updated_at": response.get("updatedAt", "")
            }

        except Exception as e:
            raise RuntimeError(f"Failed to get status: {e}") from e

    def __repr__(self) -> str:
        return f"StudyWrapper(study_name='{self.study_name}', storage={self._storage})"
