# SGX HSE06 低扰动 post-kernel 遥测设计

## 状态

- 对话设计：用户已于 2026-08-11 批准方案 A。
- 本文档：等待用户书面复核。
- 实现、推送与远端 CI：尚未开始。

## 背景与已知证据

当前调查对象是原始 nodeid：

```text
pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad
```

LibXC 7.1.2 的正式 Windows installed-wheel 证据中已经存在一次真实科学断言失败：

- run `31345422470`，artifact `9048584095`；
- Windows Python 3.12，profile `omp4-blas1`；
- attempt 95，settings-2/HSE06；
- analytic `g[0,2] = 0.00679004385313231`；
- finite difference `0.006788983797758873`；
- difference `1.0600553734373824e-06`，原 `assertAlmostEqual(..., places=6)` 失败。

该 artifact 的 installed-wheel、PySCF 2.14.0、LibXC 7.1.2、pip、26 个 DLL linkage、records、CSV 和逐 attempt 日志均已严格验收，因此这不是 packaging 或 evidence-pipeline 故障。

现有 Stage 2 遥测随后恢复了原九子例顺序，只在第八个 settings-2/HSE06 子例启用每个 SCF cycle 的 callback：

- exact head `2133114d93af1c7cb18f1acdc5693e871d8632db`；
- run `31404086927`，artifact `9071911403`；
- Windows Python 3.12，installed-wheel，`omp4-blas1`，200 repeats；
- frozen validator SHA-256 `38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2`；
- `valid=true`、`200/200 pass`、`0 fail`、`0 nonconverged`、`NOT_REPRODUCED/HOLD`。

该结果不是 `PASS/FIXED`。200 次样本中，最大 post-extra 误差为 `3.9149584421874217e-07`，仍低于六位断言失败边界；14 次 near-boundary attempt 的 plus phase 都在第 22 个主循环结束，plus/minus Extra-cycle shift 差分把约 `1e-9` 的 counterfactual pre-extra error 放大到约 `3.94e-7`。这支持 Extra-cycle asymmetry 是首要机制假设，但没有捕获 failure，不能确认根因。

当前 telemetry callback 在每个 SCF cycle 都执行 Python closure、复制标量并更新字典。它可能改变线程调度、allocator 状态或浮点归约时序，形成 Heisenberg effect。方案 A 将其缩减为每个 base/plus/minus phase 仅一次的 `post_kernel` 观测。

## 目标

1. 保持原九子例顺序、原输入、原收敛参数和原两条断言不变。
2. 删除目标子例的 per-cycle callback 扰动，只在 base、plus、minus 各自的 `post_kernel` 调用中复制一次标量。
3. 从同一 attempt 的 plus/minus pre-extra 与 post-extra 能量重算有限差分，判断 Extra-cycle shift 是否解释真实六位断言失败。
4. 以 source smoke、Windows installed-wheel 1-repeat witness、Windows Python 3.12 `omp4-blas1` 200-repeat formal 三层证据验证实验。
5. 若捕获 failure，形成可证伪的机制结论；若仍为 `0/200`，保持 `NOT_REPRODUCED/HOLD`，不把问题标为已解决。

## 非目标

- 不修改 `delta=1e-4`、`conv_tol=1e-12`、`conv_check=True`、`max_cycle`、LibXC 版本或线程 profile。
- 不放宽、替换、跳过或 retry 原 `places=12` 平移断言与 `places=6` finite-difference 断言。
- 不修改 PySCF production module、SCF kernel、SGX production behavior、workflow、runner、Windows verifier 或依赖。
- 不把诊断分支作为上游 PR，不在本实验中设计最终 production fix。
- 不把 `0/200`、Actions 绿色或 Extra-cycle 相关性写成“已修复”。
- 不在本实验后立即更新 `pyscf/pyscf#3312` 为 resolved；该 issue 只有在可维护最终方案和对应 CI 证据完成后才更新。
- 不同时派发其他 profile、三 nodeid 完整矩阵或更大的 600-repeat 实验。

## 分支与证据隔离

为保持 Stage 2 的 exact head 与 artifact 可追溯，新实验从 `2133114d93af1c7cb18f1acdc5693e871d8632db` 创建新的隔离 worktree/branch：

