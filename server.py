import sys
import socket
from threading import Thread
from time import sleep
import threading

# Intermediate log lists
ReaderList = []
WriterList = []

# Thread lock
lock = threading.Lock()

# Global variables
rSeq = 1
sSeq = 0
rNum = 1
rID = 0
wID = 0
oVal= -1

# Fetch maximum number of clients to serve
max_clients = int(sys.argv[1])

# Server port -- Assumed to be well-known
port = 8995


def handle_request(c):

	while True:

		# Wait until data is received.
		data = c.recv(1024).decode()

		global rID, wID, rSeq, sSeq, rNum, oVal, ReaderLine, ReaderList, WriterLine, WriterList, max_trials

		if data == "Client: Read Request.":
			
			lock.acquire()
			c.sendall(str.encode(str(rSeq)))  
			rSeq+=1
			c.recv(1024).decode()
			rNum+=1
			lock.release()
			c.sendall(str.encode(str(oVal)))
			lock.acquire()
			rID=c.recv(1024).decode().strip()
			print("-- Handling READ request from reader #" + rID)	
			sSeq+=1
			rNum=rNum-1
			c.sendall(str.encode(str(sSeq))) 
			ReaderList.append((sSeq,oVal,rID,rNum))
			lock.release()
			

		elif data == "Client: Write Request.":
			lock.acquire()
			c.sendall(str.encode(str(rSeq))) 
			rSeq+=1 
			lock.release()
			lock.acquire()
			wID=c.recv(1024).decode().strip()
			oVal = wID
			print("-- Handling WRITE request from writer #" + wID)	
			WriterList.append((sSeq,oVal,wID))
			sSeq+=1
			c.sendall(str.encode(str(sSeq))) 
			lock.release()

	# Close
	c.close()


if __name__ == "__main__":

	# Number of clients that have been served 
	current_clients = 0

	# Create socket
	mysocket = socket.socket()
	# Prevent socket.error: [Errno 98] Address already in use
	mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	mysocket.bind(("0.0.0.0", port))
	mysocket.listen(5)

	# Thread pool for joining 
	threads = []
	
	# Alert
	print("# === Server started on port:",port,"=== #")
	
	# Run server indefinitely 
	while True:
		c, addr = mysocket.accept()
		current_clients+=1
		thread = Thread(target = handle_request, args = (c,))
		thread.daemon = True
		thread.start()
		threads.append(thread)
		print("Currently serving",current_clients,"out of",max_clients,"clients")
		if current_clients == max_clients:
			break
	
	# Wait for all threads to complete
	for thread_instance in threads:
		thread_instance.join(timeout=10.0)
	
	# Close socket
	mysocket.close()
	
	# Iterate through the Readerlist and write to file
	with open("serverlog.txt",'a+' ) as output_file:

		# Write log files for readers
		output_file.write("Readers:\nsSeq\toVal\trID\trNum\n")
		for row in ReaderList:
			for item in row:
				output_file.write(''.join([str(item) , "\t\t"]))
			output_file.write("\n")	
		
		# Write log files for writers
		output_file.write("Writers:\nsSeq\toVal\twID\n")	
		for row in WriterList:
			for item in row:
				output_file.write(''.join([str(item) , "\t\t"]))
			output_file.write("\n")	
		output_file.close()

	# Exit gracefully
	print("Gracefully exiting.. Good bye.")
	sys.exit(0)