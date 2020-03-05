// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here
// KEYBOARD = 24575
// SCREEN = 16384

(RESET)
	// reset current
	@16384
	D=A
	@CUR
	M=D
	
(CHECK)
	//check keyboard
	@24576
	D=M
	@FILL
	D;JNE

(CLEAR)
	// clear current
	@CUR
	A=M
	M=0
	
	// increment
	D=A+1
	@CUR
	M=D
	
	// check reset
	@24576
	D=D-A
	@RESET
	D;JEQ
	@CHECK
	0;JMP

(FILL)
	//fill current
	@CUR
	A=M
	M=0
	M=!M
	
	// increment
	D=A+1
	@CUR
	M=D
	
	// check reset
	@24576
	D=D-A
	@RESET
	D;JEQ
	@CHECK
	0;JMP