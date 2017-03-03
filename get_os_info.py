#!python
#==========================================================#
# sjdillon
# gather specs and details from servers
# - use pre install to confirm appropriate specs
# - use post installs to confirm software versions
# - output formatted for quick wiki pasting
#==========================================================#
import paramiko
from paramiko import SSHClient
import StringIO

uname='myname'
cert='C:\xxxx\.ssh\id_rsa'

f = open(cert)
s = f.read()
keyfile = StringIO.StringIO(s)
key = paramiko.RSAKey.from_private_key(keyfile)

#connect
def ssh_connect(host,uname, pw=None):
	ssh = SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.load_system_host_keys()
	ssh.connect(host,username=uname, pkey=key)
	return ssh

def run_it(command,ssh):
	(stdin, stdout, stderr) = ssh.exec_command(command)
	for line in stderr.readlines():
		if line:
			print 'error: %s' % line
	for line in stdout.readlines():
		return line

def get_os_info(host, uname,dse=False):
	ssh=ssh_connect(host,uname)
	cpu_cnt=run_it("lscpu | grep \"CPU(s):\" | gawk '{print $2}'",ssh)
	os_version=run_it('cat /etc/redhat-release',ssh)
	bit=run_it("uname -m",ssh)
	cpu_type=run_it("cat /proc/cpuinfo | grep 'model name' | uniq",ssh)
	space=run_it("df -h /opt | grep /opt | gawk '{print $1}'",ssh)
	ntp=run_it("ntpstat",ssh)
	if dse:
		dse=run_it("dse -v",ssh)
		cassandra=run_it("dse cassandra -v",ssh)
		java=run_it("java -version 2>&1",ssh)

	ram=run_it("free -g | grep Mem | awk '{print $2}'",ssh)
	servername=run_it("hostname",ssh)
	ssh.close()	
	print '*host:* %s' % (host)
	print '*server:* %s' % (servername.replace("\n", ""))
	print '*cpus(%s):* %s' % (cpu_cnt.replace("\n", ""),cpu_type.replace('model name	: ','').replace("\n", ""))
	print '*bit:* %s' % (bit.replace("\n", ""))
	print '*os:* %s' % (os_version.replace("\n", ""))
	if space:
		print '*disk:* %s' % (space.replace("\n", ""))
	print '*ram:* %sGB' % (ram.replace("\n", ""))
		
	if ntp:
		print '*ntp:* %s' % (ntp.replace("\n", ""))
	if dse:
		print '*java version:* %s' % (java.replace("\n", "").strip("java version").strip('"'))
		print '*dse_version:* %s' % (dse.replace("\n", ""))	
		print '*cassandra_version:* %s' % (cassandra.replace("\n", ""))		
	print ''	
		

servers=['xxxxxxxs01.xxxx.xxxx.com','xxxxxxxs02.xxxx.xxxx.com','xxxxxxxs03.xxxx.xxxx.com']
for host in servers:	
 	get_os_info(host, uname, dse=True)
