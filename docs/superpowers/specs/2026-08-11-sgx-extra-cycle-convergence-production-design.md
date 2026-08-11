# SGX Extra-cycle 收敛修复生产设计

## 状态

- 对话设计：用户已批准方案 A。
- 本书面规格：等待用户复核批准。
- 生产代码、上游分支、PR 和修复后 CI：尚未开始。

## 决策摘要

采用两层最小修复：

1. 在通用 SCF driver 中完成 Draft PR #3331 所定义的控制流修复：Extra cycle 被收敛检查拒绝后，从该物理 density/Fock 状态继续主循环，而不是立即返回未收敛结果。
2. 在 SGX mixin 中提供 energy 与 orbital-gradient 同时满足的收敛不变量。Extra cycle 仍使用现有 `10 * conv_tol` 和 `3 * conv_tol_grad` 放宽值，但不能再仅凭较小 orbital gradient 接受具有不稳定能量的状态。

两层职责分开提交和评审。SGX 修复在本地临时叠加通用 continuation 进行端到端验证；上游 PR 最终保持独立，避免把 Draft #3331、SGX 科学边界和历史 telemetry 混成一个提交。

## 目标

1. 消除 SGX finite-difference gradient 在 Extra-cycle 能量不对称下的偶发六位断言失败。
2. 保留 PySCF 默认非 SGX、非 smearing 的 Extra-cycle `energy OR gradient` 接受规则。
3. 让任何被收敛 hook 拒绝的 Extra cycle 可以继续 SCF，而不是丢弃可继续迭代的物理状态。
4. 保持原始 SGX nodeid、九个子例顺序、`delta=1e-4`、`conv_tol=1e-12`、`conv_check=True` 和两条科学断言不变。
5. 将通用 driver 行为和 SGX-specific 收敛语义分别形成可由上游长期维护的最小 PR。
6. 修复后用 installed-wheel artifact 完成目标三个 nodeid 的正式矩阵验收，再更新 `pyscf/pyscf#3312`。

## 已确认事实与证据

### 上游基线

- 2026-08-11 实时 `pyscf/pyscf:master`：`aa2ad20897104dead09d53fc532a5d3b34203d83`。
- `pyscf/scf/hf.py` 的主循环默认要求 energy 与 gradient 同时收敛。
- 主循环通过后，可选 Extra cycle 使用放宽后的阈值，并在没有自定义 hook 时按 energy 或 gradient 任一通过即接受。
- 当前 driver 即使自定义 `check_convergence` 拒绝 Extra cycle，也会离开循环并返回；它不会从 Extra-cycle density/Fock 继续迭代。
- `pyscf/sgx/sgx.py::_SGXHF` 当前只用 `post_kernel()` 清理 `_in_scf`，没有 SGX-specific `check_convergence()`。

### 机制确认

正式证据绑定如下：

| 项目 | 值 |
| --- | --- |
| run | `31455915215` |
| job | `93669525839` |
| artifact | `9089592334`, `precision-Windows-py3.12` |
| artifact digest | `sha256:aea26093c844bc5d212e40e5f03fb411d09fe9cd4631b786e129b730075ad5a9` |
| tested head | `21ea447c298f0539bae6f60759bd0f5a1d88964c` |
| environment | Windows Python 3.12 installed wheel, `omp4-blas1` |
| runtime dependency | LibXC 7.1.2, 26 wheel-local native DLLs |
| records | 200 attempts, 199 pass, 1 fail, 0 nonconverged |
| validator | `504764e378d4704fb6122970f53694e11abeadc5d098f0ebfb9937269be64652` |
| verdict | `MECHANISM_CONFIRMED` |

attempt 65 的关键量为：

- analytic gradient：`0.006790043852737959 Hartree/Bohr`；
- post-extra finite difference：`0.006789326261312357 Hartree/Bohr`；
- post-extra error：`7.175914256019739e-7`，原六位断言失败；
- counterfactual pre-extra finite difference：`0.0067900435246793156 Hartree/Bohr`；
- pre-extra error：`3.280586436185673e-10`，原六位语义通过；
- plus Extra-cycle shift：`-8.412825991399586e-12 Hartree`；
- minus Extra-cycle shift：`2.6267343855579384e-10 Hartree`；
- Extra-cycle finite-difference contribution：`-7.172633669590255e-7 Hartree/Bohr`；
- reconstruction residual：`6.702148195149651e-19 Hartree/Bohr`。

