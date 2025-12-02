# HDL Benchmark Suite for PicoRV32

A benchmark suite for testing HDL implementations on the PicoRV32 RISC-V processor. Inspired by SWE-Bench, but for hardware design.

## What's This?

This benchmark suite lets you test LLMs (or humans) on real hardware design tasks. Each task requires modifying the PicoRV32 core to add a feature, and the solution must pass the full test suite.

The framework handles cloning, patching, testing, and reporting results automatically.

## Directory Structure

```
hdl-bench/
├── instances/          # Task configs (JSON)
├── patches/            # Reference solutions (git diffs)
├── specs/              # Task descriptions
├── scripts/            # Automation
│   └── run_instance.py
└── README.md
```

## Prerequisites

You'll need:
- Python 3.6+
- Git
- RISC-V GNU toolchain (riscv64-elf-gcc or riscv32-unknown-elf-gcc)
- Icarus Verilog (iverilog, vvp)
- Make

Install on macOS:
```bash
brew install riscv64-elf-gcc iverilog
```

Install on Ubuntu/Debian:
```bash
sudo apt-get install gcc-riscv64-unknown-elf iverilog
```

## Tasks

### Task 1: Branch Counter

Add a counter that tracks conditional branch instructions (beq, bne, blt, bge, bltu, bgeu). Readable via CSR 0xBC0.

- Spec: `specs/picorv32_task1_spec.md`
- Config: `instances/picorv32_task1.json`
- Patch: `patches/picorv32_task1_ref.diff`

### Task 2: Load/Store Counter

Add a counter for load/store instructions (lb, lh, lw, lbu, lhu, sb, sh, sw). Readable via CSR 0xBC1.

- Spec: `specs/picorv32_task2_spec.md`
- Config: `instances/picorv32_task2.json`
- Patch: `patches/picorv32_task2_ref.diff`

## Running Tests

### Automated (Recommended)

```bash
cd hdl-bench
python3 scripts/run_instance.py instances/picorv32_task1.json patches/picorv32_task1_ref.diff
```

The script clones the repo, applies the patch, runs tests, and returns JSON with pass/fail status.

### Manual

If you want to test manually:

```bash
git checkout picorv32_benchmark_v1  # or commit 3a232e7
git apply hdl-bench/patches/picorv32_task1_ref.diff
make TOOLCHAIN_PREFIX=riscv64-elf- test
```

You should see `branch_counter..OK` and `ALL TESTS PASSED.` in the output.

## Adding New Tasks

Here's how I add new tasks:

1. **Create a branch**
   ```bash
   git checkout picorv32_benchmark_v1
   git checkout -b picorv32_taskN_solution
   ```

2. **Implement the feature**
   - Edit `picorv32.v` 
   - Add test file in `tests/`
   - Add `TEST(...)` to `firmware/start.S`

3. **Test it**
   ```bash
   make clean
   make TOOLCHAIN_PREFIX=riscv64-elf- test
   ```

4. **Generate patch**
   ```bash
   git add <your files>
   git diff --cached picorv32_benchmark_v1 > hdl-bench/patches/picorv32_taskN_ref.diff
   ```

5. **Create instance JSON**
   Create `hdl-bench/instances/picorv32_taskN.json` with task config (see format below).

6. **Write spec**
   Create `hdl-bench/specs/picorv32_taskN_spec.md` describing what needs to be done.

7. **Validate**
   ```bash
   python3 hdl-bench/scripts/run_instance.py \
     hdl-bench/instances/picorv32_taskN.json \
     hdl-bench/patches/picorv32_taskN_ref.diff
   ```

## Instance JSON Format

Each task needs a JSON config file:

```json
{
  "task_id": "picorv32_taskN",
  "repo": "https://github.com/YosysHQ/picorv32.git",
  "baseline_commit": "3a232e7",
  "baseline_tag": "picorv32_benchmark_v1",
  "spec_path": "specs/picorv32_taskN_spec.md",
  "ref_patch_path": "patches/picorv32_taskN_ref.diff",
  "allowed_paths": ["picorv32.v", "firmware/", "tests/"],
  "test_cmds": ["make TOOLCHAIN_PREFIX=riscv64-elf- test"],
  "timeout_s": 600,
  "success_strings": ["ALL TESTS PASSED.", "taskN_test..OK"],
  "forbidden_strings": ["FAIL", "$fatal", "assertion"]
}
```

## Baseline

All tasks start from commit `3a232e7` (tagged `picorv32_benchmark_v1`). This keeps things consistent and makes patches reproducible.

## Troubleshooting

**Patch won't apply?**
- Make sure you're on a clean baseline: `git reset --hard picorv32_benchmark_v1`
- Check that the patch was generated from the right commit
- Look for context line mismatches

**Tests failing?**
- Check toolchain: `riscv64-elf-gcc --version`
- Check Verilog tools: `iverilog -v`
- Make sure test names match `TEST(...)` macros in `firmware/start.S`

**Runner script issues?**
- Python version: `python3 --version` (needs 3.6+)
- Git can clone the repo?
- Patch file path correct?

## Contributing

When adding tasks:
- Keep the same structure as existing tasks
- Write tests that check themselves
- Put requirements in the spec file
- Test with the runner before committing
- Keep patches focused - only what's needed for the task

## License

Same as PicoRV32 (ISC License).
