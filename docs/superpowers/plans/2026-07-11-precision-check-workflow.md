# Precision Check Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 解耦三平台 full 与29项精度 check，修复 Linux 环境采集失败，并通过 artifact 保存完整诊断证据。

**Architecture:** Linux/macOS 共用源码验证 job 与 Bash runner，Windows 使用独立的 installed-wheel job 与 PowerShell runner。公共环境采集器和统一结果目录构成 artifact 契约，full 工作流不复用新 check 入口。

**Tech Stack:** GitHub Actions YAML、Bash、PowerShell、Python 标准库、`unittest`。

## Global Constraints

- Full 仅 `workflow_dispatch`，且不改变内部打包验证逻辑。
- Check 矩阵固定为 Ubuntu 3.8/3.12/3.13、macOS 3.8/3.13、Windows 3.12/3.13。
- 第一阶段每项测试只运行1次；7组合全部通过后才能改为100次。
- 不安装新的本地 Python 包。
- 不修改29项 node ID、数值容差或 PySCF 数值代码。
- 所有 artifact 使用 `actions/upload-artifact@v7`。

---

### Task 1: 固化工作流结构测试

**Files:**
- Modify: `tools/windows/tests/test_windows_ci_workflow.py`
- Create: `tools/windows/tests/test_precision_check_workflow.py`

**Interfaces:**
- Consumes: GitHub Actions YAML 和 runner 文本。
- Produces: 对 full/check 触发器、7项矩阵、脚本边界及 artifact 契约的静态回归检查。

- [ ] 编写失败测试，断言新工作流存在、旧工作流消失、矩阵恰为7项、无 `continue-on-error`、上传 artifact，并断言 Windows full 不再包含 check job。
- [ ] 运行 `python -m unittest tools.windows.tests.test_precision_check_workflow tools.windows.tests.test_windows_ci_workflow -v`，确认因目标结构尚不存在而失败。
- [ ] 仅在测试表达错误时修正测试，不创建生产文件。

### Task 2: 修复环境采集器 namespace 崩溃

**Files:**
- Create: `tools/windows/tests/test_collect_precision_environment.py`
- Modify: `.github/workflows/collect_precision_environment.py`

**Interfaces:**
- Consumes: 可选的 `pyscf` module，其中 `__file__` 可以为 `None`。
- Produces: `native_libraries(module)` 始终返回列表且不会因 namespace package 崩溃。

- [ ] 编写失败测试，构造 `types.SimpleNamespace(__file__=None)` 并断言 `native_libraries` 返回空列表。
- [ ] 运行该测试并确认出现与运行 `29136144582` 相同的 `TypeError`。
- [ ] 在 `native_libraries` 开头读取 `__file__`；为空时直接返回 `[]`。
- [ ] 重新运行测试，确认通过。

### Task 3: 整理 check/full 工作流和脚本

**Files:**
- Create: `.github/workflows/ci-precision-check.yml`
- Modify: `.github/workflows/ci-windows.yml`
- Delete: `.github/workflows/ci-linux-precision.yml`
- Rename: `.github/workflows/run_linux_precision_tests.sh` to `.github/workflows/run_unix_precision_tests.sh`
- Rename: `.github/workflows/ci-precision-diagnostics.yml` to `.github/workflows/tmp/ci-precision-diagnostics.yml`
- Rename: `.github/workflows/precision_experiments.py` to `.github/workflows/tmp/precision_experiments.py`

**Interfaces:**
- Consumes: `precision-selected-nodeids.txt`、平台构建脚本、两个 check runner。
- Produces: 7组合自动 check、两个仅手动 full 工作流和冻结 diagnostics 归档。

- [ ] 新工作流创建 `precision-unix` 与 `precision-windows` 两个 job，配置批准的矩阵和触发器。
- [ ] Unix job 在 build/test 采集前导出仓库源码 `PYTHONPATH`，调用 `run_unix_precision_tests.sh`。
- [ ] Windows job 调用 `run_windows_precision_tests.ps1`，不经过 `run_ci_windows.ps1`。
- [ ] 两个 job 使用 `if: always()` 上传 `tmp/precision-results`；Windows同时纳入 build logs。
- [ ] 从 `ci-windows.yml` 删除 check、push、PR、schedule 和 full 永久禁用条件，只保留手动 full。
- [ ] 原样移动两个 diagnostics 文件，不改内部内容。
- [ ] 运行 Task 1 和 Task 2 的测试，确认全部通过。

### Task 4: 静态验证并提交单次 check

**Files:**
- Verify all files above.

**Interfaces:**
- Consumes: 完成的工作流与测试。
- Produces: 可推送的单次 check 提交。

- [ ] 用 PowerShell/YAML 文本检查确认7个矩阵组合、每项1次、两个排除组合不存在。
- [ ] 运行全部 `tools/windows/tests` 静态测试。
- [ ] 检查 `git diff --check` 与 `git status --short`。
- [ ] 提交实现并推送 `win64-CI`。

### Task 5: 运行并巡查单次矩阵

**Files:**
- No repository changes unless a CI bug is confirmed.

**Interfaces:**
- Consumes: GitHub Actions run、job logs、7份 artifact。
- Produces: 7组合各完成29项且每项1次的证据。

- [ ] 定位 push 触发的 `ci-precision-check` run id。
- [ ] 每15分钟检查7个 job；基础设施/脚本早期失败时读取完整日志并停止100次阶段。
- [ ] 对确认的 bug 先增加最小回归测试，再实施修复、验证、提交、推送和重新运行。
- [ ] 下载或检查每份 artifact，确认名单、CSV、日志和环境文件齐全。
- [ ] 只有7个 job 都记录29个测试且零失败时进入 Task 6。

### Task 6: 提升到100次并运行

**Files:**
- Modify: `.github/workflows/run_unix_precision_tests.sh`
- Modify: `.github/workflows/run_windows_precision_tests.ps1`

**Interfaces:**
- Consumes: 已通过的单次矩阵。
- Produces: 每个平台每项测试100次的矩阵运行。

- [ ] 先更新静态测试，要求两个 runner 的重复次数为100，并确认测试失败。
- [ ] 将 Unix `repeats` 和 Windows传给验证器及 runner metadata 的重复次数改为100。
- [ ] 运行静态测试、`git diff --check`，提交并推送。
- [ ] 巡查100次运行并报告每个组合的完成度、失败频率和 artifact 状态；不自动放宽数值容差。