```text
codex/investigate/libxc-712-sgx-post-kernel-telemetry
```

该分支只用于诊断，commit subject 使用 `[skip ci]`，远端 workflow 只通过显式 `workflow_dispatch` 启动。旧 Stage 2 branch/head、artifact 和 frozen validator保持不变。

若最终确认机制并需要 production RED/GREEN，必须在提交时重新获取实时 `pyscf/pyscf:master`，从该 live master 创建新的 `codex/fix/*` 或 `codex/test/*` 分支，只移植必要改动。

## 设计

### 1. 保留 exact 原 nodeid 与九子例顺序

继续使用当前 exact singleton selection：

```text
pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad
```

原方法内九次 `_check_finite_diff_grad(...)` 调用的顺序保持不变，只有第八个 settings-2/HSE06 调用启用 telemetry。现有 dedicated telemetry method 可保留用于本地 smoke，但不得替代原 nodeid 的远端证据。

### 2. 移除 per-cycle callback

telemetry 路径不再设置 `mf.callback`，也不再保存每个主循环的 `locals()` 或最后一次 callback snapshot。普通测试路径继续保持 telemetry 默认关闭。

这项修改只减少观测次数，不声称完全消除扰动：实例属性替换、三个标量快照、JSON 序列化和输出仍可能影响 allocator/timing。结论必须明确限定为“比 per-cycle callback 更低扰动”。

### 3. 分别包装 base 与 scanner 的 `post_kernel`

不能把一个捕获了 base bound method 的 wrapper 直接复制到 scanner。`SCF_Scanner.__init__` 使用 `self.__dict__.update(mf_obj.__dict__)`；若 wrapper closure 调用绑定到 base 的原方法，plus/minus 的 `SGX.post_kernel()` 会错误清理 base 而不是 scanner，改变 `_in_scf` 行为。

实现使用一个 module-local helper，分别对 base、plus、minus 三次 operation 安装短生命周期 instance wrapper：

```text
run_with_post_kernel_snapshot(owner, phase, snapshots, operation)
```

helper 的合同为：

1. 记录 `owner.__dict__` 中是否已有 `post_kernel` instance shadow 及其原值。
2. 保存当前 `owner.post_kernel` bound method；wrapper 只绑定当前 owner。
3. wrapper 先调用保存的原 `post_kernel(envs)`，再立即复制当前 phase 的标量，并记录调用次数。
4. 执行传入的 operation；无论 operation、原 hook 或 snapshot 是否异常，都在 `finally` 中恢复原 instance/class lookup 状态。
5. 若原来没有 instance shadow，恢复时删除临时 instance 属性，而不是把 bound method 写回 `__dict__`；若原来已有 shadow，则精确恢复原对象。
6. operation 正常返回时要求 wrapper 恰好调用一次；零次或多次均判为实验合同错误。
7. 返回 operation 的原结果，不捕获或改写科学异常。

调用顺序固定为：

1. 以 base `mf` 为 owner 包装 `gradient.kernel()`，得到 `g` 和 base snapshot；随后立即恢复 base。
2. 恢复 base 后才调用 `mf.as_scanner()`。
3. 以 `mf_scanner` 为 owner 单独包装 plus scanner call，得到 `e1` 和 plus snapshot；立即恢复 scanner。
4. 再以同一 `mf_scanner` 为 owner 重新安装独立 wrapper，包装 minus scanner call，得到 `e2` 和 minus snapshot；立即恢复 scanner。

plus 与 minus 不共享一个持续存在的 wrapper 或可变 phase closure。每个 phase 都由 operation 边界提供名称，因此不会因 minus 覆盖 plus 状态，也不会把 base-bound method 复制到 scanner。

wrapper 的固定调用顺序是：

```text
original_post_kernel(envs)
copy_json_safe_scalars(envs)
```

原 hook 必须恰好调用一次且先执行。这样即使 telemetry scalar 转换失败，SGX 的 `_in_scf=False` 清理已经完成；原 hook 自身异常则原样传播，不生成伪证据。

### 4. `post_kernel` 可观测边界

`pyscf/scf/hf.py` 在主循环和可选 Extra cycle 后恰好调用一次：

```python
mf.post_kernel(locals())
```

Extra cycle 执行后：

