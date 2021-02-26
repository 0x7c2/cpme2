#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import diag
import os, time
import func

class diag_troubleshooting_f2f_worker(diag):
	page         = "Troubleshooting.F2F Worker"
	title        = "Debug F2F Worker Connections"
	isFirewall   = True
	isManagement = False
	isClusterXL  = False
	minVersion   = 8020

	content = ['This command enables:', 'echo 1 > /proc/cpkstats/fw_worker_[workerid]_stats', '', 'and prints the results:', 'cat /proc/cpkstats/fw_worker_[workerid]_stats', '', 'last but no least, it will disable debug:', 'echo 0 > /proc/cpkstats/fw_worker_[workerid]_stats']
	isTable = False

	workers = []

	def change_f2f_stats(self, worker_id, val):
		self.debug(3, "echo " + str(val) + " > /proc/cpkstats/fw_worker_" + str(worker_id) + "_stats")
		os.system("echo " + str(val) + " > /proc/cpkstats/fw_worker_" + str(worker_id) + "_stats")

	def getall_f2f_worker(self):
		workers = []
		for filename in os.listdir("/proc/cpkstats/"):
			if "fw_worker_" in filename and "_stats" in filename and not "raw" in filename:
				workers.append(int(filename.replace("fw_worker_","").replace("_stats","")))
		return workers

	def enable_disable(self, action = 0):
		self.workers = self.getall_f2f_worker()
		for worker in self.workers:
			self.change_f2f_stats(worker, action)

	def set_enable(self):
		self.isTable = True
		self.enable_disable(1)

	def set_disable(self):
		self.enable_disable(0)

	def run_loop(self):
		self.content = []
		stats = []
		stats_sort = []
		self.content.append([ "Worker", "Type", "Cycles", "Time ago", "Proto", "Source", "SPORT", "Destination", "DPORT" ])
		for worker in self.workers:	
			for line in func.tail_and_head('/proc/cpkstats/fw_worker_' + str(worker) + '_stats', 18, 16):
				raw = str(line).replace('\t','').replace('\n','')
				raw = raw.split()
				s_worker  = worker
				s_type    = raw[0].replace(':','')
				s_cycles  = int(raw[1])
				s_timeago = int(raw[2])
				raw = raw[3:]
				s_data    = ' '.join(raw)
				new = { 'worker': s_worker, 'type': s_type, 'cycles': s_cycles, 'timeago': s_timeago, 'data': s_data }
				stats.append(new)
		stats_sort = sorted(stats, key=lambda k: k['cycles'], reverse=True)
		for s in stats_sort:
			if "," in s["data"]:
				data = s["data"].replace("<","").replace(">","").split(",")
				if len(data) > 4:
					proto = str(data[5]).strip()
					if proto == "1":
						proto = "ICMP"
					if proto == "6":
						proto = "TCP"
					if proto == "17":
						proto = "UDP"
					src = data[1].strip()
					src_p = data[2].strip()
					dst = data[3].strip()
					dst_p = data[4].strip()
					self.content.append([ str(s["worker"]), str(s["type"]), str(s["cycles"]), str(s["timeago"]), proto, src, src_p, dst, dst_p ])



class diag_troubleshooting_clusterxl_state(diag):
	page         = "Troubleshooting.ClusterXL State"
	title        = "Show ClusterXL State"
	isFirewall   = True
	isManagement = False
	isClusterXL  = True
	minVersion   = 8020

	content      = [ 'Starting Output...' ]
	isDebugCommand = False
	isTable = False

	def run_loop(self):
		out, err = func.execute_command('cphaprob state ; echo ; cphaprob -a if')
		self.content = out.read().split('\n')



