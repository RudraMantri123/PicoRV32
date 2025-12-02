# picorv32_task1: Branch Instruction Counter

## Context

PicoRV32 is a small RISC-V (RV32I) CPU core. This task is about adding a performance counter that counts conditional branch instructions.

## What to Do

Add a 32-bit counter register that increments every time a conditional branch instruction executes. The counter should be readable via a CSR (Control and Status Register).

### Counter Details

Add a register called `count_branch` (32 bits). It increments whenever one of these branch instructions executes:
- `beq` - branch if equal
- `bne` - branch if not equal  
- `blt` - branch if less than (signed)
- `bge` - branch if greater or equal (signed)
- `bltu` - branch if less than (unsigned)
- `bgeu` - branch if greater or equal (unsigned)

Important: Count ALL branches, whether they're taken or not. The counter increments when `is_beq_bne_blt_bge_bltu_bgeu` is true.

### Reset

The counter resets to 0 when `resetn` goes low.

### CSR Access

Make it readable via CSR address `0xBC0`:
```
csrr xN, 0xBC0  // Reads count_branch into register xN
```

The decode pattern should match other counters (rdcycle, rdinstr):
- Opcode: `7'b1110011`
- CSR address [31:20]: `12'hBC0`
- funct3 [14:12]: `3'b010` (CSRR)
- Full match: `mem_rdata_q[31:12] == 20'hBC002`

### Enable Condition

Only active when `ENABLE_COUNTERS` is set (like the other counters).

### Testing

Create a test file `tests/branch_counter.S` that:
- Reads initial counter value with `csrr x10, 0xBC0`
- Runs some branches (e.g., 5 branches in a loop)
- Checks the counter incremented correctly
- Runs more branches (e.g., 3 not-taken branches)
- Verifies final value

Add `TEST(branch_counter)` to `firmware/start.S`.

When you run `make TOOLCHAIN_PREFIX=riscv64-elf- test`, you should see:
- `branch_counter..OK`
- `ALL TESTS PASSED.`

### Constraints

- Don't change the top-level module interface
- Only modify `picorv32.v`, `firmware/start.S`, and add `tests/branch_counter.S`
- Counter wraps on overflow (normal 32-bit unsigned behavior)
- Should work with existing counter code (rdcycle, rdinstr)
- Include in `is_rdcycle_rdcycleh_rdinstr_rdinstrh` wire for consistency