- `envs['e_tot']` 是 post-extra energy；
- `envs['last_hf_e']` 是进入 Extra cycle 前的 energy；
- `envs['norm_gorb']` 与 `envs['norm_ddm']` 是 Extra cycle 后的 scalar；
- local `conv_tol` 已乘 10，`conv_tol_grad` 已乘 3；
- `envs['scf_conv']` 是最终 post-check convergence，而不是 main-loop convergence。

Extra cycle 未执行时，`last_hf_e` 只是前一主循环 energy，不能当作 pre-extra energy。因此 schema 仅在确认 Extra cycle 已执行时填充 `pre_extra_energy` 和 `extra_shift`，否则两者必须为 JSON `null`。

本实验固定 `mf.conv_tol=1e-12`、`conv_check=True`。`extra_executed` 的观测规则为：

```text
conv_check is true
and effective_conv_tol == configured_conv_tol * 10
```

其中 `configured_conv_tol` 来自当前 phase 的 `envs['mf'].conv_tol`，`effective_conv_tol` 来自 local `envs['conv_tol']`。validator 同时要求 configured value 精确为本实验的 `1e-12`，并检查 relaxed `conv_tol_grad`、有限性和字段类型。不得用 `final_converged` 或 `extra_shift != 0` 推断 Extra cycle 是否执行，因为 Extra cycle 已执行后仍可能把最终 convergence 判为 false。

### 5. Marker schema v2

为避免旧 schema-v1 validator 接受语义不同的字段，新实验使用新 prefix：

```text
PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 {json}
```

`schema_version` 固定为整数 `2`。payload 至少包含：

```text
schema_version
instrumentation.mode
instrumentation.per_cycle_callback
instrumentation.expected_phase_count
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
phases.base
phases.plus
phases.minus
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
result.reconstruction_residual
```

固定 instrumentation 值：

```text
mode = post_kernel_once_per_phase
per_cycle_callback = false
expected_phase_count = 3
```

每个 phase 的字段为：

```text
cycle
configured_conv_tol
effective_conv_tol
effective_conv_tol_grad
conv_check
extra_executed
pre_extra_energy
post_energy
extra_shift
final_converged
final_norm_gorb
final_norm_ddm
```

类型与 null 规则：

- `cycle` 是正整数；
- `conv_check`、`extra_executed`、`final_converged` 是严格 bool；
- `configured_conv_tol`、`effective_conv_tol`、`effective_conv_tol_grad`、`post_energy`、`final_norm_gorb`、`final_norm_ddm` 是有限 float；
- `extra_executed=true` 时 `pre_extra_energy` 与 `extra_shift` 必须是有限 float，且 `extra_shift = post_energy - pre_extra_energy`；
- `extra_executed=false` 时 `pre_extra_energy` 与 `extra_shift` 必须为 null；
- 三个 phase 必须各出现恰好一次，不接受缺失、重复或额外 phase。

固定 case 与单位：

```text
settings_index = 2
settings = [true, true, true, true, true]
precision = 6
xc = HSE06
delta = 1e-4
translation_places = 12
finite_difference_places = 6
energy = Hartree
gradient = Hartree/Bohr
displacement = Angstrom
```

### 6. 重算公式与语义边界

若 plus/minus 都确认执行 Extra cycle：

```text
fd_pre  = (E_plus_pre  - E_minus_pre)  / (2 * delta) * BOHR
fd_post = (E_plus_post - E_minus_post) / (2 * delta) * BOHR
extra_contribution = (plus.extra_shift - minus.extra_shift) / (2 * delta) * BOHR
reconstruction_residual = fd_post - fd_pre - extra_contribution
error_pre  = analytic_gradient - fd_pre
error_post = analytic_gradient - fd_post
```

若 plus 或 minus 没有执行 Extra cycle，`fd_pre`、`error_pre`、`finite_difference_pre_pass`、`extra_contribution` 和 `reconstruction_residual` 必须为 null；`fd_post` 与原 assertion mirror 仍然存在。

`finite_difference_pre` 只是使用位移 phase 的 pre-extra energy 构造的 counterfactual finite difference。analytic gradient 仍来自 base 的正常 post-extra 轨道，因此不得称为“完全 pre-extra gradient”。

assertion mirror 必须精确使用 unittest 的 places 语义：

