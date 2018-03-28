import sys
from time import sleep
from random import uniform as rand_float
import Pyro4 as pyro

# Arguments and assignments
arguments = sys.argv[1:] # Fetch arguments, discarding script name
rID = arguments[0]
num_acc = int(arguments[1])
host = arguments[2]
rmi_port = int(arguments[3])
ReaderList = []


# Fetch the remote client handler object

name_server = pyro.locateNS(host = host, port=rmi_port)
client_handler_uri = name_server.lookup('client_handler')
client_handler = pyro.Proxy(client_handler_uri)

for iteration in range (0,num_acc):
	
	rSeq, sSeq, oVal = client_handler.handle_reader(rID)
	ReaderList.append((rSeq, sSeq, oVal))
	sleep(rand_float(0,10))  

client_handler.close()

# Create log file 

print(''.join(["Client Type: Reader \nClient Name: ",str(rID),"\nrSeq\tsSeq\toVal"]))

# Iterate through the Readerlist and write to file
for row in ReaderList:
	row_string = ''
	for item in row:
		row_string+=(str(item)+'\t'*2)
	print(row_string)