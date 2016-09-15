#!/usr/bin/env python
import rh_defines
NUM_OF_RX_PORTS       =   6
NUM_OF_TX_PORTS       =   46
GPON_TX_PERIPHERAL    =   0x00
GPON_RX_PERIPHERAL    =   0x01
CO_RUNNER             =   0x02
BPM_PERIPHERAL        =   0x03
SBPM_PERIPHERAL       =   0x04
ETH0_TX_PERIPHERAL    =   0x05
ETH0_RX_PERIPHERAL    =   0x06
ETH1_TX_PERIPHERAL    =   0x07
ETH1_RX_PERIPHERAL    =   0x08
ETH2_TX_PERIPHERAL    =   0x09
ETH2_RX_PERIPHERAL    =   0x0A
ETH3_TX_PERIPHERAL    =   0x0B
ETH3_RX_PERIPHERAL    =   0x0C
ETH4_TX_PERIPHERAL    =   0x0D
ETH4_RX_PERIPHERAL    =   0x0E
INGRESS_HANDLER       =   0x0F

NUM_OF_IH_CLASSES      =  16
NUM_OF_SOURCE_PORTS    =  270

ETH0_RX_SRC_ADDRESS	=   0x01
ETH1_RX_SRC_ADDRESS	=   0x02
ETH2_RX_SRC_ADDRESS	=   0x03
ETH3_RX_SRC_ADDRESS	=   0x04
ETH4_RX_SRC_ADDRESS	=   0x05
ETH5_RX_SRC_ADDRESS	=   0x00
GPON_RX_SRC_ADDRESS	=   0x00

ETH0_TX_SRC_ADDRESS =	0x11
ETH1_TX_SRC_ADDRESS =	0x12
ETH2_TX_SRC_ADDRESS =	0x13
ETH3_TX_SRC_ADDRESS =	0x14
ETH4_TX_SRC_ADDRESS =	0x15
ETH5_TX_SRC_ADDRESS =	0x10
GPON_TX_SRC_ADDRESS =	0x10

CPU_SRC_ADDRESS    =	0x06

PACKET_DDR_BUFFER_SIZE           =    2048
PACKET_SRAM_BUFFER_SIZE          =    128
BUFFER_DESCRIPTOR_LENGTH         =    8
CHUNK_BUFFER_DESCRIPTOR_LENGTH   =    4
GPON_RX_BUFFER_LENGTH            =    128
PERIPHERAL_PORT_BIT_MASK         =    0x0000000F
TCONT_INDEX_BIT_MASK             =    0x000003F0

SOP_BIT_MASK                     =    0x00000008
EOP_BIT_MASK                     =    0x00000010
EXCEPTION_BIT_MASK               =    0x00000001
CRC_ERROR_BIT_MASK               =    0x00000002
ERROR_BIT_MASK                   =    0x80000000
PCI_VALID_BIT_MASK               =    0x80000000

MAX_NUM_OF_BPM_BUFFERS      =   0x1000
BPM_SRAM_ADDRESS            =   0x1000
VALID_BUFFER_MASK           =   0x0001;
BPM_BUFFERS_BASE            =   0x1D0000
DDR_BUFFER_PAYLOAD_OFFSET   =   0x08

MAX_BD_FIFO_DEPTH    =   8
GR_MODE              =   0
GI_MODE              =   1

NUM_OF_FLOWS            =   0x100
INVALID_LUT_TABLE       =   0x0F
INVALID_PORT_NUMBER     =   0x3F
INVALID_BUFFER_NUMBER   =   0xFFFF

TX_TIME = 0
RX_TIME = 1

class BPM_BUFFER:
	taken = 0
	owner = 0
	mcnt = 0

class FLOW_CONFIG:
	mode = 0
	crc_release = 0

class TX_PACKET:
	tx_packet_length  = 0
	tx_port  = 0
	src_port = 0
	buffer_number = 0
	crc_calc = 0
	port_id = 0
	packet [ ]*PACKET_DDR_BUFFER_SIZE 

class SOURCE_PORT:
	source_port_id  = 0
	class_id  = 0
	flow_id = 0
	wan = 0
	override_enable = 0

class PLOAM_CONFIG:
	class_id = 0
	override_enable = 0

class CLASS:
	key  = 0
	mask = 0

class CLASS_CONFIG: 
	table_0  = 0
	table_1  = 0
	table_2  = 0
	table_3  = 0
	target_memory  = 0
	target_memory_override_enable  = 0
	target_runner  = 0
	target_runner_override_enable  = 0
	dscp_table  = 0
	direct_mode = 0
	direct_mode_override_enable  = 0
	drop_config  = 0
	dest_config  = 0

class SRAM_BUFFER:
	prev_BN = 0
	next_BN  = 0
	next_valid  = 0
	multicast_counter  = 0

