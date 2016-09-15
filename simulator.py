#!/usr/bin/env python
import array
from numpy import zeros,uint32
import opcodes

COMMON_SEGMENT_SIZE    = 64 * 1024
DDR_SIZE         = 64 * 1024 * 1024 
PACKET_SRAM_SIZE = 512 * 1024 

class semaphore:

	def __init__ (self):
		self.enable_wakeup = False
		self.status = False
		self.wakeup = False
		self.thread = 0
		self.runner = 0
		self.owner_thread = 0
		self.owner_runner = 0
                
class simulator:
	
	SEMAPHOR_CTRL_0  =  0x50
	SEMAPHOR_CTRL_1  =  0x54
	SEMAPHORE_0_STATUS = SEMAPHOR_CTRL_0
	SEMAPHORE_1_STATUS = SEMAPHOR_CTRL_0 + 1
	SEMAPHORE_2_STATUS = SEMAPHOR_CTRL_0 + 2
	SEMAPHORE_3_STATUS = SEMAPHOR_CTRL_0 + 3
	SEMAPHORE_4_STATUS = SEMAPHOR_CTRL_1 
	SEMAPHORE_5_STATUS = SEMAPHOR_CTRL_1 + 1
	SEMAPHORE_6_STATUS = SEMAPHOR_CTRL_1 + 2
	SEMAPHORE_7_STATUS = SEMAPHOR_CTRL_1 + 3
	common_segment = array.array('L')
	semaphores = []*8	
	common_filename = ""
	ddr = [] * DDR_SIZE 
	packet_sram = [] * PACKET_SRAM_SIZE
	# (base,size,end,offset)
	ddr_space = (0,0,0,0)

	def __init__(self,common_filename):
		self.common_filename = common_filename
		for s in range(len(self.semaphores)):
			self.semaphores.append(semaphore())
		self.ddr = zeros(DDR_SIZE,'L')
		self.packet_sram = zeros(PACKET_SRAM_SIZE,'L')
		fobj = open(self.common_filename,'rb')
		self.common_segment.fromfile(fobj,COMMON_SEGMENT_SIZE//4)
		self.common_segment.byteswap()
		fobj.close()
		self.clock = 0
		self.speed = 50
		self.current_speed = 0
