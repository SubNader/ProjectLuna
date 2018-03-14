import sys
import socket
from time import sleep
from random import uniform as rand_float

# Arguments and assignments
arguments = sys.argv[1:] # Fetch arguments, discarding script name
c = socket.socket()
rID = arguments[0]
num_acc = int(arguments[1])
host = arguments[2]
port = 8995 # Well-known
rSeq=0
oVal= -1
sSeq=0
ReaderList = []

# Alert
print("Assigned reader ID:",rID,"\nNumber of accesses:", num_acc, "\nServer:",host,":",port)

# Connect to host on the specified port
c.connect((host, port))

for iteration in range (0,num_acc):
	
	# Read request procedure
	c.sendall("Client: Read Request.".encode())
	rSeq = c.recv(1024).decode()
	c.sendall("separaor".encode())
	oVal = c.recv(1024).decode()
	c.sendall(rID.encode())
	sSeq = c.recv(1024).decode()
	ReaderList.append((rSeq,sSeq,oVal))
	sleep(rand_float(0,10))


# Create log file 
with open(''.join(["log",rID,".txt"]),'a+' ) as output_file:

	output_file.write(''.join(["Client Type: Reader \nClient Name: ",rID,"\nrSeq\tsSeq\toVal\n"]))

	# Iterate through the Readerlist and write to file
	for row in ReaderList:
		for item in row:
			output_file.write(''.join([str(item) , "\t"]))
		output_file.write("\n")	
	output_file.close()

