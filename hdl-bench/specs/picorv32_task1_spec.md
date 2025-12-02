# picorv32_task1: Branch Instruction Counter

## Context

PicoRV32 is a small RISC-V (RV32I) processor core implementation. This task requires adding a performance counter that tracks the number of conditional branch instructions executed by the processor.

## Requirements

### Feature: Branch Instruction Counter

Add a new 32-bit performance counter register that counts the number of conditional branch instructions (beq, bne, blt, bge, bltu, bgeu) that are executed/retired by the processor.

### Behavioral Requirements

1. **Counter Register**: Add a 32-bit register `count_branch` that increments whenever a conditional branch instruction completes execution.

2. **Reset Behavior**: The counter must reset to 0 when the processor is reset (when `resetn` is low).

3. **Increment Condition**: The counter increments when any of the following conditional branch instructions are executed:
   - `beq` (branch if equal)
   - `bne` (branch if not equal)
   - `blt` (branch if less than, signed)
   - `bge` (branch if greater than or equal, signed)
   - `bltu` (branch if less than, unsigned)
   - `bgeu` (branch if greater than or equal, unsigned)

   Note: The counter should increment for ALL conditional branch instructions, regardless of whether the branch is taken or not taken. The counter increments when the branch instruction is executed (when `is_beq_bne_blt_bge_bltu_bgeu` is true).

4. **CSR Access**: The counter must be readable via a custom CSR (Control and Status Register) at address `0xBC0` using the `csrr` instruction:
   ```
   csrr xN, 0xBC0  // Reads count_branch into register xN
   ```

5. **CSR Decode Pattern**: The CSR instruction decode should match the pattern used by other counter CSRs (rdcycle, rdinstr):
   - Opcode: `7'b1110011` (CSR instruction opcode)
   - CSR address [31:20]: `12'hBC0`
   - funct3 [14:12]: `3'b010` (CSRR)
   - Full pattern: `mem_rdata_q[31:12] == 20'hBC002`

6. **Enable Condition**: The counter should only be active when `ENABLE_COUNTERS` parameter is set (same as other counters).

### Expected Observable Effects

1. **Test Program**: A test program (`tests/branch_counter.S`) must be created that:
   - Reads the initial counter value via `csrr x10, 0xBC0`
   - Executes a known number of conditional branch instructions (e.g., 5 branches in a loop)
   - Reads the counter again and verifies it incremented by the expected amount
   - Executes additional conditional branches (e.g., 3 branches that are not taken)
   - Verifies the final counter value

2. **Test Integration**: The test must be added to `firmware/start.S` using the `TEST(branch_counter)` macro.

3. **Success Criteria**: When running `make TOOLCHAIN_PREFIX=riscv64-elf- test`, the output must include:
   - `branch_counter..OK`
   - `ALL TESTS PASSED.`

### Constraints

- Do not modify external interfaces of the top-level module
- Only modify `picorv32.v`, `firmware/start.S`, and add `tests/branch_counter.S`
- The counter must wrap around on overflow (32-bit unsigned arithmetic)
- The implementation must be compatible with existing counter infrastructure (rdcycle, rdinstr)
- The counter increments for all conditional branch instructions, whether taken or not taken
- The counter should be included in the `is_rdcycle_rdcycleh_rdinstr_rdinstrh` wire assignment for consistency with other counters
