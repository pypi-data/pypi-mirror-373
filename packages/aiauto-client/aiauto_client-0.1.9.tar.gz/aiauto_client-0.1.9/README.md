# AIAuto - Hyperparameter Optimization Client Library

AIAuto는 Kubernetes 기반의 분산 HPO(Hyperparameter Optimization) 시스템을 위한 클라이언트 라이브러리입니다.
사용자 python lib <-> Next.js 서버 사이 Connect RPC (HTTP/1.1) 통신 담당

## 설치
- `pip install aiauto-client optuna`

## API 레퍼런스

### create_study 파라미터
- `study_name` (str): Study 이름
- `direction` (str): 단일 목적 최적화 방향 ("minimize" 또는 "maximize")
- `directions` (List[str]): 다중 목적 최적화 방향 리스트 (direction과 상호 배타적)
- `sampler` (object/dict): Optuna sampler 객체 또는 dict (선택적)
- `pruner` (object/dict): Optuna pruner 객체 또는 dict (선택적)

**주의**: `direction`과 `directions`는 둘 중 하나만 지정해야 합니다.

### optimize 파라미터
- `objective` (Callable): Trial을 인자로 받는 목적 함수
- `n_trials` (int): 총 trial 수
- `parallelism` (int): 동시 실행 Pod 수 (기본값: 2)
- `requirements_file` (str): requirements.txt 파일 경로 (requirements_list와 상호 배타적)
- `requirements_list` (List[str]): 패키지 리스트 (requirements_file과 상호 배타적)
- `resources_requests` (Dict[str, str]): 리소스 요청 (기본값: {"cpu": "256m", "memory": "256Mi"})
- `resources_limits` (Dict[str, str]): 리소스 제한 (기본값: {"cpu": "256m", "memory": "256Mi"})
- `runtime_image` (str): 커스텀 런타임 이미지 (None이면 자동 선택)
- `use_gpu` (bool): GPU 사용 여부 (기본값: False)

**주의**: `requirements_file`과 `requirements_list`는 둘 중 하나만 지정해야 합니다.

## 지원 런타임 이미지 확인
```python
import aiauto

# 사용 가능한 이미지 확인
for image in aiauto.RUNTIME_IMAGES:
    print(image)
```

## 실행 흐름
### token 발급 # TODO
- `https://dashboard.aiauto.pangyo.ainode.ai` 에 접속하여 ainode 에 로그인 한 후
- `https://dashboard.aiauto.pangyo.ainode.ai/token` 으로 이동하여 aiauto 의 token 을 발급
- 아래 코드 처럼 발급한 token 을 넣어 AIAutoController singleton 객체를 초기화, OptunaWorkspace 를 활성화 시킨다
```python
import aiauto

ac = aiauto.AIAutoController('<token>')
```
- `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 OptunaWorkspace 와 optuna-dashboard 링크를 확인할 수 있음
- 아래 코드 처럼 study 를 생성하면 `https://dashboard.aiauto.pangyo.ainode.ai/study` 에서 확인할 수 있고 optuna-dashboard 링크에서도 확인 가능 
```python
study_wrapper = ac.create_study(
    study_name='test',
    direction='maximize',  # or 'minimize'
)
```
- 아래 코드 처럼 생성한 study 애서 objective 함수를 작성하여 넘겨주면 optimize 를 호출하면 `https://dashboard.aiauto.pangyo.ainode.ai/trialbatch` 에서 확인할 수 있고 optuna-dashboard 링크에서도 확인 가능
```python
study_wrapper.optimize(
    objective=func_with_parameter_trial,
    n_trials=4,
    parallelism=2,
    use_gpu=False,
    runtime_image=aiauto.RUNTIME_IMAGES[0],
)
```
- 종료 됐는지 optuna-dashboard 가 아닌 코드로 확인하는 법
```python
study_wrapper.get_status()
# {'study_name': 'test', 'count_active': 0, 'count_succeeded': 10, 'count_pruned': 0, 'count_failed': 0, 'count_total': 10, 'count_completed': 10, 'dashboard_url': 'https://optuna-dashboard-10f804bb-52be-48e8-aa06-9f5411ed4b0d.aiauto.pangyo.ainode.ai', 'last_error': '', 'updated_at': '2025-09-01T11:31:49.375Z'}
while study_wrapper.get_status()['count_completed'] <= study_wrapper.get_status()['count_total']:
    sleep(10)  # 10초 마다 한 번 씩
```
- best trial 을 가져오는 법
```python
TODO
```

