# `.github/workflows` CI 流程地图

本文记录当前分支三平台 full 验证、精度 check 以及相关脚本的职责。运行状态不写入本文，以免随 GitHub Actions 运行变化而过期。

## 总览

| 流程 | 平台与版本 | 触发方式 | 验证对象 | 入口 |
| --- | --- | --- | --- | --- |
| Full | Linux 3.8/3.12、Linux aarch64 3.9、macOS 3.13 | `workflow_dispatch` | 源码构建后的完整测试 | `ci.yml` |
| Windows full | Windows 3.13 | `workflow_dispatch` | 干净环境中安装 wheel 后的完整测试 | `ci-windows.yml` |
| Precision check | Linux 3.8/3.12/3.13、macOS 3.8/3.13、Windows 3.12/3.13 | `push`、`pull_request`、`workflow_dispatch` | `precision-selected-nodeids.txt` 中的10项待排查测试 | `ci-precision-check.yml` |
| Precision diagnostics | 同上，可按平台筛选 | `workflow_dispatch` | 选择一个诊断族，保存计算中间量和限量快照 | `ci-precision-diagnostics.yml` |

暂时排除 macOS 3.12 和 Windows 3.8。Precision check 使用 `fail-fast: false`，但不允许失败；一个组合失败不会取消其他组合，最终工作流仍会失败。

100次阶段按 node ID 分成3个分片；每个平台/版本产生3个 job，共21个 job。每个 node ID 只属于一个分片，并在该分片中完整运行100次。完成29项筛选实验后，名单已缩减到10项。

## Full 验证

### Linux 与 macOS

```text
ci.yml
└─ run_ci.sh
   ├─ ci_linux|ci_macos/deps_apt.sh
   ├─ ci_linux|ci_macos/python_deps.sh
   ├─ ci_linux|ci_macos/build_pyscf.sh
   └─ run_tests.sh
      └─ pytest pyscf/
```

- `ci.yml` 只允许手动触发。
- Linux/macOS 在源码树构建动态库，并在源码环境运行完整测试。
- Linux aarch64 使用 manylinux 容器中的独立构建与测试命令。
- 这条流程与 precision check 分离，本轮不调整内部逻辑。

### Windows

```text
ci-windows.yml: windows-build-full
└─ run_ci_windows.ps1 -Mode full
   ├─ ci_windows/create_build_env.ps1
   ├─ ci_windows/build_wheel_ci.ps1
   ├─ ci_windows/create_test_env.ps1
   └─ ci_windows/run_tests.ps1
      └─ ci_windows/verify_installed_wheel_ci.ps1 -Mode full
```

- `ci-windows.yml` 只允许手动触发。
- 使用 Conda 和 MSYS2/UCRT64 构建 wheel。
- 在独立测试环境安装 wheel，清空源码 `PYTHONPATH`，暂存测试目录后运行完整验证。
- `run_ci_windows.ps1` 仍保留 `check`/`full` 两种模式，但新 precision check 不再经过这个入口。

## Precision check

`ci-precision-check.yml` 包含两个 job。

### Linux 与 macOS：`precision-unix`

```text
ci-precision-check.yml
├─ ci_linux|ci_macos/deps_apt.sh
├─ ci_linux|ci_macos/python_deps.sh
├─ ci_linux|ci_macos/build_pyscf.sh
├─ collect_precision_environment.py   # build 环境
└─ run_unix_precision_tests.sh
   ├─ collect_precision_environment.py # test 环境
   └─ 逐项运行 precision-selected-nodeids.txt
```

- Linux/macOS 保持源码构建验证。
- 采集 build 环境前设置仓库源码 `PYTHONPATH`，避免将插件提供的 namespace package 误认为完整 PySCF。
- `run_unix_precision_tests.sh` 负责名单读取、逐项日志、CSV 和 Markdown 汇总。

### Windows：`precision-windows`