```text
translation_assertion_pass = round(abs(translation_l1), 12) == 0
finite_difference_pre_pass = round(abs(error_pre), 6) == 0
finite_difference_post_pass = round(abs(error_post), 6) == 0
```

marker 在原两条 assertion 之前输出恰好一行；实际 pytest assertion 仍是唯一 pass/fail gate，顺序、表达式和 places 不变。`reconstruction_residual` 只证明算术一致性，不是独立根因证据。

## Validator 与证据合同

旧 validator SHA-256 `38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2` 已绑定 schema-v1 archive，必须保持不可变。

新实验在本地忽略路径创建新的标准库-only validator：

```text
.agents/active/precision-ci/scripts/validate_sgx_hse06_post_kernel_telemetry.py
```

它从冻结 schema-v1 validator 的已审查版本派生，但使用新文件名和独立 SHA-256：保留通用 file/runtime/run/artifact provenance 逻辑，只替换 prefix、marker schema/normalization、机制分类字段和对应 fixture/mutation self-tests。旧文件的 SHA-256 在派生前后都必须仍为 `38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2`，不得重构成共享可变模块或让历史 archive 依赖新代码。

新 validator 有独立自测和每份 evidence archive 内的冻结副本。它不进入 PySCF 调查分支或未来 PR。validator 必须 fail closed 地验证：

1. run/job/artifact/head/branch/tested SHA identity；
2. source-tree 与 installed-wheel provenance；
3. exact singleton 原 nodeid、profile `omp4-blas1`、repeats 和 attempt 连续性；
4. records、CSV、summary、physical logs 与引用一一对应；
5. 每个 log 恰好一个 v2 marker，拒绝 duplicate JSON keys；
6. schema、类型、finite/null、Extra-cycle execution rule、公式与 assertion mirror；
7. pytest exit/status 与原 assertion 结果一致；
8. Windows installed-wheel 的 LibXC 7.1.2、pip check 0、26 个 wheel-local DLL linkage。

validator 的结构/provenance 错误返回 nonzero 并写 `INVALID`。有效科学 failure 仍返回 valid evidence，由 verdict 字段分类，不能因 Actions 红色而丢弃或自动 rerun。

## TDD 与实现范围

### RED

1. contract 先期待 v2 prefix、`schema_version=2`、instrumentation 与 assertion mirror；当前 v1 fixture 应失败。
2. exact source runner 先用新 validator 读取当前 Stage 2 v1 evidence；应只因 marker/schema 不匹配得到 `INVALID`，证明 validator 不会混用旧证据。
3. 在 `test_rks.py` 为 module-local operation helper 增加一个不运行 SCF 的最窄 fake-owner 测试：验证原 `post_kernel` 恰好先调用一次、snapshot 恰好后调用一次、operation 返回值不变，以及 normal/operation-error/snapshot-error/既有 instance-shadow 四种路径都恢复精确 instance/class lookup 状态。该测试不得依赖源码字符串或 AST，也不进入远端 exact-singleton selection。

### GREEN

1. 用三个逐 operation、逐 owner 恢复的 wrapper 调用替换 per-cycle callback，保持普通 telemetry-off 路径不变。
2. dedicated nodeid source run：恰好一个 v2 marker、三个 phase、无 v1 marker。
3. 原九子例 nodeid source run：恰好一个 v2 marker，marker 仍来自第八个 settings-2/HSE06 子例。
4. contract suite 与新 validator self-tests 全绿；旧 frozen validator self-tests 和旧 archive 复验仍全绿，证明没有改写历史证据。
5. `git diff --check`、UTF-8 no BOM、既有 mixed-EOL 守卫和 tracked scope 检查通过。

实现 commit 预计只修改：

1. `pyscf/sgx/grad/test/test_rks.py`；
2. `.github/workflows/test_precision_investigation_contract.py`。

现有 exact singleton selection 文件保持不变。新 validator、self-test fixture 与 audit report 位于 `.agents/`，不进入提交。

## 执行门禁

### Gate 0：本地 source smoke

- exact original nodeid；
- profile `4/1`；
- repeats `1`；
- tested SHA 等于新 implementation head；
- record `1`、marker `1`、v1 marker `0`；
- v2 validator verdict `SMOKE_PASS`；
- 原两条 assertion 未改变。

