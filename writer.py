import sys
from time import sleep
from random import uniform as rand_float
import Pyro4 as pyro

# Arguments and assignments
arguments = sys.argv[1:] # Fetch arguments, discarding script name
wID = arguments[0]
num_acc = int(arguments[1])
host = arguments[2]
rmi_port = int(arguments[3])
WriterList = []


# Fetch the remote client handler object

name_server = pyro.locateNS(host = host, port=rmi_port)
client_handler_uri = name_server.lookup('client_handler')
client_handler = pyro.Proxy(client_handler_uri)

for iteration in range (0,num_acc):
	
	rSeq,sSeq = client_handler.handle_writer(wID)
	WriterList.append((rSeq,sSeq))
	sleep(rand_float(0,10))   

client_handler.close()

# Create log file 

print(''.join(["Client Type: Writer \nClient Name: ",str(wID),"\nrSeq\tsSeq"]))

# Iterate through the WriterList and write to file

for row in WriterList:
	row_string = ''
	for item in row:
		row_string+=(str(item)+'\t'*2)
	print(row_string)