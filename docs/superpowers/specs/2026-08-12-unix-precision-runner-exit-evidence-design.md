# Unix precision runner 退出证据设计

## 背景与当前判定

Task 7 Phase B 要求 Windows 与 Ubuntu 的 UHF singleton 产物在同一 tested
SHA 上通过严格 validator。当前 Unix 执行链缺少 validator 已要求的直接
runner 退出证据：`.github/workflows/run_unix_precision_tests.sh` 在
`set -euo pipefail` 下直接调用 `run_precision_tests.py`，但不生成
`runner-exit-code.txt`。

现有 Linux run `31548408412`、artifact `9123362435` 因此判定为
`INVALID`。其中 20/20 records 与 summary 只能作为 advisory evidence，不能
替代缺失的 runner 退出码，也不能升级为 production `PASS`。Windows run
`31548379750` 已通过既有严格 installed-wheel 验证，但修复退出证据会产生新
commit 和新 tested SHA；旧 Windows `PASS` 不能与新 SHA 的 Linux 结果配对。

本设计采用已批准的方案 A：在 Unix wrapper 中捕获并持久化它所调用的
Python runner 的原始退出码。实现只允许修改：

- `.github/workflows/run_unix_precision_tests.sh`
- `.github/workflows/test_precision_investigation_contract.py`

不修改 Python runner、strict validator、workflow、科学参数、nodeid、repeat、
thread profile、pytest 配置或任何科学断言。

## 目标

Unix wrapper 对每一次实际 Python runner 调用都必须产生直接、可归档、可由
严格 validator 读取的退出证据：

1. runner 返回 `0` 时，wrapper 返回 `0`，并写入字节精确的
   `runner-exit-code.txt`，内容为 `0\n`；
2. runner 返回非零值 `N` 时，wrapper 写入 `N\n` 后返回同一个 `N`；
3. runner 非零时，Python runner 已写入 output directory 的 records、logs、
   summary 和其他证据保持在原位置，供现有 `if: always()` artifact upload
   收集；
4. output directory 创建或退出码文件写入失败时，wrapper 必须非零退出，不得
   伪造成功，也不得用 runner 原退出码掩盖证据写入失败。

`runner-exit-code.txt` 是 transport/evidence 元数据，不改变测试结果。strict
validator 继续独立要求退出码与 records 状态一致。

## 选择的架构：wrapper 捕获并透传

### 控制流

wrapper 保留文件开头的 `set -euo pipefail`，解析现有四个参数并计算
`repo_root`。在调用 Python 前，它必须先对 `output_dir` 执行 `mkdir -p`。
Python 命令及其所有现有参数保持字节语义不变，只用 Bash 的 `if/else` 包围：

```bash
mkdir -p "$output_dir"
runner_exit=0
if python "$repo_root/.github/workflows/run_precision_tests.py" \
  --nodeids-file "$nodeids_file" \
  --repeats "$repeats" \
  --profile "$profile" \
  --output-dir "$output_dir" \
  --tested-sha "${GITHUB_SHA:-$(git -C "$repo_root" rev-parse HEAD)}" \
  --working-directory "$repo_root" \
  --rootdir "$repo_root" \
  --pytest-config "$repo_root/pytest.ini" \
  --environment-mode source-tree \
  --collector "$repo_root/.github/workflows/collect_precision_environment.py"; then
  runner_exit=0
else
  runner_exit=$?
fi
printf '%s\n' "$runner_exit" > "$output_dir/runner-exit-code.txt"
exit "$runner_exit"
```

实现不得用 `command || runner_exit=$?`、临时关闭 `set -e`、pipeline、subshell
或第二次 runner 调用替代上述结构。

`if` 条件中的命令不触发 Bash `errexit` 的提前终止，因此 `else` 内紧邻的
`$?` 是 Python runner 的原始退出码。退出码写成功后，最后一个 `exit` 透传同一
值。若 `mkdir -p`、redirection 或 `printf` 失败，`set -e` 使 wrapper 在显式
透传前失败；该失败是正确的 fail-closed 结果，因为缺少完整退出证据的 artifact
不能被认为有效。若 runner 被 signal 终止，Bash 提供的 `128 + signal` 状态按同一
规则记录和透传。

