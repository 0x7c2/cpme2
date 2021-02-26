#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func


class check_health_sensors(check):
	page         = "Health.Hardware"
	category     = "Soft Sensors"
	title        = "Sensor"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "cpstat -f sensors os"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if "|" in line and not "Name" in line and not "-------" in line:
				data = line.split("|")
				state = "PASS"
				s_name = data[1].strip()
				s_val  = data[2].strip()
				s_unit = data[3].strip()
				s_type = data[4].strip()
				s_stat = data[5].strip()
				if s_stat != "0":	state = "FAIL"
				self.add_result(s_type + " -> " + s_name, state, s_val + " " + s_unit)
			


class check_health_ipmi(check):
	page         = "Health.Hardware"
	category     = "IPMI Sensors"
	title        = "Sensor"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		found = False
		for e in func.ipmiInfo():
			found = True
			sensor = e[0].strip()
			value  = e[1].strip()
			vtype  = e[2].strip()
			sstate = e[3].strip()
			if value != "na" and value != "0x0" and value != "0.000":
				state = "WARN"
				if sstate == "ok":	state = "PASS"
				if sstate == "na":	state = "INFO"
			self.add_result(self.title + " - " + sensor, state, value + " " + vtype)
		if not found:
			self.add_result(self.title + " -> Could not found any sensor!", "INFO", "")


class check_health_securexl_dos_blacklist(check):
	page         = "Health.SecureXL"
	category     = "DoS Blacklist"
	title        = "Blacklist entry"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fwaccel dos blacklist -s"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if "is empty" in line:
				self.add_result("Blacklist is empty", "PASS", "")
				return
			self.add_result(self.title, "WARN", line.strip())


class check_health_securexl_dos_whitelist(check):
	page         = "Health.SecureXL"
	category     = "DoS Whitelist"
	title        = "Whitelist entry"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fwaccel dos whitelist -s"
	isCommand    = True

	def run_check(self):
		if len(self.commandOut) < 4:
			self.add_result("Whitelist is empty", "PASS", "")
		else:
			for line in self.commandOut:
				self.add_result(self.title, "WARN", line.strip())


class check_health_securexl_dos(check):
	page         = "Health.SecureXL"
	category     = "DoS"
	title        = "SXL DoS Config"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fwaccel dos config get"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			data = line.split(":")
			f = data[0].strip()
			v = data[1].strip()
			self.add_result(self.title + " (" + f + ")", "INFO", v)




class check_health_firewall_dynamic_split(check):
	page         = "Health.Firewall"
	category     = "Information"
	title        = "Dynamic Split"
	isFirewall   = True
	isManagement = False
	minVersion   = 8040
	command      = "dynamic_split -p"
	isCommand    = True

	def run_check(self):
		if "off" in self.commandOut[0]:
			self.add_result(self.title, "INFO", "not active")
		else:
			self.add_result(self.title, "INFO", "active")


class check_health_firewall_mode(check):
	page         = "Health.Firewall"
	category     = "Information"
	title        = "Firewall Mode"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "lsmod"
	isCommand    = True

	def run_check(self):
		if "fwmod" in self.commandOut:
			self.add_result(self.title, 'INFO', 'User Mode')
		else:
			self.add_result(self.title, 'INFO', 'Kernel Mode')
			

class check_health_mgmt_gui_clients(check):
	page         = "Health.Management"
	category     = "Information"
	title        = "GUI Clients"
	isFirewall   = False
	isManagement = True
	minVersion   = 8020
	command      = "cp_conf client get"
	isCommand    = True

	def run_check(self):
		found = False
		for o in self.commandOut:
			if "Any" in o:
				self.add_result(self.title, 'WARN', 'Any')
				found = True
		if not found:
			for o in self.commandOut:
				self.add_result(self.title, 'INFO', str(o))
			

class check_health_firewall_protection_parser(check):
	page         = "Health.Firewall"
	category     = "Information"
	title        = "Protection Parsers"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = 'cat $FWDIR/state/local/FW1/local.set | grep -A4 parser_settings_profile | grep ":val" | uniq | awk "{print $2}" | tr -d "()"'
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if line.strip() != "":
				self.add_result(self.title, 'INFO', line.strip('\n').replace(':val ','').replace('"','').strip())



