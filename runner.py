#!/usr/bin/env python
import array
import sys
import struct
from bitstring import BitString
from numpy import zeros,uint32
from time import time
import opcodes
import random

SIMULATE = True

DEFAULT_MAX_MESSAGES = 5
MAX_NUM_OF_BPM_BUFFERS     = 0x1000
BPM_SRAM_ADDRESS           = 0x1000
VALID_BUFFER_MASK          = 0x0001
BPM_BUFFERS_BASE           = 0x1D0000
DDR_BUFFER_PAYLOAD_OFFSET  = 0x08
STALL_NORMAL = 0
STALL_NO_CONTEXT = 1
STALL_DMA = 2
STALL_BBTX = 3
STALL_BBMSG = 4
STALL_LDIO = 5
STALL_RAMMAN = 6
STALL_CNTUP = 7

BBMSG_FIFO_DEPTH = 4 
BBTX_FIFO_DEPTH = 4 
HASH_FIFO_DEPTH = 4  
DMA_FIFO_DEPTH = 7 # 20 for verification
COUNTERS_FIFO_DEPTH = 4
SCHEDULER_CLOCKS = 16
USEC_TO_CLOCKS  = 300 
CLOCK_TYPE_NORMAL = 0
MEMORY_OFFSET = 3
NUMBER_OF_THREADS = 32 
NUMBER_OF_GLOBAL_REGISTERS  = 8 
NUMBER_OF_PRIVATE_REGISTERS = 24 
DATA_SEGMENT_SIZE  = 48 * 1024
CODE_SEGMENT_SIZE  = 32 * 1024
CODE_SEG_SIZE = CODE_SEGMENT_SIZE // 4
CONTEXT_SEGMENT_SIZE = NUMBER_OF_THREADS * NUMBER_OF_PRIVATE_REGISTERS * 4  
MAX_RELATIVE_JMP_DISTANCE = 0xFFF 
CODE_0_SEGMENT_SIZE = 16 * 1024
IO_SIZE          = 1024 
CALL_STACK_DEPTH = 4 
FW_CONTROL       =  0x00
PERIPHERAL_CTS   =  0x04
                 
LKUP0_RESULT     =  0x10
LKUP1_RESULT     =  0x14
LKUP2_RESULT     =  0x18
LKUP3_RESULT     =  0x1C
                 
LKUP0_FWCFG      =  0x20
LKUP1_FWCFG      =  0x24
LKUP_CAM_FWCFG_0 =  0x28
LKUP_CAM_FWCFG_1 =  0x2C
                 
DDR_LKUP0_RESULT =  0x30
DDR_LKUP1_RESULT =  0x34
DDR_LKUP2_RESULT =  0x38
DDR_LKUP3_RESULT =  0x3C
                 
RAMRD_RESULT_0   =  0x40
RAMRD_RESULT_1   =  0x44
RAMRD_RESULT_2   =  0x48
RAMRD_RESULT_3   =  0x4C
                 
SEMAPHOR_CTRL_0  =  0x50
SEMAPHOR_CTRL_1  =  0x54
PARSER_SUM       =  0x58
PARSER_CHKSUM    =  0x5C
                 
TIMER_CTRL_0     =  0x60
TIMER_CTRL_1     =  0x64
MS_CNT_VAL       =  0x68
T0_VAL           =  0x6C
T1_VAL           =  0x70
                 
CNTR_LOCK        =  0x74
RUNNER_GPIO      =  0x78
DDR_OFFSET       =  0x7C
                 
FW_INT_CTRL0     =  0x80
FW_INT_CTRL1     =  0x84
FW_INT_CTRL2     =  0x88
FW_WAKEUP_REG    =  0x8C
                 
BBMSG_0   =  0x90
BBMSG_1   =  0x94
BBMSG_2   =  0x98

CRC_RESULT_IO_ADDRESS   =   RAMRD_RESULT_0

SCHEDULER_IO_ADDRESS    =   FW_WAKEUP_REG  

TIMER_CONTROL_IO_ADDRESS  =    TIMER_CTRL_0
TIMER_EXTEND_IO_ADDRESS   =    TIMER_CTRL_1
TIMER_IO_ADDRESS          =    MS_CNT_VAL
TIMER_0_VAL_IO_ADDRESS    =    T0_VAL
TIMER_1_VAL_IO_ADDRESS    =    T1_VAL

INT3_0_ADDR    =   FW_INT_CTRL0
INT7_4_ADDR    =   FW_INT_CTRL1
INT11_8_ADDR   =   FW_INT_CTRL2


HASH_RESULT_IO_ADDRESS0	=  LKUP0_RESULT
HASH_RESULT_IO_ADDRESS1	=  LKUP1_RESULT
HASH_RESULT_IO_ADDRESS2	=  LKUP2_RESULT
HASH_RESULT_IO_ADDRESS3	=  LKUP3_RESULT


DMALU_RESULT_IO_ADDRESS0  = DDR_LKUP0_RESULT
DMALU_RESULT_IO_ADDRESS1  = DDR_LKUP1_RESULT
DMALU_RESULT_IO_ADDRESS2  = DDR_LKUP2_RESULT
DMALU_RESULT_IO_ADDRESS3  = DDR_LKUP3_RESULT


CAM_RESULT_IO_ADDRESS0	=  RAMRD_RESULT_0
CAM_RESULT_IO_ADDRESS1	=  RAMRD_RESULT_1
CAM_RESULT_IO_ADDRESS2	=  RAMRD_RESULT_2
CAM_RESULT_IO_ADDRESS3	=  RAMRD_RESULT_3

PARS_RESULT_IO_ADDRESS	= PARSER_SUM

IH_BUFFER_SIZE   =   256
IH_BUFFERS_NUMBER  = 64 
MODE_DISABLE = 0
MODE_RUNNING = 1
MODE_STEP = 2
MODE_DEBUG = 3
DMA_SRAM_TO_DDR_MIN = 15 
DMA_SRAM_TO_DDR_MAX = 100 
DMA_DDR_TO_SRAM_MIN = 40 
DMA_DDR_TO_SRAM_MAX = 100 
BBTX_MIN  = 15  
BBTX_MAX  = 60  
BBMSG_MIN = 2 
BBMSG_MAX = 40 
CNTUP_MIN = 5 
CNTUP_MAX = 15 
PARS_MIN = 5 
PARS_MAX = 15 
HASH_MIN  = 5 
HASH_MAX  = 15 
CRYPT_MIN = 5 
CRYPT_MAX = 15 

PC_MASK = 0x00007FFC
CHANGES = 0x5000

CRC_TYPE_32 = 0
CRC_TYPE_16 = 1
CRC_TYPE_10 = 2
CRC_TYPE_5 = 3

Z_FLAG_BIT   = 0  
N_FLAG_BIT   = 1  
CY_FLAG_BIT  = 2  
OVF_FLAG_BIT = 3  
JBIT_FLAG_BIT = 4 

Z_FLAG   = 1 << Z_FLAG_BIT 
N_FLAG   = 1 << N_FLAG_BIT 
CY_FLAG  = 1 << CY_FLAG_BIT 
OVF_FLAG = 1 << OVF_FLAG_BIT 
JBIT_FLAG = 1 << JBIT_FLAG_BIT 

CRC_TYPE_MAC  = CRC_TYPE_16 
CRC_TYPE_FLOW = CRC_TYPE_16 
CRC_TYPE_HEC  = CRC_TYPE_5 

CRC_HEC_LENGTH = 3 
CRC_HEC_MASK   = 0x0007FFFF 

def unsigned(val):
	return struct.unpack('L',uint32(val))[0]
logfile = []
def log(listfile,line):
	""" print current line to list file,
	 if it is an error or warning message print it to stdout also """ 
	if listfile != 0:
		#print line
		if line.startswith("ERROR") or line.startswith("WARNING"):
			print line

		if not line.endswith('\n'):
			line += '\n'
		#listfile.write(line)
		logfile.append(line)
		if len(logfile) >= 1: #:
			for i in range(len(logfile)):
				listfile.write(logfile[i])
			logfile[:] = []
	else:
		print line
class CRC:
	crcinit_direct = 0
	crcinit_nondirect = 0
	crc_high_bit = 0
	crc_mask = 0
	order = 0
	polynom = 0
	crc_init = 0
	direct = 0
	crc_xor = 0
	reflect_in = 0
	reflect_out = 0

	def CRC_32_init (self):
		self.crcinit_direct = 0
		self.crcinit_nondirect = 0
		self.crc_high_bit = 0
		self.crc_mask = 0
		self.order = 32
		self.polynom = 0x04C11DB7
		self.crc_init = 0xFFFFFFFF
		self.direct = 1
		self.crc_xor = 0xFFFFFFFF
		self.reflect_in = 0
		self.reflect_out = 0
	def CRC_16_init (self):
		self.crcinit_direct = 0
		self.crcinit_nondirect = 0
		self.crc_high_bit = 0
		self.crc_mask = 0
		self.order = 16
		self.polynom = 0x1021
		self.crc_init = 0xFFFF
		self.direct = 1
		self.crc_xor = 0
		self.reflect_in = 0
		self.reflect_out = 0
	def CRC_10_init (self):
		self.crcinit_direct = 0
		self.crcinit_nondirect = 0
		self.crc_high_bit = 0
		self.crc_mask = 0
		self.order = 10
		self.polynom = 0x0233
		self.crc_init = 0x03FF
		self.direct = 1
		self.crc_xor = 0
		self.reflect_in = 0
		self.reflect_out = 0
	def CRC_5_init (self):
		self.crcinit_direct = 0
		self.crcinit_nondirect = 0
		self.crc_high_bit = 0
		self.crc_mask = 0
		self.order = 5
		self.polynom = 0x05
		self.crc_init = 0x00
		self.direct = 1
		self.crc_xor = 0
		self.reflect_in = 0
		self.reflect_out = 0

class timer:

	status = 0
	mode = 0
	enable  = 1
	urgent  = 0
	thread  = 0
	origvalue  = 0
	value  = 0

class timer_config:

	reset  = 0
	pause  = 0
	t0_width  = 0
	t1_width  = 0
	value  = 0

class hash:
	valid = 0
	ready = 0
	clock = 0
	source_a = 0
	source_c = 0
	result  = 0
	key_size = 0
	cs  = 0
	res_slot = 0
	rq = 0
	invoke = 0
	update_r16 = 0
	async_enable  = 0
	mt  = 0
	table_number = 0
	thread = 0
	
class ramman:
	valid = 0
	ready = 0
	clock = 0
	source_a = 0
	source_c = 0
	type = 0
	result = 0
	length  = 0
	eth  = 0
	last  = 0
	key  = 0
	mask  = 0
	key_size  = 0
	res_slot = 0
	invoke  = 0
	thread  = 0

class bbtx:
	valid  = 0
	clock  = 0
	thread  = 0	
	source  = 0
	destination  = 0
	length  = 0
	last  = 0
	inc  = 0
class bbmsg:
	valid  = 0
	clock  = 0
	thread  = 0	
	type  = 0
	size  = 0
	destination  = 0
	message_hi = 0
	message_lo = 0
	
class dma:
	valid  = 0
	clock  = 0
	thread  = 0
	invoke  = 0
	mask  = 0
	sram_to_ddr  = 0
	source  = 0
	destination  = 0
	length  = 0
	res_slot  = 0
	dmalu  = 0
	common_or_private  = 0
	mem  = 0
	stall  = 0
	global_mask = 0
class cntup:
	valid  = 0
	clock  = 0
	group_offset  = 0
	counter_number  = 0
	value  = 0
	size  = 0
	operation  = 0
	mode  = 0
class crypt:
	valid  = 0
	clock  = 0
	chunk_address  = 0
	chunk_size  = 0
	hash  = 0
	first  = 0
	last  = 0
	invoke  = 0
	thread  = 0
  
class  hw_accelerators:
	bbtx_in  = 0
	bbtx_out  = 0
	bbtx_count  = 0	
	dma_in  = 0
	dma_out  = 0
	dma_count  = 0	
	bbmsg_in  = 0
	bbmsg_out  = 0
	bbmsg_count  = 0	
	cntup_in  = 0
	cntup_out  = 0
	cntup_count  = 0	
	hash_in  = 0
	hash_out  = 0
	hash_count  = 0
	hash = []*HASH_FIFO_DEPTH
	cntup = []*COUNTERS_FIFO_DEPTH
	dma = []*DMA_FIFO_DEPTH
	bbtx = []*BBTX_FIFO_DEPTH
	bbmsg = []*BBMSG_FIFO_DEPTH

	def __init__(self):
		self.crypt = crypt()		
		for t in range(HASH_FIFO_DEPTH):
			self.hash.append(hash())
		for t in range(COUNTERS_FIFO_DEPTH):
			self.cntup.append(cntup())
		for t in range(DMA_FIFO_DEPTH):
			self.dma.append(dma())
		for t in range(BBTX_FIFO_DEPTH):
			self.bbtx.append(bbtx())
		for t in range(BBMSG_FIFO_DEPTH):
			self.bbmsg.append(bbmsg())
		self.ramman = ramman()

class scheduler:

	sync_wakeup_request = []* NUMBER_OF_THREADS  
	async_wakeup_request_normal = []* NUMBER_OF_THREADS  
	async_wakeup_request_urgent = []* NUMBER_OF_THREADS  
	mask = []*NUMBER_OF_THREADS  
	async_enable = []* NUMBER_OF_THREADS 
	previous_context = 0 
	current_context = 0 
	next_context = 0 
	next_context_valid = 0 
	save_context = 0 

	def __init__ (self):
		for i in range(NUMBER_OF_THREADS):
			self.sync_wakeup_request.append(0)
			self.async_wakeup_request_normal.append(0)
			self.async_wakeup_request_urgent.append(0)
			self.mask.append(1)
			self.async_enable.append(0)

class pipe:
	opcode_ds1 = 0
	opcode_ds2 = 0
	pc_ds1 = 0
	pc_ds2 = 0
	clock = 0

class stall_pc:
	pc = 0
	delay_pc = 0
	enter_stall = 0