```text
ci-precision-check.yml
└─ run_windows_precision_tests.ps1
   ├─ ci_windows/create_build_env.ps1
   ├─ ci_windows/build_pyscf.ps1
   ├─ collect_precision_environment.py # build 环境
   ├─ ci_windows/create_test_env.ps1
   ├─ ci_windows/verify_installed_wheel_ci.ps1 -Mode check
   └─ collect_precision_environment.py # test 环境
```

- Windows check 构建 wheel，并在干净测试环境安装后验证。
- `PYTHONPATH` 在验证期间被清空，避免从源码树导入。
- 10项名单作为文件传给 installed-wheel 验证器。

## Precision diagnostics

`ci-precision-diagnostics.yml` 只允许手动触发，不是 PR gating check。输入选择诊断族、重复次数、平台族和线程数。Unix 复用现有源码构建脚本；Windows 通过 `run_windows_precision_diagnostics.ps1` 构建并安装 wheel，再在清空 `PYTHONPATH` 的测试环境运行同一个 `precision_experiments.py`。

诊断脚本覆盖9个实验族，其中 `eom` 同时覆盖 IP/EA 两个 nodeid。每次尝试写入 JSONL 标量和数组 fingerprint；完整 NPZ 仅保存首个通过样本以及每种失败签名的首个样本。

## Artifact 内容

每个矩阵组合都通过 `actions/upload-artifact@v7` 上传 `tmp/precision-results/`，即使测试失败也执行上传步骤。

通用内容：

- `selected-nodeids.txt`
- `attempts.csv`、`summary.csv`、`summary.md`
- `logs/` 中每项测试的完整 pytest 日志
- `environment/build/` 与 `environment/test/`
- `runtime.json`、`pip-freeze.txt`、`pip-list.json`、`pip-check.txt`
- `runner-config.txt`
- Python、系统镜像、线程变量、编译器、CMake、原生库哈希与链接信息

Windows 另外包含：

- `wheel-metadata.json`
- build/test Conda 清单
- installed-wheel Markdown/JSON 报告
- `.github/workflows/ci_windows/build-logs/`

下载7份 artifact 后，可以比较失败频率、完整错误日志、包版本、编译环境、原生库及 wheel 信息，并据此生成跨平台分析报告。

100次分片运行会产生21份 artifact，名称带 `shard-0`、`shard-1` 或 `shard-2`。同一平台的3份 `summary.csv` 和 `attempts.csv` 合并后覆盖原来的29项，每项仍有100次记录。

## 文件职责

| 文件 | 职责 |
| --- | --- |
| `ci.yml` | Linux/macOS full 工作流 |
| `ci-windows.yml` | Windows full 工作流 |
| `ci-precision-check.yml` | 三平台10项精度 check |
| `ci-precision-diagnostics.yml` | 手动、非 gating 的计算路径诊断 |
| `precision-selected-nodeids.txt` | 三平台共享的10项待排查 node ID |
| `precision_experiments.py` | 9类诊断入口、中间量与限量快照记录器 |
| `run_ci.sh`、`run_tests.sh` | Linux/macOS full 调度与测试 |
| `run_ci_windows.ps1` | Windows full 主调度，保留旧 check 入口 |
| `run_unix_precision_tests.sh` | Linux/macOS precision check runner |
| `run_windows_precision_tests.ps1` | Windows precision check runner |
| `run_windows_precision_diagnostics.ps1` | Windows installed-wheel diagnostics runner |
| `collect_precision_environment.py` | 三平台环境、包和原生库证据采集 |
| `ci_linux/`、`ci_macos/` | Unix 平台依赖与源码构建脚本 |
| `ci_windows/` | Windows 环境、wheel 构建和 installed-wheel 验证脚本 |

## 暂存内容

`.github/workflows/tmp/` 不会被 GitHub Actions 当作工作流目录加载。当前暂存实验原始数据、报告和本文档。diagnostics workflow 与脚本已移回 `.github/workflows/`，可被 GitHub Actions 识别，但仍只接受手动触发。