class check_health_firewall_dispatcher_stat(check):
	page         = "Health.Firewall"
	category     = "Information"
	title        = "Dispatcher statistics"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fw ctl pstat -m | grep -i 'fwmultik enqueue fail stats' -A 22 | grep -v 'fail stats:'"
	isCommand    = True

	def run_check(self):
		error = False
		for d in self.commandOut:
			tmp = d.split(":")
			if len(tmp) < 2:
				continue
			field = tmp[0].replace('\t','').strip(' ')
			val   = tmp[1].strip(' ')
			if val != '0':
				error = True
				self.add_result(self.title + " [" + field + "]", "WARN", val)
		if not error:
			self.add_result(self.title, "PASS", "")


class check_health_clusterxl_sync_stat(check):
	page         = "Health.ClusterXL"
	category     = "Summary"
	title        = "ClusterXL Sync statistics"
	isFirewall   = True
	isManagement = False
	isClusterXL  = True
	minVersion   = 8020
	command      = "cphaprob syncstat"
	isCommand    = True

	def run_check(self):

		fields = ["Lost updates", "Lost bulk update events", "Oversized updates not sent", "Sent reject notifications", "Received reject notifications"]
		error = False
		for d in self.commandOut:
			# check sync status
			if "Sync status" in d:
				tmp = d.split(":")
				field = tmp[0].strip(' ')
				val = tmp[1].strip(' ')
				if val == "OK":
					state = "PASS"
					detail = ""
				else:
					state = "FAIL"
					detail = val
				self.add_result(self.title + " [" + field + "]", state, detail)
			# check statistics
			for f in fields:
				if f in d:
					val = d.replace(f, '').replace('.','').strip()
					if val != "0":
						state = "WARN"
						detail = val
						error = True
						self.add_result(self.title + " [" + f + "]", state, detail)
		if not error:
			self.add_result(self.title + " [Statistics]", "PASS", "")



class check_health_licensing_sum(check):
	page         = "Health.Licensing"
	category     = "License Status"
	title        = "Licensing"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "cpstat os -f licensing | grep '|' | awk 'NR>1 {print $0}'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			state = "FAIL"
			if "|" in line:
				data = line.split('|')
				blade = data[2].strip(" ")
				status = data[3].strip(" ")
				expiration = data[4].strip(" ")
				active = data[6].strip(" ")
				quota = data[7].strip(" ")
				used = data[8].strip(" ")
				if status == "Not Entitled":
					state = "INFO"
				if status == "Expired" and active == "0":
					state = "WARN"
				if status == "Entitled":
					state = "PASS"
				self.add_result(self.title + " (Blade: "+blade+")", state, status)
	

class check_health_sic_state(check):
	page         = "Health.Firewall"
	category     = "Information"
	title        = "Secure Internal Communication State"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "cp_conf sic state"
	isCommand    = True

	def run_check(self):
		found = False
		for line in self.commandOut:
			if ":" in line:
				if 'Trust established' in line:
					self.add_result(self.title, 'PASS', line)
				else:
					self.add_result(self.title, 'FAIL', line)
	

class check_health_firewall_fragments(check):
	page         = "Health.Firewall"
	category     = "Networking"
	title        = "Firewall Fragments"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "cpstat -f fragments fw | awk 'NR>2 {print $0}'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			data = line.strip('\n')
			if data != "":
				state = "FAIL"
				d = data.split(":")
				field = d[0].strip(' ')
				value = d[1].strip(' ')
				if int(value) < 100:
					state = "WARN"
				if value == "0":
					state = "PASS"
				self.add_result(self.title + " (" + field + ")", state, value)
		
class check_health_firewall_tables(check):
	page         = "Health.Firewall"
	category     = "Kernel Tables"
	title        = "Table Overflows"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		tables = ['connections', 'fwx_cache']
		for t in tables:
			out, err = func.execute_command("fw tab -t " + t + " | grep limit")
			out = out.read().strip('\n').split(',')
			if out[len(out)-1].strip(' ') == "unlimited":
				self.add_result(self.title + " [" + t + "]", "PASS", "unlimited")
			else:
				t_limit = int(out[len(out)-1].replace('limit ','').strip(' '))
				out, err = func.execute_command("fw tab -t " + t + " -s | grep " + t)
				out = out.read().strip('\n').split()
				t_peak = int(out[4])
				t_val  = int(out[3])
				m = False
				if t_peak > (t_limit * 0.9):
					self.add_result(self.title + " [" + t + "]", "WARN", "peak: " + str(t_peak) + "/" + str(t_limit))
					m = True
				if t_val > (t_limit * 0.9):
					self.add_result(self.title + " [" + t + "]", "FAIL", "current: " + str(t_val) + "/" + str(t_limit))
					m = True
				if not m:
					self.add_result(self.title + " [" + t + "]", "PASS", str(t_val) + "/" + str(t_limit))

		