class rh:
	rx_frequency = []*NUM_OF_RX_PORTS
	rx_clocks_count = []*NUM_OF_RX_PORTS
	rx_generator_enable = []*NUM_OF_RX_PORTS

	normal_rx_thread_number = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	direct_rx_thread_number = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	normal_rx_descriptor_ptr = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	direct_rx_descriptor_ptr = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	normal_rx_queue_size = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	direct_rx_queue_size = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	normal_rx_buffers_count = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS
	direct_rx_buffers_count = [[]*NUM_OF_RUNNERS]*NUM_OF_RX_PORTS

	normal_rx_filled_buffers_count = []*NUM_OF_RX_PORTS
	direct_rx_filled_buffers_count = []*NUM_OF_RX_PORTS

	ih_buffer = []*[IH_BUFFER_SIZE
static SOURCE_PORT_T    ih_source_port = []*NUM_OF_SOURCE_PORTS 
static PLOAM_CONFIG_T   ploam_config;
static CLASS_T          ih_class = []*NUM_OF_IH_CLASSES
static CLASS_CONFIG_T   ih_class_config = []*NUM_OF_IH_CLASSES
	ih_flow_id = 0
	ih_source_port_number = 0
	ih_class_id = 0
	ih_flow_mode = 0
	ih_target_runner = 0


static unsigned int  tx_frequency[NUM_OF_TX_PORTS];
static unsigned int  tx_clocks_count[NUM_OF_TX_PORTS];
static unsigned int  tx_thread_number[NUM_OF_TX_PORTS];
static unsigned int  tx_request_in_progress[NUM_OF_TX_PORTS];
static unsigned int  tx_ack_pending[NUM_OF_TX_PORTS];
static unsigned int  tx_peripheral_runner[NUM_OF_TX_PORTS];
static TX_PACKET_T   tx_packet[MAX_BD_FIFO_DEPTH];

static unsigned int  copy_rx_buffer_in_process;
static unsigned int  rx_buffer_offset;
static unsigned int  rx_buffer_length;
static unsigned int  rx_port = ETH4_RX_SRC_ADDRESS + 1;
static unsigned char rx_buffer[PACKET_DDR_BUFFER_SIZE];

static unsigned int  runner_buffers_state[IH_BUFFERS_NUMBER][NUM_OF_RUNNERS];
static RH_UINT32     runner_current_buffer[NUM_OF_RUNNERS];
static unsigned int  runner_buffers_number[NUM_OF_RUNNERS];
static unsigned int  assigned_runner_buffers_number[NUM_OF_RUNNERS];
static unsigned int  runner_buffers_base[NUM_OF_RUNNERS];
static unsigned int  assigned_runner_buffers_base[NUM_OF_RUNNERS];
static unsigned int  ih_response_address[NUM_OF_RUNNERS];

static unsigned int  tcont_index_sram_address;
static RX_DESCRIPTOR_HI_T     user_rx_descriptor_hi;
static RX_DESCRIPTOR_LO_T     user_rx_descriptor_lo;
static TX_DESCRIPTOR_HI_T     user_tx_descriptor_hi;
static TX_DESCRIPTOR_LO_T     user_tx_descriptor_lo;


static BPM_BUFFER_T  bpm_buffers [MAX_NUM_OF_BPM_BUFFERS]; 
static FLOW_CONFIG_T flow_config [NUM_OF_FLOWS]; 

static unsigned int  taken_bpm_buffers = 0;
static unsigned int  bpm_wakeup_enable;
static unsigned int  bpm_thread_number;
static unsigned int  bpm_buffers_number = MAX_NUM_OF_BPM_BUFFERS;
static unsigned int  bpm_buffer_size = PACKET_DDR_BUFFER_SIZE;
static unsigned int  bpm_buffers_base = BPM_BUFFERS_BASE;
static unsigned int  bpm_sram_address = BPM_SRAM_ADDRESS;
static unsigned int  payload_offset = DDR_BUFFER_PAYLOAD_OFFSET;
static unsigned int  tx_payload_multiplier = 1;

static unsigned int  extra_headers_start_address;
static unsigned int  header_size;
static unsigned int  bd_fifo_depth = MAX_BD_FIFO_DEPTH;
static unsigned int  bd_fifo_in_ptr = 0;
static unsigned int  bd_fifo_out_ptr = 0;

static SRAM_BUFFER_T packet_sram_buffers[NUMBER_OF_SRAM_BUFFERS];
static unsigned int  sram_buffers_head;
static unsigned int  sram_buffers_tail;

static unsigned int  direct_mode_matrix[8][8];
static unsigned int  target_memory_matrix[8][8];


static unsigned int  serial_number[NUM_OF_RX_PORTS] =
{ 0, 0, 0, 0, 0, 0 };

static FILE          *rx_data_file[NUM_OF_RX_PORTS] =
{ NULL, NULL, NULL, NULL, NULL, NULL };

static FILE          *tx_data_file[NUM_OF_TX_PORTS] =
{ NULL, NULL, NULL, NULL, 
  NULL, NULL, NULL, NULL, 
  NULL, NULL, NULL, NULL, 
  NULL, NULL, NULL };

static char          *rx_file_name[NUM_OF_RX_PORTS] =
{
    "gpon-rh-sim.rx",
    "eth0-rh-sim.rx", "eth1-rh-sim.rx", "eth2-rh-sim.rx", "eth3-rh-sim.rx", "eth4-rh-sim.rx", 
};

static char *tx_file_name[NUM_OF_TX_PORTS] =
{
    "gpon0-rh-sim.tx", "gpon1-rh-sim.tx", "gpon2-rh-sim.tx", "gpon3-rh-sim.tx",
    "gpon4-rh-sim.tx", "gpon5-rh-sim.tx", "gpon6-rh-sim.tx", "gpon7-rh-sim.tx",
    "gpon8-rh-sim.tx", "gpon9-rh-sim.tx", "gpon10-rh-sim.tx", "gpon11-rh-sim.tx",
    "gpon12-rh-sim.tx", "gpon13-rh-sim.tx", "gpon14-rh-sim.tx", "gpon15-rh-sim.tx",
    "gpon16-rh-sim.tx", "gpon17-rh-sim.tx", "gpon18-rh-sim.tx", "gpon19-rh-sim.tx",
    "gpon20-rh-sim.tx", "gpon21-rh-sim.tx", "gpon22-rh-sim.tx", "gpon23-rh-sim.tx",
    "gpon24-rh-sim.tx", "gpon25-rh-sim.tx", "gpon26-rh-sim.tx", "gpon27-rh-sim.tx",
    "gpon28-rh-sim.tx", "gpon29-rh-sim.tx", "gpon30-rh-sim.tx", "gpon31-rh-sim.tx",
    "gpon32-rh-sim.tx", "gpon33-rh-sim.tx", "gpon34-rh-sim.tx", "gpon35-rh-sim.tx",
    "gpon36-rh-sim.tx", "gpon37-rh-sim.tx", "gpon38-rh-sim.tx", "gpon39-rh-sim.tx",
    "co-runner-rh-sim.tx" , 
    "eth0-rh-sim.tx" , "eth1-rh-sim.tx" , "eth2-rh-sim.tx" , "eth3-rh-sim.tx" , 
    "eth4-rh-sim.tx" 
};
	def rh_main_parse (self,msg):
		if msg[0] == rh_defines.MESSAGE_TYPE_RESTART:
			self.readUserConfigurationParameters()
			self.initRunnerHandlerStateMachine()
		elif msg[0] == rh_defines.MESSAGE_TYPE_RESET:
			self.readUserConfigurationParameters()
			self.openRxFiles()
			self.openTxFiles()
			self.initRunnerHandlerStateMachine()
		elif msg[0] == rh_defines.MESSAGE_TYPE_CLOCK:
			self.generateRhSimRxClock()
			self.generateRhSimTxClock()
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_ACK_NORMAL or msg[0] == rh_defines.MESSAGE_TYPE_BB:
			self.ackRhMessageTypeHandle(msg[1:],rh_defines.IH_NORMAL_MODE)
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_ACK_DIRECT:
			self.ackRhMessageTypeHandle(msg[1:],rh_defines.IH_DIRECT_MODE)
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_NACK:
			self.nackRhMessageTypeHandle(msg[1:])
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_PACKET_DESCRIPTOR:
			self.packetDescriptorRhMessageTypeHandle()
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_BN_ALLOC:
			self.alloc_bpm(0)
		elif msg[0] == rh_defines.MESSAGE_TYPE_BUFFER_ALLOC:
			self.alloc_bpm(1)
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_BN_FREE:
			self.free_bpm()
		elif msg[0] == rh_defines.MESSAGE_TYPE_BB_MCNT_SET:
			self.multicast()
		elif msg[0] == rh_defines.MESSAGE_TYPE_BBTX_DATA:
			self.bbTxRhMessageTypeHandle(msg[1:])
		elif msg[0] == rh_defines.MESSAGE_TYPE_IH_ACK:
			self.release_runner_buffer()
		elif msg[0] == rh_defines.MESSAGE_TYPE_IH_PD:
			self.process_runner_packet(msg[1:])

	def process_runner_packet (self,msg):
		return
	def readUserConfigurationParameters(self):
		try:
			user_config_file = open ("runner.cfg", "r")

		except IOError:
			print "Cannot open file 'sim.log'"
		return
	def initRunnerHandlerStateMachine(self):
		return
	def readUserConfigurationParameters(self):
		return
	def openRxFiles(self):
		return
	def openTxFiles(self):
		return
	def initRunnerHandlerStateMachine(self):
		return
	def generateRhSimRxClock(self):
		return
	def generateRhSimTxClock(self):
		return
	def ackRhMessageTypeHandle(self,msg,mode):
		return
	def nackRhMessageTypeHandle(self,msg):
		return
	def packetDescriptorRhMessageTypeHandle(self):
		return
	def alloc_bpm(self,type):
		return
	def free_bpm(self):
		return
	def multicast(self):
		return
	def bbTxRhMessageTypeHandle(self,msg):
		return
	def release_runner_buffer(self):
		return