plus、minus 和 base 三个 phase 都完成主循环并执行 Extra cycle。minus phase 的能量变化 `2.6267343855579384e-10 Hartree` 大于放宽后的 `1e-11` energy threshold，而 orbital gradient `4.0347904631078535e-9` 小于放宽后的 `3e-6` gradient threshold。当前 Extra-cycle OR 规则因此接受该状态；不对称能量 shift 经有限差分分母放大，精确解释原断言失败。

这证明问题位于 PySCF SCF/SGX 收敛语义，不是 LibXC 7.1.2、Windows wheel packaging、DLL linkage、pytest evidence 或 reference 数据错误。

### 相关上游工作

- Draft PR [#3331](https://github.com/pyscf/pyscf/pull/3331) 当前为 OPEN、Draft、MERGEABLE、REVIEW_REQUIRED，head `2f1be97e3b522333d9f5aa4dd50d96421a275abe`，base `7e665e9b8b5ce9b4a35c49dc938e1c03b09d4320`。
- #3331 已实现“拒绝 Extra cycle 后继续 SCF”的方向，并增加 smearing-specific convergence hook，但需要重基到实时 master、收紧测试和重新处理上游反馈。
- [#3324](https://github.com/pyscf/pyscf/pull/3324) 已 CLOSED 且未合并；maintainer 明确表示无需修改测试。其 displacement 或 `conv_check=False` 变体不属于本设计。

## 非目标

- 不修改 LibXC、libcint、XCFun、wheel packaging 或依赖版本。
- 不修改 SGX finite-difference 的 displacement、precision、断言 places、测试顺序或 reference 数值。
- 不关闭 `conv_check`，不增加 retry、`max_cycle` 或迭代容差，不隐藏异常。
- 不把 Extra cycle 的默认全局 OR 条件改成全局 AND。
- 不复制一套 SGX-local SCF driver。
- 不把 telemetry hook、selection 文件、validator 或 evidence parser 放入 production PR。
- 不将 diagnostic branch 直接转换为上游 PR 分支。
- 不在修复和正式矩阵完成前把 `pyscf/pyscf#3312` 的 SGX nodeid 标为 resolved。

## 架构

### 1. 通用 SCF：拒绝 Extra cycle 后继续

通用修改位于 `pyscf/scf/hf.py::kernel()`，并由 #3331 负责。

每个主循环 iteration 的状态机为：

```text
main iteration
  -> main convergence false: continue main loop
  -> main convergence true and conv_check false: return converged
  -> main convergence true and conv_check true: run Extra cycle
       -> Extra convergence true: return converged
       -> Extra convergence false: retain physical density/Fock and continue main loop
```

具体不变量：

1. 主循环继续使用原始 `conv_tol` 与 `conv_tol_grad`。
2. Extra cycle 使用独立的 environment snapshot，提供 `10 * conv_tol`、`3 * conv_tol_grad` 和 `extra_cycle=True`；不得原地放大主循环阈值。
3. 没有自定义 hook 时，Extra-cycle 接受条件仍为 energy 或 gradient 任一通过。
4. 自定义 `check_convergence(envs)` 的 bool 结果是该阶段唯一接受判据；hook 异常原样传播。
5. Extra cycle 被拒绝时，下一主循环从其 density、`vhf` 和无 level-shift 的 physical Fock 继续；不得回退到 Extra cycle 前的状态。
6. 被拒绝的 Extra cycle 不调用 `post_kernel()`，不伪造成功，不重置迭代计数；`post_kernel()` 仍只在 kernel 最终返回前调用一次。
7. checkpoint 保存的 environment 必须反映 Extra-cycle 的实际 relaxed thresholds、`extra_cycle=True` 与最终 `scf_conv`。
8. 到达 `max_cycle` 时仍未通过检查，返回原有未收敛语义；不得 retry 或自动放宽阈值。

这项改动改变的是“拒绝之后是否继续”的控制流，不改变非 SGX/non-smearing 的默认收敛公式。

### 2. SGX：energy 与 gradient 同时满足

SGX-specific 修改位于 `pyscf/sgx/sgx.py::_SGXHF`。

默认 hook 合同为：

```python
energy_converged = abs(envs['e_tot'] - envs['last_hf_e']) < envs['conv_tol']
gradient_converged = envs['norm_gorb'] < envs['conv_tol_grad']
return energy_converged and gradient_converged
```

语义边界：

1. 主循环收到原始 thresholds，因此行为与当前默认主循环 AND 条件一致。
2. Extra cycle 收到 driver 提供的 `10x/3x` relaxed thresholds，但仍要求两项同时通过。
3. SGX 不自行判断、运行或重复 Extra cycle；它只定义 convergence predicate。
4. 用户在实例上显式赋值 `mf.check_convergence = callable` 时，Python instance shadow 继续覆盖 `_SGXHF` 默认方法；用户 hook 的返回值和异常不被包裹或改写。
5. 现有 `check_convergence=None` 语义保持不变：实例显式设置 `None` 时，kernel 走 generic formula。正式 SGX 验证不使用该 opt-out，也不借此绕过 SGX invariant。
6. SGX 与 active smearing 组合时，两者的默认目的均是拒绝 energy 未稳定但 gradient 已小的状态；不为组合场景新增 method-chaining 抽象，也不改变调用顺序生成的现有 MRO。

### 3. 两层组合的数据流

对 attempt 65 类型的 minus phase：

```text
main AND passes
  -> Extra cycle executes
  -> relaxed energy check fails
  -> relaxed gradient check passes
  -> SGX AND rejects Extra result
  -> generic driver keeps Extra density/Fock and resumes main loop
  -> later main AND and Extra AND must both pass before return
```

SGX hook 单独只能把当前 Extra state 标为未收敛；没有通用 continuation 时，driver 仍会立即返回未收敛结果。通用 continuation 单独只能继续迭代；没有 SGX hook 时，gradient-only 的 Extra state仍会被默认 OR 接受。因此两个提交都是端到端修复的必要组成，但它们的职责和测试必须独立。

## 兼容性与公共接口

- 不新增公共参数、配置文件或依赖。
- `SCF.check_convergence` 仍是 `callable(envs) -> bool` hook。
- environment 新增或固定使用的 `extra_cycle` 仅用于内部阶段识别；不改变现有函数签名。
- 默认 RHF/UHF/DFT 的主循环 criterion 不变；默认 Extra cycle 仍是 relaxed OR。
- SGX 默认由 class method 提供 AND criterion；实例级自定义 hook 保持最高优先级。
- `conv_check=False` 继续跳过 Extra cycle，并在主循环通过后返回；本设计不改变该公开开关。
- `post_kernel()`、callback、checkpoint 和 `mf.cycles` 的既有调用边界必须由回归测试保护。

## 错误处理与停止条件

- 自定义 hook、`get_veff`、`get_fock`、checkpoint 或 `post_kernel` 的异常原样传播；不转换为 convergence false，不自动重试。
- Extra-cycle environment 缺少必要键时测试应失败，而不是使用猜测性默认值。
- 若 continuation 后出现非有限 energy/gradient、状态回退或循环无法在原 `max_cycle` 内结束，停止叠加补丁并重新审查 driver 状态传递。
- 若三次独立 RED/GREEN 尝试都不能同时满足通用 control-flow test、SGX predicate test 和原 nodeid，停止当前方案并重新设计。
- CI 绿色但未覆盖原断言、exact tested SHA、runtime LibXC 和 installed-wheel provenance 时不构成完成证据。

## TDD 设计

### A. 通用 continuation RED/GREEN（#3331）

位置固定为 #3331 已使用的 `pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing`，行为合同为：

1. 自定义 hook 让主循环正常通过。
2. 第一次 Extra-cycle check 确定性返回 false。
3. 断言 driver 没有立即返回，并至少观察到第二次 Extra-cycle check。
4. 后续 check 通过后，solver 在原 `max_cycle` 内 converged。
5. 记录第一次被拒绝 Extra state 后的下一主循环确实使用该 physical density/Fock，而不是重启或回退。
6. 默认非自定义 Extra-cycle OR criterion 用独立 regression 保持不变。

RED 必须先在实时 master 上证明当前 driver 在第一次拒绝后直接返回或未进入第二次 check。GREEN 只包含最小 loop/state 变更，不引入 SGX 文件。

### B. SGX predicate RED/GREEN

在 `pyscf/sgx/test/test_sgx.py` 增加不运行完整 SCF 的确定性单元测试，直接构造 attempt 65 的 Extra-cycle environment：

```text
abs(e_tot - last_hf_e) = 2.6267343855579384e-10
conv_tol = 1e-11
norm_gorb = 4.0347904631078535e-9
conv_tol_grad = 3e-6
extra_cycle = true
```

测试先证明当前 SGX 没有 callable default hook，或会沿用 generic OR 接受该状态；GREEN 后必须拒绝该 energy-fail/gradient-pass 状态。再用表驱动覆盖：

| energy | gradient | expected |
| --- | --- | --- |
| pass | pass | true |
| pass | fail | false |
| fail | pass | false |
| fail | fail | false |

另加实例级 override test，证明显式 `mf.check_convergence = custom` 仍被调用且其结果优先。

### C. 原科学 nodeid

`pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad` 保持原文件科学逻辑不变：

- 九个子例和顺序不变；
- `delta=1e-4` 不变；
- settings-2 precision `6` 不变；
- translation `places=12` 与 finite-difference `places=6` 不变；
- 不添加 retry、telemetry 或 diagnostic selection。

production branch 必须对该文件做 blob/diff 守卫。若实时 master 在实施前变化，只允许接收上游无关改动，不允许为了 GREEN 修改上述边界。

## 分支、提交与 PR 边界

### #3331 通用分支

1. 实施前重新 fetch `pyscf/pyscf:master`。
2. 在 `codex/fix/uhf-smearing-convergence` 的独立 worktree 中重基 Draft #3331 到该 exact master。
3. 保留并收紧两个职责：generic rejected-Extra continuation 与 smearing-specific AND convergence。
4. 处理 reviewer 关于 `conv_tol=1e-8` 的建议时以 RED/GREEN 为准；不得用 tolerance-only 变更替代控制流修复。
5. PR #3331 不包含 SGX module、SGX gradient test、telemetry 或 LibXC CI 文件。

### SGX 独立分支

1. 从实施时实时 upstream master 新建独立 `codex/fix/sgx-extra-cycle-convergence` worktree。
2. SGX commit 只修改 `_SGXHF` convergence behavior 与最窄 SGX unit tests。
3. 本地和 fork CI 可临时把该 commit 叠加在重基后的 #3331 generic commit 上验证端到端行为。
4. #3331 合并后，将 SGX branch 重基到包含 generic continuation 的新 master，确认最终 PR diff 不再携带 #3331 commit。
5. #3331 未合并时，只有 maintainer 明确同意 stacked dependency 才发布 SGX PR；否则保持本地/fork 验证状态。
6. 若 maintainer 要求合并成一个 PR，先获得新的范围确认，不在当前设计下自动扩大 #3331。

### 调查资产

以下内容全部保留在 `.agents/` archive 或调查分支，不进入 production PR：

- post-kernel telemetry hooks 与 marker；
- schema-v1/v2 validators；
- diagnostic nodeid selection；
- 200-repeat raw logs、records、CSV、summary 和 environment snapshots；
- heartbeat、dispatch latch 和本地审查报告。

## 验证阶梯

### Gate 0：静态与最窄单测

- generic continuation RED/GREEN；
- SGX 4-case predicate table；
- instance-level custom hook priority；
- default generic Extra-cycle OR regression；
- `git diff --check`、tracked scope、encoding/EOL；
- production diff 中不存在 telemetry prefix、validator、selection 或断言变更。

### Gate 1：本地组合验证

在临时 stacked worktree 中按 `generic commit -> SGX commit` 顺序运行：

1. 通用 SCF/`test_addons.py` 聚焦回归；
2. `pyscf/sgx/test/test_sgx.py`；
3. 原 `pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad`；
4. profile `1/1` 和历史失败 profile `4/1` 的 source-tree smoke。

所有 scientific assertions 保持原样。资源失败与科学 failure 分开记录，不以重跑覆盖首份证据。

### Gate 2：Windows installed-wheel witness

在 exact stacked head 上派发 Windows Python 3.12、`omp4-blas1`、原 SGX nodeid、1 repeat。严格核对：

- exact run/job/head/branch/artifact identity；
- installed-wheel import；
- runtime LibXC 7.1.2；
- pip check 0；
- 26 个 wheel-local DLL linkage；
- 原 nodeid 1/1 pass；
- 不存在 telemetry marker 或 source-tree shadow。

### Gate 3：SGX 正式 200-repeat

同一 frozen head、Windows Python 3.12、`omp4-blas1`、原 SGX nodeid、200 repeats。要求 200/200 满足原断言、0 retry、0 hidden exception、0 nonconverged，并逐条验收 records、logs、summary、environment 和 tested SHA。

这一步验证历史失败条件，但仍不是三个 nodeid 的最终矩阵。

### Gate 4：三个 LibXC 相关 nodeid 的最终矩阵

在最终可提交的 production integration head 上，使用三个原始 nodeid：

1. `pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda`
2. `pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad`
3. `pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda`

正式矩阵沿用本调查已建立的 7 个 OS/Python 组合与 4 个线程 profile：

- Windows Python 3.12/3.13；
- Ubuntu Python 3.8/3.12/3.13；
- macOS Python 3.8/3.13；
- profiles `1/1`、`4/1`、`1/4`、`4/4`；
- 每个 nodeid 每 job 200 repeats。

总门禁为 28 个 artifacts、16,800 条 records。按 profile 分波派发，每波完成后独立验收再扩大；单 job 接近既定 300 分钟安全门禁时按 CI 操作规范取消并分片，超时不得记为数值失败。

每份 artifact 必须证明 runtime dependency、tested SHA、profile、attempt 连续性、原 assertion、逐日志引用和 native linkage。Actions 绿色本身不足以通过门禁。

## `pyscf/pyscf#3312` 更新门禁

只有在以下事实形成闭环后才更新对应状态：

1. generic continuation 已由 #3331 或其上游认可替代方案合并；
2. SGX convergence commit 已合并，或 maintainer 已接受明确可维护的 stacked integration 路径；
3. 三个 nodeid 的最终矩阵 artifact 全部验收；
4. 原始断言、runtime LibXC 7.1.2、根因和最终修复方式都有可公开链接的证据。

issue 评论应分别列出三个 nodeid，而不是用单一“LibXC fixed”概括：

- 已解决项标记完成，并附 PR/merge commit、CI run/artifact、原断言和原因；
- 未解决项保持未勾选，明确当前 failure、最新实验结论和下一步；
- SGX 项说明根因是 PySCF Extra-cycle convergence asymmetry，LibXC 7.1.2 只是复现环境而非缺陷来源；
- 诊断 telemetry 只作为根因证据，不作为 production fix。

在三项都达到可由上游长期维护的终态前，不关闭全部巡检，不把 Goal 标记完成。

## 被否决方案

### 1. 复用 #3324 的 test-only 修改

修改 displacement 或关闭 `conv_check` 会绕开首个致错步骤，但不修复生产 SCF 行为，并已被 maintainer 拒绝。

### 2. 全局把 Extra-cycle OR 改成 AND

这会改变所有 SCF 方法的历史收敛行为，影响面远大于已确认的 SGX/smearing 边界。默认 OR 保留。

### 3. 在 SGX 内复制 SCF continuation driver

会产生两套循环、DIIS、checkpoint、callback 和 state-transfer 逻辑，维护成本高且容易漂移。SGX 只提供 predicate。

### 4. 只增加容差、迭代上限或 retry

这些做法会隐藏偶发 failure，不能解释 attempt 65 的确定性能量不对称，也违反原科学断言门禁。

### 5. 在 production PR 保留 telemetry

telemetry 已完成根因职责，继续保留会扩大 test surface、改变时序并污染上游 diff。production 只保留最小 RED/GREEN。

### 6. 在修复前先做完整 density/Fock rebuild 对比

post-kernel evidence 已以 `6.7e-19` reconstruction residual 确认 Extra-cycle shift 对 failure 的解释。继续扩大诊断不会改变当前最小修复决策；只有 A 的 RED/GREEN 失败时才重启更深指纹实验。

## 完成标准

本设计只有在以下全部满足时才算完成：

1. #3331 的 generic continuation 在实时 master 上有确定性 RED/GREEN，并解决 reviewer 门禁；
2. SGX AND predicate 有 attempt-65 synthetic RED、四象限测试和 custom-hook priority 证据；
3. 两个提交组合后，原 SGX nodeid 在 Windows installed-wheel `omp4-blas1` 200/200 通过；
4. 三个原始 nodeid 的 28-artifact 正式矩阵通过并完成独立 artifact 验收；
5. production PR diff 不包含测试放宽、telemetry、validator、selection、依赖或打包改动；
6. `pyscf/pyscf#3312` 按 nodeid 更新 PR、CI、artifact、根因和最终解决方式；
7. 相关 heartbeat、PS1 fallback 和临时巡检在完整目标结束时全部停止并归档。
