#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func

class check_gaia_scheduled_backup(check):
	page         = "GAiA.0verview"
	category     = "GAiA Settings"
	title        = "Scheduled Backup Config"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "func.gaia_get_value('backup-scheduled')"
	isCommand    = False

	def run_check(self):
		if self.commandOut:
			self.add_result(self.title, 'PASS', '')
		else:
			self.add_result(self.title, 'WARN', 'not configured')
		

class check_gaia_check_snapshots(check):
	page         = "GAiA.0verview"
	category     = "Environment"
	title        = "Existing GAiA Snapshots"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "lvs | grep -v 'wi-ao'  | tail -n +2"
	isCommand    = True

	def run_check(self):
		found = False
		for o in self.commandOut:
			temp = ' '.join(o.split())
			cols = temp.split(' ')
			if len(cols)>1:
				found = True
				name = cols[0].strip(' ').strip('\n')
				vg   = cols[1].strip(' ').strip('\n')
				attr = cols[2].strip(' ').strip('\n')
				size = cols[3].strip(' ').strip('\n')
				detail = vg + " / " + name + " (" + size + ")"
			if "hwdiag" in name or "fcd_GAIA" in name:
				self.add_result(self.title, 'INFO', detail)
			else:
				self.add_result(self.title, 'WARN', detail)
		if not found:
			self.add_result(self.title, 'INFO', '')


class check_gaia_check_cpuse_agent_version(check):
	page         = "GAiA.CPUSE"
	category     = "Agent"
	title        = "Deployment Agent Version"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "$DADIR/bin/da_cli da_status"
	isCommand    = True

	def run_check(self):
		found = False
		for o in self.commandOut:
			if 'up to date' in o:
				found = True
				self.add_result(self.title, 'PASS', '')
		if not found:
			self.add_result(self.title, 'WARN', 'new version available')


class check_gaia_check_cpuse_agent_pending_reboot(check):
	page         = "GAiA.CPUSE"
	category     = "Agent"
	title        = "Deployment Agent Pending Reboot"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "$DADIR/bin/da_cli is_pending_reboot"
	isCommand    = True

	def run_check(self):
		found = False
		for o in self.commandOut:
			if 'no reboot' in o:
				found = True
				self.add_result(self.title, 'PASS', '')
		if not found:
			self.add_result(self.title, 'WARN', 'Reboot pending!')


class check_gaia_check_cpuse_agent_packages(check):
	page         = "GAiA.CPUSE"
	category     = "Packages"
	title        = "Packages available for install"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "$DADIR/bin/da_cli packages_info status=available"
	isCommand    = True

	def run_check(self):
		found = False
		for o in self.commandOut:
			if 'filename' in o:
				tmp = o.split(':')[1].replace('"','').replace(',','')
				self.add_result(self.title, 'WARN', tmp)
				found = True
		if not found:
			self.add_result(self.title, 'PASS', '')


class check_gaia_check_proxy_settings(check):
	page         = "GAiA.0verview"
	category     = "GAiA Settings"
	title        = "Proxy Configuration"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "func.gaia_get_value('proxy:ip-address')"
	isCommand    = False

	def run_check(self):
		if self.commandOut:
			proxy_port = func.gaia_get_value('proxy:port')
			self.add_result(self.title, 'INFO', self.commandOut + ':' + proxy_port)
		else:
			self.add_result(self.title, 'INFO', 'direct')


class check_gaia_ntp(check):
	page         = "GAiA.0verview"
	category     = "GAiA Settings"
	title        = "NTP - Time and Date"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "ntpstat"
	isCommand    = True

	def run_check(self):
		found = False
		for o in self.commandOut:
			if 'synchronised to' in o:
				self.add_result(self.title, "PASS", "")
				found = True
		if not found:
			self.add_result(self.title, "FAIL", "")


class check_gaia_dns_external_checkpoint(check):
	page         = "GAiA.Connectivity"
	category     = "DNS Resolver"
	title        = "DNS Lookup [checkpoint.com]"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "nslookup checkpoint.com | awk 'NR>3 { print $0 }'"
	isCommand    = True

	def run_check(self):	
		passme = False
		detail = ""
		for line in self.commandOut:
			if 'Address:' in line:
				if '209' in line:
					passme = True
					detail = line.strip()
		if passme:
			self.add_result(self.title, 'PASS', detail)
		else:
			self.add_result(self.title, 'FAIL', detail)


class check_gaia_dns_external_heise(check):
	page         = "GAiA.Connectivity"
	category     = "DNS Resolver"
	title        = "DNS Lookup [heise.de]"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "nslookup heise.de | awk 'NR>3 { print $0 }'"
	isCommand    = True

	def run_check(self):
		passme = False
		detail = ""
		for line in self.commandOut:
			if 'Address:' in line:
				if '193' in line:
					passme = True
					detail = line.strip()
		if passme:
			self.add_result(self.title, 'PASS', detail)
		else:
			self.add_result(self.title, 'FAIL', detail)
	