### 文件格式与路径

- 文件路径固定为 `$output_dir/runner-exit-code.txt`；不新增参数或环境变量。
- 内容只允许十进制非负退出码、一个 LF：精确正则为 `^[0-9]+\n$`。
- `0\n` 和 `23\n` 的预期字节分别为 `b'0\n'` 和 `b'23\n'`。
- 这些字节全部位于 ASCII 子集，因此同时是 UTF-8 without BOM；不得写 BOM、
  CRLF、空格、标签或说明文字。
- wrapper 与 Python contract test 自身继续使用 UTF-8 without BOM、LF-only、
  final LF。shell 文件保持现有 executable bit。
- workflow 已用 `tmp/precision-results/**` 且 `if: always()` 上传，不修改 upload
  step。wrapper 在 runner 前创建目录，确保成功和失败路径都有证据落点。

本设计不要求临时文件、rename、锁或新 schema。每个 CI job 使用独立的干净
output directory；直接写最终文件是满足当前单 writer 边界的最小方案。

## 错误处理

| 场景 | 必须行为 | 证据判定 |
| --- | --- | --- |
| output path 已是普通文件 | `mkdir -p` 失败，wrapper 非零退出，runner 调用 `0` 次 | INVALID/operational；不得声称测试结果 |
| runner 返回 `0` | 写精确 `0\n`，wrapper 返回 `0` | validator 仍需核对全部 records |
| runner 返回 `23` | 保留 runner 产物，写精确 `23\n`，wrapper 返回 `23` | 可归档的失败证据，不是 PASS |
| runner 被 signal 终止 | 写 Bash 原始非零状态并透传 | 可归档的 operational/test failure evidence |
| output directory 已存在且 exit path 已是目录 | runner 调用 `1` 次并保留 sentinel；redirection 失败使 wrapper 非零，exit path 仍不是普通文件 | fail closed；artifact 不完整 |
| 其他退出码文件写入失败 | wrapper 非零退出，即使 runner 原先返回 `0` | fail closed；artifact 不完整 |
| records 与退出码矛盾 | wrapper 不修正 records | strict validator 判 INVALID |
| artifact upload 失败 | 不重跑 runner、不重写退出码 | 保留 run 身份，按 artifact latency/failure 流程处理 |

wrapper 不捕获、转换或重试 Python runner 的 stdout/stderr，也不把非零转换为
成功。任何自动 retry 都会破坏首个失败与退出码的一一对应，因此禁止。

## TDD 设计

### 测试边界

在 `.github/workflows/test_precision_investigation_contract.py` 中新增一个行为测试，
真实执行仓库内 `run_unix_precision_tests.sh`，但把临时 `bin` 目录置于 `PATH`
最前，并在其中提供可执行的 fake `python`。测试必须通过
`subprocess.run(command, shell=False)` 调用 `resolve_bash()` 返回的绝对路径，
其中 `command` 是 Bash 绝对路径、真实 wrapper 和四个 wrapper 参数组成的 argv；不得只读取脚本文本
或用字符串 `grep` 推断行为。

#### `resolve_bash()` 设计

contract test 新增单一 helper `resolve_bash() -> Path`，禁止让 Windows 的
`shutil.which('bash')` 偶然选中 WSL compatibility shim：

1. Windows 上先调用 `shutil.which('git')`。结果必须存在，resolve 后文件名必须为
   `git.exe`，其直接父目录名按 case-insensitive 比较只能是 `cmd` 或 `bin`。
2. Git 安装根固定为 `git.exe` 父目录的父目录；Bash candidate 固定为该根下的
   `bin/bash.exe`，必须 resolve 为普通可执行文件。Windows 分支完全不采用
   `shutil.which('bash')` 的结果，也没有其他 fallback。
3. normalize 后位于 `%SystemRoot%/System32` 内的 `git.exe` 或 Bash candidate
   必须拒绝；尤其不得执行 `C:\Windows\System32\bash.exe`，因为该路径是 WSL
   compatibility shim，不是本测试要求的 MSYS Bash。
4. 对 candidate 执行
   `subprocess.run([str(candidate), '--version'], capture_output=True,
   text=True, shell=False)`。exit 必须为 `0`，stdout/stderr 合并后按
   case-insensitive 搜索必须包含 `gnu bash` 和 `msys`，否则明确失败。