class diag_troubleshooting_throughput(diag):
	page         = "Troubleshooting.Throughput"
	title        = "Show troughput"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020

	content      =  ["Please wait, while starting Output..."]
	isDebugCommand = False
	isTable = False

	last_rx_bytes = {}
	last_tx_bytes = {}

	rx_bytes = {}
	tx_bytes = {}

	rx_sum = {}
	tx_sum = {}

	ipaddr = {}

	nics = []

	def run_loop(self):
		showme = True
		# grab all active nics
		if len(self.nics) < 1:
			out, err = func.execute_command('ifconfig | grep HWaddr')
			for data in out.read().split('\n'):
				if "Ethernet" in data:
					raw = data.split()
					nic = raw[0].strip()
					self.nics.append(nic)
		# grab ip address from interface
		if len(self.ipaddr) < 1:
			for nic in self.nics:
				if nic not in self.ipaddr:
					ipa = "0.0.0.0"
					out, err = func.execute_command('ifconfig ' + nic + ' | grep "inet addr"')
					data = out.read()
					if data != "":
						data = data.split(':')[1]
						ipa = data.split(' ')[0]
					self.ipaddr[nic] = ipa
		# grab rx and tx bytes
		for nic in self.nics:
			out, err = func.execute_command('cat /sys/class/net/' + nic + '/statistics/rx_bytes')
			data = out.read()
			if nic not in self.last_rx_bytes:
				showme = False
			else:
				self.rx_bytes[nic] = int(data.strip()) - int(self.last_rx_bytes[nic])
			self.last_rx_bytes[nic] = int(data.strip())

			out, err = func.execute_command('cat /sys/class/net/' + nic + '/statistics/tx_bytes')
			data = out.read()
			if nic not in self.last_tx_bytes:
				showme = False
			else:
				self.tx_bytes[nic] = int(data.strip()) - int(self.last_tx_bytes[nic])
			self.last_tx_bytes[nic] = int(data.strip())

		# grab rx and tx sum bytes
		for nic in self.nics:
			out, err = func.execute_command('ifconfig ' + nic + ' | grep byte')
			data = out.read()
			data = data.split(':')
			self.rx_sum[nic] = data[1].split()[1][1:] + " " + data[1].split()[2][:-1]
			self.tx_sum[nic] = data[2].split()[1][1:] + " " + data[2].split()[2][:-1]

		if showme:
			self.isTable = True
			self.content = []
			self.content.append([ "Interface" , "IP-Address" , "RX Rate", "TX Rate", "RX Sum", "TX Sum" ])
			for nic in self.nics:
				nic_rx_r_txt = ""
				nic_tx_r_txt = ""
				nic_ip = self.ipaddr[nic]
				nic_rx_r = self.rx_bytes[nic] * 8
				if nic_rx_r > (1024*1024) and nic_rx_r_txt == "":
					nic_rx_r_txt = str(round(nic_rx_r/(1024*1024))) + " MBit"
				if nic_rx_r > (1024) and nic_rx_r_txt == "":
					nic_rx_r_txt = str(round(nic_rx_r/(1024))) + " KBit"
				if nic_rx_r <= (1024) and nic_rx_r_txt == "":
					nic_rx_r_txt = str(round(nic_rx_r)) + " Bit"
				nic_tx_r = self.tx_bytes[nic] * 8
				if nic_tx_r > (1024*1024) and nic_tx_r_txt == "":
					nic_tx_r_txt = str(round(nic_tx_r/(1024*1024))) + " MBit"
				if nic_tx_r > (1024) and nic_tx_r_txt == "":
					nic_tx_r_txt = str(round(nic_tx_r/(1024))) + " KBit"
				if nic_tx_r <= (1024) and nic_tx_r_txt == "":
					nic_tx_r_txt = str(round(nic_tx_r)) + " Bit"
				nic_rx_s = str(self.rx_sum[nic])
				nic_tx_s = str(self.tx_sum[nic])
				self.content.append([ nic , nic_ip, nic_rx_r_txt, nic_tx_r_txt, nic_rx_s, nic_tx_s ])

