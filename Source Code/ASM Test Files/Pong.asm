D;JNE
@SP
A=M-1
M=-1
(END_EQ)
@R15        
A=M
0;JMP
@R15
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@END_GT
D;JLE
@SP
A=M-1
M=-1
(END_GT)
@R15        
A=M
0;JMP
@R15
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=0
@END_LT
D;JGE
@SP
A=M-1
M=-1
(END_LT)
@R15        
A=M
0;JMP
@5
M=D
@SP
AM=M+1
M=D
@4
D=A
@R13
D=D+M
(RET_ADDRESS_CALL1)
@SP                     
AM=M-1
D=M
@THIS
AM=M-1
D=M
@THIS
A=M+1
D=A
@R14
M=D
@RET_ADDRESS_CALL2
D=A
@95
0;JMP
(RET_ADDRESS_CALL2)
@SP                 
AM=M-1
D=M
@R5
