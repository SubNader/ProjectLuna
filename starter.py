import paramiko
from time import sleep

# Debug mode
debug = False

# Read in the properties file
parameters = dict()
with open('system.properties') as config_file:
	for line in config_file:
		property_line = line.strip().split('=')
		# Fetch parameter name and value
		full_param_name = property_line[0].split('.')
		param_name = full_param_name[-1]
		param_value = property_line[1]
		# Handle the RMI registry parameter
		if full_param_name[-2] == 'rmiregistry':
			param_name = 'rmi_' + param_name
		# Append parameter
		parameters[param_name] = param_value

# Parse the properties file components
server_ip = parameters['server']
rmi_port = parameters['rmi_port']
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
		if debug:
			print("Fetched Reader", id, "| IP:", readers[id])
	
	# Handle writers
	elif(parameter.startswith("writer")):
		id = parameter[len("writer"):]
		writers[id] = parameters[parameter]
		if debug:
			print("Fetched Writer", id, "| IP:", writers[id])

# Server starting component
server_username = ""
server_password = "" 
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username=server_username, password=server_password)

# Prepare command
command = "nohup python3 -u ~/ProjectLuna/server.py"

# Start server over SSH
max_clients = (len(readers)+len(writers))
server_command = command+' '+str(max_clients)+' '+server_ip+' '+parameters['rmi_port']+' </dev/null  >>~/ProjectLuna/server.log 2>&1 &'
if debug:
	print("Server run command:", server_command)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(server_command)

# Alert
print("Started RMI server on",server_ip,":",rmi_port)

# Close connection
ssh.close()

# Sleep for a bit before starting clients
sleep(5)

# Set reader and writer script commands
reader_command = "nohup python3 ~/ProjectLuna/reader.py"
writer_command = "nohup python3 ~/ProjectLuna/writer.py"

# SSH credentials
ssh_username=""
ssh_password=""

# Start readers
for  reader_id, reader_address in readers.items():
	print("Starting reader", reader_id,"client on", reader_address)
	
	# Start reader over SSH
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(reader_address, username=ssh_username, password=ssh_password)
	final_reader_command = reader_command+' '+reader_id+' '+parameters['numberOfAccesses']+' '+parameters['server']+' '+parameters['rmi_port']+' </dev/null >>~/ProjectLuna/reader_'+reader_id+'.log 2>&1 &'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(final_reader_command)
	
	# Alert
	if debug:
		print("Reader run command:", final_reader_command)
	
	# Close connection
	ssh.close()

# Start writers
for writer_id, writer_address in writers.items():
	print("Starting writer", writer_id,"client on", writer_address)

	# Start writer over SSH
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(writer_address, username=ssh_username, password=ssh_password)
	final_writer_command = writer_command+' '+writer_id+' '+parameters['numberOfAccesses']+' '+parameters['server']+' '+parameters['rmi_port']+' </dev/null >>~/ProjectLuna/writer_'+writer_id+'.log 2>&1 &'
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(final_writer_command)
	
	# Alert
	if debug:
		print("Writer run command:", final_writer_command)
	
	# Close connection
	ssh.close()