## Jupyter Notebook 사용 시 주의사항

Jupyter Notebook이나 Python REPL에서 정의한 함수는 Serialize 할 수 없습니다
대신 `%%writefile` magic 울 사용하여 파일로 저장한 후 import 하세요.

### Jupyter에서 objective 함수 작성 방법
- objective 함수를 파일로 저장
```python
%%writefile my_objective.py
import aiauto
import optuna

def objective(trial: optuna.trial.Trial):
    """
    이 함수는 외부 서버에서 실행됩니다.
    모든 import는 함수 내부에 작성하세요.
    """
    import torch  # 함수 내부에서 import
    
    x = trial.suggest_float('x', -10, 10)
    y = trial.suggest_float('y', -10, 10)
    return (x - 2) ** 2 + (y - 3) ** 2
```
- 저장한 함수를 import해서 사용
```python
import aiauto
from my_objective import objective

ac = aiauto.AIAutoController('<token>')
study = ac.create_study('test', 'minimize')
study.optimize(objective, n_trials=10, parallelism=2)
```

## 빠른 시작

### 1. 간단한 예제 (수학 함수 최적화)

```python
import optuna
import aiauto


# `https://dashboard.aiauto.pangyo.ainode.ai` 에 접속하여 ainode 에 로그인 한 후 aiauto 의 token 을 발급
# AIAutoController singleton 객체를 초기화 하여, OptunaWorkspace 를 활성화 시킨다 (토큰은 한 번만 설정)
ac = aiauto.AIAutoController('<token>')
# `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 OptunaWorkspace 와 optuna-dashboard 링크를 확인할 수 있음

# StudyWrapper 생성
study_wrapper = ac.create_study(
    study_name="simple_optimization",
    direction="minimize"
    # sampler=optuna.samplers.TPESampler(),  # optuna 에서 제공하는 sampler 그대로 사용 가능, 참고 https://optuna.readthedocs.io/en/stable/reference/samplers/index.html
)
# `https://dashboard.aiauto.pangyo.ainode.ai/study` 에서 생성된 study 확인 가능

# objective 함수 정의
def objective(trial: optuna.trial.Trial):
    """실제 실행은 사용자 로컬 컴퓨터가 아닌 서버에서 실행 될 함수"""
    x = trial.suggest_float('x', -10, 10)
    y = trial.suggest_float('y', -10, 10)
    return (x - 2) ** 2 + (y - 3) ** 2

# 사용자 모델 학습 or 최적화 실행 (서버에서 병렬 실행)
study_wrapper.optimize(
    objective,
    n_trials=100,
    parallelism=4  # 동시 실행 Pod 수
)
# `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 optuna-dashboard 링크에서 결과 확인 가능
```

### 2. PyTorch 모델 최적화 (Single Objective)

```python
import optuna
import aiauto


# `https://dashboard.aiauto.pangyo.ainode.ai` 에 접속하여 ainode 에 로그인 한 후 aiauto 의 token 을 발급
# AIAutoController singleton 객체를 초기화 하여, OptunaWorkspace 를 활성화 시킨다 (토큰은 한 번만 설정)
ac = aiauto.AIAutoController('<token>')
# `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 OptunaWorkspace 와 optuna-dashboard 링크를 확인할 수 있음

# StudyWrapper 생성
study_wrapper = ac.create_study(
    study_name="pytorch_optimization",
    direction="minimize",
    # sampler=optuna.samplers.TPESampler(),  # optuna 에서 제공하는 sampler 그대로 사용 가능, 참고 https://optuna.readthedocs.io/en/stable/reference/samplers/index.html
    pruner=optuna.pruners.PatientPruner(  # optuna 에서 제공하는 pruner 그대로 사용 가능, 참고 https://optuna.readthedocs.io/en/stable/reference/pruners.html
        optuna.pruners.MedianPruner(),
        patience=4,
    ),
)
# `https://dashboard.aiauto.pangyo.ainode.ai/study` 에서 생성된 study 확인 가능

