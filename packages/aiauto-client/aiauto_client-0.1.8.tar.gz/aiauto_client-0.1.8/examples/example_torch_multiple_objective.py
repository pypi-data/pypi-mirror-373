"""
  $ pip install aiauto-client optuna
  # 코드에서 다음 부분에 front 에서 발급한 토큰 입력
  # ac = aiauto.AIAutoController('<token>')

주의사항:
  - torch는 로컬에 설치하지 마세요
  - objective 함수 내부의 모든 import 와 코드는 외부 서버에서 실행됨
  - Mac ARM 환경에서도 문제없이 실행 가능

실행:
  $ python example_torch_multiple_objective.py
"""

import optuna
import aiauto


# 사용 가능한 런타임 이미지 목록 확인
print("Available runtime images:")
for image in aiauto.RUNTIME_IMAGES:
    print(f"  - {image}")
print()

# TODO singleton 객체에 토큰 값 지정하면 객체 초기화 시 설정 됨
ac = aiauto.AIAutoController('<token>')


# multi objective without pruning (accuracy + FLOPS)
def objective_multi(trial):
    """
    다중 목적 함수: accuracy 최대화 + FLOPS 최소화
    hyper parameter tuning을 할 때는 데이터의 일부만 사용하여 빠르게 HPO를 한다

    이 함수는 외부 서버의 GPU 인스턴스에서 실행됩니다.
    모든 import 와 클래스 정의는 objective 함수 내부에 있어야 합니다.
    이 안에서 import 하는 lib 들은 optimize 를 호출할 때 requirements list 로 넘겨야 합니다
    """
    # ====================== 외부 서버에서만 실행되는 코드 시작 =========================
    from os.path import join
    from typing import List

    import torch
    from torch import nn, optim
    from torch.utils.data import DataLoader, random_split, Subset
    from torchvision import transforms, datasets
    import torch.nn.functional as F
    from fvcore.nn import FlopCountAnalysis

    from optuna.artifacts import upload_artifact


    # objective 함수의 매개변수로 받아온 optuna 자체의 trial 을 aiauto 에서 사용하는 TrialController 로 Warpping Log 찍는 용도
    # log 는 optuna dashboard 에서 확인 가능
    # 하나의 trial objective 함수 안에서만 사용하는 trial 객체
    tc = aiauto.TrialController(trial)

    # ======================= Neural Network 모델 정의 ===========================
    class Net(nn.Module):
        def __init__(
            self,
            features: List[int],
            dropout: float,
            dims: List[int],
        ):
            if len(features) != 3:
                raise ValueError("Feature list must have three elements")
            if len(dims) > 3:
                raise ValueError("Dimension list must have less than three elements")

            super().__init__()

            # image: 3 * 32 * 32 * 60000
            # Conv2d 공식: output_size = (input_size - kernel_size + 2*padding) / stride + 1
            layers = [
                # (batch, 3, 32, 32)
                nn.Conv2d(3, features[0], 3, padding=1),
                # (batch, features[0], 32, 32)
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                # (batch, features[0], 16, 16)

                nn.Conv2d(features[0], features[1], 3, padding=1),
                # (batch, features[1], 16, 16)
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                # (batch, features[1], 8, 8)

                nn.Conv2d(features[1], features[2], 3, padding=1),
                # (batch, features[2], 8, 8)
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                # (batch, features[2], 4, 4)

                nn.Flatten(),
            ]

            input_dim = features[2] * 4 * 4
            for dim in dims:
                layers.append(nn.Linear(input_dim, dim))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout))
                input_dim = dim

            classes = 10
            layers.append(nn.Linear(input_dim, classes))

            self.layers = nn.Sequential(*layers)

        def forward(self, x):
            logits = self.layers(x)
            return F.log_softmax(logits, dim=1)

    # ===================== 하이퍼파라미터 서치 스페이스 정의 ==========================
    batch_size = trial.suggest_categorical('batch_size', [16, 32, 64, 128])
    lr = trial.suggest_float('learning_rate', 0.001, 0.3, log=True)
    momentum = trial.suggest_float('momentum', 0.0, 1.0, step=0.05)
    features = [
        trial.suggest_int(f'feature{i}', 4, 64, log=True) for i in range(3)
    ]
    dropout = trial.suggest_float('dropout', 0.2, 0.5)
    n_layers = trial.suggest_int('n_layers', 1, 3)
    dims = [
        trial.suggest_int(f'dims{i}', 4, 128, log=True) for i in range(n_layers)
    ]
    epochs = trial.suggest_int('epochs', 20, 300, step=10)

    tc.log(f'batch_size={batch_size}, lr={lr}, momentum={momentum}, features={features}, dropout={dropout}, dims={dims} epochs={epochs}')

    # 데이터 샘플링 옵션 - 튜닝 시에만 사용
    data_fraction_number = trial.suggest_categorical('data_fraction_number', [4, 8])
    data_subset_idx = trial.suggest_int('data_subset_idx', 0, data_fraction - 1)

    tc.log(f'data_fraction_number={data_fraction_number}, data_subset_idx={data_subset_idx}')

    # ============================ GPU 존재 확인 =================================
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA not available')
    # GPU 없으면 cpu 지정 GPU 없으면 위 처럼 Error 를 일으키던지, cpu 를 지정하던지 알아서 하면 됨
    # 현재는 무조건 GPU 를 사용하는 예제라 Error 를 일으킴
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    model = Net(features, dropout, dims).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    # ======================== CIFAR-10 데이터 준비 ===============================
    valid_ratio: float = 0.3
    seed: int = 42
    # hyper parameter tuning 을 할 때는 데이터의 일부만 사용하여 빠르게 HPO 를 하고
    # objective_detailed 로 best trial 의 세팅으로 전체 데이터를 학습한다
    dataset = datasets.CIFAR10(
        root="/tmp/cifar10_data",  # Pod의 임시 디렉토리 사용
        train=True,
        download=True,
        transform=transforms.ToTensor(),
    )
    # 전체 데이터를 train, valid로 분할
    n_total = len(dataset)
    n_valid = int(n_total * valid_ratio)
    n_train = n_total - n_valid
    train_set, valid_set = random_split(
        dataset,
        [n_train, n_valid],
        generator=torch.Generator().manual_seed(seed),
    )

    # 일부 데이터만 사용하는 경우
    if data_fraction_number > 1:
        # data_set 을 data_fraction_number 로 나누어 data_subset_idx 번째 데이터만 사용
        def get_data_subset(data_set, fraction_number, idx):
            subset_size = len(data_set) // fraction_number
            start_idx = idx * subset_size
            end_idx = start_idx + subset_size if idx < fraction_number - 1 else len(data_set)
            indices = list(range(start_idx, end_idx))
            return Subset(data_set, indices)

        # train_set, valid_set 일부만 사용
        train_set = get_data_subset(train_set, data_fraction_number, data_subset_idx)
        valid_set = get_data_subset(valid_set, data_fraction_number, data_subset_idx)
        tc.log(f'subset dataset: data_fraction_number {data_fraction_number}, data_subset_idx {data_subset_idx}, train {len(train_set)}, valid {len(valid_set)}, batch_size {batch_size}')

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2)
    valid_loader = DataLoader(valid_set, batch_size=batch_size, shuffle=True, num_workers=2)

    # =========================== 학습 및 검증 루프 ================================
    tc.log('Start multiple objective training...')
    for epoch in range(epochs):  # multi objective 는 pruning 없으므로 그냥 suggestion 받은 값 사용
        model.train()
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            if batch_idx % (len(train_loader) // 4) == 0:  # 1 epoch 당 4번만 로그
                tc.log(f'epoch: {epoch}, batch: {batch_idx}, loss: {loss.item()}')
            loss.backward()
            optimizer.step()

        # 검증 정확도 계산
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for inputs, targets in valid_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                _, pred = torch.max(outputs, 1)
                total += targets.size(0)
                correct += (pred == targets).sum().item()
        accuracy = correct / total
        tc.log(f'epoch: {epoch}, accuracy: {accuracy}')

        # multi-objective optimization에서는 intermediate report, pruning 지원하지 않음
        trial.report(accuracy, epoch)

    # FLOPS 계산
    dummy_input = torch.randn(1, 3, 32, 32).to(device)
    flops = FlopCountAnalysis(model, (dummy_input,)).total()

    # ====================== 학습 완료 후 최종 모델 스냅샷 저장 ========================
    try:
        filename = f'{trial.study.study_name}_{trial.number}'
        model_path = join(ac.get_artifact_tmp_dir(), filename)
        # 모델 임시 폴더에 저장
        torch.save(
            model.state_dict(),
            model_path,
        )
        # optuna 에 artifact 업로드
        artifact_id = upload_artifact(
            artifact_store=ac.get_artifact_store(),
            storage=ac.get_storage(),
            study_or_trial=trial,
            file_path=model_path,
        )
        # artifact_id trial 에 user_attr 에 저장 (optuna dashboard 에서 확인하기 위함)
        trial.set_user_attr('artifact_id', artifact_id)
    except Exception as e:
        tc.log(f'Fail to save model file {filename}: {e}')

    # objective 함수 리턴
    return accuracy, flops
    # ====================== 외부 서버에서만 실행되는 코드 끝 ===========================


def objective_detailed(trial):
    """
    best trial의 세팅으로 전체 데이터를 학습한다
    """
    # ====================== 외부 서버에서만 실행되는 코드 시작 =========================
    from typing import List

    import torch
    from torch import nn, optim
    from torch.utils.data import DataLoader
    from torchvision import transforms, datasets
    import torch.nn.functional as F
    from fvcore.nn import FlopCountAnalysis

    from optuna.artifacts import upload_artifact


    # objective 함수의 매개변수로 받아온 optuna 자체의 trial 을 aiauto 에서 사용하는 TrialController 로 Warpping Log 찍는 용도
    # log 는 optuna dashboard 에서 확인 가능
    # 하나의 trial objective 함수 안에서만 사용하는 trial 객체
    tc = aiauto.TrialController(trial)

    # ======================= Neural Network 모델 정의 ===========================
    class Net(nn.Module):
        def __init__(
            self,
            features: List[int],
            dropout: float,
            dims: List[int],
        ):
            if len(features) != 3:
                raise ValueError("Feature list must have three elements")
            if len(dims) > 3:
                raise ValueError("Dimension list must have less than three elements")

            super().__init__()

            # image: 3 * 32 * 32 * 60000
            # Conv2d 공식: output_size = (input_size - kernel_size + 2*padding) / stride + 1
            layers = [
                # (batch, 3, 32, 32)
                nn.Conv2d(3, features[0], 3, padding=1),
                # (batch, features[0], 32, 32)
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                # (batch, features[0], 16, 16)

                nn.Conv2d(features[0], features[1], 3, padding=1),
                # (batch, features[1], 16, 16)
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                # (batch, features[1], 8, 8)

                nn.Conv2d(features[1], features[2], 3, padding=1),
                # (batch, features[2], 8, 8)
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                # (batch, features[2], 4, 4)

                nn.Flatten(),
            ]

            input_dim = features[2] * 4 * 4
            for dim in dims:
                layers.append(nn.Linear(input_dim, dim))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout))
                input_dim = dim

            classes = 10
            layers.append(nn.Linear(input_dim, classes))

            self.layers = nn.Sequential(*layers)

        def forward(self, x):
            logits = self.layers(x)
            return F.log_softmax(logits, dim=1)

    # ===================== best trial의 하이퍼파라미터 사용 =========================
    batch_size = trial.params['batch_size']
    lr = trial.params['learning_rate']
    momentum = trial.params['momentum']
    features = [trial.params[f'feature{i}'] for i in range(3)]
    dropout = trial.params['dropout']
    n_layers = trial.params['n_layers']
    dims = [trial.params[f'dims{i}'] for i in range(n_layers)]
    epochs = trial.params['epochs']

    tc.log(f'Using best trial params: batch_size={batch_size}, lr={lr}, momentum={momentum}, features={features}, dropout={dropout}, dims={dims} epochs={epochs}')

    # ============================ GPU 존재 확인 =================================
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA not available')
    # GPU 없으면 cpu 지정 GPU 없으면 위 처럼 Error 를 일으키던지, cpu 를 지정하던지 알아서 하면 됨
    # 현재는 무조건 GPU 를 사용하는 예제라 Error 를 일으킴
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    model = Net(features, dropout, dims).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    # ====================== CIFAR-10 전체 데이터 로드 =============================
    train_dataset = datasets.CIFAR10(
        root="/tmp/cifar10_data",
        train=True,
        download=True,
        transform=transforms.ToTensor(),
    )
    test_dataset = datasets.CIFAR10(
        root="/tmp/cifar10_data",
        train=False,
        download=True,
        transform=transforms.ToTensor(),
    )

    tc.log(f'full dataset: train {len(train_dataset)}, test {len(test_dataset)}, batch_size {batch_size}')

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    # ================= best_trial 전체 데이터 학습 및 검증 루프 ======================
    tc.log('Start full dataset training...')
    for epoch in range(epochs):  # best_trial 의 epochs 사용
        model.train()
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            # train_loader 크기에 맞춰서 적절히 조금만 로그 출력
            if batch_idx % (len(train_loader) // 4) == 0:  # 1 epoch 당 4번만 로그
                tc.log(f'epoch: {epoch}, batch: {batch_idx}/{len(train_loader)}, loss: {loss.item():.4f}')
            loss.backward()
            optimizer.step()

            # FrozenTrial은 pruning 지원하지 않음 (should_prune 항상 False)
            # 전체 데이터 학습이므로 pruning 불필요

    # ====================== 학습 완료 후 최종 모델 스냅샷 저장 ========================
    try:
        filename = f'{trial.study.study_name}_{trial.number}'
        model_path = join(ac.get_artifact_tmp_dir(), filename)
        # 모델 임시 폴더에 저장
        torch.save(
            model.state_dict(),
            model_path,
        )
        # optuna 에 artifact 업로드
        artifact_id = upload_artifact(
            artifact_store=ac.get_artifact_store(),
            storage=ac.get_storage(),
            study_or_trial=trial,
            file_path=model_path,
        )
        # artifact_id trial 에 user_attr 에 저장 (optuna dashboard 에서 확인하기 위함)
        trial.set_user_attr('artifact_id', artifact_id)
    except Exception as e:
        tc.log(f'Fail to save model file {filename}: {e}')

    # 검증 정확도 계산
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            _, pred = torch.max(outputs, 1)
            total += targets.size(0)
            correct += (pred == targets).sum().item()
    accuracy = correct / total
    tc.log(f'accuracy for test: {accuracy:.4f}')

    # FLOPS 계산
    dummy_input = torch.randn(1, 3, 32, 32).to(device)
    flops = FlopCountAnalysis(model, (dummy_input,)).total()

    return accuracy, flops
    # ====================== 외부 서버에서만 실행되는 코드 끝 ===========================


if __name__ == '__main__':
    # ======================= Multiple-objective study =========================
    study = ac.create_study(
        study_name='cifar10_torch_multiple_objective',
        sampler=optuna.samplers.TPESampler(),
        directions=['maximize', 'minimize'],  # accuracy maximize, FLOPS minimize
        # multi objective has no pruner
    )

    # ========================= subset data optimize ===========================
    study.optimize(
        objective_multi(),
        n_trials=100,
        parallelism=4,  # n_jobs 대신 parallelism 사용
        use_gpu=True,  # GPU 사용
        # runtime_image = "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",  # default image for use_gpu True
        # requirements.txt 대신 리스트로 전달 (외부 서버에서 설치)
        requirements_list=[
            'torch',
            'torchvision',
            'fvcore',  # FLOPS 계산용 (multi-objective 사용 시)
        ],
        # CallbackTopNArtifact은 클라이언트 측에서는 사용 불가 (runner 에서 자동으로 지정 됨)
    )

    for trial in study.best_trials[:5]:  # 상위 5개만
        print(f'  Best Values (Accuracy, FLOPS): {trial.values}')
        print(f'  Best Params:')
        for key, val in trial.params.items():
            print(f'    {key}: {val}')
        print()

    # ========================== full data optimize ============================
    # best_trial 의 파라미터를 사용해서 전체 데이터로 학습
    study.enqueue_trial(study.best_trial)
    study.optimize(
        objective_detailed,
        n_trials=1,  # enqueue 한 만큼만 실행
        parallelism=1,
        use_gpu=True,
        # runtime_image = "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",  # default image for use_gpu True
        requirements_list=['torch', 'torchvision', 'fvcore'],
    )
