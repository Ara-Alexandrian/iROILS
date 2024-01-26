import paramiko
import time

# Update these variables with your actual server details
hostname = '192.168.1.47'
username = 'root'
password = '2Apple@@'
container_name = 'ollama'

# Establish an SSH client and connect to the server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

# Command to stop and start the Docker container
stop_command = f'docker stop {container_name}'
start_command = f'docker start {container_name}'

try:
    stdin, stdout, stderr = ssh.exec_command(stop_command)
    print(stdout.read().decode())  # Print the output of the command
    print(stderr.read().decode())  # Print any error messages
    time.sleep(10)  # Corrected to time.sleep
    stdin, stdout, stderr = ssh.exec_command(start_command)
    print(stdout.read().decode())  # Print the output of the command
    print(stderr.read().decode())  # Print any error messages
finally:
    ssh.close()  # Close the SSH connection

print(f"The container '{container_name}' should be restarting now.")
