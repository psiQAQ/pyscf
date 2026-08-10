# SGX HSE06 Extra-cycle 遥测设计

## 状态

- 对话设计：已批准。
- 本文档：等待用户复核。
- 实现、推送和远端诊断 CI：尚未开始。

## 背景

调查基线为 `codex/investigate/libxc-712-release-revalidation@07c0641e9dcb97930ed0fb4b5014b61132e962b4`。该提交包含 PySCF 2.14.0、LibXC 7.1.2、`MAXORDER=3`、Windows installed-wheel 精度 runner 和 schema-v2 runtime provenance；`pyscf/sgx/grad/test/test_rks.py` 与实时 `pyscf/pyscf:master@aa2ad20897104dead09d53fc532a5d3b34203d83` 完全一致。

正式 `omp4-blas1` 波覆盖七个 OS/Python 组合、三个原 nodeid、每项 200 次，共 4,200 次原 pytest attempt。4,199 次通过；唯一失败为：

- run `31345422470`，Windows Python 3.12.10；
- `pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad`；
- attempt 95，settings-2/HSE06；
- analytic `g[0,2] = 0.00679004385313231`；
- finite difference `0.006788983797758873`；
- difference `1.0600553734373824e-06`，原 `assertAlmostEqual(..., places=6)` 失败。

该 artifact 的 wheel、LibXC 7.1.2、pip、import、26 个 DLL linkage、records、CSV 和日志引用均有效，因此这是科学断言失败，不是 packaging 或 evidence-pipeline 故障。现有日志因测试把 SCF 输出发送到 `/dev/null`，不能直接证明当前失败发生在 Extra cycle。

历史同一子例曾证明：位移 scanner 主循环收敛后，默认 Extra cycle 可把一个位移能量移动约 `2.63e-10 Ha`，经中心有限差分放大为约 `7.18e-7` 的梯度误差。当前误差对应约 `4.0064e-10 Ha` 的正负位移差分能量扰动，量级相容，但“当前仍为同一根因”只是待检验假设。

## 目标

1. 在不改变科学输入或原断言的前提下，捕获 base、plus 和 minus 三个 SCF phase 的最后主循环能量与 kernel 返回能量。
2. 从同一 attempt 重算 pre-extra 与 post-extra finite difference，判断 Extra-cycle energy shift 是否完整解释当前 mismatch。
3. 若 Extra cycle 被证伪，保留足够边界证据以决定是否升级到 density/Fock/`veff` 指纹诊断。
4. 诊断代码只存在于隔离调查分支；最终上游 RED/GREEN 必须从提交时实时 upstream master 另建最小分支。

## 非目标

- 不修改 `delta=1e-4`、`conv_tol=1e-12`、`conv_check=True`、`max_cycle`、线程 profile 或 LibXC 版本。
- 不放宽、替换或重试原六位断言。
- 不把 `0/200` 解释为稳定、已修复或可关闭门禁。
- 不复用已被维护者否决的 test-only `mf_scanner.conv_check=False` 作为最终修复。
- 不移植旧 `precision_experiments.py` 大型诊断框架，除非标量遥测证明分叉早于 Extra cycle。

## 设计概览

采用两阶段实验。

### Stage 1：隔离子例

新增独立诊断 nodeid，仅运行 settings-2/HSE06。Windows Python 3.12、`omp4-blas1` 重复 200 次。它把每个 attempt 从九个子例降为一个，先以较低成本获取干净的机制证据。

若 Stage 1 捕获至少一个完整 failure 和一个完整 pass，立即停止扩展并判别机制。若 `0/200`，不能作稳定性结论，进入 Stage 2。

### Stage 2：恢复原顺序

选择原 `test_finite_diff_grad` nodeid，保持 settings 0/1 和前七个 XC 子例照常执行，只在第八个 settings-2/HSE06 子例启用相同遥测。该阶段恢复 attempt 95 所处的 warm/cache/allocator 顺序。

Stage 2 只在 Stage 1 `0/200` 后通过独立 follow-up commit 启用，避免预先扩大 Stage 1 改动。若 Stage 2 `0/200`，状态为 `NOT_REPRODUCED/HOLD`，不继续派发其他 profile 或完整矩阵。

## 组件与数据流

### 1. 可选标量遥测

现有 `_check_finite_diff_grad` 增加默认关闭的可选 telemetry 参数。原 `test_finite_diff_grad` 在 Stage 1 提交中保持原调用和数值行为。

启用时：

