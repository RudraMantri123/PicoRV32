# HDL Benchmark Suite for PicoRV32

This directory contains a comprehensive benchmark suite for testing HDL (Hardware Description Language) implementations on the PicoRV32 RISC-V processor core.

## Overview

The benchmark suite provides a structured framework for:
- Defining independent benchmark tasks (features/bugfixes)
- Implementing reference solutions with tests
- Automating verification through patches and test runners
- Ensuring reproducibility and provenance

## Directory Structure

```
hdl-bench/
├── instances/          # JSON configuration files for each benchmark task
├── patches/            # Reference solution patches (git diffs)
├── specs/              # Markdown specifications for each task
├── scripts/            # Automation scripts
│   └── run_instance.py # Main runner script
└── README.md          # This file
```

## Prerequisites

- Python 3.6+
- Git
- RISC-V GNU toolchain (riscv64-elf-gcc or riscv32-unknown-elf-gcc)
- Icarus Verilog (iverilog, vvp)
- Make

### Installing Dependencies

macOS (Homebrew):
```bash
brew install riscv64-elf-gcc iverilog
```

Ubuntu/Debian:
```bash
sudo apt-get install gcc-riscv64-unknown-elf iverilog
```

## Benchmark Tasks

### Task 1: Branch Instruction Counter

Specification: specs/picorv32_task1_spec.md  
Instance Config: instances/picorv32_task1.json  
Reference Patch: patches/picorv32_task1_ref.diff

Adds a CSR-accessible counter (0xBC0) that tracks the number of conditional branch instructions (beq, bne, blt, bge, bltu, bgeu) executed.

### Task 2: Load/Store Instruction Counter

Specification: specs/picorv32_task2_spec.md  
Instance Config: instances/picorv32_task2.json  
Reference Patch: patches/picorv32_task2_ref.diff

Adds a CSR-accessible counter (0xBC1) that tracks the number of load/store memory instructions (lb, lh, lw, lbu, lhu, sb, sh, sw) executed.

## Running Benchmarks

### Using the Runner Script

To run a benchmark instance:

```bash
cd hdl-bench
python3 scripts/run_instance.py instances/picorv32_task1.json patches/picorv32_task1_ref.diff
```

The script will:
1. Clone the PicoRV32 repository
2. Checkout the baseline commit (3a232e7)
3. Apply the reference patch
4. Run the test commands
5. Verify success/forbidden strings
6. Return a JSON result: {"task_id": "...", "status": "pass"} or {"status": "fail", ...}

### Manual Testing

To manually test a task:

```bash
# From the picorv32 repository root
git checkout picorv32_benchmark_v1  # or commit 3a232e7
git apply hdl-bench/patches/picorv32_task1_ref.diff
make TOOLCHAIN_PREFIX=riscv64-elf- test
```

Expected output should include:
- branch_counter..OK (for task1) or loadstore_counter..OK (for task2)
- ALL TESTS PASSED.

## Creating New Benchmark Tasks

### Step-by-Step Workflow

1. Create a Git Branch
   ```bash
   git checkout picorv32_benchmark_v1
   git checkout -b picorv32_taskN_solution
   ```

2. Implement the Feature/Test
   - Modify picorv32.v as needed
   - Create test file in tests/
   - Add TEST(...) macro to firmware/start.S

3. Verify Locally
   ```bash
   make clean
   make TOOLCHAIN_PREFIX=riscv64-elf- test
   ```

4. Generate Reference Patch
   ```bash
   git add <modified_files>
   git diff --cached picorv32_benchmark_v1 > hdl-bench/patches/picorv32_taskN_ref.diff
   ```

5. Create Instance Configuration
   - Create hdl-bench/instances/picorv32_taskN.json
   - Define task_id, baseline_commit, test_cmds, success_strings, etc.

6. Create Specification
   - Create hdl-bench/specs/picorv32_taskN_spec.md
   - Document requirements, constraints, and expected behavior

7. Validate with Runner
   ```bash
   python3 hdl-bench/scripts/run_instance.py \
     hdl-bench/instances/picorv32_taskN.json \
     hdl-bench/patches/picorv32_taskN_ref.diff
   ```

## Instance JSON Format

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

## Baseline Commit

All tasks use commit 3a232e7 (tagged as picorv32_benchmark_v1) as the baseline. This ensures:
- Consistent starting point
- Reproducible patches
- Clean separation between tasks

## Troubleshooting

### Patch Application Fails

- Ensure you're starting from a clean baseline: git reset --hard picorv32_benchmark_v1
- Verify patch was generated from the correct baseline commit
- Check for context mismatches in the patch file

### Test Failures

- Verify toolchain is installed: riscv64-elf-gcc --version
- Check that Icarus Verilog is available: iverilog -v
- Ensure test labels match TEST(...) macro in firmware/start.S

### Runner Script Issues

- Ensure Python 3.6+ is available: python3 --version
- Check that Git can clone the repository
- Verify patch file path is correct and accessible

## Contributing

When adding new tasks:
1. Follow the existing task structure
2. Ensure tests are comprehensive and self-checking
3. Document all requirements in the spec file
4. Validate with the runner script before committing
5. Keep patches minimal and focused on the task

## License

This benchmark suite follows the same license as the PicoRV32 project (ISC License).
