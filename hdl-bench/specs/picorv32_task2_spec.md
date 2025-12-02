# picorv32_task2: Load/Store Instruction Counter

## Context

PicoRV32 is a small RISC-V (RV32I) CPU core. This task adds a counter that tracks load and store memory instructions.

## What to Do

Add a 32-bit counter that increments every time a load or store instruction completes. Make it readable via CSR.

### Counter Details

Add a register `count_loadstore` (32 bits). It increments when these instructions finish:
- Loads: `lb`, `lh`, `lw`, `lbu`, `lhu`
- Stores: `sb`, `sh`, `sw`

The counter increments when the memory operation completes (when `mem_done` is asserted), even if the operation fails.

### Reset

Resets to 0 when `resetn` is low.

### CSR Access

Readable via CSR address `0xBC1`:
```
csrr xN, 0xBC1  // Reads count_loadstore into register xN
```

Decode pattern (same style as other counters):
- Opcode: `7'b1110011`
- CSR address [31:20]: `12'hBC1`
- funct3 [14:12]: `3'b010` (CSRR)
- Full pattern: `mem_rdata_q[31:12] == 20'hBC102`

### Enable Condition

Only active when `ENABLE_COUNTERS` is set.

### Testing

Create `tests/loadstore_counter.S` that:
- Reads initial value: `csrr x10, 0xBC1`
- Executes some loads/stores (e.g., 3 loads + 2 stores = 5 total)
- Checks counter incremented by 5
- Executes more (e.g., 2 loads + 1 store = 3 total)
- Verifies final value

Add `TEST(loadstore_counter)` to `firmware/start.S`.

Running `make TOOLCHAIN_PREFIX=riscv64-elf- test` should show:
- `loadstore_counter..OK`
- `ALL TESTS PASSED.`

### Constraints

- Don't modify top-level module interface
- Only touch `picorv32.v`, `firmware/start.S`, and add `tests/loadstore_counter.S`
- Counter wraps on overflow (32-bit unsigned)
- Compatible with existing counter infrastructure
- Increments when memory ops complete in `cpu_state_ldmem` and `cpu_state_stmem` states
