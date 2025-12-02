# picorv32_task2: Load/Store Instruction Counter

## Context

PicoRV32 is a small RISC-V (RV32I) processor core implementation. This task requires adding a performance counter that tracks the number of load and store memory instructions executed by the processor.

## Requirements

### Feature: Load/Store Instruction Counter

Add a new 32-bit performance counter register that counts the number of load and store memory instructions (lb, lh, lw, lbu, lhu, sb, sh, sw) that are executed/retired by the processor.

### Behavioral Requirements

1. **Counter Register**: Add a 32-bit register `count_loadstore` that increments whenever a load or store instruction completes execution.

2. **Reset Behavior**: The counter must reset to 0 when the processor is reset (when `resetn` is low).

3. **Increment Condition**: The counter increments when any of the following memory instructions are retired:
   - Load instructions: `lb`, `lh`, `lw`, `lbu`, `lhu`
   - Store instructions: `sb`, `sh`, `sw`

   Note: The counter should increment when the memory operation completes (when `mem_done` is asserted), regardless of whether the operation succeeds or fails.

4. **CSR Access**: The counter must be readable via a custom CSR (Control and Status Register) at address `0xBC1` using the `csrr` instruction:
   ```
   csrr xN, 0xBC1  // Reads count_loadstore into register xN
   ```

5. **CSR Decode Pattern**: The CSR instruction decode should match the pattern used by other counter CSRs (rdcycle, rdinstr):
   - Opcode: `7'b1110011` (CSR instruction opcode)
   - CSR address [31:20]: `12'hBC1`
   - funct3 [14:12]: `3'b010` (CSRR)
   - Full pattern: `mem_rdata_q[31:12] == 20'hBC102`

6. **Enable Condition**: The counter should only be active when `ENABLE_COUNTERS` parameter is set (same as other counters).

### Expected Observable Effects

1. **Test Program**: A test program (`tests/loadstore_counter.S`) must be created that:
   - Reads the initial counter value via `csrr x10, 0xBC1`
   - Executes a known number of load/store instructions (e.g., 3 loads + 2 stores = 5 total)
   - Reads the counter again and verifies it incremented by the expected amount
   - Executes additional load/store instructions (e.g., 2 loads + 1 store = 3 total)
   - Verifies the final counter value

2. **Test Integration**: The test must be added to `firmware/start.S` using the `TEST(loadstore_counter)` macro.

3. **Success Criteria**: When running `make TOOLCHAIN_PREFIX=riscv64-elf- test`, the output must include:
   - `loadstore_counter..OK`
   - `ALL TESTS PASSED.`

### Constraints

- Do not modify external interfaces of the top-level module
- Only modify `picorv32.v`, `firmware/start.S`, and add `tests/loadstore_counter.S`
- The counter must wrap around on overflow (32-bit unsigned arithmetic)
- The implementation must be compatible with existing counter infrastructure (rdcycle, rdinstr)
- The counter increments when memory operations complete in both `cpu_state_ldmem` and `cpu_state_stmem` states

