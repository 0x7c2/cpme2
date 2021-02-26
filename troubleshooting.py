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


