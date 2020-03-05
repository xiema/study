//push constant 0    
@0    
D=A
@SP
M=M+1
A=M-1
M=D
//pop local 0        
@0        
D=A
@LCL
D=M+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
(LOOP_START)
//push argument 0    
@0    
D=A
@ARG
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
//push local 0
@0
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
//add None None
@SP
AM=M-1
D=M
A=A-1
M=D+M
//pop local 0	   
@0	   
D=A
@LCL
D=M+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push argument 0
@0
D=A
@ARG
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
//push constant 1
@1
D=A
@SP
M=M+1
A=M-1
M=D
//sub None None
@SP
AM=M-1
D=M
A=A-1
M=M-D
//pop argument 0     
@0     
D=A
@ARG
D=M+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push argument 0
@0
D=A
@ARG
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
@SP
AM=M-1
D=M
@LOOP_START
D;JNE
//push local 0
@0
D=A
@LCL
A=M+D
D=M
@SP
M=M+1
A=M-1
M=D
