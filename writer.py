import sys
import socket
from time import sleep
from random import uniform as rand_float

# Arguments and assignments
arguments = sys.argv[1:] # Fetch arguments, discarding script name
c = socket.socket()
wID = arguments[0]
num_acc = int(arguments[1])
host = arguments[2]
port = 8995 # Well-known
rSeq=0
sSeq=0
WriterList = []

# Alert
print("Assigned writer ID:",wID,"Number of accesses:", num_acc,"Server:",host,":",port)

# Connect to host on the specified port
c.connect((host, port)) 


for iteration in range (0,num_acc):

	# Write request procedure
	c.send("Client: Write Request.".encode())
	rSeq = c.recv(1024).decode()
	c.send(bytes(wID.encode()))
	sSeq = c.recv(1024).decode()
	WriterList.append((rSeq,sSeq))
	sleep(rand_float(0,10))   

# Create log file 
with open(''.join(["log",wID,".txt"]),'a+' ) as output_file:

	output_file.write(''.join(["Client Type: Writer \nClient Name: ",wID,"\nrSeq\tsSeq\n"]))

	# Iterate through the WriterList and write to file
	for row in WriterList:
		for item in row:
			output_file.write(''.join([str(item) , "\t"]))
		output_file.write("\n")	
	output_file.close()