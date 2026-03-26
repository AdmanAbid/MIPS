addi $t0, $zero, 4
addi $t1, $zero, 2

add  $t2, $t0, $t1     # 6
sw   $t2, 0($zero)     # MEM[0] = 6

lw   $t3, 0($zero)     # t3 = 6

beq  $t2, $t3, OK
addi $t4, $zero, 1     # should not execute

OK:
addi $t4, $zero, 15