# objective 함수 정의
# https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html 참고
def objective(trial: optuna.trial.Trial):
    """
    실제 실행은 사용자 로컬 컴퓨터가 아닌 서버에서 실행 될 함수
    모든 import는 함수 내부에 존재해야 함
    """
    import torch
    from torch import nn, optim
    from torch.utils.data import DataLoader, random_split, Subset
    from torchvision import transforms, datasets
    import torch.nn.functional as F

    # 하이퍼파라미터 샘플링
    lr = trial.suggest_float('learning_rate', 1e-5, 1e-1, log=True)
    momentom = trial.suggest_float('momentom', 0.1, 0.99)
    batch_size = trial.suggest_categorical('batch_size', [16, 32, 64, 128])
    epochs = trial.suggest_int('epochs', 10, 100, step=10)
    
    # 모델 정의
    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 6, 5)
            self.pool = nn.MaxPool2d(2, 2)
            self.conv2 = nn.Conv2d(6, 16, 5)
            self.fc1 = nn.Linear(16 * 5 * 5, 120)
            self.fc2 = nn.Linear(120, 84)
            self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x 
    
    # 모델 정의 및 학습 (GPU 자동 사용)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = Net().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentom)
    
    # 데이터 로드
    train_set = datasets.CIFAR10(
        root="/tmp/cifar10_data",  # Pod의 임시 디렉토리 사용
        train=True,
        download=True,
        transform=[
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ],
    )
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2)

    test_set = datasets.CIFAR10(
        root="/tmp/cifar10_data",  # Pod의 임시 디렉토리 사용
        train=False,
        download=True,
        transform=[
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ],
    )
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=True, num_workers=2)
    
    # 학습
    min_epochs_for_pruning = max(50, epochs // 5)  # 최소 50 epoch 또는 전체의 1/5 후부터 pruning
    total_loss = 0.0
    for epoch in range(epochs):  # loop over the dataset multiple times
        running_loss = 0.0
        model.train()
        for i, (inputs, targets) in enumerate(train_loader, 0):
            inputs, targets = inputs.to(device), targets.to(device)
            # zero the parameter gradients
            optimizer.zero_grad()
            # forward + backward + optimize
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
    
            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:    # print every 2000 mini-batches
                print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')
        
        # intermediate result 보고 및 초기 중단 검사 - 최소 epochs 후 부터만 pruning
        trial.report(running_loss, epoch)
        total_loss += running_loss
        if epoch >= min_epochs_for_pruning and trial.should_prune():
            raise optuna.TrialPruned()
        
    return total_loss

# GPU Pod에서 실행
study_wrapper.optimize(
    objective,
    n_trials=100,
    parallelism=4,
    use_gpu=True,  # GPU 사용
    requirements_list=['torch', 'torchvision']  # Pod에서 자동 설치
)
```

### 3. Multi-Objective 최적화 (Accuracy + FLOPS)

```python
import optuna
import aiauto


# `https://dashboard.aiauto.pangyo.ainode.ai` 에 접속하여 ainode 에 로그인 한 후 aiauto 의 token 을 발급
# AIAutoController singleton 객체를 초기화 하여, OptunaWorkspace 를 활성화 시킨다 (토큰은 한 번만 설정)
ac = aiauto.AIAutoController('<token>')
# `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 OptunaWorkspace 와 optuna-dashboard 링크를 확인할 수 있음

# StudyWrapper 생성
study_wrapper = ac.create_study(
    study_name="pytorch_multiple_optimization",
    direction=["minimize", "minimize"],  # loss minimize, FLOPS minimize
    # sampler=optuna.samplers.TPESampler(),  # optuna 에서 제공하는 sampler 그대로 사용 가능, 참고 https://optuna.readthedocs.io/en/stable/reference/samplers/index.html
)
# `https://dashboard.aiauto.pangyo.ainode.ai/study` 에서 생성된 study 확인 가능

# objective 함수 정의
# https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html 참고
def objective(trial: optuna.trial.Trial):
    """
    실제 실행은 사용자 로컬 컴퓨터가 아닌 서버에서 실행 될 함수
    모든 import는 함수 내부에 존재해야 함
    """
    import torch
    from torch import nn, optim
    from torch.utils.data import DataLoader, random_split, Subset
    from torchvision import transforms, datasets
    import torch.nn.functional as F
    from fvcore.nn import FlopCountAnalysis

    # 하이퍼파라미터 샘플링
    lr = trial.suggest_float('learning_rate', 1e-5, 1e-1, log=True)
    momentom = trial.suggest_float('momentom', 0.1, 0.99)
    batch_size = trial.suggest_categorical('batch_size', [16, 32, 64, 128])
    epochs = trial.suggest_int('epochs', 10, 100, step=10)

    # 모델 정의
    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 6, 5)
            self.pool = nn.MaxPool2d(2, 2)
            self.conv2 = nn.Conv2d(6, 16, 5)
            self.fc1 = nn.Linear(16 * 5 * 5, 120)
            self.fc2 = nn.Linear(120, 84)
            self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

        # 모델 정의 및 학습 (GPU 자동 사용)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = Net().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentom)

    # 데이터 로드
    train_set = datasets.CIFAR10(
        root="/tmp/cifar10_data",  # Pod의 임시 디렉토리 사용
        train=True,
        download=True,
        transform=[
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ],
    )
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2)

    test_set = datasets.CIFAR10(
        root="/tmp/cifar10_data",  # Pod의 임시 디렉토리 사용
        train=False,
        download=True,
        transform=[
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ],
    )
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=True, num_workers=2)

    # 학습
    total_loss = 0.0
    # multiple objective 는 pruning 미지원
    for epoch in range(epochs):  # loop over the dataset multiple times
        running_loss = 0.0
        model.train()
        for i, (inputs, targets) in enumerate(train_loader, 0):
            inputs, targets = inputs.to(device), targets.to(device)
            # zero the parameter gradients
            optimizer.zero_grad()
            # forward + backward + optimize
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:    # print every 2000 mini-batches
                print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')

        # multiple objective 는 pruning 미지원
    
    # FLOPS 계산
    dummy_input = torch.randn(1, 3, 32, 32).to(device)
    flops = FlopCountAnalysis(model, (dummy_input,)).total()
        
    return total_loss, flops