class check_gaia_z_check_connectivity(check):
	page         = "GAiA.Connectivity"
	category     = "Check Point Services"
	title        = "Connection"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		proxy = ""
		urls = []
		urls.append(['http://cws.checkpoint.com/APPI/SystemStatus/type/short','Social Media Widget Detection'])
		urls.append(['http://cws.checkpoint.com/URLF/SystemStatus/type/short','URL Filtering Cloud Categorization'])
		urls.append(['http://cws.checkpoint.com/AntiVirus/SystemStatus/type/short','Virus Detection'])
		urls.append(['http://cws.checkpoint.com/Malware/SystemStatus/type/short','Bot Detection'])
		urls.append(['https://updates.checkpoint.com/','IPS Updates'])
		urls.append(['http://dl3.checkpoint.com','Download Service Updates '])
		urls.append(['https://usercenter.checkpoint.com/usercenter/services/ProductCoverageService','Contract Entitlement '])
		urls.append(['https://usercenter.checkpoint.com/usercenter/services/BladesManagerService','Software Blades Manager Service'])
		urls.append(['http://resolver1.chkp.ctmail.com','Suspicious Mail Outbreaks'])
		urls.append(['http://download.ctmail.com','Anti-Spam'])
		urls.append(['http://te.checkpoint.com','Threat Emulatin'])
		urls.append(['http://teadv.checkpoint.com','Threat Emulation Advanced'])
		urls.append(['http://kav8.zonealarm.com/version.txt','Deep inspection'])
		urls.append(['http://kav8.checkpoint.com','Traditional Anti-Virus'])
		urls.append(['http://avupdates.checkpoint.com/UrlList.txt','Traditional Anti-Virus, Legacy URL Filtering'])
		urls.append(['http://sigcheck.checkpoint.com/Siglist2.txt','Download of signature updates'])
		urls.append(['http://secureupdates.checkpoint.com','Manage Security Gateways'])
		urls.append(['https://productcoverage.checkpoint.com/ProductCoverageService','Makes sure the machines contracts are up-to-date'])
		urls.append(['https://sc1.checkpoint.com/sc/images/checkmark.gif','Download of icons and screenshots from Check Point media storage servers'])
		urls.append(['https://sc1.checkpoint.com/za/images/facetime/large_png/60342479_lrg.png','Download of icons and screenshots from Check Point media storage servers'])
		urls.append(['https://sc1.checkpoint.com/za/images/facetime/large_png/60096017_lrg.png','Download of icons and screenshots from Check Point media storage servers'])
		urls.append(['https://push.checkpoint.com','Push Notifications '])
		urls.append(['http://downloads.checkpoint.com','Download of Endpoint Compliance Updates'])

		for url in urls:
			out, err = func.execute_command('curl_cli -Lisk ' + proxy + url[0] + ' | head -n1')
			data = out.read().strip('\n').strip(' ')
			if "OK" in data or "Found" in data or "Moved" in data or "Connection established" in data:
				state = "PASS"
				detail = ""
			else:
				state = "FAIL"
				detail = data
			self.add_result(self.title + " [" + url[1] + "]", state, detail)


class check_gaia_interface_stats(check):
	page         = "GAiA.Networking"
	category     = "Statistics"
	title        = "Interface statistics"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		values_rx = ["rx_dropped", "rx_crc_errors", "rx_errors", "rx_fifo_errors", "rx_frame_errors", "rx_length_errors", "rx_missed_errors", "rx_over_errors"]
		values_tx = ["tx_aborted_errors", "tx_carrier_errors", "tx_dropped", "tx_errors", "tx_fifo_errors", "tx_heartbeat_errors", "tx_window_errors"]
		out, err = func.execute_command('ls -1 /sys/class/net | grep -vE "(lo|bond|vpn|sit|\.)"')
		for line in out:
			interface = line.strip('\n')
			i = 0
			error = False
			while i<len(values_rx):
				read, err = func.execute_command('cat /sys/class/net/'+interface+'/statistics/'+values_rx[i])
				val = read.read().strip('\n')
				state = "PASS"
				detail = ""
				if val != "0":
					state = "FAIL"
					detail = val
					error = True
				self.add_result(self.title + " (" + interface + " - " + values_rx[i] + ")", state, detail)
				i = i + 1
			if not error:
				for t in values_rx:
					self.results.pop()
				self.add_result(self.title + " (" + interface + " - rx/all" + ")", "PASS", "")
			i = 0
			error = False
			while i<len(values_tx):
				read, err = func.execute_command('cat /sys/class/net/'+interface+'/statistics/'+values_tx[i])
				val = read.read().strip('\n')
				state = "PASS"
				detail = ""
				if val != "0":
					state = "FAIL"
					detail = val
					error = True
				self.add_result(self.title + " (" + interface + " - " + values_rx[i] + ")", state, detail)
				i = i + 1
			if not error:
				for t in values_tx:
					self.results.pop()
				self.add_result(self.title + " (" + interface + " - tx/all" + ")", "PASS", "")


