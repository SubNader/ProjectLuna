# Starter component - Starts the clients and servers over SSH 

# Imports
import paramiko
import subprocess

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
ssh.connect(server_ip, username="root", password="")

# Prepare command
directory = ""
command = ' '.join(["nohup python3",directory])
server_script_filename = "server.py"

# Start server over SSH
max_clients = (len(readers)+len(writers))
server_command = ''.join([command, server_script_filename,' ', str(max_clients), ' >/dev/null 2>&1 &'])
print(server_command)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(server_command)

for line in iter(ssh_stdout.readline,""):
	print(line)
print("Started server on",server_ip,":",server_port)


# Set reader and writer script filenames
reader_script_filename = "reader.py"
writer_script_filename = "writer.py"
directory = ""
command = ''.join(["nohup python3", ' ', directory])

# Start readers
for  reader_id, reader_address in readers.items():
	print("Starting reader", reader_id,"client on", reader_address)
	
	# Start reader over SSH | Assuming password-less root access is enabled

	ssh.connect(reader_address, username="root", password="")
	reader_command = ''.join([command , reader_script_filename,' ', reader_id,' ', parameters['numberOfAccesses'],' ',  parameters['server'], ' >/dev/null 2>&1 &'])
	print(reader_command)

	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(reader_command)
	for line in iter(ssh_stdout.readline,""):
		print(line)

# Start writers
for writer_id, writer_address in writers.items():
	print("Starting a writer", writer_id,"client on", writer_address)

	# Start writer over SSH | Assuming password-less root access is enabled
	ssh.connect(writer_address, username="root", password="")
	writer_command = ''.join([command, writer_script_filename,' ', writer_id,' ', parameters['numberOfAccesses'],' ', parameters['server'], ' >/dev/null 2>&1 &'])
	print(writer_command)
	
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(writer_command)
	for line in iter(ssh_stdout.readline,""):
		print(line)