# GPU Pod에서 실행
study_wrapper.optimize(
    objective,
    n_trials=100,
    parallelism=4,
    use_gpu=True,  # GPU 사용
    requirements_list=['torch', 'torchvision', 'fvcore']  # Pod에서 자동 설치
)
```

### 4. Ask/Tell 패턴 및 Optuna 자체의 Study

```python
import optuna
import aiauto

# `https://dashboard.aiauto.pangyo.ainode.ai` 에 접속하여 ainode 에 로그인 한 후 aiauto 의 token 을 발급
# AIAutoController singleton 객체를 초기화 하여, OptunaWorkspace 를 활성화 시킨다 (토큰은 한 번만 설정)
ac = aiauto.AIAutoController('<token>')
# `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 OptunaWorkspace 와 optuna-dashboard 링크를 확인할 수 있음 

# Study 생성
study_wrapper = ac.create_study(
    study_name="test",
    direction='minimize',
    # sampler=optuna.samplers.TPESampler(),  # optuna 에서 제공하는 sampler 그대로 사용 가능, 참고 https://optuna.readthedocs.io/en/stable/reference/samplers/index.html
    # pruner=optuna.pruners.PatientPruner(  # optuna 에서 제공하는 pruner 그대로 사용 가능, 참고 https://optuna.readthedocs.io/en/stable/reference/pruners.html
    #     optuna.pruners.MedianPruner(),
    #     patience=4,
    # )
)
# `https://dashboard.aiauto.pangyo.ainode.ai/study` 에서 생성된 study 확인 가능

# 실제 optuna.Study 객체 획득 (로컬에서 ask/tell 가능)
study = study_wrapper.get_study()

# Ask/Tell 패턴으로 최적화
trial = study.ask()

# 파라미터 최적화
x = trial.suggest_float('x', -10, 10)
y = trial.suggest_float('y', -10, 10)

# 사용자 모델 학습 or 최적화 실행 (서버에서 병렬 실행)
ret = (x - 2) ** 2 + (y - 3) ** 2

# 결과 보고
study.tell(trial, ret)
# `https://dashboard.aiauto.pangyo.ainode.ai/workspace` 에서 생성된 optuna-dashboard 링크에서 결과 확인 가능
```

# lib build
```bash
make build push
```
