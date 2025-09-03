"""
  $ pip install aiauto-client optuna
  # 코드에서 다음 부분에 front 에서 발급한 토큰 입력
  # ac = aiauto.AIAutoController('<token>')

주의사항:
  - objective 함수 내부의 모든 import 와 코드는 외부 서버에서 실행됨
  - Mac ARM 환경에서도 문제없이 실행 가능

실행:
  $ python simple_example.py
"""

import aiauto


# 사용 가능한 런타임 이미지 목록 확인
print("Available runtime images:")
for image in aiauto.RUNTIME_IMAGES:
    print(f"  - {image}")
print()

# TODO singleton 객체에 토큰 값 지정하면 객체 초기화 시 설정 됨
ac = aiauto.AIAutoController('<token>')


# single objective accuracy
def simple_objective(trial):
    import optuna
    import aiauto
    """
    간단한 2차 함수 최적화
    (x - 2)^2 + (y - 3)^2 를 최소화

    이 함수는 외부서버에서 실행됩니다.
    모든 import 와 클래스 정의는 objective 함수 내부에 있어야 합니다.
    이 안에서 import 하는 lib 들은 optimize 를 호출할 때 requirements list 로 넘겨야 합니다
    """
    # ====================== 외부 서버에서만 실행되는 코드 시작 =========================
    # objective 함수의 매개변수로 받아온 optuna 자체의 trial 을 aiauto 에서 사용하는 TrialController 로 Warpping Log 찍는 용도
    # log 는 optuna dashboard 에서 확인 가능
    # 하나의 trial objective 함수 안에서만 사용하는 trial 객체
    tc = aiauto.TrialController(trial)

    # 하이퍼파라미터 샘플링
    x = trial.suggest_float('x', -10, 10)
    y = trial.suggest_float('y', -10, 10)

    tc.log(f'Trial {trial.number}: x={x:.2f}, y={y:.2f}')

    # 목적 함수 계산
    value = (x - 2) ** 2 + (y - 3) ** 2
    tc.log(f'Objective value: {value:.4f}')

    return value
    # ====================== 외부 서버에서만 실행되는 코드 끝 ===========================


if __name__ == '__main__':
    # ========================== 간단한 2차 함수 최적화 =============================
    study = ac.create_study(
        study_name="simple_quadratic",
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=42),
    )
    study.optimize(
        simple_objective,
        n_trials=20,
        parallelism=2,  # 동시 실행 Pod 수
        # use_gpu=False,  # default
        # runtime_image = "ghcr.io/astral-sh/uv:python3.8-bookworm-slim",  # default image for use_gpu False
    )

    print('\nBest trials:')
    print(f'  Best value (accuracy): {study.best_value:.4f}')
    print(f'  Best params:')
    for key, val in study.best_params.items():
        print(f'    {key}: {val}')
    print()
