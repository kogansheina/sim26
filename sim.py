#!/usr/bin/env python
import os
import array
import runner
import simulator
import opcodes
from datetime import datetime

#-------------
#	Main
#-------------
def main(argv):
	command_file_name = ''
	code0 = ''
	code1 = ''
	common = ''
	data0 = ''
	data1 = ''
	ctx0 = ''
	ctx1 = ''
	runner0 = 0
	runner1 = 0
	simulatorins = 0
	if len(argv) == 1:
		print  "\n Syntax: \n\n"
#        Options:\n \
#            -fFile		Commands file\n \
#		    -code0<file>		Object file for Runner 0\n \
#		    -code1<file>   	Object file for Runner 1\n \
#		    -data0<file>		Data file for Runner 0\n \
#		    -data1<file>   	Data file for Runner 1\n \
#		    -context0<file>	Context file for Runner 0\n \
#		    -context1<file>    Context file for Runner 1\n \
#		    -common<file>		Comman data file\n"
	else:
		print "Start at : "
		print datetime.now()
		for i in range (1,len(argv)):
			if argv[i].startswith ('-f'):
				command_file_name = argv[i][2:]
			elif argv[i].startswith("-code0"):
				code0 = argv[i][6:]
			elif argv[i].startswith("-code1"):
				code1 = argv[i][6:]
			elif argv[i].startswith("-data0"):
				data0 = argv[i][6:]
			elif argv[i].startswith("-data1"):
				data1 = argv[i][6:]
			elif argv[i].startswith("-context0"):
				ctx0 = argv[i][9:]
			elif argv[i].startswith("-context1"):
				ctx1 = argv[i][9:]
			elif argv[i].startswith("-common"):
				common = argv[i][7:]
			else:
				print "File name needed"
	if command_file_name != '':
		fobj = open(command_file_name,'r')
		for line in fobj:
			args = line.split()
			for i in range(len(args)):
				if args[i].startswith("-code0"):
					code0 = args[i][6:]
				elif args[i].startswith("-code1"):
					code1 = args[i][6:]
				elif args[i].startswith("-data0"):
					data0 = args[i][6:]
				elif args[i].startswith("-data1"):
					data1 = args[i][6:]
				elif args[i].startswith("-context0"):
					ctx0 = args[i][9:]
				elif args[i].startswith("-context1"):
					ctx1 = args[i][9:]
				elif args[i].startswith("-common"):
					common = args[i][7:]
		fobj.close()

	simulatorins = simulator.simulator(common)
	if code0 != '':
		runner0 = runner.runner(0,code0,data0,ctx0,simulatorins)		
	if code1 != '':
		runner1 = runner.runner(1,code1,data1,ctx1,simulatorins)
		
	if runner0:
		if runner1:
			runner0.addCorunner(runner1)
		runner0.run()
	if runner1:
		if runner0:
			runner1.addCorunner(runner0)
		runner1.run()
	print "Stop at : "
	print datetime.now()

if __name__ == '__main__':
	from sys import argv
	main(argv)

