from tkinter import *
import os
identityCounter =0 
t = 0
def updateValue(i):
    i = i[::-1]
    finalValue = 0
    counter = 0
    for item in i:
        finalValue+=int(item)*(2**counter)
        counter+=1
    return finalValue

def convert(axis,mode,opcode,address,indexer):
    switcher = {
        "X":"0",
        "Y":"1",
        "D":"0",
        "I":"1",
        "ADD":"0001",
        "SUB":"0010",
        "AND":"0011",
        "LDA":"0101",
        "STO":"0110",
        "CMP":"0111",
        "JMP":"1001",
        "BSA":"1010",
        "ISZ":"1011",
        "SHL":"1101",
        "SHR":"1110",
        "COM":"1111",
        "PSH":"000",
        "POP":"100",
        "INP":'101',
        "OUT":'001',
        "ION":'110',
        "IOF":'010',
        "CLA":'111',
        "HLT":"011",
        "HLT ":"011",
        

    }
    global identityCounter

    adjust = 10
    
    if (axis != 'X' and axis != 'Y'):
        adjust = 12
        address = 0
    if (axis == 'X' or axis == 'Y'):
        adjust = 10       

    if (mode in io or mode in stkop):
        adjust = 12
        address = 0
    
    if address == "#":
        address = 0

    if address not in indexer.keys():
        indexer.update({address:int(address)})
        identityCounter+=1

    a = indexer[address]
    x = '{0:b}'.format(int(a))
    for i in range(0,adjust-len(x)):
        x = "0"+x
    if (mode in io or mode in stkop):
        return(switcher[axis]+switcher[mode]+x)
    if (axis == 'X' or axis == 'Y'):
        return(switcher[axis]+switcher[mode]+switcher[opcode]+x) 
    if (axis != 'X' or axis != 'Y'):
        return("0"+switcher[axis+mode+opcode]+x)

stkop = ["PSH","POP","CLA"]
pref = ["HLT"]
io = ["INP","OUT"]
io2 = ["ION","IOF"]

def change_content(r,content):
    r['text'] = content


class Memory():

    def __init__(self):
        self.memorysize = 1024
        self.MEMORY = []
        self.stacksize = 64
        self.REALMEMORY = []
        self.indexer = {}
        self.output= None
        self.stackout = None
        self.SetMemory()
    
    def Print(self):
        if(self.output != None and self.stackout!=None):
            self.output.delete('1.0', END)
            self.stackout.delete('1.0', END)
            for i in range(0,self.memorysize-self.stacksize):
                self.output.insert(END,self.MEMORY[i]+"\n")
            for j in range(self.memorysize-self.stacksize,self.memorysize):
                self.stackout.insert(END,self.MEMORY[j]+"\n")

    def SetMemory(self):
        self.MEMORY = []
        self.stacksize = 64
        self.REALMEMORY = []
        self.indexer = {}
        self.output= None
        self.stackout = None
        for i in range(0,self.memorysize):
            WORD = "0000000000000000"
            self.MEMORY.append(WORD)
            self.REALMEMORY.append("")


    def LOAD(self,r):
        #Preprocessing Raw string
        raw = r.get(1.0,END)
        temp = raw.split('\n')
        startIndex = len(self.indexer)
        insI = 0
        for i in range(startIndex,startIndex+len(temp)-1):
            if(temp[insI] not in pref):
                x = temp[insI].split(' ')
            if(temp[insI][2:] in stkop or temp[insI][2:] in io):
                x = temp[insI].split(' ')
                x = x + ["#","#"]
            if (temp[insI] in pref or temp[insI] in io2):
                x = temp[insI]+" "
            code = convert(x[0],x[1],x[2],x[3],self.indexer)
            real = x[0]+x[1]+x[2]+x[3]
            self.REALMEMORY[i] = real
            self.MEMORY[i] = code
            insI = insI+1
        self.Print()
    def ALLOCATE(self,r):
        raw = r.get(1.0,END)
        temp = raw.split('\n')
        for i in range(0,len(temp)-1):
            x = temp[i].split(':')
            self.indexer.update({str(x[0]):i})
            self.REALMEMORY[i] = int(x[1])
            j = '{0:b}'.format(int(x[1]))
            for k in range(0,16-len(j)):
                j = "0"+j
            self.MEMORY[i] = j
        self.Print()

