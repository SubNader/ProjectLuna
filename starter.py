# Starter component - Starts the clients and servers over SSH 

# Imports
import paramiko

# Read in the properties file
parameters = dict()
with open('system.properties') as config_file:
	for line in config_file:
		property_line = line.strip().split('=')
		# Fetch parameter name and value
		param_name = property_line[0].split('.')[-1]
		param_value = property_line[1]
		# Print parameter name and value
		parameters[param_name]=param_value

# Parse the properties file components
server_ip = parameters['server']
server_port = parameters['port']
n_readers = parameters['numberOfReaders']
n_writers = parameters['numberOfWriters']

# Fetch readers and writers
readers = dict()
writers = dict()
for parameter in parameters:

	# Handle readers
	if(parameter.startswith("reader")):
		id = parameter[len("reader"):]
		readers[id] = parameters[parameter]
		print("Fetched Reader", id, "| IP:", readers[id])
	
	# Handle writers
	elif(parameter.startswith("writer")):
		id = parameter[len("writer"):]
		writers[id] = parameters[parameter]
		print("Fetched Writer", id, "| IP:", writers[id])


# Server starting component

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.connect(server_ip, username="", password="")

# Prepare command
command = "nohup python3 -u ~/ProjectLuna/server.py"

# Start server over SSH
max_clients = (len(readers)+len(writers))
server_command = command+' '+str(max_clients)+' </dev/null >/dev/null 2>&1 &'
print("Server run command:", server_command)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(server_command)

# Alert
print("Started server on",server_ip,":",server_port)

# Close connection
ssh.close()

# Set reader and writer script commands
reader_command = "nohup python3 ~/ProjectLuna/reader.py"
writer_command = "nohup python3 ~/ProjectLuna/writer.py"

# SSH credentials
ssh_username=""
ssh_password=""

# Start readers
for  reader_id, reader_address in readers.items():
	print("Starting a reader", reader_id,"client on", reader_address)
	
	# Start reader over SSH | Assuming password-less root access is enabled
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.connect(reader_address, username=ssh_username, password=ssh_password)
	final_reader_command = reader_command+' '+reader_id+' '+parameters['numberOfAccesses']+' '+parameters['server']+' </dev/null >/dev/null 2>&1 &'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(final_reader_command)
	# Alert
	print("Reader run command:", final_reader_command)
	
	# Close connection
	ssh.close()

# Start writers
for writer_id, writer_address in writers.items():
	print("Starting a writer", writer_id,"client on", writer_address)

	# Start writer over SSH | Assuming password-less root access is enabled
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.connect(writer_address, username=ssh_username, password=ssh_password)
	final_writer_command = writer_command+' '+writer_id+' '+parameters['numberOfAccesses']+' '+parameters['server']+' </dev/null >/dev/null 2>&1 &'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(final_writer_command)
	
	# Alert
	print("Writer run command:", final_writer_command)
	
	# Close connection
	ssh.close()