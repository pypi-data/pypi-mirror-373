import aiauto
import optuna
from unittest.mock import patch


def objective(trial):
    """간단한 이차함수 최적화 예제"""
    # TrialController를 사용한 로깅
    tc = aiauto.TrialController(trial)
    tc.log("Starting simple optimization example")

    # 하이퍼파라미터 샘플링
    x = trial.suggest_float('x', -10, 10)
    y = trial.suggest_float('y', -10, 10)

    # 목적함수: (x-2)² + (y-5)² 최소화
    result = (x - 2) ** 2 + (y - 5) ** 2

    tc.log(f"x={x:.3f}, y={y:.3f}, result={result:.3f}")

    return result


def main():
    print("🚀 AIAuto 소스코드 직렬화 로컬 테스트")

    # AIAutoController의 storage를 InMemoryStorage로 패치
    with patch.object(aiauto.AIAutoController, '__init__', lambda self: None):
        controller = aiauto.AIAutoController()
        # 로컬 테스트용 InMemoryStorage 설정
        controller.storage = optuna.storages.InMemoryStorage()
        controller.artifact_store = optuna.artifacts.FileSystemArtifactStore('./artifacts')

        # 소스코드 직렬화 테스트
        print("\n=== 소스코드 직렬화 테스트 ===")
        study_wrapper = controller.create_study(
            objective=objective,
            study_name='local_test',
            direction='minimize'
        )

        print("✅ StudyWrapper 생성 성공!")

        # 최적화 실행
        print("\n=== 최적화 실행 ===")
        study_wrapper.optimize(n_trials=10)

        # 결과 출력
        print(f"\n🎉 최적화 완료!")
        print(f"📊 Best value: {study_wrapper.best_value:.3f}")
        print(f"🔧 Best params: {study_wrapper.best_params}")

        # 이론적 최적해: x=2, y=5, result=0
        print(f"💡 이론적 최적해: x=2, y=5, result=0")
        print(f"📈 오차: {study_wrapper.best_value:.3f}")


if __name__ == "__main__":
    main()