5. Linux/macOS 继续使用 `shutil.which('bash')`，resolve 后要求普通可执行文件，
   并执行相同 `--version` probe；exit 必须为 `0` 且输出包含 `gnu bash`，但不要求
   `msys`。

本机已核实的 Windows discovery facts 为：

```text
git  = D:\Program Files\Git\cmd\git.exe
bash = D:\Program Files\Git\bin\bash.exe
GNU bash, version 5.2.15(1)-release (x86_64-pc-msys)
```

任何 discovery/probe 失败都是 test harness failure，不得 skip，也不得回退到 WSL、
`cmd.exe` 或 PowerShell shell emulation。

临时目录放在 repository `tmp` 下，传给 Bash 的 nodeids、output directory、
调用记录和 fake artifact 路径都使用相对 repository root 的 POSIX-style 路径。
这避免 Windows drive-letter 在 MSYS 环境变量中的二次解释，同时在 Linux 与
macOS 上保持同一调用。`PATH` 用宿主 `os.pathsep` 前置 fake `bin`；fake 文件使用
LF、UTF-8 without BOM，并在 POSIX/MSYS 支持的文件系统上设置 executable bit。
本机 Windows 的 Git/MSYS Bash 已实测可把宿主 `os.pathsep=';'` 构造的 `PATH`
转换为 MSYS command lookup；测试保留该方式，不手写冒号分隔或调用 `env.exe`。

测试环境显式设置：

- `GITHUB_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`，从而验证
  `--tested-sha` 且完全绕开 wrapper 的 `git rev-parse` fallback；
- `FAKE_PYTHON_EXIT` 为当前 subtest 的 `0` 或 `23`；
- fake invocation record 与 fake evidence 文件都位于本 subtest 的 output
  directory。

fake `python` 必须：

1. 先把收到的每个 argv 写到 output directory 之外的 invocation record，使用可
   无歧义恢复参数边界的 NUL 分隔格式；因此即使 output path 无效也能计算调用次数；
2. 从 argv 中要求 `--output-dir` 恰好出现一次，读取其下一项，并先要求该路径已经
   是 directory；fake 自身绝不执行 `mkdir`；
3. 若 output directory 不存在或不是 directory，返回保留给 harness 的非零状态，
   不创建目录、不写 sentinel，也不返回 `FAKE_PYTHON_EXIT`；
4. 只有 output directory 已存在时，才在其中写固定 fake evidence sentinel，然后
   返回 `FAKE_PYTHON_EXIT`；
5. 不导入或执行真实 `run_precision_tests.py`，因此测试不运行科学计算。

这组职责对所有 case 不变。测试负责决定 output path 的初始形态；fake 只观察，
不修复被测 wrapper 应承担的目录创建或退出文件写入职责。

### RED

先只增加测试并在当前 wrapper 上运行。RED 分成不同边界，不宣称所有 case 都只因
同一个原因失败。

#### 目录预创建 RED

output directory 初始不存在，`FAKE_PYTHON_EXIT=0`。fake 先记录 invocation，随后
要求 output directory 已存在且绝不自行创建。当前 wrapper 没有 `mkdir -p`，因此
该 case 允许观察到 fake 因目录未预创建而返回 harness failure；GREEN 后必须由
wrapper 先创建目录，fake 才写 sentinel 并返回 `0`。

#### 退出码 `0` / `23` RED

测试分别预创建两个 output directories，再执行两次 wrapper：

- success subtest 的 wrapper exit 已是 `0`，但 `runner-exit-code.txt` 缺失；
- failure subtest 的 wrapper exit 已是 `23`，fake evidence 仍在，但
  `runner-exit-code.txt` 缺失；
- 这两个 subtests 的 fake 都被调用恰一次、argv 和 sentinel 都已正确；当前 RED 的
  唯一失败断言必须是缺少精确退出文件。

#### fail-closed RED

另外增加两个独立行为 case：

1. output path 预先创建为普通文件。GREEN 要求 `mkdir -p` 先失败、wrapper 非零、
   invocation record 证明 fake 调用 `0` 次。当前 wrapper 会越过缺失的 precreate
   gate 并调用 fake，因此该行为断言先 RED。