1. 创建与原测试相同的 SGX RKS 对象并应用相同 settings，把外部 `phase` 初始化为 `base`。
2. 在调用 base `gradient.kernel()` 之前安装只读 callback。
3. callback 根据 `phase` 记录 base、plus、minus，且每次立即复制所需 scalar；不得保存 `envs`/`locals()` 原引用。
4. base gradient 返回后立即保存 `mf.e_tot` 和 `mf.converged`，然后才调用 `mf.as_scanner()`。
5. 把 `phase` 切到 `plus` 并调用 scanner；返回后立即保存 `e1` 和 `mf_scanner.converged`。只有保存完成后才能把 `phase` 切到 `minus`，随后同样立即保存 `e2` 和 scanner convergence，避免 minus 覆盖 plus 状态。
6. 每个 phase 的最后 callback energy 是最后主循环 energy。只有最后 callback 的 `scf_conv=True` 且 `conv_check=True` 时，`extra_executed=True`，post energy 与 main energy 之差定义为有限的 Extra-cycle shift；否则 `extra_executed=False` 且 `extra_shift=null`。
7. 计算 translation 与 finite-difference 诊断字段，并在原两条 assertion 之前输出恰好一行 JSON marker。

callback 立即复制以下字段：

- `cycle = envs['cycle'] + 1`；
- `e_tot`、`last_hf_e`、`e_tot - last_hf_e`；
- `norm_gorb`、`norm_ddm`；
- `scf_conv`、`conv_tol`、`conv_tol_grad`、`conv_check`。

Python frame 的 locals 可能被后续 `locals()` 刷新，因此保存原 `envs` 引用会污染 main-loop 证据，是禁止实现。

### 2. 不覆盖 SGX `post_kernel`

`pyscf/sgx/sgx.py` 的 `post_kernel()` 负责把 `_in_scf` 恢复为 `False`。诊断不得 monkeypatch 或替换该 hook，否则会改变后续 SGX grid/reset 行为。

只读 callback 加 kernel 返回值足以完成 energy-shift closure。该设计不记录 Extra-cycle 的 `norm_gorb`、`norm_ddm` 或 relaxed-OR 命中分支，因此结论仅限于“Extra-cycle energy shift 是否解释 finite-difference mismatch”，不得表述为完整 Extra-cycle gate telemetry。

### 3. Marker schema

每个有效 attempt 在 assertion 前输出一行：

```text
PYSCF_SGX_HSE06_TELEMETRY_V1 {json}
```

payload 的 `schema_version` 固定为整数 `1`，至少包含：

```text
schema_version
units.energy
units.gradient
units.displacement
case.settings_index
case.settings
case.precision
case.xc
case.delta
case.translation_places
case.finite_difference_places
phases.base.main
phases.base.post_energy
phases.base.post_converged
phases.base.extra_executed
phases.base.extra_shift
phases.plus.main
phases.plus.post_energy
phases.plus.post_converged
phases.plus.extra_executed
phases.plus.extra_shift
phases.minus.main
phases.minus.post_energy
phases.minus.post_converged
phases.minus.extra_executed
phases.minus.extra_shift
result.analytic_gradient
result.translation_l1
result.translation_assertion_pass
result.finite_difference_pre
result.finite_difference_post
result.gradient_error_pre
result.gradient_error_post
result.finite_difference_pre_pass
result.finite_difference_post_pass
result.extra_contribution
result.closure_residual
```

定义：

```text
fd_pre  = (E_plus_main - E_minus_main) / (2 * delta) * BOHR
fd_post = (E_plus_post - E_minus_post) / (2 * delta) * BOHR
extra_contribution = fd_post - fd_pre
error_pre  = analytic_gradient - fd_pre
error_post = analytic_gradient - fd_post
closure_residual = error_post - (error_pre - extra_contribution)
```

`closure_residual` 按上述定义是算术一致性 invariant，不是独立的机制证据。机制判定必须同时检查同一 failure 的 pre/post 原断言语义，以及 `fd_post - fd_pre` 是否与 plus/minus 两个逐 phase `extra_shift` 的差分方向和量级一致。

单位固定为：energy=`Hartree`、gradient=`Hartree/Bohr`、displacement=`Angstrom`；SCF norm 保存 PySCF 原始 atomic-unit scalar。除条件性 `extra_shift=null` 外，所有数值字段必须是有限实数；`extra_executed=True` 时对应 shift 必须有限，`extra_executed=False` 时对应 shift 必须为 null。`translation_assertion_pass` 精确镜像原 `assertAlmostEqual(translation_l1, 0, places=12)` 的 `round(abs(translation_l1), 12) == 0` 语义；finite-difference 的 pre/post pass 字段同样使用 `round(abs(error), 6) == 0`。这些字段用于区分第一条平移断言和第二条 finite-difference 断言，实际 pytest assertion 仍是唯一 pass/fail gate，顺序与参数保持不变。

marker 只包含 scalar 和已有计算结果，避免复制 density/Fock/`veff` 数组造成明显 timing 或 allocator 扰动。runner 已用 pytest `-s`、`capture_output=True` 并无条件写入逐 attempt log，无需修改 runner 或 workflow。

## 文件范围

除本文档外，Stage 1 实现 commit 只修改三个文件：

1. `pyscf/sgx/grad/test/test_rks.py`：可选 telemetry 与独立诊断 method；
2. `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt`：仅含独立诊断 nodeid；
3. `.github/workflows/test_precision_investigation_contract.py`：selection 与 marker evidence contract。

