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

# Log alerts to file
log_alerts = False

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
			if log_alerts:
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
			if log_alerts:
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
	if log_alerts:
		print("# === Server started on port:",port,"=== #")
	
	# Run server indefinitely 
	while True:
		c, addr = mysocket.accept()
		current_clients+=1
		thread = Thread(target = handle_request, args = (c,))
		thread.daemon = True
		thread.start()
		threads.append(thread)
		if log_alerts:
			print("Currently serving",current_clients,"out of",max_clients,"clients")
		if current_clients == max_clients:
			break
	
	# Wait for all threads to complete
	for thread_instance in threads:
		thread_instance.join(timeout=10.0)
	
	# Close socket
	mysocket.close()
	
	# Iterate through the Readerlist and write to file

	# Write log files for readers
	print("Readers:\n\nsSeq\toVal\trID\trNum")
	for row in ReaderList:
		row_string = ''
		for item in row:
			row_string+=(str(item)+'\t'*2)
		print(row_string)

	# Write log files for writers
	print("\nWriters:\n\nsSeq\toVal\twID")	
	for row in WriterList:
		row_string = ''
		for item in row:
			row_string+=(str(item)+'\t'*2)
		print(row_string)

	# Exit gracefully
	if log_alerts:
		print("Gracefully exiting.. Good bye.")
	sys.exit(0)
