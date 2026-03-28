# -------- INITIAL STATE --------
# $sp = 15

# -------- MAIN --------
addi $t0, $zero, 4        # t0 = 4
addi $t1, $zero, 3        # t1 = 3

# ---- push caller context ----
subi $sp, $sp, 1          # sp = 14
sw   $t0, 0($sp)

subi $sp, $sp, 1          # sp = 13
sw   $t1, 0($sp)

# ---- "call" function ----
j FUNC

# ---- return point ----
RETURN:

# ---- restore caller context ----
lw   $t1, 0($sp)          # restore t1 = 3
addi $sp, $sp, 1          # sp = 14

lw   $t0, 0($sp)          # restore t0 = 4
addi $sp, $sp, 1          # sp = 15

# continue execution
addi $t3, $t2, 1          # t3 = function_result + 1

j END


# -------- FUNCTION --------
FUNC:
# Function: compute t2 = (t0 + t1) * 2
# Using shifts instead of multiply

add  $t2, $t0, $t1        # t2 = 4 + 3 = 7
sll  $t2, $t2, 1          # t2 = 14

# modify t0, t1 internally (should NOT affect caller after restore)
addi $t0, $zero, 9
addi $t1, $zero, 8

# return
j RETURN


# -------- END --------
END:


# result:
# $t0 = 4          # restored
# $t1 = 3          # restored
# $t2 = 14         # function result
# $t3 = 15         # t2 + 1 = 15
# $sp = 15         # fully restored
# Memory[14] = 4
# Memory[13] = 3