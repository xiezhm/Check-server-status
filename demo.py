#!/usr/bin/env python
# _*_coding:utf-8_*_
import paramiko,ConfigParser,threading,paramiko.ssh_exception

class Paramiko(object):
	"""docstring for Paramiko"""
	def __init__(self,item):
		self.config = ConfigParser.ConfigParser()
		self.config.read('service.conf')
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.item = item

	def connect(self,command):
		try:
			self.client.connect(hostname=self.config.get(self.item,'ip'),
							port=self.config.getint(self.item,'port'),
							username=self.config.get(self.item,'user'),
							password=self.config.get(self.item,'passwd'),
							timeout=5)
		except (paramiko.AUTH_FAILED,paramiko.BadHostKeyException) as e:
			print self.config.get(self.item,'ip'),e
		else:
			stdin,stdout,stderr = self.client.exec_command(command,timeout=2,bufsize=4096)
			cmd_result = stdout.read(),stderr.read()
			for line in cmd_result:
				return line
		finally:
			pass

	def service_men(self):
		men_total = int(self.connect("cat /proc/meminfo|grep 'MemTotal'|awk '{print $2}'"))/1024
		men_free = int(self.connect("cat /proc/meminfo|grep 'MemFree'|awk '{print $2}'"))/1024
		return "men_total:%s\nmen_free:%s\nmen_use:%s"%(men_total,men_free,float(men_total-men_free)/men_total)

	def service_uptime(self):
		runtime = self.connect("uptime |awk -F',' '{print $1,$2,$3}'")
		return "service_uptime:%s"%runtime

	def service_disk(self):
		disk_info = self.connect("df -h|sed -n '2,$p'")
		disk_warn = self.connect("df -P |sed -n '2,$p'|awk '{print $(NF-1),$NF}' |sed 's/%//g'|awk '{if($1>= 80){print $0}}'")
		return "service_disk:%s\nservice_warn:%s"%(disk_info,disk_warn)

	def cpu_info(self):
		cpu_mode = self.connect("cat /proc/cpuinfo |grep 'model name'|awk -F':' '{print $2}'|head -1")
		cpu_core = self.connect("cat /proc/cpuinfo |grep 'processor'|wc -l")
		return "cpu_mode:%s\ncpu_core:%s"%(cpu_mode,cpu_core)

	def __del__(self):
		print("=======^^^^^"+self.config.get(self.item,'ip')+":^^^^^^====================")


def test(item):
	try:
		service = Paramiko(item)
		service_cpu = service.cpu_info()
		service_disk = service.service_disk()
		service_uptime = service.service_uptime()
		service_men = service.service_men()
		print service_cpu+'\n'+service_disk+'\n'+service_uptime+'\n'+service_men
	except Exception as e:
		print e

def run():
	try:
		config = ConfigParser.ConfigParser()
		config.read("service.conf")
		threads = []
		for item in config.sections():
			items=threading.Thread(target=test(item))
			threads.append(items)
		for t in threads:
			t.setDaemon(True)
			t.start()
		t.join()
	except Exception as e:
		pass

if __name__ == "__main__":
	run()








