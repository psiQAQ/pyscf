# UHF smearing 最终合并版专项复验

**#3410 最终实现完成专项复验。** 验收日期：2026-11-07（Asia/Shanghai）。
Linux 完成 1000/1000、Windows installed wheel 完成 200/200 个新进程正式样本；
每个平台另有完整节点预检 1/1，以及分子/PBC smearing 回归 9/9。
未发现需要新增生产代码修复的实际缺陷。

## 版本与输入

- 科学基线 B：`ab749b4fd00f95a08ad00997356c9f6f77fc8674`。
- [#3410](https://github.com/pyscf/pyscf/pull/3410) 最终 head：
  `e7d2001bc49df99b65cd182fc3cb70ea9948724b`。
- 合并提交：`fd6b6898a3d06fa0628f9d8544476a856dc711a8`，是 B 的祖先。
- 合并提交至 B 的 `pyscf/scf/smearing.py`、`pyscf/scf/hf.py` 未变，目标测试方法 AST 相同。
- 本分支相对 B 的科学源码、原测试、`setup.py`、`pyproject.toml`、`MANIFEST.in` 均未变；
  没有加载 SGX 候选，也没有新增依赖声明。旧 `ce71ff65` 候选结果不计入本次验收。

完整节点为 `pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing`。
输入保持 Fe₂，间距 2.01 Å，LANL2DZ 基组/ECP，spin=6、charge=0、symmetry=False。
两个 UHF 对象按原顺序创建并运行：

| 阶段 | 输入和现行断言 |
|---|---|
| 1 | Fermi smearing，sigma=0.01，fix_spin=True；e_tot 五位、entropy 三位 |
| 2 | 新建 UHF 对象，sigma 改为 0.1，fix_spin=False，conv_tol=1e-9；e_free 七位、e_tot 四位、entropy 三位，且 converged=True |

实现仅使用 `check_convergence`：可用时检查自由能变化 dF，必要时回退 dE；
主循环为能量与梯度条件的 AND；extra 由 `envs['scf_conv']` 识别，在放宽阈值后使用 OR。
没有 `check_extra_convergence` hook。本次不改变此语义或恢复历史 e_tot 五位标准。

## 正式证据

| 范围 | 实际结果 | 运行与工具版本 |
|---|---|---|
| Windows Python 3.13.17 | Passed，200/200，2×100 | [42281471449](https://github.com/psiQAQ/pyscf/actions/runs/42281471449)，`98508952b6b7ce9a94ffb484514188176f59848e` |
| Linux Python 3.12.16，第一批有效记录 | Passed，821 次，8×100+21 | [42284337939](https://github.com/psiQAQ/pyscf/actions/runs/42284337939)，`af1a268c866689faeb2632d5efe0731cb4ebfb27` |
| Linux Python 3.12.16，补齐记录 | Passed，179/179，100+79 | [42286423369](https://github.com/psiQAQ/pyscf/actions/runs/42286423369)，`af1f80d392f8b9245757b66d229a1c69c02b8232` |

第一行运行的整体结论为 failure，源于同一运行中 Linux formal runner 缺少原生 BLAS；
Windows 200 次及两个平台的预检/小范围回归分别核验通过。第二行整体结论为 cancelled；
其 821 个完整记录经过逐轮审计，分片 8 的第 22 次被取消中断，未计入通过数。
第三行整体结论为 success。没有把整体工作流颜色替代样本验收。

所有 Linux 正式样本使用同一个 wheel；补跑只更正 runner 的运行环境，未重建或替换 wheel。
构建工具提交均为 `98508952b6b7ce9a94ffb484514188176f59848e`，与后续运行工具提交分别记录。

| wheel | SHA-256 |
|---|---|
| Linux | `b3c5c4d2d3f5346dd46aa47d9133d955244e1cf9208dc43517c215c9dee51d8b` |
| Windows | `3b4db4e3104185bf368937a778dec6ea5206a93f6e155c49fec7d13eac08acb1` |

每个平台从包含 B 原科学源码的检出构建 wheel，在源码树外的独立 venv 安装运行；
714 个打包 Python 文件逐字节核对，原测试文件另按哈希校验后放入安装环境。
没有用主工作区源码覆盖加旧 DLL 作为正式证据。

## 环境与线程

| 项目 | Linux | Windows |
|---|---|---|
| Python | 3.12.16 | 3.13.17 |
| NumPy / SciPy / h5py | 2.5.4 / 1.18.1 / 3.16.0 | 2.5.4 / 1.18.1 / 3.16.0 |
| PySCF / pytest | 2.15.0（源码 B）/ 8.4.2 | 2.15.0（源码 B）/ 8.4.2 |
| LibXC / XCFun | 7.1.2 / 2.1.1 | 7.1.2 / 2.1.1 |
| 请求的 OMP/BLAS 配置 | 4/4 | 4/4 |
| 运行时 OpenMP API | 4 | 4 |
| NumPy、SciPy OpenBLAS API | 各 4 | 各 4 |
| PySCF 链接的 BLAS | reference BLAS，串行 1 | OpenBLAS，API 报告 4 |

Linux 的串行 BLAS 由已加载库的实际路径识别；不把环境变量 4 误记为该库实际使用 4 线程。
每次运行均记录 Python 小版本、加载库路径/哈希、原生线程 API、runner image、进程身份及私有临时目录。
完整版本、库配置和各分片差异见 [acceptance-summary.json](acceptance-summary.json)。

## 原断言、收敛记录与回归范围

Passed（工件审计）：每个正式记录具有原始日志、JSON、JUnit、启动进程记录；
恰好执行目标 nodeid，没有 skip/deselected，没有放松断言。1200 个样本身份唯一，均由新进程启动。
`sys.setprofile` 只读取原收敛函数与 hf.kernel 的返回帧，未替换科学方法或改变输入；
它会增加 Python 观测开销。本验收不属于性能基准。
主循环/extra 的 dF、dE、梯度、阈值、e_tot、entropy 与收敛返回值均已核验。
两个 Fe₂ 阶段在本次全部正式样本中均收敛。

第二阶段的实际范围（能量单位 Hartree，entropy 为测试返回的无量纲值）：

| 指标 | Linux 1000 次 | Windows 200 次 |
|---|---|---|
| e_free | [-244.7984202572187, -244.79842025447962] | [-244.79842025721885, -244.7984202553502] |
| e_tot | [-243.08699751952162, -243.08699210317866] | [-243.08699570583263, -243.08699313210525] |
| entropy | [17.114227376054416, 17.11428151300971] | [17.114245513586216, 17.114271232449727] |
| converged | 1000/1000 | 200/200 |

每个平台的 9 个现有回归节点均 Passed；未计入正式 1000/200 次：

- `pyscf/scf/test/test_addons.py::KnownValues::test_rohf_smearing1`
- `pyscf/scf/test/test_addons.py::KnownValues::test_rhf_smearing_nelec`
- `pyscf/scf/test/test_addons.py::KnownValues::test_smearing_mu0`
- `pyscf/pbc/scf/test/test_addons.py::KnownValues::test_krhf_smearing`
- `pyscf/pbc/scf/test/test_addons.py::KnownValues::test_kuhf_smearing`
- `pyscf/pbc/scf/test/test_addons.py::KnownValues::test_kuhf_smearing1`
- `pyscf/pbc/scf/test/test_addons.py::KnownValues::test_rhf_smearing`
- `pyscf/pbc/scf/test/test_addons.py::KnownValues::test_uhf_smearing`
- `pyscf/pbc/scf/test/test_addons.py::KnownValues::test_smearing_for_custom_H`

## 保留的失败与未运行项

- Failed（验证基础设施）：最初本机线程探针误选 SciPy `_fblas`，修正后通过；两个调度记录均保留。
- Failed（验证基础设施）：[42280992780](https://github.com/psiQAQ/pyscf/actions/runs/42280992780)
  的子进程导入了包级 `smearing` 函数而非模块，pytest 未执行；该运行工件与取消记录保留。
- Failed（runner 环境）：42281471449 的 1000 次 Linux 启动因缺少 `libblas.so.3` 在导入时终止，
  pytest 实际执行 0 个测试；1000 份日志/进程记录保留，不能计为 1000 个科学断言失败或通过。
- Not Run to completion（取消中断）：42284337939 的分片 8 第 22 次仅收集了测试，未完成断言；
  分片 2 未执行测试。已完成 821 次保留，随后补足 179 次。
- 审计工具纠正：Windows venv launcher PID 与实际解释器 PID 可不同；两者原始记录均保留，
  修正了把两者强行等同的初始审计假设。最终汇总也修正了多路径 artifact 的目录层级假设。
  这两项不改变科学结果，不需要重跑正式样本。
- Not Run（范围外）：全量套件、其他 Python/平台/线程组合、SGX 子项验收。
- Not Run（人工步骤）：用户审阅和上游 issue 更新。本任务未新建修复 PR、未更新或关闭 #3312。

## 证据入口与复核

[acceptance-summary.json](acceptance-summary.json) 绑定 run、源码/工具提交、wheel 哈希、
工件 ZIP 哈希、逐轮审计文件哈希、汇总脚本哈希和准确计数。
完整本地 `ACCEPTANCE.json` 另含 1200 条结果文件哈希索引。
原始工件、原始 ZIP、workflow/job 元数据和日志均已下载到任务私有目录；
GitHub 工件保留期为 90 天，本地副本独立保留。

复核工具为 [collect_run.py](collect_run.py)、[audit_evidence.py](audit_evidence.py) 与
[assemble_acceptance.py](assemble_acceptance.py)。每次命令必须使用独立、属于本任务的输出目录。
最终结论限于 B、所列环境与这些实际样本，不包含历史候选或其他课题结果。

## Notes

OpenAI Codex 协助检查最终代码、编写验证工具、运行专项测试及整理证据/草稿。
所有诊断基础设施只保留在个人 fork 验证分支。按照 AI_POLICY.md，
任何上游提交或 issue 更新均由用户理解、审阅后亲自完成。