2. output directory 预创建成功，但 `runner-exit-code.txt` 预先创建为 directory；
   `FAKE_PYTHON_EXIT=0`。fake 必须调用恰一次、写 sentinel 并返回 `0`；GREEN 要求
   wrapper 的 redirection 失败并非零退出，sentinel 保留，而且 exit path 仍不是
   ordinary file。当前 wrapper 不尝试写 exit file，会错误返回 `0`，因此该行为断言
   先 RED。

若 RED 因找不到 Bash、fake `python` 未被调用、路径转换或其他 harness 问题而
偏离上述各 case 的预期失败边界，不得进入实现；先修正测试 harness。只有预创建的
`0` / `23` cases 要求 RED 唯一指向缺少 `runner-exit-code.txt`。

### GREEN

应用最小 wrapper 修改后，同一个行为测试验证以下完整状态表：

| 初始 output 状态 | fake exit | wrapper exit | exit file | sentinel | fake calls |
| --- | --- | --- | --- | --- | --- |
| 不存在 | `0` | `0` | bytes `b'0\n'` | 存在且内容精确 | `1` |
| 预建 directory | `0` | `0` | bytes `b'0\n'` | 存在且内容精确 | `1` |
| 预建 directory | `23` | `23` | bytes `b'23\n'` | 仍存在且内容精确 | `1` |
| 普通文件 | 不得调用 | 非零 | 不存在 ordinary exit file | 不存在 | `0` |
| 预建 directory，exit path 是 directory | `0` | 非零 | 仍为 directory，不是 ordinary file | 保留且内容精确 | `1` |

argv 必须证明 wrapper 仍调用 exact
`$repo_root/.github/workflows/run_precision_tests.py`，并完整保留现有参数：
`--nodeids-file`、`--repeats`、`--profile`、`--output-dir`、
`--tested-sha`、`--working-directory`、`--rootdir`、`--pytest-config`、
`--environment-mode source-tree` 和 `--collector`。测试还要断言
`runner-exit-code.txt` 没有 UTF-8 BOM、没有 CR、没有尾随字节。

现有 workflow 字符串合同测试可以继续保护 `if: always()` 和 artifact path，
但它不能代替上述行为测试。新功能的 RED/GREEN 证据必须来自真实 wrapper 子进程。

### 平台验证

push 前的平台门禁仅在本机 Windows 的 MSYS/Git Bash 上运行完整四案例合同和
普通静态检查。四案例包括目录预创建、预建目录下 runner `0`/`23`、output path
为普通文件，以及 exit path 为目录；不得用 WSL、`cmd.exe`、`shell=True`、
PowerShell 模拟 Bash 或字符串 grep 代替真实 wrapper 子进程。MSYS 路径差异只允许
通过收紧临时路径和 argv 规范化处理，不允许降低目录预创建、调用次数、退出码、
sentinel 或文件字节断言。

实现代码仍保持 Linux/macOS 与 Windows/MSYS 共用的行为合同和 `resolve_bash()`
分支，但本地没有原生 Linux/macOS host。因此 push 前无需、也不得声称已经运行或
通过原生 Linux/macOS contract test。真实 Unix 边界由 push 后的 macOS witness
artifact 提供直接证据，而不是由未执行的本地平台测试推断。

## 部署与重新取证

### 独立 CI evidence commit

实现阶段从 validation branch
`codex/test/sgx-extra-cycle-convergence-validation` 的精确 head
`2eb90e3f99219e28390570d13bd906cfe6e17012` 开始。实现作为一个独立的 CI
evidence commit 叠加在该 head 上，diff 恰好包含 Unix wrapper 与其 contract
test 两个文件。不得混入 scientific source、nodeid selection、validator、workflow、
heartbeat、文档或 archive 修改。

在本机 MSYS Bash 完整四案例合同、完整 contract test、Bash/Python 静态门禁、
encoding/EOL/mode/scope 检查全部通过后，先独立 review commit 与 RED/GREEN
证据。只有 review 接受并获得既有远端权限后，才以普通 fast-forward push 把同一
validation branch 更新到新 head。不得 force-push、改写旧 commit 或把 evidence
commit 合并进科学修复 commit；push 前不要求原生 Linux/macOS test evidence。