class check_health_firewall_allocations(check):
	page         = "Health.Firewall"
	category     = "Memory"
	title        = "Failed Allocations"
	isFirewall   = True
	isManagement = False
	isClusterXL  = False
	minVersion   = 8020
	command      = 'fw ctl pstat | grep -ioE "[0-9]+ failed" | grep -vc "0 failed"'
	isCommand    = True

	def run_check(self):
		for o in self.commandOut:
			if o != "" and o == "0":
				self.add_result(self.title, 'PASS', '')
			elif o != "":
				self.add_result(self.title, 'FAIL', o)


class check_health_firewall_crash(check):
	page         = "Health.Firewall"
	category     = "Processes"
	title        = "Existing crash data"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):
		out, err = func.execute_command("ls -l /var/log/crash")
		for line in out:
			tmp = line.strip('\n')
			if 'total 0' == tmp:
				self.add_result(self.title + " [/var/log/crash]", 'PASS', '')
			if 'admin' in tmp:
				f = tmp.split()
				f = f[len(f)-1]
				self.add_result(self.title + " [/var/log/crash]", 'FAIL', f)
		out, err = func.execute_command("ls -l /var/log/dump/usermode")
		for line in out:
			tmp = line.strip('\n')
			if 'total 0' == tmp:
				self.add_result(self.title + " [/var/log/dump/usermode]", 'PASS', '')
			if 'admin' in tmp:
				f = tmp.split()
				f = f[len(f)-1]
				self.add_result(self.title + " [/var/log/dump/usermode]", 'FAIL', f)


class check_health_process_cpwd(check):
	page         = "Health.Processes"
	category     = "Processes in cpwd"
	title        = "Processes"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "cpwd_admin list | awk 'NR>1 { print $1,$2,$4 }'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if line != "":
				data = line.strip('\n').split(" ")
				proc = data[0]
				pid = data[1]
				start = data[2]
				state = "PASS"
				detail = ""
				if start != "1":
					state = "WARN"
					detail = "Process restarted!"
				if not pid.isdigit():
					state = "FAIL"
					detail = "PID missing!"
				self.add_result(self.title + " (" + proc + ")", state, detail)
		
		

class check_health_process_zombie(check):
	page         = "Health.Processes"
	category     = "Zombie Processes"
	title        = "Processes"
	isFirewall   = True
	isManagement = True
	isClusterXL  = False
	minVersion   = 8020
	command      = "ps auxw | grep -E '(Z|defunct)'"
	isCommand    = True

	def run_check(self):
		error = False
		for line in self.commandOut:
			if not "grep" in line and not "%CPU" in line and not line == "":
				data = line.strip('\n').split()
				pid = data[1]
				stat = data[7]
				cmd = data[10]
				state = "FAIL"
				detail = pid + " - " + cmd
				self.add_result(self.title + " ["+detail+"]", state, "")
				error = True
		if not error:
			self.add_result(self.title, "PASS", "")
		
		
class check_health_clusterxl_state(check):
	page         = "Health.ClusterXL"
	category     = "State"
	title        = "ClusterXL State"
	isFirewall   = True
	isManagement = False
	isClusterXL  = True
	minVersion   = 8020
	command      = "cphaprob state | head -n 7 | tail -n 2 | sed 's/(local)//g' | awk '{ print $5,$4 }'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if line != "":
				data = line.strip('\n').split(" ")
				node = data[0]
				stat = data[1]
				state = "PASS"
				detail = stat
				if stat != "ACTIVE" and stat != "STANDBY":
					state = "FAIL"
					detail = stat
				self.add_result(self.title + " ("+node+")", state, detail)
		
		
class check_health_clusterxl_ccp_encr(check):
	page         = "Health.ClusterXL"
	category     = "CCP"
	title        = "ClusterXL CCP Encryption"
	isFirewall   = True
	isManagement = False
	isClusterXL  = True
	minVersion   = 8020
	command      = "cphaprob ccp_encrypt"
	isCommand    = True

	def run_check(self):
		state = "INFO"
		detail = ""
		for line in self.commandOut:
			tmp = line.strip('\n').strip(' ')
			if tmp != "":
				detail = tmp
		self.add_result(self.title, state, detail)
		
		