class Register():
    def __init__(self,size,t):
        self.t = t
        self.output=None
        self.bits = size
        self.value=None
        self.outputVal="0000000000000000"
        if(t == "NUM"):
            self.value = int(0)
        if(t == "FULL"):
            self.value = "0000000000000000"
    
    def update(self):
        self.output['text'] = self.outputVal

acx = Register(16,"NUM")
acy = Register(16,"NUM")
pc = Register(10,"NUM")
ar = Register(10,"NUM")
ir = Register(10,"FULL")
dr = Register(16,"NUM")
tr = Register(16,"NUM")
sp = Register(10,"NUM")
inpr = Register(10,"NUM")
outr = Register(10,"NUM")
memory = Memory()

class Architecture():
    def __init__(self,acx,acy,pc,ar,ir,dr,tr,sp,inpr,outr,memory):
        self.x = acx
        self.y = acy
        self.pc = pc
        self.ir = ir
        self.ar = ar
        self.dr = dr
        self.tr = tr
        self.sp = sp
        self.inpr = inpr
        self.outr = outr
        self.memory = memory
        self.pc.value = 0
        self.sp.value = self.memory.memorysize-self.memory.stacksize -1
    
    def setStackSize(self,source):
        size = int(source.get())
        self.memory.stacksize = size
        self.sp.value = self.memory.memorysize-self.memory.stacksize -1
        self.memory.Print()


    def prepare(self):
        self.pc.value = len(self.memory.indexer)-identityCounter
        x = '{0:b}'.format(int(self.pc.value))
        j = '{0:b}'.format(int(self.sp.value))
        for i in range(0,10-len(x)):
            x = "0"+x
        for i in range(0,10-len(j)):
            j = "0"+j
        self.sp.outputVal = j
        self.pc.outputVal = x
        self.pc.update()
        self.sp.update()
    def ModifyOutput(self,val,outputsource):
        if outputsource.t == "FULL":
            if isinstance(val,str):
                if(val.find("#") == -1):
                    a = val[0]
                    b = val[1]
                    c = val[2:5]
                    d = val[5:]
                    t = 0
                if(val.find("#") != -1):
                    a = val[0]
                    b = val[1:val.find("#")]
                    c = "#"
                    d = "#"
                    t = 1
                outputsource.outputVal = convert(a,b,c,d,self.memory.indexer)
            if isinstance(val,int):
                val = '{0:b}'.format(int(val))
                for i in range(0,16-len(val)):
                    val = "0"+val
                outputsource.outputVal = val
        if outputsource.t == "NUM":
            x = '{0:b}'.format(int(val))
            for i in range(0,outputsource.bits-len(x)):
                x = "0"+x
            outputsource.outputVal = x 
        outputsource.update()

    def ModifyMemory(self,r):
        x = '{0:b}'.format(int(r.value))
        for i in range(0,16-len(x)):
            x = "0"+x
        self.memory.MEMORY[self.ar.value] = x
        self.memory.Print()

    
    #Operations
    def DECODE(self,val): 
        print(val)
        print(t)
        if("#" not in val and "HLT" not in val):
            value = self.memory.indexer[val[5:]]
            self.ar.value = int(value)
        if(val[1] == "I"):
            self.Mar_TO_AR()        
            print(self.ar.value)
        print(val)
        if(val.find('LDA') != -1):
            return "LOAD_INSTRUCTION"
        if(val.find('ADD') != -1):
            return "ADD_INSTRUCTION"
        if(val.find('SUB') != -1):
            return "SUB_INSTRUCTION"
        if(val.find('AND') != -1):
            return "AND_INSTRUCTION"
        if(val.find('CMP') != -1):
            return "CMP_INSTRUCTION"
        if(val.find('STO') != -1):
            return "STORE_INSTRUCTION"
        if(val.find('JMP') != -1):
            return "JUMP_INSTRUCTION"
        if(val.find('BSA') != -1):
            return "BSA_INSTRUCTION"
        if(val.find('ISZ') != -1):
            return "ISZ_INSTRUCTION"
        if(val.find('COM') != -1):
            return "COM_INSTRUCTION"       
        if(val.find("SHL") != -1):
            return "SHL_INSTRUCTION"
        if(val.find("SHR") != -1):
            return "SHR_INSTRUCTION"
        if(val.find("PSH") != -1):
            return "PSH_INSTRUCTION"
        if(val.find("POP") != -1):
            return "POP_INSTRUCTION"
        if(val.find("INP") != -1):
            return "INP_INSTRUCTION"
        if(val.find("OUT") != -1):
            return "OUT_INSTRUCTION"
        if(val.find("ION") != -1):
            return "ION_INSTRUCTION"
        if(val.find("IOF") != -1):
            return "IOF_INSTRUCTION"
        if(val.find("CLA") != -1):
            return "CLA_INSTRUCTION"
        if(val.find('HLT') != -1):
            return "HALT"
        
    def RUN_PROGRAM(self):
        s = 1
        while(s == 1):
            s = self.FetchDecodeExecute()
        
    
    def FetchDecodeExecute(self):
        self.PC_TO_AR()
        self.INCREMENT_PC()
        self.Mar_TO_IR()
        print(self.ir.value)
        routine = self.DECODE(self.ir.value)
        if(routine == "LOAD_INSTRUCTION"):
            self.LOAD(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "ADD_INSTRUCTION"):
            self.ADD(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "SUB_INSTRUCTION"):
            self.SUB(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "CMP_INSTRUCTION"):
            self.CMP(self.ir.value[0],self.ir.value[1],self.ir.value[5:]) 
        if(routine == "AND_INSTRUCTION"):
            self.AND(self.ir.value[0],self.ir.value[1],self.ir.value[5:])        
        if(routine == "STORE_INSTRUCTION"):
            self.STO(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "JUMP_INSTRUCTION"):
            self.JMP(self.ir.value[0],self.ir.value[1],self.ir.value[5:])            
        if(routine == "BSA_INSTRUCTION"):
            self.BSA(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "ISZ_INSTRUCTION"):
            self.ISZ(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "COM_INSTRUCTION"):
            self.COM(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "SHL_INSTRUCTION"):
            self.SHL(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "SHR_INSTRUCTION"):
            self.SHR(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "CLA_INSTRUCTION"):
            self.CLA(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "PSH_INSTRUCTION"):
            self.PUSH(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "POP_INSTRUCTION"):
            self.POP(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "INP_INSTRUCTION"):
            self.POP(self.ir.value[0],self.ir.value[1],self.ir.value[5:])
        if(routine == "HALT"):
            return 0
        return 1


    
    def LOAD(self,axis,mode,address):
        self.Mar_TO_DR()
        if(axis == 'X'):
            self.DR_TO_XR()
        if(axis == 'Y'):
            self.DR_TO_YR()
    
    def ADD(self,axis,mode,address):
        self.Mar_TO_DR()
        if(axis == "X"):
            self.x.value = int(self.x.value) + int(self.dr.value)
            self.ModifyOutput(self.x.value,self.x)
        if(axis == "Y"):
            self.y.value = int(self.y.value) + int(self.dr.value)
            self.ModifyOutput(self.y.value,self.y)
        

    def AND(self,axis,mode,address):
        self.Mar_TO_DR()
        if(axis == "X"):
            self.x.value = self.x.value & self.dr.value
            self.ModifyOutput(self.x.value,self.x)
        if(axis == "Y"):
            self.y.value = self.y.value & self.dr.value
            self.ModifyOutput(self.y.value,self.y)
        

    def SUB(self,axis,mode,address):
        self.Mar_TO_DR()
        if(axis == "X"):
            self.x.value = int(self.x.value) - int(self.dr.value)
            self.ModifyOutput(self.x.value,self.x)
        if(axis == "Y"):
            self.y.value = int(self.y.value) - int(self.dr.value)
            self.ModifyOutput(self.y.value,self.y)


    def STO(self,axis,mode,address):
        if(axis == "X"):
            self.XR_TO_Mar()
        if(axis == "Y"):
            self.YR_TO_Mar()
    
    def JMP(self,axis,mode,address):
        if(axis == "X"):
            self.AR_TO_PC()

    def CMP(self,axis,mode,address):
        self.Mar_TO_DR()
        if(axis == "X"):
            if(self.x.value == self.dr.value):
                self.SET_XR()
            else:
                self.RESET_XR()
        if(axis == "Y"):
            if(self.y.value == self.dr.value):
                self.SET_YR()
            else:
                self.RESET_YR()

    def BSA(self,axis,mode,address):
        self.PC_TO_Mar()
        self.INCREMENT_AR()
        self.AR_TO_PC()
    
    def ISZ(self,axis,mode,address):
        self.Mar_TO_DR()
        self.INCREMENT_DR()
        self.DR_TO_Mar()
        if(int(self.dr.value) == 0):
            self.INCREMENT_PC()

    def COM(self,axis,mode,address):
        if(axis == "X"):
            self.COM_X()
            self.XR_TO_Mar()
        if(axis =="Y"):
            self.COM_Y()
            self.YR_TO_Mar()
    
    def SHL(self,axis,mode,address):
        if(axis == "X"):
            self.LEFTSHIFT_XR(mode)
        if(axis == "Y"):
            self.LEFTSHIFT_YR(mode)
    
    def SHR(self,axis,mode,address):
        if(axis == "X"):
            self.RIGHTSHIFT_XR(mode)
        if(axis == "Y"):
            self.RIGHTSHIFT_YR(mode)

    def PUSH(self,axis,mode,address):
        self.INCREMENT_SP()
        self.SP_TO_AR()
        if(axis == "X"):
            self.XR_TO_Mar()
        if(axis == "Y"):
            self.YR_TO_Mar()
        
    def POP(self,axis,mode,address):
        self.SP_TO_AR()
        self.Mar_TO_DR()
        if(axis == "X"):
            self.DR_TO_XR()
        if(axis == "Y"):
            self.DR_TO_YR()
        self.DECREMENT_SP()
    
    def INP(self,axis,mode,address):
        if(axis == "X"):
            self.INPR_TO_XR()
        if(axis == "Y"):
            self.INPR_TO_YR()
    
    def OUT(self,axis,mode,address):
        if(axis == "X"):
            self.XR_TO_OUTR()
        if(axis == "Y"):
            self.YR_TO_OUTR()
    
    def CLA(self,axis,mode,address):
        if(axis == "X"):
            self.XR_CLEAR()
        if(axis == "Y"):
            self.YR_CLEAR()

    #Microoperations

    def SP_TO_AR(self):
        self.ar.value = self.sp.value
        self.ModifyOutput(self.ar.value,self.ar)

    def INCREMENT_SP(self):
        self.sp.value = self.sp.value + 1
        self.ModifyOutput(self.sp.value,self.sp)

    def DECREMENT_SP(self):
        self.sp.value = self.sp.value - 1  
        self.ModifyOutput(self.sp.value,self.sp)

    def INCREMENT_PC(self):
        self.pc.value = self.pc.value + 1
        self.ModifyOutput(self.pc.value,self.pc)

    def INCREMENT_AR(self):
        self.ar.value = self.ar.value + 1
        self.ModifyOutput(self.ar.value,self.ar)
    
    def INCREMENT_DR(self):
        self.dr.value = self.dr.value + 1
        self.ModifyOutput(self.dr.value,self.dr)
    
    def INCREMENT_XR(self):
        self.x.value = self.x.value + 1
        self.ModifyOutput(self.x.value,self.x)
    
    def INCREMENT_YR(self):
        self.y.value = self.y.value + 1
        self.ModifyOutput(self.y.value,self.y)

    def SET_XR(self):
        self.x.value = 1
        self.ModifyOutput(self.x.value,self.x)
    
    def RESET_XR(self):
        self.x.value = 0
        self.ModifyOutput(self.x.value,self.x)
    
    def SET_YR(self):
        self.y.value = 1
        self.ModifyOutput(self.y.value,self.y)
    
    def RESET_YR(self):
        self.y.value = 0
        self.ModifyOutput(self.y.value,self.y)

    def COM_X(self):
        self.x.value = -self.x.value
        self.ModifyOutput(self.x.value,self.x)
    
    def COM_Y(self):
        self.y.value = -self.y.value
        self.ModifyOutput(self.y.value,self.y)

    def PC_TO_AR(self):
        self.ar.value = self.pc.value
        self.ModifyOutput(self.ar.value,self.ar)

    def PC_TO_Mar(self):
        self.memory.REALMEMORY[self.ar.value] = self.pc.value
        self.ModifyMemory(self.pc)
        
    def Mar_TO_AR(self):
        self.ar.value = self.memory.REALMEMORY[self.ar.value]
        self.ModifyOutput(self.ar.value,self.ar)

    def Mar_TO_IR(self):
        self.ir.value = self.memory.REALMEMORY[self.ar.value]
        self.ModifyOutput(self.ir.value,self.ir)

    def Mar_TO_DR(self):
        self.dr.value = self.memory.REALMEMORY[self.ar.value]
        self.ModifyOutput(self.dr.value,self.dr)

    def Mar_TO_TR(self):
        self.tr.value = self.memory.REALMEMORY[self.ar.value]
        self.ModifyOutput(self.tr.value,self.tr)
    
    def DR_TO_XR(self):
        self.x.value = self.dr.value
        self.ModifyOutput(self.x.value,self.x)

    def DR_TO_YR(self):
        self.y.value = self.dr.value
        self.ModifyOutput(self.y.value,self.y)
    
    def XR_TO_Mar(self):
        self.memory.REALMEMORY[self.ar.value] = self.x.value
        self.ModifyMemory(self.x)
    def YR_TO_Mar(self):
        self.memory.REALMEMORY[self.ar.value] = self.y.value
        self.ModifyMemory(self.y)
    
    def XR_TO_TR(self):
        self.tr.value = self.x.value
        self.ModifyOutput(self.tr.value,self.tr)

    def YR_TO_TR(self):
        self.tr.value = self.y.value
        self.ModifyOutput(self.tr.value,self.tr)

    def AR_TO_PC(self):
        self.pc.value = self.ar.value
        self.ModifyOutput(self.pc.value,self.pc)
    def DR_TO_Mar(self):
        self.memory.REALMEMORY[self.ar.value] = self.dr.value
        self.ModifyMemory(self.dr)
    def INPR_TO_XR(self):
        self.x.value = self.inpr.value
        self.ModifyOutput(self.x.value,self.x)
    def INPR_TO_YR(self):
        self.y.value = self.inpr.value
        self.ModifyOutput(self.y.value,self.y)
    def XR_TO_OUTR(self):
        self.outr.value = self.x.value
        self.ModifyOutput(self.outr.value,self.outr)
    def YR_TO_OUTR(self):
        self.outr.value = self.y.value
        self.ModifyOutput(self.outr.value,self.outr)
    def XR_CLEAR(self):
        self.x.value = 0
        self.ModifyOutput(self.x.value,self.x)
    def YR_CLEAR(self):
        self.y.value = 0
        self.ModifyOutput(self.y.value,self.y)
    


    def LEFTSHIFT_XR(self,bit):
        if(bit == "D"):
            bit = "0"
        if(bit == "I"):
            bit = "1"
        self.x.outputVal = self.x.outputVal+bit
        self.x.outputVal = self.x.outputVal[1:]
        self.x.value = updateValue(self.x.outputVal)
        self.ModifyOutput(self.x.value,self.x)
    
    def RIGHTSHIFT_XR(self,bit):
        if(bit == "D"):
            bit = "0"
        if(bit == "I"):
            bit = "1"
        self.x.outputVal = bit+self.x.outputVal
        self.x.outputVal = self.x.outputVal[:-1]
        self.x.value = updateValue(self.x.outputVal)
        self.ModifyOutput(self.x.value,self.x)
    
    def LEFTSHIFT_YR(self,bit):
        if(bit == "D"):
            bit = "0"
        if(bit == "I"):
            bit = "1"
        self.y.outputVal = self.y.outputVal+bit
        self.y.outputVal = self.y.outputVal[1:]
        self.y.value = updateValue(self.y.outputVal)
        self.ModifyOutput(self.y.value,self.y)
    
    def RIGHTSHIFT_YR(self,bit):
        if(bit == "D"):
            bit = "0"
        if(bit == "I"):
            bit = "1"
        self.y.outputVal = self.y.outputVal+bit
        self.y.outputVal = self.y.outputVal[:-1]
        self.y.value = updateValue(self.y.outputVal)
        self.ModifyOutput(self.y.value,self.y)


architecture = Architecture(acx,acy,pc,ar,ir,dr,tr,sp,inpr,outr,memory)