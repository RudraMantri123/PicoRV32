# See LICENSE for license details.

#*****************************************************************************
# branch_counter.S
#-----------------------------------------------------------------------------
#
# Test branch instruction counter CSR 0xBC0
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV32U
.option arch, +zicsr
RVTEST_CODE_BEGIN

  # Read initial value of branch counter
  csrr x10, 0xBC0

  # Run 5 branches (taken)
  li x11, 5
  li x12, 0
loop:
  addi x12, x12, 1
  bne x12, x11, loop

  # Read branch counter again
  csrr x13, 0xBC0
  sub x14, x13, x10
  li x15, 5
  bne x14, x15, fail

  # Run 3 branches (not taken)
  li x1, 1
  beq x0, x1, not_taken1
  beq x0, x1, not_taken2
  beq x0, x1, not_taken3
  j after_nottaken
not_taken1: j fail
not_taken2: j fail
not_taken3: j fail
after_nottaken:

  # Read final branch counter value
  csrr x16, 0xBC0
  sub x17, x16, x13
  li x18, 4
  bne x17, x18, fail

  RVTEST_PASS

fail:
  RVTEST_FAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
