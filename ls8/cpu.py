"""CPU functionality."""

import sys

# OP CODES:  
LDI = 0b10000010 # 130 
PRN = 0b01000111 # 71
HLT = 0b00000001 # 1
ADD = 0b10100000 # 160 
MUL = 0b10100010 # 162
PUSH = 0b01000101 # 69
POP = 0b01000110 # 70
CALL = 0b01010000 # 80
RET = 0b00010001 # 17 
CMP = 0b10100111 # 167  
JMP = 0b01010100 # 84
JEQ = 0b01010101 # 85
JNE = 0b01010110 # 86
XOR = 0b10101011 # 
AND = 0b10101000 # 168
OR =  0b10101010 # 170

class CPU:
    """Main CPU class."""

    def __init__(self):
        
        self.FL = 0b00000000    # equal flag 
        self.SP = 7             # stack pointer
        self.pc = 0             # program counter
        self.reg = [0] * 8      # 8 registers
        self.ram = [0] * 256    # 256 ram storage
        self.running = True
        # opcode instructions:
        self.instructions = {
            LDI: self.LDI,
            PRN: self.PRN,
            ADD: self.ADD,
            MUL: self.MUL,
            PUSH: self.PUSH,
            POP: self.POP,
            HLT: self.HLT,
            CALL: self.CALL,
            RET: self.RET,
            CMP: self.CMP,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE,
            XOR: self.XOR,
            AND: self.AND,
            OR: self.OR 
        }
    
    def LDI(self, operand_a: int, operand_b: int) -> None:
        """Set the value of a register to an integer.
        
        LDI register immediate
        """
        self.reg[operand_a] = operand_b

    def PRN(self, operand_a: int, operand_b: int) -> None:
        """Print numeric value stored in the given register.
        
        PRN register
        """
        print(f'printing... {self.reg[operand_a]}')
    

    def ADD(self, operand_a: int, operand_b: int) -> int:
        """Add the value in two registers and store the result in registerA
        
        ADD registerA registerB
        """
        self.alu('ADD', operand_a, operand_b)

    def MUL(self, operand_a: int, operand_b: int) -> int:
        """Multiply the values in two registers together and store the result in registerA.
        
        MUL registerA registerB
        """
        self.alu('MUL', operand_a, operand_b)

    def XOR(self, operand_a:int, operand_b: int) -> int:
        """
        Perform a bitwise-XOR between the values in registerA and registerB, 
        storing the result in registerA.
        
        XOR registerA registerB
        """
        self.alu('XOR', operand_a, operand_b)
        
    
    def AND(self, operand_a:int, operand_b: int) -> int:
        """Bitwise-AND the values in registerA and registerB, then store the result in registerA
        
        AND registerA registerB
        """
        self.alu('AND', operand_a, operand_b)
        
    
    def OR(self, operand_a:int, operand_b: int) -> int:
        """Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
        
        OR registerA registerB
        """    
        self.alu('OR', operand_a, operand_b)

    def PUSH(self, operand_a: int, operand_b: int) -> None:
        """Push the value in the given register on the stack.
            - Decrement the SP.
            - Copy the value in the given register to the address pointed to by SP.
            
        PUSH register
        """        
        # decrement self.SP (stack pointer)
        self.reg[self.SP] -= 1
        # copy value from register into ram address pointed by self.SP
        address = self.reg[self.SP]
        self.ram_write(self.reg[operand_a], address)

    def POP(self, operand_a: int, operand_b: int) -> int:
        """Pop the value at the top of the stack into the given register.
            - Copy the value from the address pointed to by SP to the given register.
            - Increment SP
            
        POP register 
        """
        address = self.reg[self.SP]
        # copy value from the self.SP address into the given register
        self.reg[operand_a] = self.ram_read(address)
        # increment self.SP (stack pointer)
        self.reg[self.SP] += 1

    def CALL(self, operand_a: int, operand_b: int) -> None: 
        """Calls a subroutine (function) at the address stored in the register.
        
        CALL register
        """       
        # decrement SP
        self.reg[self.SP] -= 1
        # push that instruction onto the stack
        self.ram_write(self.pc + 2, self.reg[self.SP])
        # PC is set to the address stored in the given register
        # We jump to that location in RAM
        self.pc = self.reg[operand_a]

    def RET(self, operand_a: int, operand_b: int) -> None:
        """Return from subroutine.
            - Pop the value from the top of the stack and store it in the PC
            
        RET
        """
        # Pop the value from the top of the stack and store it in the PC.
        address = self.reg[self.SP]
        self.pc = self.ram_read(address)
        # increment self.SP (stack pointer)
        self.reg[self.SP] += 1

    def HLT(self, operand_a: int, operand_b: int) -> None:
        """Halt the CPU (and exit the emulator)
        
        HLT
        """   
        self.running = False

    def CMP(self, operand_a: int, operand_b: int) -> None:
        """Compare the values in two registers.
        
        CMP registerA registerB
        """
        self.alu('CMP', operand_a, operand_b)
    
    def JMP(self, operand_a: int, operand_b: int) -> None:
        """Jump to the address stored in the given register.
            - Set the PC to the address stored in the given register.
            
        JMP register    
        """ 
        # Set the `PC` to the address stored in the given register.
        self.pc = self.reg[operand_a]

        
        # Else, we have to increment PC by 2 to go to next instruction (THIS SHOULD BE IN THE SPEC)
        # since otherwise all it does is equivalent to pass     
    def JEQ(self, operand_a: int, operand_b: int) -> None:
        """If equal flag is set (true), jump to the address stored in the given register."""
        
        if self.FL & 0b1 == 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2 
            
    def JNE(self, operand_a: int, operand_b: int) -> None:
        """If E flag is clear (false, 0), jump to the address stored in the given register."""
        if self.FL & 0b1 == 0:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
    
    
    """
    ROM:
    """   
    def load(self, filename) -> None:
        """Load a program into memory."""
        address = 0
        with open(filename, 'r') as f:
            program = f.readlines()
            for line in program:
                line = line.split('#')
                line = line[0].strip()
                if line == '':
                    continue
                # convert to binary and save to ram
                # silly contrived thing in our python simulator
                self.ram[address] = int(line, 2)
                address += 1
    """
    ALU:
    """
    # math operations on A and B, storing and returning from A
    # registers limited to 8 bits, 0-255, so bitwise AND with 255 to do modulus 
    def alu(self, op, reg_a: int, reg_b: int) -> int:
        """ALU operations."""
        
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 0xFF
            
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 0xFF
            
        elif op == "CMP": # Compare the values in two registers. `FL` bits: `00000LGE`
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            else:
                self.FL = 0b00000010 
                
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 0xFF
            
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 0xFF
            
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 0xFF            
        else:
            raise Exception("Unsupported ALU operation")

        return self.reg[reg_a]

    def ram_read(self, address: int) -> int:
        """Return an address in RAM."""

        return self.ram[address]

    def ram_write(self, value: int, address: int) -> None:
        """Set an address in RAM to a certain value."""

        self.ram[address] = value

    def trace(self) -> None:
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X | %02X %02X %02X |" % (
            self.pc,
            self.FL,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
        
    """
    RUN:
    """    
    def run(self):
        """Run the CPU."""

        while self.running is True:
            IR = self.ram_read(self.pc)
            #self.trace()
          
            instruction_length = (IR >> 6) + 1 
            operand_a = self.ram_read(self.pc + 1) 
            operand_b = self.ram_read(self.pc + 2)
            # if the op code is in the instructions, execute from branch table
            if IR in self.instructions:
                self.instructions[IR](operand_a, operand_b)
            else:
                print("Invalid instruction")
            if not IR & 0b00010000: # increment program counter except in case of JNE, JEQ, RET 
                self.pc += instruction_length

            # self.pc += instruction_length
            # self.trace()