class check_gaia_disk_space(check):
	page         = "GAiA.0verview"
	category     = "Harddisk"
	title        = "Disk Space"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "df -h | sed s/\ \ */\;/g | cut -d ';' -f 6,4 | awk 'NR>1 {print $1}'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			state = "FAIL"
			data = str(line).strip('\n').split(";")
			if len(data) < 2:
				continue
			if "M" in data[0]:
				state = "WARN"
			if "G" in data[0]:
				state = "PASS"
			if data[1] == "/boot" or data[1] == "/dev/shm":
				state = "PASS"
			self.add_result(self.title + " (" + data[1] + ")", state, data[0]) 


class check_gaia_cpu_usage(check):
	page         = "GAiA.0verview"
	category     = "CPU"
	title        = "CPU Usage"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		if func.isFirewall():
			out, err = func.execute_command("fw ctl affinity -l")
			affinity = out.read()
		else:
			affinity = ""
		dbcur = func.execute_sqlite_query("select name_of_cpu,max(cpu_usage) from UM_STAT_UM_CPU_UM_CPU_ORDERED_TABLE group by name_of_cpu;")
		for row in dbcur:
			worker = ""
			nic = ""
			daemon = ""
			cpu = row[0]
			for line in affinity.split('\n'):
				if "CPU "+str(cpu)+'#' in line +'#':
					if "Kernel" in line:
						if worker != "":
							worker = worker + ", "
						worker = worker + line.split(":")[0].replace("Kernel ", "")
					elif "Daemon" in line:
						daemon = "Daemon(s), "
					else:
						if nic != "":
							nic = nic + ", "
						nic = nic + line.split(":")[0]
			load = str(row[1]).split(".")[0]
			state = "PASS"
			if int(load) > 85 and nic != "":
				state = "FAIL"
			elif int(load) > 85 and nic == "":
				state = "WARN"
			if nic != "":
				nic = nic + ", "
			self.add_result(self.title + " (peak - CPU " + str(cpu) + "): " + daemon + nic + worker, state, load + "%")
		dbcur = func.execute_sqlite_query("select name_of_cpu,avg(cpu_usage) from UM_STAT_UM_CPU_UM_CPU_ORDERED_TABLE group by name_of_cpu;")
		for row in dbcur:
			worker = ""
			nic = ""
			daemon = ""
			cpu = row[0]
			for line in affinity.split('\n'):
				if "CPU "+str(cpu)+'#' in line+'#':
					if "Kernel" in line:
						if worker != "":
							worker = worker + ", "
						worker = worker + line.split(":")[0].replace("Kernel ", "")
					elif "Daemon" in line:
						daemon = "Daemon(s), "
					else:
						if nic != "":
							nic = nic + ", "
						nic = nic + line.split(":")[0]
			load = str(row[1]).split(".")[0]
			state = "PASS"
			if int(load) > 50:
				state = "WARN"
			if int(load) > 50 and nic != "":
				state = "FAIL"
			if int(load) > 85 and worker != "":
				state = "FAIL"
			if nic != "":
				nic = nic + ", "
			self.add_result(self.title + " (avg - CPU " + str(cpu) + "): " + daemon + nic + worker, state, load + "%")
		dbcur.close()


class check_gaia_memory_usage(check):
	page         = "GAiA.0verview"
	category     = "Memory"
	title        = "Memory Usage"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		mem_total = 0
		mem_avg = 0
		mem_peak = 0
		dbcur = func.execute_sqlite_query("select max(real_total) from UM_STAT_UM_MEMORY;")
		for row in dbcur:
			mem_total = row[0]

		dbcur = func.execute_sqlite_query("select avg(real_used) from UM_STAT_UM_MEMORY;")
		for row in dbcur:
			mem_avg = row[0]

		dbcur = func.execute_sqlite_query("select max(real_used) from UM_STAT_UM_MEMORY;")
		for row in dbcur:
			mem_peak = row[0]

		dbcur.close()
		mem_avg_used = int(str(mem_avg/mem_total*100).split(".")[0])
		mem_peak_used = int(str(mem_peak/mem_total*100).split(".")[0])

		state = "PASS"
		if mem_avg_used > 70:
			state = "WARN"
		if mem_avg_used > 90:
			state = "FAIL"
		self.add_result(self.title + " (average)", state, str(mem_avg_used)+"%")

		state = "PASS"
		if mem_peak_used > 80:
			state = "WARN"
		self.add_result(self.title + " (peak)", state, str(mem_peak_used)+"%")

		out, err = func.execute_command("free -g | grep -i swap | awk '{print $3,$4}'")
		data = out.read().strip('\n').split(" ")
		used = data[0]
		avail = data[1]
		percent = str(int(used) / int(avail) * 100).split(".")[0]
		state = "WARN"
		if percent == "0":
			state = "PASS"
		self.add_result(self.title + " (swap)", state, percent + "%")
		