不修改：

- `.github/workflows/ci-precision-check.yml`；
- `.github/workflows/run_precision_tests.py`；
- Windows build/verification scripts；
- PySCF production modules、LibXC 配置或依赖文件。

## RED/GREEN 与本地验证

### RED

1. 先增加 selection contract；因 selection 文件不存在而失败。
2. selection 指向尚不存在的 exact diagnostic nodeid；`pytest --collect-only` 失败。

### GREEN

1. selection contract 调用现有 `load_runner().load_nodeids()`，断言只返回 exact diagnostic nodeid。
2. 复用既有 failed-attempt runner 集成测试：临时 pytest fixture 输出 marker 后失败，验证 record 指向的 log 中 marker 恰为一行、JSON 可解析、`schema_version=1` 且必要 case/assertion 字段存在。该测试证明失败 attempt 仍保存 evidence，不新增 runner parser。
3. contract suite 全绿；exact nodeid `--collect-only` 恰好一个 item。
4. source-tree `repeats=1` smoke：一个 record、一个 pass、一个合法 marker。
5. Windows installed-wheel `repeats=1` smoke：从隔离 venv/site-packages 导入 wheel，运行时 LibXC 7.1.2，marker 与原 assertion 均有效。

静态源码字符串、AST method-body 检查、YAML 文本匹配和新 validator 均不属于本次范围。

## 远端执行与验收

Stage 1 dispatch：

```text
platform=windows
python_version=3.12
profile=4/1
repeats=200
nodeids_file=.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt
```

派发前必须记录 branch、head SHA、run ID 和预期 artifact。artifact 验收要求：

- run/head/tested SHA 一致；
- Windows installed-wheel、site-packages import、LibXC 7.1.2、pip check 和 DLL linkage 有效；
- 200 records、attempt `1..200`、200 个物理日志及引用完整；
- 每个有效日志恰好一个合法 marker：`schema_version=1`、单位和 case 精确、全部必要 phase/assertion 字段存在，且数值/`extra_executed`/条件性 null 满足 schema；
- pytest return code 与原 assertion 决定的 status 一致；
- 无 retry 覆盖失败。

任何 provenance 缺失、marker 缺失/重复、schema 不合法、线程或科学参数漂移均判为 `INVALID`，先修复实验，不进入下一阶段。

## 判定与停止条件

- `REPRODUCED`：捕获至少一个 telemetry 完整的原断言 failure。
- `MECHANISM_CONFIRMED`：base/plus/minus 的最后主循环和 post check 都 converged，`conv_check=True`，translation 原断言通过；同一 failure 的 post-extra finite-difference 原六位语义失败、pre-extra 语义通过，且 plus/minus Extra-cycle shift 的差分方向和量级解释 observed error。`abs(closure_residual) <= 1e-12` 只作为算术 consistency check。
- `MECHANISM_FALSIFIED`：在满足 `REPRODUCED`、同一 attempt 的 post-extra finite-difference 原断言失败、上述 main/post convergence 前提全部满足且 translation 通过时，pre-extra 仍失败，或 Extra-cycle energy-shift contribution 的方向/量级不能解释 observed error。通过的 attempt 不能单独用来证伪当前 failure 机制。下一步才升级到 density/Fock/`veff` 指纹。
- `INCONCLUSIVE_NONCONVERGED`：任一 phase 的最后 main callback `scf_conv=False`，或 main converged 但 post check 的 `post_converged=False`。前者不会执行 Extra cycle，后者是独立的 convergence finding；两者都不能用于确认或证伪当前“已接受 Extra cycle 扰动有限差分”的假设。
- `REPRODUCED_OTHER_ASSERTION`：translation 原断言先失败。保留 evidence，但不得把该 attempt 用作 finite-difference Extra-cycle 机制证据。
- `NOT_REPRODUCED/HOLD`：一个阶段 200 个有效样本均通过。Stage 1 进入 Stage 2；Stage 2 则停止本轮并保持门禁。
- `INVALID`：实验合同或 provenance 不完整。

按当前唯一失败估计发生率约 `0.5%`，200 次至少捕获一次的概率约 63.3%，`0/200` 的 95% 单侧上界约 1.49%。因此任何 `0/200` 都不能写成 `PASS`、`FIXED` 或“问题不存在”。

## 分支与上游边界

设计文档提交保留在 LibXC 调查分支。实现阶段从该已审查提交创建 `codex/investigate/libxc-712-sgx-extra-cycle-telemetry` 隔离 worktree；诊断 branch 不创建上游 PR。

若机制确认，先用证据设计最小生产 RED/GREEN，再从提交时实时 `pyscf/pyscf:master` 新建 `codex/fix/*` 或 `codex/test/*`，只移植必要改动。旧 test-only `conv_check=False`、旧大型诊断框架和当前 CI 基础设施提交都不得混入上游修复。