class check_health_clusterxl_ccp_multiver(check):
	page         = "Health.ClusterXL"
	category     = "CCP"
	title        = "ClusterXL CCP Multiversion"
	isFirewall   = True
	isManagement = False
	isClusterXL  = True
	minVersion   = 8020
	command      = "cphaprob release"
	isCommand    = True

	def run_check(self):
		state = "INFO"
		handle = False
		for line in self.commandOut:
			tmp = line.strip('\n')
			if handle and tmp != "":
				a = tmp.split()
				if "Mismatch" in a[len(a)-1]:
					detail = a[len(a)-3] + " " + a[len(a)-2] + " " + a[len(a)-1]
					state = "WARN"
				else:
					detail = a[len(a)-2] + " " + a[len(a)-1]
				id = tmp.replace(detail, '').strip(' ')
				self.add_result(self.title + " [ID: "+id+"]", state, detail)

			if "ID" in tmp:
				handle = True
		
		
class check_health_clusterxl_pnotes(check):
	page         = "Health.ClusterXL"
	category     = "PNotes"
	title        = "ClusterXL PNotes"
	isFirewall   = True
	isManagement = False
	isClusterXL  = True
	minVersion   = 8020
	command      = "cpstat ha -f all"
	isCommand    = True

	def run_check(self):
		t = False
		found = False
		table = ""
		for line in self.commandOut:
			if found and '--------------------' in line:
				t = False
			if t and "|" in line and not "Descr" in line and not "-----" in line:
				data = line.split('|')
				p_name = data[1].strip(' ')
				p_stat = data[2].strip(' ')
				if p_stat != "OK":
					state = "FAIL"
					detail = p_stat
				else:
					state = "PASS"
					detail = ""
				self.add_result(self.title + " [" + p_name + "]", state, detail)
				found = True
			if "Problem Notification table" in line:
				t = True
		

class check_health_firewall_aging(check):
	page         = "Health.Firewall"
	category     = "Information"
	title        = "Aggressive Aging"
	isFirewall   = True
	isManagement = False
	isClusterXL  = False
	minVersion   = 8020
	command      = "fw ctl pstat | grep Aggre"
	isCommand    = True

	def run_check(self):
		data = self.commandOut[0].strip('\n').strip(' ')
		if data == "Aggressive Aging is enabled, not active":
			state = "PASS"
			detail = ""
		else:
			state = "WARN"
			detail = data
		self.add_result(self.title, state, detail)


class check_health_corexl_dispatcher(check):
	page         = "Health.CoreXL"
	category     = "CoreXL Dispatcher"
	title        = "CoreXL Dispatcher"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fw ctl multik dynamic_dispatching get_mode"
	isCommand    = "True"

	def run_check(self):
		found = False
		for line in self.commandOut:
			if "is On" in line:
				self.add_result(self.title, "PASS", "Active")
				found = True
				return
		if not found:
			self.add_results(self.title, "FAIL", "Not active!")



class check_health_corexl_stats(check):
	page         = "Health.CoreXL"
	category     = "CoreXL Balancing"
	title        = "CoreXL Balancing"
	isFirewall   = True
	isManagement = False
	isClusterXL  = False
	minVersion   = 8020
	command      = "fw ctl multik stat"
	isCommand    = True

	def run_check(self):
		stats = []
		raw = []
		for line in self.commandOut:
			if not "ID" in line and not "-----" in line:
				data = line.split('|')
				id = data[0].strip(' ')
				active = data[1].strip(' ')
				cpu = int(data[2])
				conns = int(data[3])
				peak = int(data[4])
				stats.append([active, cpu, conns, peak])
				raw.append([str(id), active, str(cpu), str(conns), str(peak)])
		state = "PASS"
		detail = ""
		for a in stats:
			for b in stats:
				if int(a[2]) > (int(b[2]) * 1.5) or int(a[3]) > (int(b[3]) * 1.3):
					state = "WARN"
					for r in raw:
						self.add_result(self.title + " (ID: " + r[0] + ", Active: " + r[1] + ", CPU: " + r[2] + ")", "WARN", "Conns: " + r[3] + " / Peak: " + r[4])
					return
		self.add_result(self.title, state, detail)


