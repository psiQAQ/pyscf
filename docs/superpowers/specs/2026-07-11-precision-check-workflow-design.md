# Precision Check Workflow Design

## 目标

将三平台 full 验证与29项精度 check 解耦。full 暂时仅允许手动触发；check 在 Linux、macOS、Windows 的指定 Python 矩阵上自动运行，并保留足以生成跨平台分析报告的原始 artifact。

## 工作流边界

- `.github/workflows/ci.yml` 保留 Linux/macOS full，仅使用 `workflow_dispatch`，不修改内部流程。
- `.github/workflows/ci-windows.yml` 删除 check，只保留 Windows full，仅使用 `workflow_dispatch`；移除永久禁用条件，但不修改 full 的步骤和参数。
- 新建 `.github/workflows/ci-precision-check.yml`，响应 `push`、`pull_request`、`workflow_dispatch`。
- 删除 `.github/workflows/ci-linux-precision.yml`。

## Check 矩阵

- `precision-unix`：Ubuntu 3.8、3.12、3.13；macOS 3.8、3.13。
- `precision-windows`：Windows 3.12、3.13。
- 排除 macOS 3.12 与 Windows 3.8。
- `fail-fast: false`，不使用 `continue-on-error`。
- 第一阶段每个 node ID 运行1次；7个组合全部完成且通过后，第二阶段改为100次。

## 平台验证方式

- Linux/macOS 复用源码依赖安装和动态库构建脚本，通过重命名后的 `run_unix_precision_tests.sh` 执行名单。
- Windows 复用 `run_windows_precision_tests.ps1`，构建 wheel、安装到干净 Conda 环境并清空 `PYTHONPATH` 后验证。
- `run_ci_windows.ps1` 保持不变，避免影响 full。

## Linux 失败修复

运行 `29136144582` 的三个 Linux job 均在环境采集阶段失败，测试未启动。Linux 安装的 `pyscf-dispersion` 暴露 `pyscf` namespace package，其 `__file__` 为 `None`；采集器直接构造 `Path(pyscf.__file__)` 导致 `TypeError`。

修复同时采用两层措施：Linux/macOS 在采集前设置仓库源码 `PYTHONPATH`；采集器仍防御 `__file__ = None`，避免 namespace package 再次中断诊断。

## Artifact 契约

每个矩阵组合使用 `actions/upload-artifact@v7`，即使测试失败也上传：

- `selected-nodeids.txt`、`attempts.csv`、`summary.csv`、`summary.md`；
- 每项测试的完整日志；
- build/test 两阶段的 `runtime.json`、`pip-freeze.txt`、`pip-list.json`、`pip-check.txt`、`runner-config.txt`；
- runner、Python、线程、编译器、CMake、原生库哈希与链接信息；
- Windows 额外包含 wheel 元数据、Conda 清单与构建日志。

CI 不自动生成跨矩阵总报告；下载7份 artifact 后应能生成与 `tmp/ci-precision-29099553026-analysis.md` 信息范围相近的报告。

## 暂存专项诊断

将以下文件原样移动到 `.github/workflows/tmp/`，不修改内部内容：

- `ci-precision-diagnostics.yml`
- `precision_experiments.py`

它们不参与29项 check，暂时不被 GitHub Actions 加载。