只有 Gate 0 valid 才允许 push 调查分支。

### Gate 1：Windows installed-wheel witness

使用现有 `Precision investigation` workflow：

```text
platform=windows-latest
python_version=3.12
profile=4/1
repeats=1
nodeids_file=.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt
```

严格验收 run/head/job/artifact、installed-wheel provenance、LibXC 7.1.2、26 DLL 和 v2 marker。只有 verdict 精确为 `SMOKE_PASS` 才进入 Gate 2。

### Gate 2：Windows formal 200

在同一 frozen head、同一 selection 和同一参数下把 repeats 改为 `200`。不派 timing-20；历史原 nodeid run 已提供约 101 分钟的直接成本证据。

等待阶段只保留一个 30 分钟 heartbeat/PS1 fallback，固定 exact run ID/head SHA；Goal paused，terminal 后 exact read-back 恢复 active。不得与 native heartbeat、`gh run watch` 或人工后台轮询并存。

## 判定与停止条件

- `MECHANISM_CONFIRMED`：同一 valid attempt 中 translation 断言通过、post-extra 原 finite-difference 断言失败、plus/minus Extra cycle 均执行且最终收敛、counterfactual pre-extra 六位语义通过，并且 `extra_contribution` 的方向与量级解释 observed error，`abs(reconstruction_residual) <= 1e-12`。
- `MECHANISM_FALSIFIED`：同一 valid、已复现 post-extra finite-difference failure 中，收敛与 schema 前提成立，但 pre-extra 仍失败，或 Extra-cycle contribution 的方向/量级不能解释误差。通过的 attempt 不能单独证伪 failure 机制。
- `INCONCLUSIVE_NONCONVERGED`：任一 phase 最终不收敛，或缺少可判别的 Extra-cycle execution evidence。保留证据，不作确认/证伪。
- `REPRODUCED_OTHER_ASSERTION`：translation assertion 先失败；不得用于 finite-difference Extra-cycle 机制结论。
- `NOT_REPRODUCED/HOLD`：200 个 valid attempt 全部通过。停止本轮，不派其他 profile、不声称修复；下一步另写 density/Fock/`veff` 最小边界指纹设计。
- `INVALID`：任何 identity、provenance、schema、marker、参数或日志合同失败。只修实验合同，不作科学结论，不用 rerun 覆盖首份证据。

## 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| wrapper 绑定到错误 owner | scanner 的 `_in_scf` 清理落到 base，改变科学行为 | base/scanner 分别保存 bound method，分别包装并在 finally 恢复 |
| wrapper 抢在原 hook 前读取或抛错 | SGX cleanup 未执行 | 固定先调用原 `post_kernel`，再复制标量 |
| 用 final convergence 推断 Extra cycle | Extra cycle 执行后可能 final false，分类错误 | 用 local/configured `conv_tol` relaxation 与 `conv_check` 判定 |
| 无 Extra cycle 时误用 `last_hf_e` | 把前一主循环能量写成 pre-extra | `extra_executed=false` 时 pre/shift 强制 null |
| v1/v2 evidence 混用 | 旧 archive 被新语义误验收 | 新 prefix、新 schema、新 validator 文件与新 SHA |
| 低扰动仍改变时序 | `0/200` 被误当修复 | 明确保持 `NOT_REPRODUCED/HOLD`，不关闭 issue 门禁 |
| Actions failure 被当基础设施失败 | 丢失首个科学 failure | validator 将 valid scientific failure 与 INVALID 分开 |

## 完成标准

本实验只有在以下全部满足时才算执行完成：

1. 新分支/commit 的 parent、scope、marker schema 和 source evidence 完整；
2. installed-wheel witness 与 formal artifact 都绑定 exact head/run/job/artifact；
3. 200 个 attempt 全部由新 validator 分类，日志和 marker 无缺失/重复；
4. 结论使用上述固定 verdict，不把绿色或 `0/200` 写成 fixed；
5. 若机制确认，另行设计从实时 upstream master 出发的最小 production RED/GREEN；
6. 若未复现或证伪，保留 HOLD 并进入下一项最小可证伪实验；
7. 在三个目标 nodeid 均具备可维护最终结论前，不把 `pyscf/pyscf#3312` 对应项标为完成。