### push 后 macOS wrapper witness

普通 fast-forward push 新 head 后，先且只先派发一条 macOS wrapper witness：

- nodeid：`pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing`
- repeats：`1`
- platform：`macos-latest`
- Python：`3.12`
- profile：`4/4`（validator profile `omp4-blas4`）
- artifact：`precision-macOS-py3.12`
- evidence mode：`source-tree`
- expected native library count：`16`

该 witness 必须通过独立 immutable latch/binding 绑定唯一 run ID，并严格验证
attempt 1、`workflow_dispatch`、workflow/branch/head、唯一 `precision` job、唯一
artifact、exact inputs、runtime LibXC、checkout/source-tree provenance、macOS
`otool -L` linkage、16 项 native inventory，以及字节精确的
`runner-exit-code.txt == b'0\n'`。冻结 validator 必须返回 `valid=true` 和 plain
`PASS`。Actions/job success、单条 pytest pass 或 artifact 存在都不能代替 strict
validator。

macOS witness 只证明新 SHA 上真实 Unix wrapper 的成功路径、退出码持久化和
source/native provenance 可归档；`repeats=1` 不是 UHF 科学稳定性结论，也不替代
后续 Ubuntu 20-repeat evidence。只有该 witness strict `PASS` 后，才解锁下面的
Windows+Ubuntu pair dispatch；witness failure 或 `INVALID` 必须保留证据并停止，
不得提前派发 pair。

### 同一新 SHA 的正式复跑

旧 archives 和 run metadata 保持 immutable。新 head 必须重新派发以下两个
UHF singleton runs，二者 tested SHA 必须精确相同：

- nodeid：`pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing`
- repeats：`20`
- Python：`3.12`
- profile：`4/4`（validator profile `omp4-blas4`）
- Windows：`windows-latest`，artifact `precision-Windows-py3.12`，
  `installed-wheel`，expected native library count `26`
- Linux：`ubuntu-latest`，artifact `precision-Linux-py3.12`，
  `source-tree`，expected native library count `16`

两次 dispatch 使用各自 immutable latch/binding，并由同一个 heartbeat 同时管理两个
精确 run IDs；不得同时启动第二个 poller。每个 run 仍需验证 attempt 1、
`workflow_dispatch`、workflow/branch/head、唯一 `precision` job、唯一 artifact、
Python/profile/repeats/nodeid、runtime LibXC、records/logs/summary/environment/native
linkage。Windows 必须重新得到 strict `PASS`，不能引用 run `31548379750` 替代；
Linux artifact 必须包含精确 `runner-exit-code.txt` 并得到 strict `PASS`，不能把
run `31548408412` 的 20/20 advisory 重新解释为有效。

只有两个新 artifact 都由冻结的 strict validator 报告 `valid=true`、`PASS`，且
报告绑定同一新 SHA，Task 7 才可恢复 Step 3。Actions/job conclusion 或 20/20 summary
单独都不满足该门禁。

## 回退与 no-replay 规则

- implementation review 未通过时，不 push；修改或重建独立 evidence commit，
  Task 7 保持暂停。
- evidence commit 已发布但发现缺陷时，使用独立 revert 或后续修复 commit；不
  force-push、不改写旧 SHA。revert 后没有新 SHA 双平台证据，Step 3 仍不得恢复。
- 不修改、补文件或重新打包旧 run `31548408412` / artifact `9123362435`，也不
  修改旧 Windows archive。旧 `INVALID` 与旧 `PASS` 判定均保留原义。
- 新 dispatch 已被 latch 记录但当前 shell 中断时，只按同一 latch、binding 和
  exact run ID 恢复；不得重放 `gh workflow run`。artifact latency 只重查同一 run，
  不触发新 run。
- macOS witness 已 dispatch 后只恢复其 exact run ID；不得为了等待或 artifact
  latency 重放 witness。witness strict `PASS` 前不得创建 Windows/Linux pair latch。
- 任一新 run 失败或 INVALID 时，保留第一份有效失败证据，停止 Step 3；修复后
  使用另一个新 SHA 和新的 immutable dispatch identity，不覆盖本轮 archive。