class runner:
	code_filename = ''
	data_filename = ''
	context_filename = ''
	co_runner = 0
	changes = []*CHANGES
	stall_dma_time = 0
	stall_bbtx_time = 0
	stall_bbmsg_time = 0
	stall_ldio_time = 0
	stall_no_context_time = 0
	max_dma_fifo = 0
	max_bbmsg_fifo = 0
	max_bbtx_fifo = 0
	pc = 0
	st = 0
	stall = STALL_NORMAL
	threads = []*NUMBER_OF_THREADS
	global_registers = []*NUMBER_OF_GLOBAL_REGISTERS
	private_registers = []*NUMBER_OF_PRIVATE_REGISTERS
	call_stack = []*CALL_STACK_DEPTH
	code_statistics = [[]*NUMBER_OF_THREADS]*CODE_SEG_SIZE
	code_segment = array.array('L')
	data_segment = array.array('L')
	context_segment = array.array('L')
	io = []*IO_SIZE
	timers = []*4
	counters_lock = 0 
	crc_constants = []
	fio = 0

	def __init__(self,id,codefile,datafile,contextfile,simulator):
		self.id = id
		self.pipe = pipe()
		self.stall_pc = stall_pc()
		self.stall_pc.enter_stall = STALL_NORMAL
		self.scheduler = scheduler()
		for i in range(NUMBER_OF_THREADS):
			self.threads[i] = i
		for i in range(CODE_SEG_SIZE):
			l = []
			tp = (0,0)
			for j in range(NUMBER_OF_THREADS):
				l.append(tp)
			self.code_statistics[i].append(l)
		self.io = zeros(IO_SIZE,'L')
		self.code_file_name = codefile
		self.data_file_name = datafile
		self.ctx_file_name = contextfile
		self.mode = MODE_DISABLE
		self.force_update = 0  
		crcClass = CRC()
		self.crc_constants.append(crcClass.CRC_32_init())
		self.crc_constants.append(crcClass.CRC_16_init())
		self.crc_constants.append(crcClass.CRC_10_init())
		self.crc_constants.append(crcClass.CRC_5_init())
		for c in crc_constants:
			c.crc_mask = (( 1 << (c.order -1) - 1) << 1 ) | 1
			c.crc_high_bit = (( 1 << (c.order -1) - 1) << 1 )
			if not c.direct:
				c.crcinit_nondirect = c.crc_init
				crc = c.crc_init
				for i in range(c.order):
					bit = crc & c.crc_high_bit
					crc <<= 1
					if bit:
						crc ^= c.polynom
				crc &= c.crc_mask
				c.crcinit_direct = crc
			else:
				c.crcinit_direct = c.crc_init
				crc = c.crc_init
				for i in range(c.order):
					bit = crc & 1
					if bit:
						crc ^= c.polynom
					crc >>= 1
					if bit:
						crc |= c.crc_high_bit
				c.crcinit_nondirect = crc
		self.previous_opcode = BitString('0x00000000')
		self.global_registers = zeros(NUMBER_OF_GLOBAL_REGISTERS,'L')
		self.private_registers = zeros(NUMBER_OF_PRIVATE_REGISTERS,'L')
		self.simulator = simulator
		self.hw_accelerators = hw_accelerators()
		self.timer = timer_config()
		for t in range(4):
			self.timers.append(timer())
		try:
			self.fio = open("sim.log","w+")
		except IOError:
			print "Cannot open file 'sim.log'"
		try:
			fobj = open(self.code_file_name,'rb')
			self.data_segment.fromfile(fobj,DATA_SEGMENT_SIZE//4)
			self.code_segment.fromfile(fobj,CODE_SEGMENT_SIZE//4)
			self.code_segment.byteswap()
			self.context_segment.fromfile(fobj,CONTEXT_SEGMENT_SIZE//4)
			fobj.close()
			fobj = open(self.data_file_name,'rb')
			self.data_segment.fromfile(fobj,DATA_SEGMENT_SIZE//4)
			self.data_segment.byteswap()
			fobj.close()
			fobj = open(self.ctx_file_name,'rb')
			self.context_segment.fromfile(fobj,CONTEXT_SEGMENT_SIZE//4)
			self.context_segment.byteswap()
			self.init_io()
			self.reset_others(id)
			self.show_scheduler ( "after reset")
		except IOError:
			print "Cannot open code/data/context file " + self.code_file_name
			return
	def reset_others (self,id):
		if id == 0:


	def init_io (self):
		self.WRITE_IO(FW_CONTROL,4,0x00000001)
		self.WRITE_IO(PERIPHERAL_CTS,4,0x00000000)
		self.WRITE_IO(LKUP0_RESULT,4,0x00000000)
		self.WRITE_IO(LKUP1_RESULT,4,0x00000000)
		self.WRITE_IO(LKUP2_RESULT,4,0x00000000)
		self.WRITE_IO(LKUP3_RESULT,4,0x00000000)
		self.WRITE_IO(LKUP0_FWCFG,4,0x00000000)
		self.WRITE_IO(LKUP1_FWCFG,4,0x00000000)
		self.WRITE_IO(LKUP_CAM_FWCFG_0,4,0x00000000)
		self.WRITE_IO(LKUP_CAM_FWCFG_1,4,0x00000000)
		self.WRITE_IO(DDR_LKUP0_RESULT,4,0x00000000)
		self.WRITE_IO(DDR_LKUP1_RESULT,4,0x00000000)
		self.WRITE_IO(DDR_LKUP2_RESULT,4,0x00000000)
		self.WRITE_IO(DDR_LKUP3_RESULT,4,0x00000000)
		self.WRITE_IO(RAMRD_RESULT_0,4,0x00000000)
		self.WRITE_IO(RAMRD_RESULT_1,4,0x00000000)
		self.WRITE_IO(RAMRD_RESULT_2,4,0x00000000)
		self.WRITE_IO(RAMRD_RESULT_3,4,0x00000000)
		self.WRITE_IO(SEMAPHOR_CTRL_0,4,0x00000000)
		self.WRITE_IO(SEMAPHOR_CTRL_1,4,0x00000000)
		self.WRITE_IO(PARSER_SUM,4,0x00003ff0)
		self.WRITE_IO(PARSER_CHKSUM,4,0x00000000)
		self.WRITE_IO(TIMER_CTRL_0,4,0x00000000)
		self.WRITE_IO(TIMER_CTRL_1,4,0x00000000)
		self.WRITE_IO(MS_CNT_VAL,4,0x00000000)
		self.WRITE_IO(T0_VAL,4,0x00000000)
		self.WRITE_IO(T1_VAL,4,0x00000000)
		self.WRITE_IO(CNTR_LOCK,4,0x00000000)
		self.WRITE_IO(RUNNER_GPIO,4,0x00000000)
		self.WRITE_IO(DDR_OFFSET,4,0x00000000)
		self.WRITE_IO(FW_INT_CTRL0,4,0x00000000)
		self.WRITE_IO(FW_INT_CTRL1,4,0x00000000)
		self.WRITE_IO(FW_INT_CTRL2,4,0x00000000)
		self.WRITE_IO(FW_WAKEUP_REG,4,0x00000000)
		self.WRITE_IO(BBMSG_0,4,0x00000000)
		self.WRITE_IO(BBMSG_1,4,0x00000000)
		self.WRITE_IO(BBMSG_2,4,0x00000000)

	def addCorunner(self,corunner):	
		""" add co-runner pointer """	
		self.co_runner = corunner
	def run (self):
		""" run simulator for runner """	
		if self.mode != MODE_RUNNING:
			self.mode = MODE_RUNNING
		while self.mode == MODE_RUNNING :  
			if self.continue_work () == 0 : 
				self.mode = MODE_DISABLE 
		if self.fio != 0:
			for i in range(len(logfile)):
				self.fio.write(logfile[i])
	def continue_work (self):
		""" continue simulation """
		if self.mode == MODE_RUNNING:
			if self.init_iocurrent_speed == 0:
				self.init_iocurrent_speed = 1
				if not self.simulator_clock():
					return 0
			else:
				self.simulator.current_speed -= 1
		elif self.mode == MODE_STEP:
			return 0
		# check changes
		return 1
	def simulator_clock (self):
		""" simulator clock - solve pipes 
			and increment clock """
		old_pc = self.pc
		olt_st = self.st
		self.simulator.clock += 1
		if self.pipe.clock == 2:
			self.pc = self.pipe.pc_ds1
			self.pipe.clock -= 1
			if self.execute_opcode(self.pipe.opcode_ds1,0)[0] == 0:
				print "invalid delay slot opcode %08X at address %08X" % ( self.pipe.opcode_ds1, self.pipe.pc_ds1 )
			self.pc = old_pc
		elif self.pipe.clock == 1:
			self.pc = self.pipe.pc_ds2
			self.pipe.clock -= 1
			if self.execute_opcode(self.pipe.opcode_ds2,0)[0] == 0:
				print "invalid delay slot opcode %08X at address %08X" % ( self.pipe.opcode_ds1, self.pipe.pc_ds2 )
			self.pc = old_pc
			self.previous_opcode[opcodes.nopOpcode['opcode'][0]:opcodes.nopOpcode['opcode'][1]] = opcodes.OPCODE_CODE_NOP
		else:
			old_pc = self.pc//4
			olt_st = self.st
			if self.stall_pc.enter_stall == STALL_NORMAL:
				if old_pc < CODE_SEGMENT_SIZE/4:
					try:							
						opcode = BitString(uint=self.code_segment[old_pc],length=32)
						buffer = self.execute_opcode(opcode,0)[1]
						if not buffer :
							log(self.fio,"clock=%d id=%d : 0x%08x => 0x%08x\tError ????" % (self.simulator.clock,self.id,old_pc*4,self.code_segment[old_pc]))
							return 0
						log(self.fio,"clock=%d id=%d : 0x%08x => 0x%08x\t%s" % (self.simulator.clock,self.id,old_pc*4,self.code_segment[old_pc],buffer))
						if len(self.changes) > 0:
							log(self.fio,"clock=%d id=%d : CHANGES: %s" % (self.simulator.clock,self.id,self.changes))
							self.changes[:] = [] # clear the list
						if not self.increment_clock():
							return 0
					except IndexError:
						print 'error %d %d' % (old_pc,CODE_SEGMENT_SIZE/4)		
						self.pc += 4
				else: return 0
		return 1

	def increment_clock(self):
		""" for every simulator clock """
		if self.simulator.clock % USEC_TO_CLOCKS == 0 and self.timer.pause == 0:
			self.timer.value += 1
			self.WRITE_IO(TIMER_IO_ADDRESS,self.timer.value,4)
		#self.check_timers()
		#self.check_semaphores()
		self.execute_ramman()
		#self.execute_dma()
		#self.execute_bbtx()
		#self.execute_bbmsg()
		#self.execute_cntup()
		if self.simulator.clock % SCHEDULER_CLOCKS == 0:
			next_context = self.scheduler.next_context
			found = 0
			g = 0
			t = 0
			thread = 0
			for g in range(8):
				if found != 0: break
				for t in range(8):
					if found != 0: break
					thread = (g//2)*8 + t
					if self.scheduler.async_wakeup_request_urgent[thread] == 1 and \
						self.scheduler.mask[thread] == 0 and \
						self.scheduler.async_enable[thread] == 1:
						self.scheduler.next_context = thread
						found = 1
					if self.scheduler.sync_wakeup_request[thread] == 1 and \
						self.scheduler.mask[thread] == 0 :
						self.scheduler.next_context = thread
						found = 2
				for t in range(8):
					if found != 0: break
					thread = (g//2)*8 + t
					if self.scheduler.async_wakeup_request_normal[thread] == 1 and \
						self.scheduler.mask[thread] == 0 and \
						self.scheduler.async_enable[thread] == 1:
						self.scheduler.next_context = thread
						found = 1
					if self.scheduler.sync_wakeup_request[thread] == 1 and \
						self.scheduler.mask[thread] == 0 :
						self.scheduler.next_context = thread
						found = 2
			if found != 0:
				self.scheduler.next_context_valid = 1
				self.changes.append(" NEXT: %08X " % (self.scheduler.next_context))
			else:
				self.changes.append(" NEXT: ?? ")
			if self.scheduler.next_context_valid == 1 and self.stall == STALL_NO_CONTEXT:
				self.stall_no_context_time += self.simulator.clock - self.stall_pc.enter_stall
				self.stall = STALL_NORMAL
				self.changes.append(" STALL: 0 ")
				for r in range(NUMBER_OF_PRIVATE_REGISTERS):
					ind = self.scheduler.current_context*NUMBER_OF_PRIVATE_REGISTERS + r
					if self.scheduler.save_context == 1:
						self.context_segment[ind] = self.private_registers[r] 
					self.private_registers[r] = self.context_segment[ind]
					self.changes.append(" REG: r%d=%08X " % (r+NUMBER_OF_GLOBAL_REGISTERS,self.private_registers[r]))
				self.st = 0
				self.scheduler.previous_context = self.scheduler.current_context ;
				self.scheduler.current_context = self.scheduler.next_context ;
				if self.scheduler.async_enable [ self.scheduler.next_context ] == 1: 
					self.scheduler.async_enable [self.scheduler.next_context ] = 0 
					self.scheduler.async_wakeup_request_normal [ self.scheduler.next_context ] = 0 
					self.scheduler.async_wakeup_request_urgent [ self.scheduler.next_context ] = 0 
					self.scheduler.sync_wakeup_request [ self.scheduler.next_context ] = 0
				else:
					self.scheduler.sync_wakeup_request [ self.scheduler.next_context ] = 0 
				self.scheduler.next_context_valid = 0
				self.pc = self.private_registers[16] >> 16
				self.pc &= PC_MASK
				if self.pc == 0:
					print "PANIC: Program counter wrapped around to address 0"
				self.changes.append(" THREAD: %08X " % (self.scheduler.current_context))
				self.show_scheduler("scheduler clock")
				if not (self.hw_accelerators.hash_count >0 or \
				self.hw_accelerators.ramman.valid == 1 or \
				self.hw_accelerators.dma_count > 0 or \
				self.hw_accelerators.bbtx_count > 0 or \
				self.hw_accelerators.bbmsg_count > 0 or \
				self.scheduler.next_context_valid == 1 ):
					if self.check_finish(1): return 0
				else:
					if self.check_finish(0): return 0
		return 1
	def execute_ramman (self):
		""" resolve CRC anf CAM_LKUP stall """
		if self.hw_accelerators.ramman.valid == 1:
			r=self.hw_accelerators.ramman.clock - self.simulator.clock
			if self.hw_accelerators.ramman.type == 1:
				self.changes.append(" CAM: %08X " % (r))
			else:
				self.changes.append(" CRCCALC: %08X " % (r))
			if r <= 0:
				if self.hw_accelerators.ramman.type == 1:
					self.hw_accelerators.ramman.result = self.camlkup(self.hw_accelerators.ramman.source_a, \
					self.hw_accelerators.ramman.key,self.hw_accelerators.ramman.key_size,self.hw_accelerators.ramman.mask)
					if self.hw_accelerators.ramman.result != -1:
						cam_result = self.hw_accelerators.ramman.result | (1 << 8)
						if self.hw_accelerators.ramman.res_slot == 0:
							self.WRITE_IO(CAM_RESULT_IO_ADDRESS0,4,cam_result)
							r = self.READ_IO(CAM_RESULT_IO_ADDRESS0,4)
							self.changes.append(" IO: word %08X=%08X " % (CAM_RESULT_IO_ADDRESS0,r))
						elif self.hw_accelerators.ramman.res_slot == 1:
							self.WRITE_IO(CAM_RESULT_IO_ADDRESS1,4,cam_result)
							r = self.READ_IO(CAM_RESULT_IO_ADDRESS1,4)
							self.changes.append(" IO: word %08X=%08X " % (CAM_RESULT_IO_ADDRESS1,r))
						elif self.hw_accelerators.ramman.res_slot == 2:
							self.WRITE_IO(CAM_RESULT_IO_ADDRESS2,4,cam_result)
							r = self.READ_IO(CAM_RESULT_IO_ADDRESS2,4)
							self.changes.append(" IO: word %08X=%08X " % (CAM_RESULT_IO_ADDRESS2,r))
						elif self.hw_accelerators.ramman.res_slot == 3:
							self.WRITE_IO(CAM_RESULT_IO_ADDRESS3,4,cam_result)
							r = self.READ_IO(CAM_RESULT_IO_ADDRESS3,4)
							self.changes.append(" IO: word %08X=%08X " % (CAM_RESULT_IO_ADDRESS3,r))
						if self.hw_accelerators.ramman.invoke == 1:
							self.scheduler.sync_wakeup_request [self.hw_accelerators.ramman.thread ] = 1 
						self.show_scheduler ( "after CAMLKUP completion")
				else:
					crc_buffer_length = self.hw_accelerators.ramman.length
					s_address = self.hw_accelerators.ramman.source_c
					local_buffer = []
					crc_result = 0
					for i in range(crc_buffer_length) :
						r = self.READ_SRAM(s_address,8)
						local_buffer.append(r)
						s_address += 1
					if self.hw_accelerators.ramman.type == 0: # crc_32
						if self.hw_accelerators.ramman.eth == 1: # eth
							self.crc_constants[CRC_TYPE_32].reflect_in = 1
						else:
							self.crc_constants[CRC_TYPE_32].reflect_in = 0
						self.crc_constants[CRC_TYPE_32].reflect_out = 0
						self.hw_accelerators.ramman.result = self.crc ( local_buffer, self.hw_accelerators.ramman.length, self.hw_accelerators.ramman.source_a, CRC_TYPE_32 )
						crc_result = self.hw_accelerators.ramman.result
					self.WRITE_IO(CRC_RESULT_IO_ADDRESS,4,crc_result)
					r = self.READ_IO(CRC_RESULT_IO_ADDRESS,4)
					self.changes.append(" IO: word %08X=%08X " % (CRC_RESULT_IO_ADDRESS,r))
				if self.stall == STALL_RAMMAN:
					self.stall = STALL_NORMAL
					self.changes.append(" STALL: 0 ")
				self.hw_accelerators.ramman.ready = 1
				self.hw_accelerators.ramman.valid = 0
				if self.stall == STALL_LDIO:
					self.stall_ldio_time += self.simulator.clock
					self.pc = self.stall_pc.pc & PC_MASK
					i=self.pc//4
					self.code_statistics[i][self.scheduler.current_context][0] = self.simulator.clock - self.stall_pc.enter_stall
					self.stall = STALL_NORMAL
					opcode = BitString(uint=self.code_segment[i],length=32)
					self.changes.append(" STALL: 0 ")
					buffer = self.execute_opcode(opcode,1)[1]
					if not buffer :
						log(self.fio,"clock=%d id=%d : 0x%08x => 0x%08x\tError ????" % (self.simulator.clock,self.id,i*4,self.code_segment[i]))
						return 0
					log(self.fio,"clock=%d id=%d : 0x%08x => 0x%08x\t%s" % (self.simulator.clock,self.id,i*4,self.code_segment[i],buffer))
					if len(self.changes) > 0:
						log(self.fio,"clock=%d id=%d : CHANGES: %s" % (self.simulator.clock,self.id,self.changes))
						self.changes[:] = [] # clear the list
					if self.stall_pc.delay_pc != 0:
						self.pc = self.stall_pc.delay_pc & PC_MASK
						i = self.pc //4
						opcode = BitString(uint=self.code_segment[i],length=32)
						buffer = self.execute_opcode(opcode,0)[1]
						if not buffer :
							log(self.fio,"clock=%d id=%d : 0x%08x => 0x%08x\tError ????" % (self.simulator.clock,self.id,i*4,self.code_segment[i]))
							return 0
						log(self.fio,"clock=%d id=%d : 0x%08x => 0x%08x\t%s" % (self.simulator.clock,self.id,i*4,self.code_segment[i],buffer))
						if len(self.changes) > 0:
							log(self.fio,"clock=%d id=%d : CHANGES: %s" % (self.simulator.clock,self.id,self.changes))
							self.changes[:] = [] # clear the list

	def camlkup (self,start, key, key_size, use_mask):
		res = -1
		#if key_size == 0: # 16bit

		#elif key_size == 1: # 32bit
							 
		#elif key_size == 2: # 64bit
							
		
		return res

	def crc (self):
		print "CRC"
	def check_finish(self,ind):
		print "check_finish"
		return 0

	def execute_opcode (self,opcode,exitstall):
		""" execute one opcode """
		r = 0
		op5 = opcode[opcodes.jmpOpcode['opcode'][0]:opcodes.jmpOpcode['opcode'][1]].unpack('uint:5')[0]
		op4 = opcode[opcodes.dmaOpcode['opcode'][0]:opcodes.dmaOpcode['opcode'][1]].unpack('uint:4')[0]
		op = opcode[opcodes.ldOpcode['opcode'][0]:opcodes.ldOpcode['opcode'][1]].unpack('uint:6')[0]
		if op4 == opcodes.OPCODE_CODE_DMARD >>2:
			r = self.opcode_dmard(opcode,op4)
		elif op4 == opcodes.OPCODE_CODE_DMAWR >>2:
			r = self.opcode_dmawr(opcode,op4)
		elif op4 == opcodes.OPCODE_CODE_DMALU >>2:
			r = self.opcode_dmaalu(opcode)
		elif op5 == opcodes.OPCODE_CODE_JMP:
			r = self.opcode_jmp(opcode)
		else:
			dict = {
				opcodes.OPCODE_CODE_LJMP:self.opcode_ljmp,
				opcodes.OPCODE_CODE_BEZ:self.opcode_jmpz,
				opcodes.OPCODE_CODE_CMPJMP:self.opcode_jmp_cmp,
				opcodes.OPCODE_CODE_ADD:self.opcode_add, 
				opcodes.OPCODE_CODE_SUB:self.opcode_sub, 
				opcodes.OPCODE_CODE_AND:self.opcode_and, 
				opcodes.OPCODE_CODE_OR: self.opcode_or,  
				opcodes.OPCODE_CODE_XOR:self.opcode_xor,
				opcodes.OPCODE_CODE_MULT:self.opcode_mult,
				opcodes.OPCODE_CODE_RET:self.opcode_ret,
				opcodes.OPCODE_CODE_LD:self.opcode_ld, 
				opcodes.OPCODE_CODE_ST:self.opcode_st, 
				opcodes.OPCODE_CODE_LDC:self.opcode_ldc, 
				opcodes.OPCODE_CODE_STC:self.opcode_stc, 
				opcodes.OPCODE_CODE_LDIO:self.opcode_ldio,
				opcodes.OPCODE_CODE_STIO:self.opcode_stio,
				opcodes.OPCODE_CODE_MOVEIMM:self.opcode_mov,
				opcodes.OPCODE_CODE_SHIFT:self.opcode_shift,
				opcodes.OPCODE_CODE_EXTRACT:self.opcode_extract,
				opcodes.OPCODE_CODE_INSERT:self.opcode_insert,
				opcodes.OPCODE_CODE_CSSVR:self.opcode_ctxswap,
				opcodes.OPCODE_CODE_HASH:self.opcode_hash,
				opcodes.OPCODE_CODE_CRCCALC:self.opcode_ramman,
				opcodes.OPCODE_CODE_BBTX:self.opcode_bbtx,
				opcodes.OPCODE_CODE_BBMSG:self.opcode_bbmsg,
				opcodes.OPCODE_CODE_FFI:self.opcode_ffi,
				opcodes.OPCODE_CODE_ICHECK:self.opcode_chksm,
				opcodes.OPCODE_CODE_CNTUP:self.opcode_counter,
				opcodes.OPCODE_CODE_CRYPT:self.opcode_crypt,
				opcodes.OPCODE_CODE_SIGNEXT:self.opcode_signext,
				opcodes.OPCODE_CODE_NOP:self.opcode_nop
				}
			if op in dict:
				functionToCall = dict[op]
				r = functionToCall(opcode,op)
			else:
				print 'Wrong opcode : 0x%x' % (op)
		return r

	def opcode_jmp (self,opcode):
		""" OPCODE = JMP """
		evaluation = 0
		execute = 0
		buff = ''
		pc = self.pc
		self.pc += 4
		jc = opcode[opcodes.jmpOpcode['call'][0]:opcodes.jmpOpcode['call'][1]].unpack('uint:1')[0]
		if jc == 1 :
			buff = 'call'
		else:
			buff = 'jmp'
		condition = opcode[opcodes.jmpOpcode['condition'][0]:opcodes.jmpOpcode['condition'][1]].unpack('uint:5')[0]
		invert = opcode[opcodes.jmpOpcode['invert_condition'][0]:opcodes.jmpOpcode['invert_condition'][1]].unpack('uint:1')[0]
		set_clr = opcode[opcodes.jmpOpcode['jmp_register'][0]:opcodes.jmpOpcode['jmp_register'][1]].unpack('uint:1')[0]
		if condition == opcodes.OPCODE_CONDITION_EQUAL:
			if invert:
				buff += '!=0\t'
			else:
				buff += '=0\t'
		elif condition == opcodes.OPCODE_CONDITION_LESS:
			if invert :
				buff += '<0\t'
			else:
				buff += '>=0\t'
		elif condition == opcodes.OPCODE_CONDITION_GREATER:
			if invert :
				buff += '>0\t'
			else:
				buff += '<=0\t'
		elif  set_clr:
			if invert :
				buff += '_clr\t'
			else:
				buff += '_set\t'			
			offset = opcode[opcodes.jmpOpcode['condition_bit_offset'][0]:opcodes.jmpOpcode['condition_bit_offset'][1]].unpack('uint:5')[0]			
		else:
			buff += '\t'
		immediate = opcode[opcodes.jmpOpcode['immediate_or_register'][0]:opcodes.jmpOpcode['immediate_or_register'][1]].unpack('uint:1')[0]		
		if immediate :
			dst = opcode[opcodes.jmpOpcode['immediate_value'][0]:opcodes.jmpOpcode['immediate_value'][1]].unpack('uint:10')[0]
			buff += '0x%x\t' % (dst)
		else:
			dst = opcode[opcodes.jmpOpcode['address_register'][0]:opcodes.jmpOpcode['address_register'][1]].unpack('uint:5')[0]
			buff += 'r%d\t' % (dst)
		delay_slot = opcode[opcodes.jmpOpcode['execute_delay_slot'][0]:opcodes.jmpOpcode['execute_delay_slot'][1]].unpack('uint:2')[0]	
		if set_clr:
			buff += 'r%d\td.%d\t' % (condition,offset)
			if  delay_slot == 1:
				buff += 'ds1\t'
			elif delay_slot == 2:
				buff += 'ds2\t'
			if not immediate:	
				predict = opcode[opcodes.jmpOpcode['update'][0]:opcodes.jmpOpcode['update'][1]].unpack('uint:1')[0]
				if  predict :
					buff += 'predict'
		elif condition != opcodes.OPCODE_CONDITION_ALWAYS :			
			if  delay_slot == 1:
				buff += 'ds1\t'
			elif delay_slot == 2:
				buff += 'ds2\t'
			if not immediate:
				predict = opcode[opcodes.jmpOpcode['update'][0]:opcodes.jmpOpcode['update'][1]].unpack('uint:1')[0]
				if  predict :
					buff += 'predict'
		if SIMULATE:
			if not set_clr and not invert and not condition:
				evaluation = 1
				execute = delay_slot
			elif set_clr:
				condition_register = self.REGISTER(condition)
				test_bit = 1 << offset
				if condition_register & test_bit == test_bit:
					evaluation = 1
				else:
					evaluation = 0
				if invert:
					evaluation = 1 - evaluation
				execute = delay_slot
			else:
				if condition == opcodes.OPCODE_CONDITION_EQUAL:
					evaluation = self.Z_FLAG_IS_SET(self.st)
				elif condition == opcodes.OPCODE_CONDITION_LESS:
					evaluation = self.N_FLAG_IS_SET(self.st)
				elif condition == opcodes.OPCODE_CONDITION_GREATER:
					evaluation = self.Z_FLAG_IS_SET(self.st) & self.N_FLAG_IS_SET(self.st)
				else:
					if condition & 0x8 == 0x8:
						evaluation = self.OVF_FLAG_IS_SET( self.st )
					elif condition & 0x4 == 0x4:
						evaluation = self.CY_FLAG_IS_SET( self.st )
				if invert:
					evaluation = 1 - evaluation
				execute = delay_slot
			if execute > 0:
				if evaluation == 1:
					if immediate:
						sign = dst >> 9
						if sign:
							jump_address = pc - ( ( ~(dst & 0x3FF) + 1 ) << 2 ) & 0xFFF 
						else:
							jump_address = pc + ( dst & 0x1ff ) << 2
					else:
						jump_address = self.REGISTER(dst)
					self.stall_pc.delay_pc = jump_address
					if jc:
						self.push_call_stack(( pc + execute * 4 ) & PC_MASK)
					ind = self.pc//4
					opcode = BitString(uint=self.code_segment[ind],length=32)
					self.pipe.opcode_ds1 = opcode
					self.pipe.pc_ds1 = self.pc
					if execute == 2:
						ind += 1
						opcode = BitString(uint=self.code_segment[ind],length=32)
						self.pipe.opcode_ds2 = opcode
						self.pipe.pc_ds2 = self.pc + 4
					else:
						self.pipe.opcode_ds2 = BitString('0xfc000000')
						self.pipe.pc_ds2 = self.pc + 4
					self.pipe.clock = 2
				else:
					self.stall_pc.delay_pc = ( self.pc + 4 ) & PC_MASK
				self.stall_pc.delay_pc &= PC_MASK
			else:
				if evaluation == 1:
					if jc:
						self.push_call_stack(( pc - (2 - execute) * 4 ) & PC_MASK)
					self.pipe.opcode_ds1 = BitString('0xfc000000')
					self.pipe.pc_ds1 = self.pc 
					self.pipe.opcode_ds2 = BitString('0xfc000000')
					self.pipe.pc_ds2 = self.pc + 4
					self.pipe.clock = 2

			if evaluation == 1:
				if immediate:
					sign = sign = dst >> 9
					if sign:
						jump_address = pc - ( (~(dst & 0x3FF) + 1 ) << 2 ) & 0xFFF 
					else:
						jump_address = pc + (dst & 0x1ff ) << 2
				else:
					jump_address = self.REGISTER(dst)
				self.pc = jump_address & PC_MASK
				self.changes.append(" JUMP: %08X " % (self.pc))
		else:
			evaluation = 1
		return (evaluation,buff)
		
	def pop_call_stack(self):
		print 'pop_call_stack - len=' + str(len(self.call_stack))
		if len(self.call_stack) > 0:
			offset = self.call_stack.pop()
			print 'pop_call_stack' + str(offset)
			return offset
		return 0
	
	def push_call_stack (self,offset):
		if len(self.call_stack) < CALL_STACK_DEPTH:
			self.call_stack.append(offset + 4)
			print 'push_call_stack' + str(offset)

	def opcode_jmpz (self,opcode,op):
		""" OPCODE = JMPZ """
		evaluation = 0
		execute = 0
		pc = self.pc
		self.pc += 4
		buff = ''
		jc = opcode[opcodes.bezOpcode['call'][0]:opcodes.bezOpcode['call'][1]].unpack('uint:1')[0]
		if jc:
			buff = 'call'
		else:
			buff = 'jmp'
		immediate = opcode[opcodes.bezOpcode['immediate_or_register'][0]:opcodes.bezOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		invert =  opcode[opcodes.bezOpcode['invert_condition'][0]:opcodes.bezOpcode['invert_condition'][1]].unpack('uint:1')[0]
		if invert:
			buff += 'nz\t'
		else:
			buff += 'z\t'
		if immediate :
			dst = opcode[opcodes.bezOpcode['immediate_value'][0]:opcodes.bezOpcode['immediate_value'][1]].unpack('uint:10')[0]
			buff += '0x%x\t' % (dst)
		else:
			dst = opcode[opcodes.bezOpcode['address_register'][0]:opcodes.bezOpcode['address_register'][1]].unpack('uint:5')[0]
			buff += 'r%d\t' % (dst)
		cond = opcode[opcodes.bezOpcode['source_a'][0]:opcodes.bezOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (cond)
		delay_slot = opcode[opcodes.bezOpcode['execute_delay_slot'][0]:opcodes.bezOpcode['execute_delay_slot'][1]].unpack('uint:2')[0]
		if delay_slot == 1:
			buff += 'ds1\t'
		elif delay_slot == 2:
			buff += 'ds2\t'
		if not immediate:
			predict = opcode[opcodes.bezOpcode['update'][0]:opcodes.bezOpcode['update'][1]].unpack('uint:1')[0]
			if predict:
				buff += 'predict'
		size = opcode[opcodes.bezOpcode['size'][0]:opcodes.bezOpcode['size'][1]].unpack('uint:2')[0]
		if size == opcodes.OPCODE_16MSB:
			buff += '16msb'
		elif size == opcodes.OPCODE_16LSB:
			buff += '16lsb'
		if SIMULATE:
			condition_register = self.REGISTER(cond)
			if size == opcodes.OPCODE_16MSB:
				condition_register &= 0x0000FFFF
			elif size == opcodes.OPCODE_16LSB:
				condition_register &= 0xFFFF0000
			if invert and condition_register != 0:
				evaluation = 1
			elif not invert and condition_register == 0:
				evaluation = 1
			if immediate:
				sign = dst >> 9
				if sign:
					jump_address = pc - (( ~(dst & 0x3FF) +1 ) << 2 ) & 0xFFF 
				else:
					jump_address = pc + ( dst & 0x1FF ) << 2
			else:
				jump_address = self.REGISTER(dst)
			jump_address &= PC_MASK
			execute = delay_slot
			if execute > 0:
				if evaluation == 1:
					self.stall_pc.delay_pc = jump_address
					if jc:
						self.push_call_stack ( ( pc + execute * 4 ) & PC_MASK)
					ind = self.pc//4
					opcode = BitString(uint=self.code_segment[ind],length=32)
					self.pipe.opcode_ds1 = opcode
					self.pipe.pc_ds1 = self.pc
					if execute == 2:
						ind += 1
						opcode = BitString(uint=self.code_segment[ind],length=32)
						self.pipe.opcode_ds2 = opcode
						self.pipe.pc_ds2 = self.pc + 4
					else:
						self.pipe.opcode_ds2 = BitString('0xfc000000')
						self.pipe.pc_ds2 = self.pc + 4
					self.pipe.clock = 2
				else:
					self.stall_pc.delay_pc = self.pc + 4
				self.stall_pc.delay_pc &= PC_MASK
			else:
				if evaluation == 1:
					if jc:
						self.push_call_stack(( pc - (2 - execute) * 4 ) & PC_MASK)
					self.pipe.opcode_ds1 = BitString('0xfc000000')
					self.pipe.pc_ds1 = self.pc 
					self.pipe.opcode_ds2 = BitString('0xfc000000')
					self.pipe.pc_ds2 = self.pc + 4
					self.pipe.clock = 2
			if evaluation == 1:
				jump_address &= PC_MASK 
				self.pc = jump_address & PC_MASK
			return (evaluation,buff)
		return (1,buff)  

	def opcode_jmp_cmp (self,opcode,op):
		evaluation = 0
		execute = 0
		buff = 'jmp_cmp\t'
		pc = self.pc
		self.pc += 4
		immediate = opcode[opcodes.cmpjmpOpcode['immediate_or_register'][0]:opcodes.cmpjmpOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if  immediate :
			dst = opcode[opcodes.cmpjmpOpcode['immediate_value'][0]:opcodes.cmpjmpOpcode['immediate_value'][1]].unpack('uint:10')[0]
			buff += '0x%x\t' % (dst)
		else:
			dst = opcode[opcodes.cmpjmpOpcode['address_register'][0]:opcodes.cmpjmpOpcode['address_register'][1]].unpack('uint:5')[0]
			buff += 'r%d\t' % (dst)
		srca = opcode[opcodes.cmpjmpOpcode['source_a'][0]:opcodes.cmpjmpOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srca)
		condition = opcode[opcodes.cmpjmpOpcode['operation'][0]:opcodes.cmpjmpOpcode['operation'][1]].unpack('uint:2')[0]
		invert = opcode[opcodes.cmpjmpOpcode['invert_condition'][0]:opcodes.cmpjmpOpcode['invert_condition'][1]].unpack('uint:1')[0]
		if condition == opcodes.OPCODE_OPERATION_EQUAL:
			if invert :
				buff += '!=\t'
			else:
				buff += '==\t'
		elif condition == opcodes.OPCODE_OPERATION_GREATER:
			if invert :
				buff += '<=\t'
			else:
				buff += '>\t'
		elif condition == opcodes.OPCODE_OPERATION_BIT_OR:
			if invert :
				buff += '!or\t'
			else:
				buff += 'or\t'
		elif condition == opcodes.OPCODE_OPERATION_BIT_AND:
			if invert :
				buff += '!and\t'
			else:
				buff += 'and\t'
		srcb = opcode[opcodes.cmpjmpOpcode['source_b'][0]:opcodes.cmpjmpOpcode['source_b'][1]].unpack('uint:5')[0]
		bsel = opcode[opcodes.cmpjmpOpcode['bsel'][0]:opcodes.cmpjmpOpcode['bsel'][1]].unpack('uint:1')[0]
		if bsel :
			buff += '0x%x\t' % (srcb)
		else:
			buff += 'r%d\t' % (srcb)
		if not immediate:
			predict = opcode[opcodes.cmpjmpOpcode['update'][0]:opcodes.cmpjmpOpcode['update'][1]].unpack('uint:1')[0]
			if predict :
				buff += 'predict'
		if SIMULATE:
			source_a = self.REGISTER(srca)
			if bsel:
				source_b = srcb
			else:
				source_b = self.REGISTER(srcb)
			if condition == opcodes.OPCODE_OPERATION_EQUAL:
				if source_a == source_b:
					evaluation = 1
				else:
					evaluation = 0
			elif condition == opcodes.OPCODE_OPERATION_GREATER:
				if source_a > source_b:
					evaluation = 1
				else:
					evaluation = 0
			elif condition == opcodes.OPCODE_OPERATION_BIT_OR:
				if source_a | source_b :
					evaluation = 1
				else:
					evaluation = 0
			else:
				if source_a & source_b:
					evaluation = 1
				else:
					evaluation = 0
			if invert:
				evaluation = 1 - evaluation
			execute = delay_slot
			if immediate:
				sign = dst >> 9
				if sign:
					jump_address = pc - (( ~(dst & 0x3FF) +1 ) << 2 ) & 0xFFF 
				else:
					jump_address = pc + (dst & 0x1FF ) << 2
			else:
				jump_address = self.REGISTER(dst)
			execute = delay_slot
			if execute > 0:
				if evaluation == 1:
					self.stall_pc.delay_pc = jump_address					
					ind = self.pc//4
					opcode = BitString(uint=self.code_segment[ind],length=32)
					self.pipe.opcode_ds1 = opcode
					self.pipe.pc_ds1 = self.pc
					self.pipe.clock = 2
				else:
					self.stall_pc.delay_pc = self.pc + 4
				self.stall_pc.delay_pc &= PC_MASK
			else:
				if evaluation == 1:	
					self.pipe.opcode_ds1 = BitString('0xfc000000')
					self.pipe.pc_ds1 = self.pc 					
					self.pipe.clock = 2
			if evaluation == 1:
				self.pc = jump_address & PC_MASK
			return (evaluation,buff)
		return (1,buff)

	def opcode_ljmp (self,opcode,op):
		""" OPCODE = LJMP """
		buff = ''
		execute = 2
		pc = self.pc
		self.pc += 4
		jc = opcode[opcodes.jmplngOpcode['call'][0]:opcodes.jmplngOpcode['call'][1]].unpack('uint:1')[0]
		if jc == 1:
			buff = 'lcall\t'
		else:
			buff = 'ljmp\t'
		dst = opcode[opcodes.jmplngOpcode['immediate_value'][0]:opcodes.jmplngOpcode['immediate_value'][1]].unpack('uint:14')[0]
		buff += '0x%x' % (dst)
		if SIMULATE:
			jump_address = (dst << 2) & PC_MASK
			self.stall_pc.delay_pc = jump_address
			print 'opcode_ljmp: %d 0x%x' % (jc,jump_address)
			if jc == 1:
				self.push_call_stack ( ( pc + execute * 4 ) & PC_MASK)
			ind = self.pc // 4
			opcode = BitString(uint=self.code_segment[ind],length=32)
			self.pipe.opcode_ds1 = opcode
			self.pipe.pc_ds1 = self.pc
			self.pipe.clock = 2
			self.stall_pc.delay_pc &= PC_MASK
			self.pc = jump_address & PC_MASK

		return (1,buff)

	def calc_dma_length (self,MIN):
		min_dma_clock = 0
		for i in range(DMA_FIFO_DEPTH) :
			if self.hw_accelerators.dma[i].valid:
				if min_dma_clock < self.hw_accelerators.dma [i].clock:
					min_dma_clock = self.hw_accelerators.dma [i].clock

		if min_dma_clock > 0:
			min_dma_clock = min_dma_clock - self.simulator.clock + 1
			if min_dma_clock < MIN:
				min_dma_clock = MIN
		else:
			min_dma_clock = MIN
		return min_dma_clock

	def dma_ctx_swap (self):
		ind = self.pc//4
		opcode = BitString(uint=self.code_segment[ind],length=32)
		self.execute_opcode(opcode,0)
		if self.stall != STALL_NORMAL:
			self.stall_pc.delay_pc = self.pc
			return 0
		ind = self.pc//4
		opcode = BitString(uint=self.code_segment[ind],length=32)
		self.execute_opcode(opcode,0)
		if self.stall != STALL_NORMAL:
			self.stall_pc.delay_pc = self.pc
			return 0
		return 1

	def dma_context_valid (self):
		self.st = 0
		for r in range(NUMBER_OF_PRIVATE_REGISTERS):
			ind = self.scheduler.current_context*NUMBER_OF_PRIVATE_REGISTERS + r
			if self.scheduler.save_context == 1:
				self.context_segment[ind] = self.private_registers[r] 
			self.private_registers[r] = self.context_segment[ind]
			self.changes.append(" REG: r%d=%08X " % (reg,self.private_registers[reg]))
		self.scheduler.previous_context = self.scheduler.current_context
		self.scheduler.current_context = self.scheduler.next_context
		if self.scheduler.async_enable[self.scheduler.next_context] == 1:
			self.scheduler.async_wakeup_request_normal[self.scheduler.next_context] = 0
			self.scheduler.async_wakeup_request_urgent[self.scheduler.next_context] = 0
			self.scheduler.async_wakeup_request[self.scheduler.next_context] = 0
			self.scheduler.async_enable[self.scheduler.next_context] = 0
		else:
			self.scheduler.async_wakeup_request[self.scheduler.next_context] = 0
		self.scheduler.next_context_valid = 0
		self.pc = self.private_registers[16] >> 16
		self.pc &= PC_MASK
		self.changes.append(" THREAD: %08X " % (self.scheduler.current_context))

	def opcode_dmard(self,opcode,op):
		pc = self.pc
		self.pc += 4
		buff = 'dma_rd\t'
		dst = opcode[opcodes.dmaOpcode['source_a'][0]:opcodes.dmaOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		srcc = opcode[opcodes.dmaOpcode['source_a'][0]:opcodes.dmaOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srcc)
		srcb = opcode[opcodes.dmaOpcode['source_b_or_immediate'][0]:opcodes.dmaOpcode['source_b_or_immediate'][1]].unpack('uint:8')[0]
		immediate = opcode[opcodes.dmaOpcode['immediate_or_register'][0]:opcodes.dmaOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			buff += '0x%x\t' % ( srcb)
		else:
			buff += 'r%d\t' % ( srcb)
		invoke = opcode[opcodes.dmaOpcode['invoke'][0]:opcodes.dmaOpcode['invoke'][1]].unpack('uint:1')[0]
		addr_calc = opcode[opcodes.dmaOpcode['addr_calc'][0]:opcodes.dmaOpcode['addr_calc'][1]].unpack('uint:1')[0]
		mask = opcode[opcodes.dmaOpcode['mask'][0]:opcodes.dmaOpcode['mask'][1]].unpack('uint:1')[0]
		update = opcode[opcodes.dmaOpcode['update_r16'][0]:opcodes.dmaOpcode['update_r16'][1]].unpack('uint:1')[0]
		context_swap = opcode[opcodes.dmaOpcode['context_swap'][0]:opcodes.dmaOpcode['context_swap'][1]].unpack('uint:1')[0]
		async_en = opcode[opcodes.dmaOpcode['async_enable'][0]:opcodes.dmaOpcode['async_enable'][1]].unpack('uint:1')[0]
		common = opcode[opcodes.dmaOpcode['common_or_private'][0]:opcodes.dmaOpcode['common_or_private'][1]].unpack('uint:1')[0]
		mem = opcode[opcodes.dmaOpcode['mem'][0]:opcodes.dmaOpcode['mem'][1]].unpack('uint:1')[0]
		if invoke:
			buff += 'invoke\t'
		if mask:
			buff += 'mask\t'
		if mem:
			buff += 'mem\t'				
		if update:
			buff += 'update\t'
		if common:
			buff += 'common\t'		
		if addr_calc:
			buff += 'addr_calc\t'	
		if context_swap:
			buff += 'ctx_swap\t'
		if async_en:
			buff += 'async_en\t'
		if SIMULATE:
			if immediate:
				length = srcb & 0xff
			else:
				length = self.REGISTER(srcb)  & 0xff
			if self.hw_accelerators.dma_count < DMA_FIFO_DEPTH:
				min_dma_clock = self.calc_dma_length(DMA_DDR_TO_SRAM_MIN)
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].clock = self.hw_accelerator_clock( min_dma_clock, ( DMA_DDR_TO_SRAM_MAX - DMA_DDR_TO_SRAM_MIN ) + min_dma_clock)
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].thread = self.scheduler.current_context
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].invoke = invoke
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].sram_to_ddr = 0
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].destination = self.REGISTER(srcc) & 0xffff
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].common_or_private = common
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mem = mem
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mask = mask
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].stall = stall
				if addr_calc:
					if self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mem == 0:
						self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].source = \
						BPM_BUFFERS_BASE + DDR_BUFFER_PAYLOAD_OFFSET + \
						( self.REGISTER(srca) & 0x00001FFF ) * PACKET_DDR_BUFFER_SIZE
					else:
						self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].source = \
						( self.REGISTER(srca) & 0x0000FFF ) * PACKET_SRAM_BUFFER_SIZE
				else:
					self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].source = \
						self.REGISTER(srca) & 0x03FFFFFF
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].length = length
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].dmalu = False
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].valid = 1
				if async_en:
					self.scheduler.async_enable[self.scheduler.current_context] = 1
				if update:
					self.private_registers[16] = ( self.private_registers[16] & 0xffff ) \
					| ( (( self.pc + 4 ) & PC_MASK) << 16 )
					if self.scheduler.next_context_valid == 0:
						self.changes.append(" REG: r16=%08X " % (self.private_registers[16]))
				if context_swap:
					if not self.dma_ctx_swap():
						return (1,buff)
					if self.scheduler.next_context_valid == 1:
						self.dma_context_valid()
				else:
					self.stall_pc.enter_stall = self.simulator.clock
					self.stall = STALL_NO_CONTEXT
					self.scheduler.save_context = 1
					self.changes.append(" STALL: 1 ")
				self.show_scheduler("after DMA_RD")
				self.hw_accelerators.dma_count += 1
				self.hw_accelerators.dma_in = ( self.hw_accelerators.dma_in + 1 ) % DMA_FIFO_DEPTH
				if self.max_dma_fifo < self.hw_accelerators.dma_count:
					self.max_dma_fifo = self.hw_accelerators.dma_count
			else:
				self.stall_pc.enter_stall = self.simulator.clock
				self.stall = STALL_DMA
				self.stall_pc.pc = pc
				self.changes.append(" STALL: 1 ")

		return (1,buff)
	
	def opcode_dmawr(self,opcode,op):
		pc = self.pc
		self.pc += 4
		buff = 'dma_wr\t'
		dst = opcode[opcodes.dmaOpcode['source_a'][0]:opcodes.dmaOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		srcc = opcode[opcodes.dmaOpcode['source_a'][0]:opcodes.dmaOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srcc)
		srcb = opcode[opcodes.dmaOpcode['source_b_or_immediate'][0]:opcodes.dmaOpcode['source_b_or_immediate'][1]].unpack('uint:8')[0]
		immediate = opcode[opcodes.dmaOpcode['immediate_or_register'][0]:opcodes.dmaOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			buff += '0x%x\t' % ( srcb)
		else:
			buff += 'r%d\t' % ( srcb)
		invoke = opcode[opcodes.dmaOpcode['invoke'][0]:opcodes.dmaOpcode['invoke'][1]].unpack('uint:1')[0]
		addr_calc = opcode[opcodes.dmaOpcode['addr_calc'][0]:opcodes.dmaOpcode['addr_calc'][1]].unpack('uint:1')[0]
		mask = opcode[opcodes.dmaOpcode['mask'][0]:opcodes.dmaOpcode['mask'][1]].unpack('uint:1')[0]
		update = opcode[opcodes.dmaOpcode['update_r16'][0]:opcodes.dmaOpcode['update_r16'][1]].unpack('uint:1')[0]
		context_swap = opcode[opcodes.dmaOpcode['context_swap'][0]:opcodes.dmaOpcode['context_swap'][1]].unpack('uint:1')[0]
		async_en = opcode[opcodes.dmaOpcode['async_enable'][0]:opcodes.dmaOpcode['async_enable'][1]].unpack('uint:1')[0]
		common = opcode[opcodes.dmaOpcode['common_or_private'][0]:opcodes.dmaOpcode['common_or_private'][1]].unpack('uint:1')[0]
		mem = opcode[opcodes.dmaOpcode['mem'][0]:opcodes.dmaOpcode['mem'][1]].unpack('uint:1')[0]
		if invoke:
			buff += 'invoke\t'
		if mask:
			buff += 'mask\t'
		if mem:
			buff += 'mem\t'				
		if update:
			buff += 'update\t'
		if common:
			buff += 'common\t'		
		if addr_calc:
			buff += 'addr_calc\t'	
		if context_swap:
			buff += 'ctx_swap\t'
		if async_en:
			buff += 'async_en\t'
		if SIMULATE:
			if immediate:
				length = srcb & 0xff
			else:
				length = self.REGISTER(srcb)  & 0xff
			if self.hw_accelerators.dma_count < DMA_FIFO_DEPTH:
				min_dma_clock = self.calc_dma_length(DMA_SRAM_TO_DDR_MIN)
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].clock = self.hw_accelerator_clock( min_dma_clock, ( DMA_SRAM_TO_DDR_MAX - DMA_SRAM_TO_DDR_MIN ) + min_dma_clock)
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].thread = self.scheduler.current_context
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].invoke = invoke
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].sram_to_ddr = 1
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].destination = self.REGISTER(srcc) & 0xffff
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].common_or_private = common
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mem = mem
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mask = mask
				if addr_calc:
					if self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mem == 0:
						self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].destination = \
						BPM_BUFFERS_BASE + DDR_BUFFER_PAYLOAD_OFFSET + \
						( self.REGISTER(srca) & 0x00001FFF ) * PACKET_DDR_BUFFER_SIZE
					else:
						self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].destination = \
						( self.REGISTER(srca) & 0x0000FFF ) * PACKET_SRAM_BUFFER_SIZE
				else:
					self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].destination = \
						self.REGISTER(srca) & 0x03FFFFFF
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].source = \
						self.REGISTER(srcc) & 0x0000FFFF
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].length = length
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].dmalu = False
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].valid = 1
				if async_en:
					self.scheduler.async_enable[self.scheduler.current_context] = 1
				if mask:
					self.scheduler.async_enable[self.scheduler.current_context] = 1
				if update:
					self.private_registers[16] = ( self.private_registers[16] & 0xffff ) \
					| ( (( self.pc + 4 ) & PC_MASK) << 16 )
					if self.scheduler.next_context_valid == 0:
						self.changes.append(" REG: r16=%08X " % (self.private_registers[16]))
				if context_swap:
					if not self.dma_ctx_swap():
						return (1,buff)
					if self.scheduler.next_context_valid == 1:
						self.dma_context_valid()
				else:
					self.stall_pc.enter_stall = self.simulator.clock
					self.stall = STALL_NO_CONTEXT
					self.scheduler.save_context = 1
					self.changes.append(" STALL: 1 ")
				self.show_scheduler("after DMA_WR")
				self.hw_accelerators.dma_count += 1
				self.hw_accelerators.dma_in = ( self.hw_accelerators.dma_in + 1 ) % DMA_FIFO_DEPTH
				if self.max_dma_fifo < self.hw_accelerators.dma_count:
					self.max_dma_fifo = self.hw_accelerators.dma_count
			else:
				self.stall_pc.enter_stall = self.simulator.clock
				self.stall = STALL_DMA
				self.stall_pc.pc = pc
				self.changes.append(" STALL: 1 ")
		return (1,buff)

	def opcode_dmaalu (self,opcode):
		pc = self.pc
		self.pc += 4
		buff = 'dma_lkup\t'
		srca = opcode[opcodes.dmaaluOpcode['source_a'][0]:opcodes.dmaaluOpcode['source_a'][1]].unpack('uint:5')[0]
		srcc = opcode[opcodes.dmaaluOpcode['source_c'][0]:opcodes.dmaaluOpcode['source_c'][1]].unpack('uint:5')[0]
		srcb = opcode[opcodes.dmaaluOpcode['source_b'][0]:opcodes.dmaaluOpcode['source_b'][1]].unpack('uint:5')[0]
		buff += 'r%d\tr%d\t' % (srca,srcc)
		immediate = opcode[opcodes.dmaaluOpcode['immediate_or_register'][0]:opcodes.dmaaluOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			buff += '0x%x\t' % (srcb)
		else:
			buff += 'r%d\t' % (srcb)
		rs = opcode[opcodes.dmaaluOpcode['res_slot'][0]:opcodes.dmaaluOpcode['res_slot'][1]].unpack('uint:3')[0]
		buff += '0x%x\t' % (rs)
		invoke = opcode[opcodes.dmaaluOpcode['invoke'][0]:opcodes.dmaaluOpcode['invoke'][1]].unpack('uint:1')[0]
		mask = opcode[opcodes.dmaaluOpcode['mask'][0]:opcodes.dmaaluOpcode['mask'][1]].unpack('uint:1')[0]
		update = opcode[opcodes.dmaaluOpcode['update_r16'][0]:opcodes.dmaaluOpcode['update_r16'][1]].unpack('uint:1')[0]
		context_swap = opcode[opcodes.dmaaluOpcode['context_swap'][0]:opcodes.dmaaluOpcode['context_swap'][1]].unpack('uint:1')[0]
		async_en = opcode[opcodes.dmaaluOpcode['async_enable'][0]:opcodes.dmaaluOpcode['async_enable'][1]].unpack('uint:1')[0]
		common = opcode[opcodes.dmaaluOpcode['common_or_private'][0]:opcodes.dmaaluOpcode['common_or_private'][1]].unpack('uint:1')[0]
		mem = opcode[opcodes.dmaaluOpcode['mem'][0]:opcodes.dmaaluOpcode['mem'][1]].unpack('uint:1')[0]
		if invoke:
			buff += 'invoke\t'		
		if mask:
			buff += 'mask\t'
		if update:
			buff += 'update\t'
		if context_swap:
			buff += 'ctx_swap\t'
		if async_en:
			buff += 'async_en\t'
		if common:
			buff += 'common\t'
		if mem:
			buff += 'sram\t'
		if SIMULATE:
			if not immediate:
				length = self.REGISTER(srcb) & 0xff
			else:
				length = srcb & 0xff
			if self.hw_accelerators.dma_count < DMA_FIFO_DEPTH:
				min_dma_clock = self.calc_dma_length(DMA_DDR_TO_SRAM_MIN)
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].clock = self.hw_accelerator_clock( min_dma_clock, ( DMA_DDR_TO_SRAM_MAX - DMA_DDR_TO_SRAM_MIN ) + min_dma_clock)
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].thread = self.scheduler.current_context
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].invoke = invoke
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].dmalu = True
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].sram_to_ddr = 0
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].destination = self.REGISTER(srcc) & 0xffff
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].source = self.REGISTER(srca) & 0x03ffffff
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].common_or_private = common
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].mem = mem
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].global_mask = mask
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].res_slot = res_slot
				self.hw_accelerators.dma [ self.hw_accelerators.dma_in ].valid = 1
				if async_en:
					self.scheduler.async_enable[self.scheduler.current_context] = 1
				if update:
					self.private_registers[16] = ( self.private_registers[16] & 0xffff ) \
					| ( (( self.pc + 4 ) & PC_MASK) << 16 )
					if self.scheduler.next_context_valid == 0:
						self.changes.append(" REG: r16=%08X " % (self.private_registers[16]))
				if context_swap:
					if not self.dma_ctx_swap():
						return (1,buff)
					if self.scheduler.next_context_valid == 1:
						self.dma_context_valid()
				else:
					self.stall_pc.enter_stall = self.simulator.clock
					self.stall = STALL_NO_CONTEXT
					self.scheduler.save_context = 1
					self.changes.append(" STALL: 1 ")
				self.show_scheduler("after DMA_LKP")
				self.hw_accelerators.dma_count += 1
				self.hw_accelerators.dma_in = ( self.hw_accelerators.dma_in + 1 ) % DMA_FIFO_DEPTH
				if self.max_dma_fifo < self.hw_accelerators.dma_count:
					self.max_dma_fifo = self.hw_accelerators.dma_count
			else:
				self.stall_pc.enter_stall = self.simulator.clock
				self.stall = STALL_DMA
				self.stall_pc.pc = pc
				self.changes.append(" STALL: 1 ")
		return (1,buff)

	def disassembly_alu(self,opcode,op):
		self.pc += 4
		buff = 'alu\t'
		dst = opcode[opcodes.aluOpcode['destination_register'][0]:opcodes.aluOpcode['destination_register'][1]].unpack('uint:5')[0]	
		buff += 'r%d\t' % (dst)
		srca = opcode[opcodes.aluOpcode['source_a'][0]:opcodes.aluOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srca)
		invert = opcode[opcodes.aluOpcode['invert_source'][0]:opcodes.aluOpcode['invert_source'][1]].unpack('uint:1')[0]
		srcb = opcode[opcodes.aluOpcode['source_b_or_immediate'][0]:opcodes.aluOpcode['source_b_or_immediate'][1]].unpack('uint:8')[0]
		immediate = opcode[opcodes.aluOpcode['immediate_or_register'][0]:opcodes.aluOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		update_flags = opcode[opcodes.aluOpcode['update_flags'][0]:opcodes.aluOpcode['update_flags'][1]].unpack('uint:1')[0]
		shift = opcode[opcodes.aluOpcode['byte_shift'][0]:opcodes.aluOpcode['byte_shift'][1]].unpack('uint:3')[0]		
		if shift == opcodes.OPCODE_BYTE_SHIFT_LEFT_1:
			buff += '<<8'
		elif shift == opcodes.OPCODE_BYTE_SHIFT_LEFT_2:
			buff += '<<16'
		elif shift == opcodes.OPCODE_BYTE_SHIFT_LEFT_3:
			buff += '<<24'
		elif shift == opcodes.OPCODE_BYTE_SHIFT_RIGHT_1:
			buff += '>>8'
		elif shift == opcodes.OPCODE_BYTE_SHIFT_RIGHT_2:
			buff += '>>16'
		elif shift == opcodes.OPCODE_BYTE_SHIFT_RIGHT_3:
			buff += '>>24'
		elif not update_flags:
			buff += 'bypass_flags'
		if op == opcodes.OPCODE_CODE_ADD:
			buff += '+'
		elif op == opcodes.OPCODE_CODE_SUB:
			buff += '-'
		elif op == opcodes.OPCODE_CODE_MULT:
			buff += '*'
		elif op == opcodes.OPCODE_CODE_AND:
			buff += 'and'
		elif op == opcodes.OPCODE_CODE_OR:
			buff += 'or'
		else:
			buff += 'xor'
		if invert:
			buff += '~'
		buff +='\t'
		if immediate :
			buff += 'd.%d\t' % (srcb)
		else:
			buff += 'r%d\t' % (srcb)
		if SIMULATE:
			old_value = self.REGISTER(dst)
			source_a = self.REGISTER(srca)
			new_value = old_value
			if immediate :
				source_b = srcb
			else:
				source_b = self.REGISTER(srcb)
			if shift == opcodes.OPCODE_BYTE_SHIFT_LEFT_1:
				source_b <<= 8
			elif shift == opcodes.OPCODE_BYTE_SHIFT_LEFT_2:
				source_b <<= 16
			elif shift == opcodes.OPCODE_BYTE_SHIFT_LEFT_3:
				source_b <<= 24
			elif shift == opcodes.OPCODE_BYTE_SHIFT_RIGHT_1:
				source_b >>= 8
			elif shift == opcodes.OPCODE_BYTE_SHIFT_RIGHT_2:
				source_b >>= 16
			elif shift == opcodes.OPCODE_BYTE_SHIFT_RIGHT_3:
				source_b >>= 24
			if invert:
				source_b = ~ source_b
			if op == opcodes.OPCODE_CODE_ADD:
				new_value = source_a + source_b
			elif op == opcodes.OPCODE_CODE_SUB:
				new_value = source_a - source_b
			elif op == opcodes.OPCODE_CODE_MULT:
				new_value = source_a * source_b
			elif op == opcodes.OPCODE_CODE_AND:
				new_value = source_a and source_b
			elif op == opcodes.OPCODE_CODE_OR:
				new_value = source_a or source_b
			else:
				new_value = source_a ^ source_b
			new_st = self.st & 0xFFFFFFF0
			if dst > 0:
				if not self.SET_REGISTER(dst,new_value):
					new_st |= OVF_FLAG
			if update_flags:
				if new_value == 0:
					new_st |= Z_FLAG
				if new_value & 0x80000000 != 0:
					new_st |= N_FLAG
				if new_value > 0xFFFFFFFF:
					new_st |= CY_FLAG
				if self.N_FLAG_IS_SET(new_st) != self.CY_FLAG_IS_SET(new_st):
					new_st |= OVF_FLAG
				self.st = new_st
				self.changes.append(" ST: 0x%08X " % (new_st))
			self.changes.append(" REG: r%d=0x%08X " % (dst,new_value))

		return buff

	def opcode_add (self,opcode,op):
		""" OPCODE = ALU """
		return self.disassembly_alu(opcode,op)       
	def opcode_sub (self,opcode,op):
		return self.disassembly_alu(opcode,op)       
	def opcode_and (self,opcode,op):
		return self.disassembly_alu(opcode,op)       
	def opcode_or (self,opcode,op):
		return self.disassembly_alu(opcode,op)        
	def opcode_xor (self,opcode,op):
		return disassembly_alu(opcode,op)       
	def opcode_mult (self,opcode,op):
		return self.disassembly_alu(opcode,op)  

	def opcode_ret (self,opcode,op):
		""" OPCODE = RET """
		pc = self.pc
		self.pc += 4
		print 'ret: 0x%x ' % (pc)
		if SIMULATE:
			ind = self.pc//4
			opcode = BitString(uint=self.code_segment[ind],length=32)
			self.pipe.opcode_ds1 = opcode
			self.pipe.pc_ds1 = self.pc
			ind += 1
			opcode = BitString(uint=self.code_segment[ind],length=32)
			self.pipe.opcode_ds2 = opcode
			self.pipe.pc_ds2 = self.pc + 4			
			self.pipe.clock = 2
			jump_address = self.pop_call_stack()
			self.stall_pc.delay_pc = jump_address
			self.pc = jump_address
		return (1,'ret') 

	def disassembly_ld (self,opcode,op):
		self.pc += 4
		buff = ''
		size = opcode[opcodes.ldOpcode['size'][0]:opcodes.ldOpcode['size'][1]].unpack('uint:2')[0]
		if size == opcodes.OPCODE_SIZE_16:
			buff += '16\t'
		elif size == opcodes.OPCODE_SIZE_32:
			buff += '32\t'
		elif size == opcodes.OPCODE_SIZE_64:
			buff += '64\t'
		else:
			buff += '8\t'
		dst = opcode[opcodes.ldOpcode['destination_register'][0]:opcodes.ldOpcode['destination_register'][1]].unpack('uint:5')[0]	
		buff += 'r%d\t' % (dst)
		direct = opcode[opcodes.ldOpcode['direct_or_index'][0]:opcodes.ldOpcode['direct_or_index'][1]].unpack('uint:1')[0]
		immediate = opcode[opcodes.ldOpcode['immediate_or_register'][0]:opcodes.ldOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		high = opcode[opcodes.ldOpcode['high_or_low'][0]:opcodes.ldOpcode['high_or_low'][1]].unpack('uint:1')[0]	
		if direct:
			immed = opcode[opcodes.ldOpcode['base_address'][0]:opcodes.ldOpcode['base_address'][1]].unpack('uint:5')[0]
			buff += 'r%d\t' % (immed)
			offset = opcode[opcodes.ldOpcode['offset'][0]:opcodes.ldOpcode['offset'][1]].unpack('uint:11')[0]
			if immed:
				buff += '0x%x\t' % (offset)
		else:
			if immediate: 
				immed = opcode[opcodes.ldOpcode['immediate'][0]:opcodes.ldOpcode['immediate'][1]].unpack('uint:16')[0]
				buff += '0x%x\t' % (immed)
			else:
				immed = opcode[opcodes.ldOpcode['base_address'][0]:opcodes.ldOpcode['base_address'][1]].unpack('uint:5')[0]
				buff += 'r%d\t' % (immed)
		if direct and not immed:
			if high :
				buff += 'high'
		if SIMULATE:
			if direct:
				if immed:
					if high:
						immed = ( immed & 0xffff0000 ) >> 16
					else:
						immed = immed & 0xffff0000 
					immed = immed & 0xfff8
					offset = offset & 0x7ff
					immed = (immed & 0x8000) + (immed + offset ) & 0x7fff
				else:
					if high:
						immed = ( immed & 0xffff0000 ) >> 16
					else:
						immed = immed & 0xffff0000
					immed = immed & 0xfff8
					r = ( offset >> 1 ) & 0x1f
					offset = self.REGISTER(r) & 0x7ff
					immed = (immed & 0x8000) + (immed + offset ) & 0x7fff
	
			else:				
				if high:
					immed = ( immed & 0xffff0000 ) >> 16
				else:
					immed = immed & 0xffff0000 
			if immed >= DATA_SEGMENT_SIZE:
				self.changes.append("ERROR: SRAM access violation on load/store from/to 0x%x" % (immed))
				return (0,buff)
			self.show_ram ("Before ld", immed )
			if op == opcodes.OPCODE_CODE_LD or op == opcodes.OPCODE_CODE_LDC:
				old_value = self.REGISTER(dst)
				old_value1 = self.REGISTER(dst + 1)
				if size == opcodes.OPCODE_SIZE_16:
					if op == opcodes.OPCODE_CODE_LDC:
						nw = self.READ_COMMON(immed,2)
					else:
						nw = self.READ_SRAM(immed,2)
				elif size == opcodes.OPCODE_SIZE_32:
					if op == opcodes.OPCODE_CODE_LDC:
						nw = self.READ_COMMON(immed,4)
					else:
						nw = self.READ_COMMON(immed,4)				
				elif size == opcodes.OPCODE_SIZE_64:
					if op == opcodes.OPCODE_CODE_LDC:
						nw = self.READ_COMMON(immed,4)				
						nw1 = self.READ_COMMON(immed+4,4)
					else:
						nw = self.READ_SRAM(immed,4)				
						nw1 = self.READ_SRAM(immed+4,4)
					if nw[0]:
						new_value1 = nw1[1]
				else:
					if op == opcodes.OPCODE_CODE_LDC:
						nw = self.READ_COMMON(immed,1)
					else:
						nw = self.READ_SRAM(immed,1)
				if nw[0]:
					new_value = nw[1]
					if dst > 0:
						self.SET_REGISTER(dst,new_value)
						self.changes.append( " REG: r%d=0x%08X " % (dst,new_value))
						if size == opcodes.OPCODE_SIZE_64:
							self.SET_REGISTER(dst+1,new_value1)
							self.changes.append( " REG: r%d=0x%08X " % (dst+1,new_value1))
				else:
					print ("EROOR")
			else: # store
				if size == opcodes.OPCODE_SIZE_8:
					new_value = self.REGISTER(dst) & 0xff
					if op == opcodes.OPCODE_CODE_STC:
						ov = self.WRITE_COMMON(immed,1,new_value)
					else:
						ov = self.WRITE_SRAM(immed,1,new_value)
				elif size == opcodes.OPCODE_SIZE_16:
					new_value = self.REGISTER(dst) & 0xffff
					if op == opcodes.OPCODE_CODE_STC:
						ov = self.WRITE_COMMON(immed,2,new_value)
					else:
						ov = self.WRITE_SRAM(immed,2,new_value)
				elif size == opcodes.OPCODE_SIZE_32:
					new_value = self.REGISTER(dst) 
					if op == opcodes.OPCODE_CODE_STC:
						ov = self.WRITE_COMMON(immed,4,new_value)
					else:
						ov = self.WRITE_SRAM(immed,4,new_value)
				else:
					new_value = self.REGISTER(dst)
					new_value1 = self.REGISTER(dst+1)
					if op == opcodes.OPCODE_CODE_STC:
						ov = self.WRITE_COMMON(immed,4,new_value)
						ov1 = self.WRITE_COMMON(immed+4,4,new_value1)
					else:
						ov = self.WRITE_SRAM(immed,4,new_value)
						ov1 = self.WRITE_SRAM(immed+4,4,new_value1)
					if ov1[0]:
						old_value1 = ov1[1]
				if ov[0]:
					old_value = ov[1]
					self.show_ram ("After st", immed )
					self.changes.append( " SRAM: word %08X=%08X " % (immed,new_value))
					if size == opcodes.OPCODE_SIZE_64:
						self.changes.append( " SRAM: word %08X=%08X  SRAM: word %08X=%08X " % (immed,new_value,immed+4,new_value1))
				else:'ERRROR'
		return buff

	def opcode_ld (self,opcode,op):
		""" OPCODE = LD """
		buff = 'ld' + self.disassembly_ld(opcode,op)
		return (1,buff) 

	def opcode_st (self,opcode,op):
		""" OPCODE = ST """
		buff = 'st' + self.disassembly_ld(opcode,op)
		return (1,buff)  

	def opcode_ldc (self,opcode,op):
		""" OPCODE = LDC """
		buff = 'ldc' + self.disassembly_ld(opcode,op)
		return (1,buff) 

	def opcode_stc (self,opcode,op):
		""" OPCODE = STC """
		buff = 'stc' + self.disassembly_ld(opcode,op)
		return (1,buff)

	def set_semaphore(self,ind,new_value,cnt):
		if self.simulator.semaphores[ind].status and self.simulator.semaphores[ind].owner_runner == self:
			if cnt == 1:
				value = new_value | 0x01
			elif cnt == 2:
				value = new_value | 0x0100
			elif cnt == 3:
				value = new_value | 0x010000
			else:
				value = new_value | 0x01000000
		else:
			if self.simulator.semaphores[ind].status:
				self.simulator.semaphores[ind].enable_wakeup = True
			if cnt == 1:
				value = new_value & 0xFE
			elif cnt == 2:
				value = new_value & 0xFEFF
			elif cnt == 3:
				value = new_value & 0xFEFFFF
			else:
				value = new_value & 0xFEFFFF
			
		return value
	
	def opcode_ldio (self,opcode,op):
		""" OPCODE = LDIO """
		self.pc += 4
		buff = 'ldio\t'
		size = opcode[opcodes.ldioOpcode['size'][0]:opcodes.ldioOpcode['size'][1]].unpack('uint:2')[0]
		if size == opcodes.OPCODE_SIZE_16:
			buff += '16\t'
		elif size == opcodes.OPCODE_SIZE_32:
			buff += '32\t'
		else:
			buff += '8\t'
		dst = opcode[opcodes.ldioOpcode['destination_register'][0]:opcodes.ldioOpcode['destination_register'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		immediate = opcode[opcodes.ldioOpcode['immediate_or_register'][0]:opcodes.ldioOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			io_address = opcode[opcodes.ldioOpcode['immediate'][0]:opcodes.ldioOpcode['immediate'][1]].unpack('uint:10')[0]
			buff += '0x%x\t' % (io_address)
		else:
			io_address = opcode[opcodes.ldioOpcode['address'][0]:opcodes.ldioOpcode['address'][1]].unpack('uint:5')[0]
			buff += 'r%d\t' % (io_address)
			high = opcode[opcodes.ldioOpcode['high_or_low'][0]:opcodes.ldioOpcode['high_or_low'][1]].unpack('uint:1')[0]
		if SIMULATE:
			if not immediate:
				if high:
					buff += 'high'
					io_address = (io_address & 0xFFFF0000) >> 16
				else:
					io_address = io_address & 0x0000ffff		
			io_address = io_address & 0x3ff
			if size == opcodes.OPCODE_SIZE_8:
				tp = self.READ_IO(io_address,1)

				if tp[0]:
					new_value = tp[1]
					if io_address == self.simulator.SEMAPHORE_0_STATUS or \
					io_address == self.simulator.SEMAPHORE_1_STATUS or \
					io_address == self.simulator.SEMAPHORE_2_STATUS or \
					io_address == self.simulator.SEMAPHORE_3_STATUS or \
					io_address == self.simulator.SEMAPHORE_4_STATUS or \
					io_address == self.simulator.SEMAPHORE_5_STATUS or \
					io_address == self.simulator.SEMAPHORE_6_STATUS or \
					io_address == self.simulator.SEMAPHORE_7_STATUS:
						ind = io_address - self.simulator.SEMAPHORE_0_STATUS
						if self.simulator.semaphores[ind].status:
							new_value = new_value & 0xfe
						elif self.simulator.semaphores[ind].owner_runner == self:
							new_value = new_value | 0x01
						else:
							new_value =  new_value & 0xfe
							self.simulator.semaphores[ind].thread = self.scheduler.current_context
							self.simulator.semaphores[ind].runner = self
							self.simulator.semaphores[ind].wakeup = True
			elif size == opcodes.OPCODE_SIZE_16:
				tp = self.READ_IO(io_address,2)
				if tp[0]:
					new_value = tp[1]
					if io_address == self.simulator.SEMAPHORE_0_STATUS or \
					io_address == self.simulator.SEMAPHORE_2_STATUS or \
					io_address == self.simulator.SEMAPHORE_4_STATUS or \
					io_address == self.simulator.SEMAPHORE_6_STATUS:				
						ind = io_address - self.simulator.SEMAPHORE_0_STATUS					
						new_value = self.set_semaphore(ind,new_value,1)
						new_value = self.set_semaphore(ind+1,new_value,2)					
			else:
				tp = self.READ_IO(io_address,4)
				if tp[0]:
					new_value = tp[1]
					if io_address == self.simulator.SEMAPHORE_0_STATUS or \
					io_address == self.simulator.SEMAPHORE_4_STATUS:
						ind = io_address - self.simulator.SEMAPHORE_0_STATUS				
						new_value = self.set_semaphore(ind,new_value,1)
						new_value = self.set_semaphore(ind+1,new_value,2)
						new_value = self.set_semaphore(ind+2,new_value,3)
						new_value = self.set_semaphore(ind+3,new_value,4)
					elif io_address == CNTR_LOCK:
						new_value |= 0x100
						if self.counters_lock:
							if self.hw_accelerators.cntup_count == 0:
								new_value |= 0x40000000
							else:
								new_value &= ~0x100
						if self.co_runner:
							if self.co_runner.counters_lock:
								if self.co_runner.hw_accelerators.cntup_count == 0:
									new_value |= 0x80000000
								else:
									new_value &= ~0x100
			if io_address == CAM_RESULT_IO_ADDRESS0 or \
			io_address == CAM_RESULT_IO_ADDRESS1 or \
			io_address == CAM_RESULT_IO_ADDRESS2 or \
			io_address == CAM_RESULT_IO_ADDRESS3:
				if self.hw_accelerators.ramman.ready == 0:
					self.stall_pc.enter_stall = self.simulator.clock
					self.stall = STALL_LDIO
					self.stall_pc.pc = self.pc
					self.changes.append( "  STALL: 1 " )
			elif io_address == HASH_RESULT_IO_ADDRESS0 or \
			io_address == HASH_RESULT_IO_ADDRESS1 or \
			io_address == HASH_RESULT_IO_ADDRESS2 or \
			io_address == HASH_RESULT_IO_ADDRESS3:
				index = self.hw_accelerators.hash_out
				if self.hw_accelerators.hash[index].valid == 1 and \
				self.hw_accelerators.hash[index].ready == 0 and \
				io_address == HASH_RESULT_IO_ADDRESS0 + self.hw_accelerators.hash[index].res_slot * 4:
					self.stall_pc.enter_stall = self.simulator.clock
					self.stall = STALL_LDIO
					self.stall_pc.pc = self.pc
					self.changes.append( "  STALL: 1 ")
			if self.stall != STALL_LDIO:
				old_value = dst
				if dst > 0:
					self.SET_REGISTER(dst,new_value)
					new_value = self.REGISTER(dst)
			else:
				old_value = 0
				new_value = 0
			if dst == 0:
				new_value = 0
			if old_value != new_value:
				self.changes.append( "  REG: r%d=%08X " % (dst,new_value))	
		return (1,buff)

	def set_extended_timer(self,ind,new_value):
		self.timers[ind].status = new_value & 1 
		self.timers[ind].mode = ( new_value >> 1 ) & 1 
		self.timers[ind].thread = ( new_value >> 2 ) & 0x1f 
		self.timers[ind].urgent = ( new_value >> 7 ) & 1
		
	def opcode_stio (self,opcode,op):
		""" OPCODE = STIO """
		self.pc += 4
		buff = 'stio\t'
		size = opcode[opcodes.ldioOpcode['size'][0]:opcodes.ldioOpcode['size'][1]].unpack('uint:2')[0]
		if size == opcodes.OPCODE_SIZE_16:
			buff += '16\t'
		elif size == opcodes.OPCODE_SIZE_32:
			buff += '32\t'
		else:
			buff += '8\t'
		src = opcode[opcodes.ldioOpcode['source_address'][0]:opcodes.ldioOpcode['source_address'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (src)
		immediate = opcode[opcodes.ldioOpcode['immediate_or_register'][0]:opcodes.ldioOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			io_address = opcode[opcodes.ldioOpcode['immediate'][0]:opcodes.ldioOpcode['immediate'][1]].unpack('uint:10')[0]
			buff += '0x%x\t' % (io_address)
		else:
			io_address = opcode[opcodes.ldioOpcode['address'][0]:opcodes.ldioOpcode['address'][1]].unpack('uint:5')[0]
			buff += 'r%d\t' % (io_address)
			high = opcode[opcodes.ldioOpcode['high_or_low'][0]:opcodes.ldioOpcode['high_or_low'][1]].unpack('uint:1')[0]
		if SIMULATE:
			if not immediate:
				if high:
					buff += 'high'
					io_address = (io_address & 0xFFFF0000) >> 16
				else:
					io_address = io_address & 0x0000ffff		
			io_address = io_address & 0x3ff
			new_value = self.REGISTER(src)
			old_value = new_value
			ioaddr = io_address & 0xFFFFFFFC
			if ioaddr == PERIPHERAL_CTS or \
			ioaddr == LKUP0_RESULT or \
			ioaddr == LKUP1_RESULT or \
			ioaddr == LKUP2_RESULT or \
			ioaddr == LKUP3_RESULT or \
			ioaddr == DDR_LKUP0_RESULT or \
			ioaddr == DDR_LKUP1_RESULT or \
			ioaddr == DDR_LKUP2_RESULT or \
			ioaddr == DDR_LKUP3_RESULT or \
			ioaddr == RAMRD_RESULT_0 or \
			ioaddr == RAMRD_RESULT_1 or \
			ioaddr == RAMRD_RESULT_2 or \
			ioaddr == RAMRD_RESULT_3 or \
			ioaddr == PARSER_SUM or \
			ioaddr == PARSER_CHKSUM or \
			ioaddr == MS_CNT_VAL:
				return (1,buff)
			if size == opcodes.OPCODE_SIZE_8:
				tp = self.READ_IO( io_address, 1 )
				if tp[0]:
					old_value = tp[1]
					if io_address == FW_CONTROL + 1 or  \
					io_address == FW_CONTROL + 2 or  \
					io_address == FW_CONTROL + 3 or  \
					io_address == LKUP0_FWCFG + 3 or  \
					io_address == LKUP1_FWCFG + 3 or  \
					io_address == LKUP_CAM_FWCFG_0 + 2 or  \
					io_address == LKUP_CAM_FWCFG_0 + 3 or  \
					io_address == LKUP_CAM_FWCFG_1 + 2 or  \
					io_address == LKUP_CAM_FWCFG_1 + 3 or  \
					io_address == TIMER_CONTROL_IO_ADDRESS + 3 or  \
					io_address == DDR_OFFSET + 2 or  \
					io_address == DDR_OFFSET + 3 or  \
					io_address == FW_WAKEUP_REG + 2 or  \
					io_address == FW_WAKEUP_REG + 3:
						return (1,buff)
					elif io_address == TIMER_CONTROL_IO_ADDRESS:
						new_value &= 0x03
						self.timer.reset = new_value & 1
						self.timer.pause = ( new_value >> 1 ) & 1
						if self.timer.reset == 1:
							self.timer.value = 0
					elif io_address == TIMER_CONTROL_IO_ADDRESS + 1:
						new_value &= 0x01
						self.timer.t0_width = new_value & 1
						if self.timer.t0_width:
							self.timers[2].enable = 1
						else:
							self.timers[2].enable = 0
					elif io_address == TIMER_CONTROL_IO_ADDRESS + 2:
						new_value &= 0x01
						self.timer.t1_width = new_value & 1
						if self.timer.t1_width:
							self.timers[3].enable = 1
						else:
							self.timers[3].enable = 0
					elif io_address == TIMER_EXTEND_IO_ADDRESS:
						self.set_extended_timer(0,new_value)
					elif io_address == TIMER_EXTEND_IO_ADDRESS + 1:
						self.set_extended_timer(1,new_value)
					elif io_address == TIMER_EXTEND_IO_ADDRESS + 2:
						self.set_extended_timer(2,new_value)
					elif io_address == TIMER_EXTEND_IO_ADDRESS + 3:
						self.set_extended_timer(3,new_value)
					elif io_address == self.simulator.SEMAPHORE_0_STATUS or \
					io_address == self.simulator.SEMAPHORE_7_STATUS or \
					io_address == self.simulator.SEMAPHORE_1_STATUS or \
					io_address == self.simulator.SEMAPHORE_2_STATUS or \
					io_address == self.simulator.SEMAPHORE_3_STATUS or \
					io_address == self.simulator.SEMAPHORE_4_STATUS or \
					io_address == self.simulator.SEMAPHORE_5_STATUS or \
					io_address == self.simulator.SEMAPHORE_6_STATUS:
						new_value &= 0x07
						ind = io_address - SEMAPHORE_0_STATUS
						if new_value & 0x04 == 0x04:
							self.simulator.semaphores[ind].enable_wakeup = True
						else:
							self.simulator.semaphores[ind].enable_wakeup = False
						if new_value & 0x02 == 0x02:
							self.simulator.semaphores[ind].status = False
						elif new_value & 0x01 == 0x01:
							if self.simulator.semaphores[ind].status == False:
								self.simulator.semaphores[ind].status = True
								self.simulator.semaphores[ind].owner_runner = self
					elif io_address == FW_CONTROL:
						new_value &= 0x01
					elif io_address == CNTR_LOCK:
						new_value &= 0x03
					elif io_address == DDR_OFFSET + 1:
						new_value &= 0x3F
					elif io_address == FW_INT_CTRL0 + 2 or \
					io_address == FW_INT_CTRL0 + 3 or \
					io_address == FW_INT_CTRL1 or \
					io_address == FW_INT_CTRL1 + 1 or \
					io_address == FW_INT_CTRL1 + 2 or \
					io_address == FW_INT_CTRL1 + 3 or \
					io_address == FW_INT_CTRL2 or \
					io_address == FW_INT_CTRL2 + 1 or \
					io_address == FW_INT_CTRL2 + 2 or \
					io_address == FW_INT_CTRL2 + 3 :
						new_value &= 0x01
					elif io_address == FW_WAKEUP_REG + 1:
						new_value &= 0x01
					elif io_address == LKUP_CAM_FWCFG_0 + 1 or io_address == LKUP_CAM_FWCFG_0 + 1:
						new_value &= 0x01
					self.WRITE_IO(io_address,1,new_value)
			elif size == opcodes.OPCODE_SIZE_16:
				tp = self.READ_IO(io_address,2)
				if tp[0]:
					old_value = tp[1]
					if io_address == FW_CONTROL + 2 or \
					io_address == LKUP_CAM_FWCFG_0 + 2 or \
					io_address == LKUP_CAM_FWCFG_1 + 2 or \
					io_address == DDR_OFFSET + 2 or \
					io_address == FW_WAKEUP_REG + 2:
						return (1,buff)
					if io_address == TIMER_CONTROL_IO_ADDRESS:
						new_value &= 0x0103
						self.timer.reset = new_value & 1
						self.timer.pause = ( new_value >> 1 ) & 1 
						self.timer.t0_width = ( new_value >> 8 ) & 1
						if self.timer.reset == 1:
							self.timer.reset = 0
						if self.timer.t0_width:
							self.timers[2].enable = 1
						else:
							self.timers[2].enable = 0
						temp = new_value
						for i in range(2):
							self.set_extended_timer(i,temp)
							temp = temp >> 8
					elif io_address == TIMER_CONTROL_IO_ADDRESS + 2:
						new_value &= 0x0101
						if self.timer.t1_width:
							self.timers[3].enable = 1
						else:
							self.timers[3].enable = 0
						temp = new_value
						for i in range(2,4):
							self.set_extended_timer(i,temp)
							temp = temp >> 8
					elif io_address == TIMER_0_VAL_IO_ADDRESS:
						self.timers[0].origvalue = new_value & 0xffff
						self.timers[0].value = ( self.timer.value + new_value ) & 0xffff
					elif io_address == TIMER_1_VAL_IO_ADDRESS:
						self.timers[1].origvalue = new_value & 0xffff
						self.timers[1].value = ( self.timer.value + new_value ) & 0xffff
					elif io_address == TIMER_0_VAL_IO_ADDRESS + 2:
						self.timers[2].origvalue = new_value & 0xffff
						self.timers[2].value = ( self.timer.value + new_value ) & 0xffff
					elif io_address == TIMER_1_VAL_IO_ADDRESS + 2:
						self.timers[3].origvalue = new_value & 0xffff
						self.timers[3].value = ( self.timer.value + new_value ) & 0xffff
					elif io_address == self.simulator.SEMAPHORE_0_STATUS or \
					io_address == self.simulator.SEMAPHORE_2_STATUS or \
					io_address == self.simulator.SEMAPHORE_4_STATUS or \
					io_address == self.simulator.SEMAPHORE_6_STATUS :
						new_value &= 0x0707
						ind = io_address - SEMAPHORE_0_STATUS
						if new_value & 0x01 == 0:
							self.simulator.semaphores[ind].status = False
						else:
							if not self.simulator.semaphores[ind].status:
								self.simulator.semaphores[ind].status = True
								self.simulator.semaphores[ind].owner_runner = self
						if new_value & 0x0100 == 0:
							self.simulator.semaphores[ind + 1].status = False
						else:
							if not self.simulator.semaphores[ind].status:
								self.simulator.semaphores[ind + 1].status = True
								self.simulator.semaphores[ind + 1].owner_runner = self
					elif io_address == FW_CONTROL:
						new_value &= 0x0001
					elif io_address == CNTR_LOCK:
						new_value &= 0x0003
					elif io_address == DDR_OFFSET + 1:
						new_value &= 0x3FFF
					elif io_address == FW_INT_CTRL0 + 2 or \
					io_address == FW_INT_CTRL1 + 2 or \
					io_address == FW_INT_CTRL2 + 2 or \
					io_address == FW_INT_CTRL1 or \
					io_address == FW_INT_CTRL2:  
						new_value &= 0x0101
					elif io_address == FW_WAKEUP_REG:
						new_value &= 0x01FF
					elif io_address == LKUP_CAM_FWCFG_0 or io_address == LKUP_CAM_FWCFG_1:
						new_value &= 0x01FF
					elif io_address == LKUP0_FWCFG + 2 or io_address == LKUP1_FWCFG + 2:
						new_value &=  0x00FF
					self.WRITE_IO(io_address,2,new_value)
			else:
				tp = self.READ_IO(io_address,4)
				if tp[0]:
					old_value = tp[1]
					if io_address == TIMER_CONTROL_IO_ADDRESS:
						new_value &= 0x00010103
						self.timer.reset = ( new_value & 1 ) 
						self.timer.pause = ( new_value >> 1 ) & 1 
						self.timer.t0_width = ( new_value >> 8 ) & 1 
						self.timer.t1_width = ( new_value >> 16 ) & 1 
						if self.timer.reset == 1 :
						    self.timer.value = 0 ;
						if self.timer.t0_width :
						    self.timers[2].enable = 1
						if self.timer.t1_width:
						    self.timers[3].enable = 1
					elif io_address == TIMER_EXTEND_IO_ADDRESS:
						temp = new_value
						for i in range(4):
							self.set_extended_timer(i,temp)
							temp = temp >> 8
					elif io_address == TIMER_0_VAL_IO_ADDRESS:
						temp = new_value
						if self.timer.t0_width:
							for i in range(0,4,2):
								self.timers[i].origvalue = temp & 0xffff
								self.timers[i].value = ( self.timer.value + temp ) & 0xffff
								temp = temp >> 16
						else:
							self.timers[0].origvalue = temp 
							self.timers[0].value = self.timer.value + temp
					elif io_address == TIMER_1_VAL_IO_ADDRESS:
						temp = new_value
						if self.timer.t0_width:
							for i in range(1,4,2):
								self.timers[i].origvalue = temp & 0xffff
								self.timers[i].value = ( self.timer.value + temp ) & 0xffff
								temp = temp >> 16
						else:
							self.timers[1].origvalue = temp 
							self.timers[1].value = self.timer.value + temp
					elif io_address == self.simulator.SEMAPHORE_0_STATUS or io_address == self.simulator.SEMAPHORE_4_STATUS:
						new_value &= 0x07070707
						ind = io_address - self.simulator.SEMAPHORE_0_STATUS
						if new_value & 0x01 == 0:
							self.simulator.semaphores[ind].status = False
						else:
							if not self.simulator.semaphores[ind].status:
								self.simulator.semaphores[ind].status = True
								self.simulator.semaphores[ind].owner_runner = self
						if new_value & 0x0100 == 0:
							self.simulator.semaphores[ind].status = False
						else:
							if not self.simulator.semaphores[ind+1].status:
								self.simulator.semaphores[ind+1].status = True
								self.simulator.semaphores[ind+1].owner_runner = self
						if new_value & 0x010000 == 0:
							self.simulator.semaphores[ind].status = False
						else:
							if not self.simulator.semaphores[ind+2].status:
								self.simulator.semaphores[ind+2].status = True
								self.simulator.semaphores[ind+2].owner_runner = self
						if new_value & 0x01000000 == 0:
							self.simulator.semaphores[ind].status = False
						else:
							if not self.simulator.semaphores[ind+3].status:
								self.simulator.semaphores[ind+3].status = True
								self.simulator.semaphores[ind+3].owner_runner = self
					elif io_address == FW_CONTROL:
						new_value &= 0x00000001
					elif io_address == LKUP0_FWCFG or io_address == LKUP1_FWCFG:
						new_value &= 0x00FFFFFF
					elif io_address == LKUP_CAM_FWCFG_0 or io_address == LKUP_CAM_FWCFG_1:
						new_value &= 0x000001FF
					elif io_address == DDR_OFFSET:
						new_value &= 0x0000FFFF
					elif io_address == DDR_OFFSET + 1:
						new_value &= 0x00003FFF
					elif io_address == CNTR_LOCK:
						self.counters_lock = new_value & 0x01
						if self.co_runner:
							if  new_value & 0x03 == 0x03:
								self.co_runner.counters_lock = 1
							else:
								self.co_runner.counters_lock = 0
					elif io_address == FW_INT_CTRL0:
						new_value &= 0x0101FFFF
					elif io_address == FW_INT_CTRL1 or io_address == FW_INT_CTRL2:
						new_value &= 0x01010101
					elif io_address == FW_WAKEUP_REG:
						new_value &= 0x000001FF
				self.WRITE_IO(io_address,4,new_value)
				if io_address == SCHEDULER_IO_ADDRESS:
					thread = new_value & 0x03
					if thread == 2:
						thread = self.scheduler.current_context
					elif thread == 1:
						thread = ( new_value & 0x000001F0 ) >> 4
					if new_value & 0x00000004 >> 2 == 1:
						self.scheduler.async_enable [ thread ] = 1 
						enable = "enable"
					else:
						enable = ""
					if new_value & 0x00000008 >> 3 == 1:
						self.scheduler.async_wakeup_request_urgent [ thread ] = 1 ;
						urgent = "urgent" ;
					else:
						self.scheduler.async_wakeup_request_normal [ thread ] = 1 ;
						urgent = "normal"
					self.show_scheduler ( "after stio 0x18" )
				#if size == opcodes.OPCODE_SIZE_8 and io_address <= INT11_8_ADDR and io_address >= INT3_0_ADDR:
				#	cpu_interrupt.type = h_to_nl(CPU_MESSAGE_TYPE_INTERRUPT) ;
				#	cpu_interrupt.message.interrupt.vector = h_to_nl(io_address & 0x0F ) ;
				#	 send_cpu(& cpu_interrupt);
			if old_value != new_value:
				self.changes.append( "  IO: %d %02X=%08X " % (size, io_address, new_value))
			
		return (1,buff)
	def show_scheduler(self,text):
		print text
		
	def opcode_mov (self,opcode,op):
		""" OPCODE = MOV """
		self.pc += 4
		buff = 'mov\t'		
		dst = opcode[opcodes.movOpcode['destination_register'][0]:opcodes.movOpcode['destination_register'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		immediate = opcode[opcodes.movOpcode['immediate_value'][0]:opcodes.movOpcode['immediate_value'][1]].unpack('uint:16')[0]
		buff += '0x%x\t' % (dst)
		high = opcode[opcodes.movOpcode['high_or_low'][0]:opcodes.movOpcode['high_or_low'][1]].unpack('uint:1')[0]
		clear = opcode[opcodes.movOpcode['clear'][0]:opcodes.movOpcode['clear'][1]].unpack('uint:1')[0]
		if high:
			buff += '<<16\t'
		if clear:
			buff += 'clear'
		if SIMULATE:
			old_value = self.REGISTER(dst)
			new_value = old_value
			if high:
				immediate <<= 16
			if clear:
				new_value = immediate
			else:
				if high:
					new_value = ( immediate & 0xffff0000 ) | ( old_value & 0x0000ffff )
				else:
					new_value = ( immediate & 0x0000ffff ) | ( old_value & 0xffff0000 )

			if dst > 0:
				self.SET_REGISTER(dst,new_value)
				new_value = self.REGISTER(dst)
			else:
				new_value = 0
			if old_value != new_value:
				self.changes.append(" REG: r%d=%08X " % (dst,new_value))

		return (1,buff) 

	def opcode_shift (self,opcode,op):
		""" OPCODE = SHIFT """
		self.pc += 4
		buff = 'shift\t'
		dst = opcode[opcodes.shiftOpcode['destination_register'][0]:opcodes.shiftOpcode['destination_register'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		mode = opcode[opcodes.shiftOpcode['mode'][0]:opcodes.shiftOpcode['mode'][1]].unpack('uint:2')[0]
		if mode == opcodes.OPCODE_SHIFT_MODE_ASR:
			buff += 'asr\t'
		elif mode == opcodes.OPCODE_SHIFT_MODE_ASL:
			buff += 'asl\t'
		elif mode == opcodes.OPCODE_SHIFT_MODE_RSR:
			buff += 'rsr\t'
		else:
			buff += 'rsr16\t'
		srca = opcode[opcodes.shiftOpcode['source_a'][0]:opcodes.shiftOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srca)
		srcb = opcode[opcodes.shiftOpcode['source_b_or_immediate'][0]:opcodes.shiftOpcode['source_b_or_immediate'][1]].unpack('uint:5')[0]
		immediate = opcode[opcodes.shiftOpcode['immediate_or_register'][0]:opcodes.shiftOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:			
			buff += 'd.%d\t' % (srcb)
		else:
			buff += 'r%d\t' % (srcb) 
		update = opcode[opcodes.shiftOpcode['update_flags'][0]:opcodes.shiftOpcode['update_flags'][1]].unpack('uint:1')[0]
		if update:
			buff += 'update_flags'
		if SIMULATE:
			old_value = self.REGISTER(dst)
			new_value = old_value
			source_1 = self.REGISTER(srca)
			if immediate:
				source_2 = srcb
			else:
				source_2 = self.REGISTER(srcb)
			if mode == opcodes.OPCODE_SHIFT_MODE_ASL:
				new_value = source_1 << source_2
				mask = 0xffffffff << ( 32 - source_2)
			elif mode == opcodes.OPCODE_SHIFT_MODE_ASR:
				new_value = source_1
				sign = source_1 & 0x80000000
				i = source_2
				while i > 0:
					new_value >>= 1
					new_value |= sign
					i -= 1
			elif mode == opcodes.OPCODE_SHIFT_MODE_RSR16:
				new_value = source_1
				temp = source_1 & 0xffff
				i = source_2
				while i > 0:
					lsb = temp & 1
					temp >>= 1
					temp |= lsb << 15
					i -= 1
				new_value = temp | ( old_value & 0xffff0000 )
			if dst > 0:
				self.SET_REGISTER(dst,new_value)
				new_value = self.REGISTER(dst)
			else:
				new_value = 0
			if old_value != new_value:
				self.changes.append(" REG: r%d=%08X " % (dst,new_value))
		return (1,buff)

	def opcode_extract (self,opcode,op):
		""" OPCODE = EXTRACT """
		self.pc += 4
		buff = 'extract\t'
		dst = opcode[opcodes.insertOpcode['destination_register'][0]:opcodes.insertOpcode['destination_register'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		srca = opcode[opcodes.insertOpcode['source_a'][0]:opcodes.insertOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srca)
		off = opcode[opcodes.insertOpcode['offset'][0]:opcodes.insertOpcode['offset'][1]].unpack('uint:5')[0]
		buff += 'd.%d\t' % (off)
		width = opcode[opcodes.insertOpcode['width'][0]:opcodes.insertOpcode['width'][1]].unpack('uint:5')[0]
		buff += 'd.%d\t' % (width)
		if SIMULATE:
			old_value = self.REGISTER(dst)
			new_value = old_value
			mask = 0
			for i in range(width) :
				mask <<= 1
				mask |= (1 << off )
			new_value = ( self.REGISTER(srca) & mask ) << off 
			if dst > 0:
				self.SET_REGISTER(dst,new_value)
				new_value = self.REGISTER(dst)
			else:
				new_value = 0
			if old_value != new_value:
				self.changes.append(" REG: r%d=%08X " % (dst,new_value))
		
		return (1,buff)

	def opcode_insert (self,opcode,op):
		""" OPCODE = INSERT """
		self.pc += 4
		buff = 'insert\t'
		dst = opcode[opcodes.insertOpcode['destination_register'][0]:opcodes.insertOpcode['destination_register'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (dst)
		srca = opcode[opcodes.insertOpcode['source_a'][0]:opcodes.insertOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\t' % (srca)
		off = opcode[opcodes.insertOpcode['offset'][0]:opcodes.insertOpcode['offset'][1]].unpack('uint:5')[0]
		buff += 'd.%d\t' % (off)
		width = opcode[opcodes.insertOpcode['width'][0]:opcodes.insertOpcode['width'][1]].unpack('uint:5')[0]
		buff += 'd.%d\t' % (width)
		if SIMULATE:
			old_value = self.REGISTER(dst)
			new_value = old_value
			mask = 0
			for i in range(width) :
				mask <<= 1
				mask |= (1 << off )
			new_value &= ~ mask
			new_value |= ( self.REGISTER(srca) << off ) & mask
			if dst > 0:
				self.SET_REGISTER(dst,new_value)
				new_value = self.REGISTER(dst)
			else:
				new_value = 0
			if old_value != new_value:
				self.changes.append(" REG: r%d=%08X " % (dst,new_value))
		
		return (1,buff) 
	def opcode_ctxswap (self,opcode,op):
		""" OPCODE = CTX_SWAP """
		pc = self.pc
		self.pc += 4
		buff = 'ctx_swap\t'
		update = opcode[opcodes.ctxswapOpcode['update_r16'][0]:opcodes.ctxswapOpcode['update_r16'][1]].unpack('uint:1')[0]
		if update:
			immed = opcode[opcodes.ctxswapOpcode['immediate_value'][0]:opcodes.ctxswapOpcode['immediate_value'][1]].unpack('uint:16')[0]
			buff += '0x%x\t' % (immed)
		save = opcode[opcodes.ctxswapOpcode['save'][0]:opcodes.ctxswapOpcode['save'][1]].unpack('uint:1')[0]
		async = opcode[opcodes.ctxswapOpcode['async_en'][0]:opcodes.ctxswapOpcode['async_en'][1]].unpack('uint:1')[0]
		if not save:
			buff += 'dont_save'
		elif async:
			buff += 'async_en'
		if SIMULATE:
			ind = self.pc//4
			opcode = BitString(uint=self.code_segment[ind],length=32)
			self.execute_opcode(opcode,0)
			if self.stall != STALL_NORMAL:
				self.stall_pc.delay_pc = self.pc
				print 'exit 1 %d' % (self.stall)
				return (1,buff)
			ind = self.pc//4
			opcode = BitString(uint=self.code_segment[ind],length=32)
			self.execute_opcode(opcode,0)
			if self.stall != STALL_NORMAL:
				self.stall_pc.delay_pc = self.pc
				return (1,buff)
			if update:
				self.private_registers[16] = (self.private_registers[16] & 0xffff) | \
				(immed << 16 )
				if self.scheduler.next_context_valid == 0:
					self.changes.append(" REG: r16=%08X " % (self.private_registers[16]))
			if async:
				self.scheduler.async_enable[self.scheduler.current_context] = 1
			self.st = 0
			if self.scheduler.next_context_valid == 1:
				for r in range(NUMBER_OF_PRIVATE_REGISTERS):
					ind = self.scheduler.current_context*NUMBER_OF_PRIVATE_REGISTERS + r
					if save:
						self.context_segment[ind] = self.private_registers[r] 
					self.changes.append(" REG: r%d=%08X " % (reg,self.private_registers[reg]))
				self.scheduler.previous_context = self.scheduler.current_context
				self.scheduler.current_context = self.scheduler.next_context
				if self.scheduler.async_enable[self.scheduler.next_context] == 1:
					self.scheduler.async_enable[self.scheduler.next_context] = 0
					self.scheduler.async_wakeup_request_normal[self.scheduler.next_context] = 0
					self.scheduler.async_wakeup_request_urgent[self.scheduler.next_context] = 0
					self.scheduler.sync_wakeup_request[self.scheduler.next_context] = 0
				else:
					self.scheduler.sync_wakeup_request[self.scheduler.next_context] = 0
				self.scheduler.next_context_valid = 0
				self.pc = (self.private_registers[16] >> 16 ) & PC_MASK
				self.changes.append(" THREAD: %08X " % (self.scheduler.current_context))
			else:
				self.stall_pc.enter_stall = self.simulator.clock
				self.stall = STALL_NO_CONTEXT
				self.scheduler.save_context = save
				self.changes.append(" STALL: 1 ")
			self.show_scheduler("after ctx_swap")
		return (1,buff)
	
	def opcode_hash (self,opcode,op):
		self.pc += 4
		buff = 'hash\t'
		srcc = opcode[opcodes.hashOpcode['source_c'][0]:opcodes.hashOpcode['source_c'][1]].unpack('uint:5')[0]
		srca = opcode[opcodes.hashOpcode['source_a'][0]:opcodes.hashOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\tr%d\t' % ( srcc,srca)
		ks = opcode[opcodes.hashOpcode['ks'][0]:opcodes.hashOpcode['ks'][1]].unpack('uint:1')[0]
		sa = opcode[opcodes.hashOpcode['sa'][0]:opcodes.hashOpcode['sa'][1]].unpack('uint:1')[0]		
		if not ks:
			buff += '48bit\t'
		else:
			buff += '60bit\t'
		if sa:
			buff += 'src\t'
		else:
			buff += 'dst\t'
		res_slot = opcode[opcodes.hashOpcode['res_slot'][0]:opcodes.hashOpcode['res_slot'][1]].unpack('unit:3')[0]
		table = opcode[opcodes.hashOpcode['table'][0]:opcodes.hashOpcode['table'][1]].unpack('unit:2')[0]
		buff += 'd.%d\td.%d\t' % (res_slot,table)
		invoke = opcode[opcodes.hashOpcode['invoke'][0]:opcodes.hashOpcode['invoke'][1]].unpack('unit:1')[0]
		rq = opcode[opcodes.hashOpcode['rq'][0]:opcodes.hashOpcode['rq'][1]].unpack('unit:1')[0]
		cs = opcode[opcodes.hashOpcode['cs'][0]:opcodes.hashOpcode['cs'][1]].unpack('unit:1')[0]
		update = opcode[opcodes.hashOpcode['update_r16'][0]:opcodes.hashOpcode['update_r16'][1]].unpack('unit:1')[0]
		if invoke:
			buff += 'invoke\t'
		if rq:
			buff += 'refresh\t'
		if cs:
			buff += 'ctx_swap\t'
		if update:
			buff += 'update'						
		return (1,buff)
	
	def opcode_ramman (self,opcode,op):
		self.pc += 4
		""" OPCODE = CRCCALC and CAM_LKP """
		srca = opcode[opcodes.crcOpcode['source_a'][0]:opcodes.crcOpcode['source_a'][1]].unpack('uint:5')[0]
		srcc = opcode[opcodes.crcOpcode['source_c'][0]:opcodes.crcOpcode['source_c'][1]].unpack('uint:5')[0]
		typ = opcode[opcodes.crcOpcode['type'][0]:opcodes.crcOpcode['type'][1]].unpack('uint:1')[0]
		immediate = opcode[opcodes.crcOpcode['immediate_or_register'][0]:opcodes.crcOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if typ == 1:
			buff = 'cam_lkp\t'
		else:
			buff = 'crc32\t'
			srcb = opcode[opcodes.crcOpcode['source_b_or_immediate'][0]:opcodes.crcOpcode['source_b_or_immediate'][1]].unpack('uint:8')[0]
		buff += 'r%d\t' % (srca)
		common = opcode[opcodes.crcOpcode['common_or_private'][0]:opcodes.crcOpcode['common_or_private'][1]].unpack('uint:1')[0]
		if typ == 0:
			if immediate:
				buff += '0x%x\tr%d\t' % (srcb,srcc)
			else:
				buff += 'r%d\tr%d\t' % (srcb,srcc)
			eth = opcode[opcodes.crcOpcode['eth'][0]:opcodes.crcOpcode['eth'][1]].unpack('uint:1')[0]
			last = opcode[opcodes.crcOpcode['last'][0]:opcodes.crcOpcode['last'][1]].unpack('uint:1')[0]
			if eth:
				buff += 'eth\t'
			if last:
				buff += 'last\t'
			if common:
				buff += 'common'
		else:
			buff += 'r%d\t' % (srcc)
			invoke = opcode[opcodes.camOpcode['invoke'][0]:opcodes.camOpcode['invoke'][1]].unpack('uint:1')[0]
			res_slot = opcode[opcodes.camOpcode['res_slot'][0]:opcodes.camOpcode['res_slot'][1]].unpack('uint:2')[0]
			use_128 = opcode[opcodes.camOpcode['use_128'][0]:opcodes.camOpcode['use_128'][1]].unpack('uint:1')[0]
			key_size = opcode[opcodes.camOpcode['key_size'][0]:opcodes.camOpcode['key_size'][1]].unpack('uint:2')[0]
			mask = opcode[opcodes.camOpcode['mask'][0]:opcodes.camOpcode['mask'][1]].unpack('uint:1')[0]
			if key_size == 0:
				buff += '16bit\t'
			elif key_size == 1:
				buff += '32bit\t'
			elif key_size == 2:
				buff += '64bit\t'
			else:
				buff += '128bit\t'
			buff += 'd.%d\t' % (res_slot)
			if invoke:
				buff += 'invoke\t'
			if mask:
				buff += 'mask\t'
			if common:
				buff += 'common'
		if SIMULATE:
			if self.hw_accelerators.ramman.valid == 0:
				if typ == 1:
					self.hw_accelerators.ramman.clock = self.hw_accelerator_clock(5, 5 + ( 125 / 100 ))
					self.hw_accelerators.ramman.source_a = self.REGISTER(srca)
					self.hw_accelerators.ramman.type = typ
					self.hw_accelerators.ramman.res_slot = res_slot
					self.hw_accelerators.ramman.key_size = key_size
					self.hw_accelerators.ramman.mask = mask
					self.hw_accelerators.ramman.invoke = invoke
					self.hw_accelerators.ramman.thread = self.scheduler.current_context
					if key_size == 0:
						self.hw_accelerators.ramman.key = self.REGISTER( srcc ) & 0x0000FFFF
					elif key_size == 1:
						self.hw_accelerators.ramman.key = self.REGISTER( srcc )
					else :
						self.hw_accelerators.ramman.key = self.REGISTER( srcc ) << 32 + self.REGISTER( srcc + 1)
				else:
					if immediate:
						length = srcb
					else:
						length = self.REGISTER(srcb)
					self.hw_accelerators.ramman.clock = self.hw_accelerator_clock( 5, 5 + ( 125 / 100 * ( length / 8 ) ) ) 
					self.hw_accelerators.ramman.source_a = self.REGISTER( srca ) 
					self.hw_accelerators.ramman.source_c = self.REGISTER( srcc ) & 0x0000FFFF 
					self.hw_accelerators.ramman.length = length 
					self.hw_accelerators.ramman.type = typ 
					self.hw_accelerators.ramman.eth = eth 
					self.hw_accelerators.ramman.last = last 
				self.hw_accelerators.ramman.ready = 0 
				self.hw_accelerators.ramman.valid = 1
			else:
				self.stall_pc.enter_stall = self.simulator.clock
				self.stall = STALL_RAMMAN 
				self.stall_pc.pc = self.pc
				self.changes.append( "  STALL: 1 " )
		return (1,buff)

	def hw_accelerator_clock (self,min,max):
		rr = random.uniform(min,max)
		return self.simulator.clock + min + rr

	def opcode_bbtx (self,opcode,op):
		self.pc += 4
		buff = 'bbtx\t'
		srcc = opcode[opcodes.bbtxOpcode['source_c'][0]:opcodes.bbtxOpcode['source_c'][1]].unpack('uint:5')[0]
		srca = opcode[opcodes.bbtxOpcode['source_a'][0]:opcodes.bbtxOpcode['source_a'][1]].unpack('uint:5')[0]
		srcb = opcode[opcodes.bbtxOpcode['source_b_or_immediate'][0]:opcodes.bbtxOpcode['source_b_or_immediate'][1]].unpack('uint:8')[0]
		immediate = opcode[opcodes.bbtxOpcode['immediate_or_register'][0]:opcodes.bbtxOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			buff += 'r%d\tr%d\t0x%x\t' % (srcc,srca,srcb)
		else:
			buff += 'r%d\tr%d\tr%d\t' % (srcc,srca,srcb)
		last = opcode[opcodes.bbtxOpcode['last'][0]:opcodes.bbtxOpcode['last'][1]].unpack('uint:1')[0]
		if last:	
			buff += 'last\t'
		inc = opcode[opcodes.bbtxOpcode['inc'][0]:opcodes.bbtxOpcode['inc'][1]].unpack('uint:1')[0]
		if inc:	
			buff += 'incremental\t'	
		wait = opcode[opcodes.bbtxOpcode['wait'][0]:opcodes.bbtxOpcode['wait'][1]].unpack('uint:1')[0]
		if wait:	
			buff += 'wait\t'
		common = opcode[opcodes.bbtxOpcode['common_or_private'][0]:opcodes.bbtxOpcode['common_or_private'][1]].unpack('uint:1')[0]
		if common:	
			buff += 'common'
		return (1,buff)  

	def opcode_bbmsg (self,opcode,op):
		""" OPCODE = BBMSG """
		pc = self.pc
		self.pc += 4
		buff = 'bbmsg\t'
		type = opcode[opcodes.bbmsgOpcode['type'][0]:opcodes.bbmsgOpcode['type'][1]].unpack('uint:3')[0]
		srca = opcode[opcodes.bbmsgOpcode['source_a'][0]:opcodes.bbmsgOpcode['source_a'][1]].unpack('uint:5')[0]
		srcb = opcode[opcodes.bbmsgOpcode['source_b_or_immediate'][0]:opcodes.bbmsgOpcode['source_b_or_immediate'][1]].unpack('uint:8')[0]
		immediate = opcode[opcodes.bbmsgOpcode['immediate_or_register'][0]:opcodes.bbmsgOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			buff += 'd.%d\tr%d\t0x%x\t' % (type,srca,srcb)
		else:
			buff += 'd.%d\tr%d\tr%d\t' % (type,srca,srcb)
		size = opcode[opcodes.bbmsgOpcode['size'][0]:opcodes.bbmsgOpcode['size'][1]].unpack('uint:1')[0]
		if size :
			buff += '64bit\t'
		wait = opcode[opcodes.bbmsgOpcode['wait'][0]:opcodes.bbmsgOpcode['wait'][1]].unpack('uint:1')[0] 
		if wait:
			buff += 'wait'
		if SIMULATE:
			if self.hw_accelerators.bbmsg_count < BBMSG_FIFO_DEPTH:
				min_bbmsg_clock = 0
				for i in range(BBMSG_FIFO_DEPTH):
					if self.hw_accelerators.bbmsg[i].valid == 1:
						if min_bbmsg_clock < self.hw_accelerators.bbmsg[i].clock:
							min_bbmsg_clock = self.hw_accelerators.bbmsg[i].clock
				if self.hw_accelerators.bbmsg_count > 0 and \
					self.hw_accelerators.bbtx[self.hw_accelerators.bbtx_out].valid == 1:
					if min_bbmsg_clock < self.hw_accelerators.bbtx[self.hw_accelerators.bbtx_out].clock:
						min_bbmsg_clock < self.hw_accelerators.bbtx[self.hw_accelerators.bbtx_out].clock - \
						self.simulator.clock + 1
					else:
						if min_bbmsg_clock > 0:
							min_bbmsg_clock = min_bbmsg_clock - self.simulator.clock + 1
						else:
							min_bbmsg_clock = BBMSG_MIN
				else:
					if min_bbmsg_clock > 0:
						min_bbmsg_clock = min_bbmsg_clock - self.simulator.clock + 1
					else:
						min_bbmsg_clock = BBMSG_MIN
				if min_bbmsg_clock < BBMSG_MIN:
					min_bbmsg_clock = BBMSG_MIN
				self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].clock = self.hw_accelerator_clock( min_bbmsg_clock, ( BBMSG_MAX - BBMSG_MIN ) + min_bbmsg_clock )
				self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].thread = self.scheduler.current_context
				self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].type = type
				self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].size = size
				self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].destination = self.REGISTER(srca)
				if immediate:
					self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].message_hi = srcb
				else:
					self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].message_hi = self.REGISTER(srcb)
				if size == 1: # 64 bit
					self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].message_lo = self.REGISTER(srcb + 1)
				self.hw_accelerators.bbmsg[self.hw_accelerators.bbmsg_in].valid = 1
				self.hw_accelerators.bbmsg_count += 1
				self.hw_accelerators.bbmsg_in = (self.hw_accelerators.bbmsg_in + 1) % BBMSG_FIFO_DEPTH
				if self.max_bbmsg_fifo < self.hw_accelerators.bbmsg_count:
					self.max_bbmsg_fifo = self.hw_accelerators.bbmsg_count
			else:
				self.stall_pc.enter_stall = self.simulator.clock
				self.stall = STALL_BBMSG
				self.stall_pc.pc = pc
				self.changes.append(" STALL: 1 ")
		return (1,buff)   
	def opcode_ffi (self,opcode,op):
		""" OPCODE = FFI """
		self.pc += 4
		buff = 'ffi'
		size = opcode[opcodes.ffiOpcode['size'][0]:opcodes.ffiOpcode['size'][1]].unpack('uint:1')[0]
		if size == opcodes.OPCODE_FFI8:
			buff += '8\t'
		else:
			buff += '16\t'
		dst = opcode[opcodes.ffiOpcode['destination_register'][0]:opcodes.ffiOpcode['destination_register'][1]].unpack('uint:5')[0]
		srca = opcode[opcodes.ffiOpcode['source_a'][0]:opcodes.ffiOpcode['source_a'][1]].unpack('uint:5')[0]
		srcb = opcode[opcodes.ffiOpcode['source_b_or_immediate'][0]:opcodes.ffiOpcode['source_b_or_immediate'][1]].unpack('uint:5')[0]
		immediate = opcode[opcodes.ffiOpcode['immediate_or_register'][0]:opcodes.ffiOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate == 1:
			buff += 'r%d\tr%d\t0x%x' % (dst,srca,srcb)
		else:
			buff += 'r%d\tr%d\tr%d' % (dst,srca,srcb)
		if SIMULATE:
			new_value = 0x20
			search = self.REGISTER(srca)
			if immediate:
				bit = srcb
			else:
				bit = self.REGISTER(srcb)
			if size == opcodes.OPCODE_FFI8:
				bit &= 0x7
				for i in range(8):
					if search & ( 1 << bit ) != 0:
						new_value = bit
						break
					bit = ( bit + 1 ) % 8
			elif size == opcodes.OPCODE_FFI16:
				bit &= 0xf
				for i in range(16):
					if search & ( 1 << bit ) != 0:
						new_value = bit
						break
					bit = ( bit + 1 ) % 16
			else:
				bit &= 0x1f
				for i in range(32):
					if search & ( 1 << bit ) != 0:
						new_value = bit
						break
					bit = ( bit + 1 ) % 32
			if dst > 0:
				self.SET_REGISTER(dst,new_value)
				new_value = self.REGISTER(dst)
			else:
				new_value = 0
			self.changes.append(" REG: r%d=%08X " % (dst,new_value))
		return (1,buff)  

	def opcode_chksm (self,opcode,op):
		self.pc += 4
		buff = 'chksm\t'
		dst = opcode[opcodes.icheckOpcode['destination_register'][0]:opcodes.icheckOpcode['destination_register'][1]].unpack('uint:5')[0]
		srcb = opcode[opcodes.icheckOpcode['source_b'][0]:opcodes.icheckOpcode['source_b'][1]].unpack('uint:5')[0]
		srca = opcode[opcodes.icheckOpcode['source_a'][0]:opcodes.icheckOpcode['source_a'][1]].unpack('uint:5')[0]
		buff += 'r%d\tr%d\tr%d\t' % (dst,srcb,srca)
		high = opcode[opcodes.icheckOpcode['high_or_low'][0]:opcodes.icheckOpcode['high_or_low'][1]].unpack('uint:1')[0]
		if high:
			buff += 'high\t'
		last = opcode[opcodes.icheckOpcode['last'][0]:opcodes.icheckOpcode['last'][1]].unpack('uint:1')[0]
		if last:
			buff += 'last'
		return (1,buff)  
	def opcode_counter (self,opcode,op):
		self.pc += 4
		buff = 'counter\t'
		operation = opcode[opcodes.counterOpcode['operation'][0]:opcodes.counterOpcode['operation'][1]].unpack('uint:1')[0]
		if not operation:
			buff += 'increment\t'
		else:
			buff += 'decrement\t'
		immeda = opcode[opcodes.counterOpcode['imm_or_reg_a'][0]:opcodes.counterOpcode['imm_or_reg_a'][1]].unpack('uint:1')[0]
		immedb = opcode[opcodes.counterOpcode['imm_or_reg_b'][0]:opcodes.counterOpcode['imm_or_reg_b'][1]].unpack('uint:1')[0]
		srca = opcode[opcodes.counterOpcode['source_a'][0]:opcodes.counterOpcode['source_a'][1]].unpack('uint:8')[0]
		if immeda:
			buff += '0x%x\t' % (srca)
		else:
			buff += 'r%d\t' % (srca)
		srcb = opcode[opcodes.counterOpcode['source_b'][0]:opcodes.counterOpcode['source_b'][1]].unpack('uint:8')[0]
		if immedb:
			buff += '0x%x\t' % (srcb)
		else:
			buff += 'r%d\t' % (srcb)
		size = opcode[opcodes.counterOpcode['size'][0]:opcodes.counterOpcode['size'][1]].unpack('uint:1')[0]
		mode = opcode[opcodes.counterOpcode['mode'][0]:opcodes.counterOpcode['mode'][1]].unpack('uint:1')[0]
		if not size:
			buff += '2bytes\t'
		else:
			buff += '4bytes\t'
		if not mode:
			buff += 'freeze'
		else:
			buff += 'wrap'
		return (1,buff) 
	def opcode_crypt (self,opcode,op):
		self.pc += 4
		crypt = opcode[opcodes.cryptOpcode['hash'][0]:opcodes.cryptOpcode['hash'][1]].unpack('uint:1')[0]
		if not crypt:
			buff = 'crypt\t'
		else:
			buff == 'auth\t'
		srca = opcode[opcodes.cryptOpcode['source_a'][0]:opcodes.cryptOpcode['source_a'][1]].unpack('uint:6')[0]
		srcb = opcode[opcodes.cryptOpcode['source_b'][0]:opcodes.cryptOpcode['source_b'][1]].unpack('uint:8')[0]
		immediate = opcode[opcodes.cryptOpcode['immediate_or_register'][0]:opcodes.cryptOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			buff += 'r%d\t0x%x\t' % (srca,srcb)
		else:
			buff += 'r%d\tr%d\t' % (srca,srcb)
		first = opcode[opcodes.cryptOpcode['first'][0]:opcodes.cryptOpcode['first'][1]].unpack('uint:1')[0]
		last = opcode[opcodes.cryptOpcode['last'][0]:opcodes.cryptOpcode['last'][1]].unpack('uint:1')[0]
		if first:
			if last:
				buff += 'single\t'
			else:
				buff += 'first\t'
		elif last:
			buff += 'last\t'
		else:
			buff += 'middle\t'
		invoke = opcode[opcodes.cryptOpcode['invoke'][0]:opcodes.cryptOpcode['invoke'][1]].unpack('uint:1')[0]
		if invoke:
			buff += 'invoke'
		return (1,buff)   
	def opcode_signext (self,opcode,op):
		self.pc += 4
		buff = 'signext\t'
		dst = opcode[opcodes.signextOpcode['destination_register'][0]:opcodes.signextOpcode['destination_register'][1]].unpack('uint:5')[0]
		srca = opcode[opcodes.signextOpcode['source_a'][0]:opcodes.signextOpcode['source_a'][1]].unpack('uint:5')[0]		
		srcb = opcode[opcodes.signextOpcode['source_b_or_immediate'][0]:opcodes.signextOpcode['source_b_or_immediate'][1]].unpack('uint:5')[0]
		buff += 'r%d\tr%d\t' % (dst,srca)
		immediate = opcode[opcodes.signextOpcode['immediate_or_register'][0]:opcodes.signextOpcode['immediate_or_register'][1]].unpack('uint:1')[0]
		if immediate:
			if srcb == 0:
				buff += '8bit'
			else:
				buff += '16bit'
		else:
			buff += 'r%d' % (srcb)
		
		return (1,buff)

	def opcode_nop (self,opcode,op):
		self.pc += 4
		return (1,'nop') 

#   Utilities
	
	def REGISTER (self,r):
		if r & 0xf < NUMBER_OF_GLOBAL_REGISTERS:
			ind = r & 0xf
			return self.global_registers[ind]
		else:
			ind = (r - NUMBER_OF_GLOBAL_REGISTERS) & 0x3f
			return self.private_registers[ind]

	def SET_REGISTER (self,r,val):
		if r & 0xf < NUMBER_OF_GLOBAL_REGISTERS:
			ind = r & 0xf
			try:
				self.global_registers[ind] = val 
			except OverflowError:
				self.global_registers[ind] = unsigned(val)
				return False
		else:
			ind = (r - NUMBER_OF_GLOBAL_REGISTERS) & 0x3f
			try:
				self.private_registers[ind] = val 
			except OverflowError:
				self.private_registers[ind] = unsigned(val)
				return False
		return True

	def Z_FLAG_IS_SET( self,st ):
		if st & Z_FLAG == Z_FLAG:
			return True
		else: return False
	def N_FLAG_IS_SET( self,st ):
		if st & N_FLAG == N_FLAG:
			return True
		else: return False
	def CY_FLAG_IS_SET( self,st ):
		if st & CY_FLAG == CY_FLAG:
			return True
		else: return False
	def OVF_FLAG_IS_SET( self,st ):
		if st & OVF_FLAG == OVF_FLAG:
			return True
		else: return False
	def JBIT_FLAG_IS_SET( self,st ):
		if st & JBIT_FLAG == JBIT_FLAG:
			return True
		else: return False

	def show_ram (self,text,address):
		base = (address & 0xfffffffc) // 4
		log(self.fio,"SRAM at 0x%x(0x%x) %s" % (base,address,text))
		b = base
		while b < base + 4 :
			try:
				v = self.data_segment[b]
				log(self.fio," %08x" % (v))
			except IndexError:
				print 'IndexError : address=0x%x base=0x%x b=0x%x' % (address,base,b)
			b += 1

	def READ_IO (self,address,width):
		base = address & 0xfffffffc
		ind = base // 4
		offset = address & 3
		try:
			old_value = self.io[ind]
			if width == 1:
				if offset == 0:
					old_value = ( old_value & 0xff000000 ) >> 24
				elif offset == 1:
					old_value = ( old_value & 0xff000000 ) >> 24
				elif offset == 2:
					old_value = ( old_value & 0x0000ff00 ) >> 8
				else:
					old_value = old_value & 0x000000ff 
			elif width == 2:
				if offset == 0:
					if sys.byteorder != "little":
						old_value = ( old_value & 0xffff0000 ) >> 16
				elif offset == 2:
					old_value = old_value & 0x0000ffff 
				else:
					print 'READ_IO violation'
					old_value = 0
			return (True,old_value)
		except IndexError:
			old_value = 0
			print 'READ_IO: Index Error : %d(%x), address=0x%08x, for %d bytes' % (ind,ind,address,width)
			return (False,old_value)

	def READ_SRAM (self,address,width):
		base = address & 0xfffffffc
		ind = base // 4
		offset = address & 3
		try:
			old_value = self.data_segment[ind]
			if width == 1:
				if offset == 0:
					old_value = ( old_value & 0xff000000 ) >> 24
				elif offset == 1:
					old_value = ( old_value & 0xff000000 ) >> 24
				elif offset == 2:
					old_value = ( old_value & 0x0000ff00 ) >> 8
				else:
					old_value = old_value & 0x000000ff 
			elif width == 2:
				if offset == 0:
					if sys.byteorder != "little":
						old_value = ( old_value & 0xffff0000 ) >> 16
				elif offset == 2:
					old_value = old_value & 0x0000ffff 
				else:
					print 'READ_SRAM violation'
					old_value = 0
			return (True,old_value)
		except IndexError:
			old_value = 0
			print 'READ_SRAM: Index Error : %d(%x), address=0x%08x, for %d bytes' % (ind,ind,address,width)
			return (False,old_value)

	def READ_COMMON (self,address,width):
		base = address & 0xfffffffc
		ind = base // 4
		offset = address & 3
		try:
			old_value = self.simulator.common_segment[ind]
			if width == 1:
				if offset == 0:
					old_value = ( old_value & 0xff000000 ) >> 24
				elif offset == 1:
					old_value = ( old_value & 0xff000000 ) >> 24
				elif offset == 2:
					old_value = ( old_value & 0x0000ff00 ) >> 8
				else:
					old_value = old_value & 0x000000ff 
			elif width == 2:
				if offset == 0:
					old_value = ( old_value & 0xffff0000 ) >> 16
				elif offset == 2:
					old_value = old_value & 0x0000ffff 
				else:
					print 'READ_COMMON violation'
					old_value = 0
			return (True,old_value)
		except IndexError:
			old_value = 0
			print 'READ_COMMON: Index Error : %d(%x), address=0x%08x, for %d bytes' % (ind,ind,address,width)
			return (False,old_value)

	def WRITE_SRAM(self,address,width,new_value):
		base = address & 0xfffffffc
		ind = base // 4
		offset = address & 3
		try:
			old_value = self.data_segment[ind]
			if width == 1:
				if offset == 0:
					new_value = ( new_value & 0xff000000 ) >> 24
					mask = ~(0xff000000 >> 24)
				elif offset == 1:
					new_value = ( new_value & 0xff000000 ) >> 24
					mask = ~(0xff000000 >> 24)
				elif offset == 2:
					new_value = ( new_value & 0x0000ff00 ) >> 8
					mask = ~(0x0000ff00 >> 8)
				else:
					new_value = new_value & 0x000000ff
					mask = ~0x000000ff 
			elif width == 2:
				if offset == 0:
					new_value = ( new_value & 0xffff0000 ) >> 16
					mask = ~(0xffff0000 > 16)
				elif offset == 2:
					new_value = new_value & 0x0000ffff 
					mask = ~0x0000ffff
			else:
				mask = 0
			temp = old_value & mask
			new_value = temp | new_value
		except IndexError:
			old_value = 0
			print 'WRITE_SRAM: Index Error on read : %d(%x), address=0x%08x, for %d bytes' % (ind,ind,address,width)
			return (False,old_value)
		try:
			self.data_segment[ind] = new_value
		except OverflowError:
			self.data_segment[ind] = unsigned(new_value)
			return (True,old_value)
		return (True,old_value)

	def WRITE_COMMON(self,address,width,new_value):
		base = address & 0xfffffffc
		ind = base // 4
		offset = address & 3
		try:
			old_value = self.simulator.common_segment[ind]
			if width == 1:
				if offset == 0:
					new_value = ( new_value & 0xff000000 ) >> 24
					mask = ~(0xff000000 >> 24)
				elif offset == 1:
					new_value = ( new_value & 0xff000000 ) >> 24
					mask = ~(0xff000000 >> 24)
				elif offset == 2:
					new_value = ( new_value & 0x0000ff00 ) >> 8
					mask = ~(0x0000ff00 >> 8)
				else:
					new_value = new_value & 0x000000ff
					mask = ~0x000000ff 
			elif width == 2:
				if offset == 0:
					new_value = ( new_value & 0xffff0000 ) >> 16
					mask = ~(0xffff0000 > 16)
				elif offset == 2:
					new_value = new_value & 0x0000ffff 
					mask = ~0x0000ffff
			else:
				mask = 0
			temp = old_value & mask
			new_value = temp | new_value
		except IndexError:
			old_value = 0
			print 'WRITE_COMMON: Index Error on read : %d(%x), address=0x%08x, for %d bytes' % (ind,ind,address,width)
			return (False,old_value)
		try:
			self.simulator.common_segment[ind] = unsigned(new_value)
		except OverflowError:
			print "Overflow"
			return (False,old_value)
		return (True,old_value)

	def WRITE_IO(self,address,width,new_value):
		base = address & 0xfffffffc
		ind = base // 4
		offset = address & 3
		try:
			old_value = self.io[ind]
			if width == 1:
				if offset == 0:
					new_value = ( new_value & 0xff000000 ) >> 24
					mask = ~(0xff000000 >> 24)
				elif offset == 1:
					new_value = ( new_value & 0xff000000 ) >> 24
					mask = ~(0xff000000 >> 24)
				elif offset == 2:
					new_value = ( new_value & 0x0000ff00 ) >> 8
					mask = ~(0x0000ff00 >> 8)
				else:
					new_value = new_value & 0x000000ff
					mask = ~0x000000ff 
			elif width == 2:
				if offset == 0:
					new_value = ( new_value & 0xffff0000 ) >> 16
					mask = ~(0xffff0000 > 16)
				elif offset == 2:
					new_value = new_value & 0x0000ffff 
					mask = ~0x0000ffff
			else:
				mask = 0
			temp = old_value & mask
			new_value = temp | new_value
		except IndexError:
			old_value = 0
			print 'WRITE_IO: Index Error on read : %d(%x), address=0x%08x, for %d bytes' % (ind,ind,address,width)
			return (False,old_value)
		try:
			self.io[ind] = new_value
		except OverflowError:
			self.io[ind] = unsigned(new_value)
			return (True,old_value)
		return (True,old_value)


