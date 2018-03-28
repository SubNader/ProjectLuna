import sys
import threading
import subprocess
from time import sleep
import Pyro4 as pyro
pyro.config.COMMTIMEOUT=10
pyro.config.THREADPOOL_SIZE=100

# Global variables
rSeq = 1
sSeq = 0
rNum = 1
rID = 0
wID = 0
oVal= -1
clients_served = 0
keep_running = True
# Intermediate log lists
ReaderList = []
WriterList = []

# Thread lock
lock = threading.Lock()

@pyro.expose
class client_handler:
	
	def handle_reader(self, reader_id):
		
		global lock, oVal, rNum, rSeq, sSeq, ReaderList

		lock.acquire() 
		rSeq+=1
		rNum+=1
		lock.release()
		lock.acquire()	
		sSeq+=1
		ReaderList.append((sSeq,oVal,reader_id,rNum))
		rNum=rNum-1
		lock.release()
		
		return rSeq, sSeq, oVal
	
	def handle_writer(self, writer_id):

		global lock, oVal, rNum, rSeq, sSeq, WriterList

		lock.acquire()
		rSeq+=1 
		lock.release()
		lock.acquire()
		oVal = writer_id	
		WriterList.append((sSeq,oVal,writer_id))
		sSeq+=1
		lock.release()

		return rSeq,sSeq

	def close(self):

		global clients_served

		lock.acquire()
		clients_served+=1
		lock.release()
		if clients_served>=max_clients:
			global keep_running
			keep_running = False

# Check if all clients have been served
def check_status():
	return keep_running

if __name__ == "__main__":

	# Fetch maximum number of clients to serve
	global max_clients
	max_clients = int(sys.argv[1])

	# Server host 

	rmi_host = sys.argv[2]

	# Server port
	rmi_port = int(sys.argv[3])

	# Log alerts to file
	log_alerts = False

	# Run nameserver
	nameserver_command = 'nohup sudo pyro4-ns -n 0.0.0.0 -p '+str(rmi_port)+' </dev/null >out 2>&1 &'
	subprocess.call(nameserver_command, shell=True)
	# Run server and get the nameserver proxy
	server_daemon = pyro.Daemon(host=rmi_host)
	sleep(5)
	nameserver = pyro.locateNS(host=rmi_host, port=rmi_port)
	# Register the client handler class
	client_handler_uri = server_daemon.register(client_handler)
	nameserver.register('client_handler', client_handler_uri)

	# Serve requests until termination
	server_daemon.requestLoop(check_status)
	server_daemon.close()
	
	# Write log files for Readers
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