## 被拒绝的替代方案

### 方案 B：在 workflow step 外层捕获退出码

让 `ci-precision-check.yml` 包裹 wrapper、捕获 `$?` 再写文件，会把同一错误处理
拆到 workflow 与 wrapper 两层，并要求绕开 step shell 的默认 fail-fast。它还会
记录 wrapper 总体状态，而不是在最接近 Python runner 的边界冻结原始状态。该方案
扩大修改范围、降低本机 wrapper 可测性，因此拒绝。

### 方案 C：从 records、summary 或 Actions conclusion 推断退出码

放宽 validator 以接受缺失文件，或根据 20/20 records、job conclusion 合成退出码，
会把直接进程证据降为推断。records 可能在 runner 末尾异常前已完整，Actions
conclusion 又混合 setup、wrapper、upload 等不同层次；二者都不能证明 Python
runner 的原始退出状态。该方案会错误地使现有 Linux artifact 看似有效，因此拒绝。

## 非目标与长期边界

- 不修改 `run_precision_tests.py`、`validate_precision_production.py` 或
  `ci-precision-check.yml`。
- 不修改 UHF/SCF/SGX implementation、测试断言、tolerance、repeat、profile、
  dependency、build、wheel 或 native linkage 规则。
- 不为成功/失败增加 retry，不重新派发旧 run，不把 advisory evidence 宣称为
  production proof。
- 不在本设计 commit 中 push、dispatch、启动 heartbeat、改变 Goal 或写生产状态。
- 该变更是 CI evidence infrastructure，必须保持为独立 commit；长期若提交上游，
  也应与 scientific fixes 分开 review，不扩大为 validator/schema 重构。
- `pyscf/pyscf#3312` 现在不更新。只有 Task 7 后续 Step 3 及完整长期验收闭环满足
  既有批准计划后，才按独立远端写入授权更新该 issue。

## 验收标准

实现和部署只有在以下条件全部满足时完成：

1. implementation diff 仅含两个批准文件，shell/Python 文件均 UTF-8 without
   BOM、LF-only、final LF，shell executable bit 不丢失；
2. observed RED 被明确拆分：output 不存在 case 允许因 wrapper 未预创建目录失败；
   output 预建的 `0` / `23` cases 唯一因缺少 exit file 失败；两个 fail-closed
   cases 分别因 runner 被错误调用和 exit redirection 未执行而失败；
3. success `0` 与 failure `23` GREEN 均验证调用一次、完整 argv、相同 wrapper
   exit、精确文件字节和非零路径 artifact 保留；
4. output ordinary-file case 验证 wrapper 非零且 fake 调用 `0` 次；exit-path
   directory case 验证 wrapper 非零、fake 调用 `1` 次、sentinel 保留且没有 ordinary
   exit file；
5. `resolve_bash()` 在 Windows 从 `git.exe` 安装根选择 MSYS Bash 并拒绝
   System32/WSL shim；push 前本机 MSYS Bash 的完整四案例合同通过，不以文本 grep
   代替执行，也不声称未执行的原生 Linux/macOS test 已通过；
6. implementation commit 在 `2eb90e3f99219e28390570d13bd906cfe6e17012`
   之上完成 Windows/MSYS 门禁和独立 review，再以普通 fast-forward push 形成新
   validation head；
7. push 后 macOS singleton/1/Python 3.12/4/4 witness 先通过冻结 validator：artifact
   含 exact `runner-exit-code.txt == b'0\n'`、source-tree/native-16/provenance，且该
   witness 只作为 wrapper transport 证据，不表述为科学稳定性结论；
8. macOS witness strict `PASS` 后，新 Windows 与 Ubuntu runs 才使用同一新 SHA、
   singleton/20/Python 3.12/4/4 由唯一 heartbeat 管理；
9. Windows installed-wheel/native-26 与 Linux source-tree/native-16 artifact 均
   通过冻结 strict validator，报告 `valid=true`、`PASS`；
10. 旧 archives 未改变、无 dispatch replay、无第二 poller、无提前更新 #3312；
11. macOS witness 与 Windows/Linux 两个新 PASS 全部满足之前，Task 7 Step 3 始终
    保持暂停。
