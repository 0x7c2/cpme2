#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func


class check_blades_synatk_config(check):
	page         = "Software Blades.SYN Defender"
	category     = "Configuration"
	title        = "Synatk"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fwaccel synatk config"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			data = line.split()
			if len(data) > 2:
				field = data[0] + " " + data[1]
				val   = data[2]
			else:
				field = data[0]
				val   = data[1]
			self.add_result(self.title + " -> " + field, "INFO", val)


class check_blades_synatk_monitor(check):
	page         = "Software Blades.SYN Defender"
	category     = "Monitor"
	title        = "Synatk"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fwaccel synatk monitor"
	isCommand    = True

	def run_check(self):
		table = False
		for line in self.commandOut:
			if table and not "------------" in line:
				data = line.split('|')
				s_if = data[1].strip()
				s_topology = data[2].strip()
				s_enforce = data[3].strip()
				s_state = data[4].strip()
				s_peak = data[5].strip()
				s_current = data[6].strip()
				state = "INFO"
				detail = ""
				if not "Disable" in s_enforce:	state = "WARN"
				if not "N/A" in s_peak:		detail = "Peak: " + s_peak + ", Current: " + s_current
				self.add_result(self.title + " ["+s_if+", "+s_topology+", Enforce: "+s_enforce+"]", state, detail)
			if "Peak" in line and "Current" in line:
				table = True



class check_blades_vpn_polsrv(check):
	page         = "Software Blades.VPN"
	category     = "Policy Server"
	title        = ""
	isFirewall   = True
	isManagement = False
	isBlade      = "vpn"
	minVersion   = 8020
	command      = "cpstat -f all polsrv"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if ":" in line:
				state = "INFO"
				data = line.split(':')
				p_field = data[0].strip()
				p_val   = data[1].strip()
				if "Down" in p_val:	state = "WARN"
				if "OK" in p_val:	state = "PASS"
				if "is down" in p_val:	state = "WARN"
				if "is up" in p_val:	state = "PASS"
				self.add_result(p_field, state, p_val)


class check_blades_ia_stat_auth(check):
	page         = "Software Blades.IA"
	category     = "Authentication"
	title        = "IA-Auth"
	isFirewall   = True
	isManagement = False
	isBlade      = "identityServer"
	minVersion   = 8020
	command      = "cpstat -f authentication identityServer"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if ":" in line:
				data = line.split(':')
				a_field = data[0].strip()
				a_val   = data[1].strip()
				self.add_result(self.title + " - " + a_field, "INFO", a_val)


class check_blades_ia_stat_login(check):
	page         = "Software Blades.IA"
	category     = "Logins"
	title        = "IA-Login"
	isFirewall   = True
	isManagement = False
	isBlade      = "identityServer"
	minVersion   = 8020
	command      = "cpstat -f logins identityServer"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			state = "INFO"
			if ":" in line:
				data = line.split(':')
				a_field = data[0].strip()
				a_val   = data[1].strip()
				if "Unsuccessful" in a_field and a_val != "0":
					state = "WARN"
				self.add_result(self.title + " - " + a_field, state, a_val)



class check_blades_ips_stat(check):
	page         = "Software Blades.IPS"
	category     = "0verview / Statistics"
	title        = "IPS"
	isFirewall   = True
	isManagement = False
	isBlade      = "ips"
	minVersion   = 8020
	command      = "ips stat"
	isCommand    = True

	def run_check(self):
		isField = False
		t_field = ""
		t_val   = ""
		for line in self.commandOut:
			if ":" in line and not "Active Profiles" in line:
				data = line.split(':')
				i_field = data[0].strip()
				i_val   = data[1].strip()
				if len(data) > 1:
					self.add_result(self.title + " - " + i_field, "INFO", i_val)
			else:
				if "Active Profiles" in line:
					t_field = line.split(':')[0].strip()
					isField = True
				if not "Active Profiles" in line and isField:
					t_val = line.strip()
					self.add_result(self.title + " - " + t_field, "INFO", t_val)
					isField = False
					t_field = ""
					t_val   = ""


class check_blades_ips_bypass(check):
	page         = "Software Blades.IPS"
	category     = "IPS Bypass"
	title        = "IPS Bypass"
	isFirewall   = True
	isManagement = False
	isBlade      = "ips"
	minVersion   = 8020
	command      = "ips bypass stat"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if ":" in line:
				data = line.split(':')
				i_field = data[0].strip()
				i_val   = data[1].strip()
				self.add_result(self.title + " - " + i_field, "INFO", i_val)


class check_blades_ssl_stats(check):
	page         = "Software Blades.SSL Interception"
	category     = "0verview / Statistics"
	title        = "SSL"
	isFirewall   = True
	isManagement = False
	isBlade      = "SSL_INSPECT"
	minVersion   = 8020
	command      = "cpstat -f all https_inspection"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			state = "INFO"
			if ":" in line:
				data = line.split(':')
				s_field = data[0].strip()
				s_val   = data[1].strip()
				if "Cannot" in s_val:
					state = "WARN"
				self.add_result(self.title + " - " + s_field, state, s_val)


class check_blades_vpn_stats(check):
	page         = "Software Blades.VPN"
	category     = "Statistics"
	title        = "VPN"
	isFirewall   = True
	isManagement = False
	isBlade      = "vpn"
	minVersion   = 8020
	command      = "cpstat -f all vpn"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			data = line.split(':')
			v_field = data[0].strip()
			v_val   = data[1].strip()
			if "error" in v_field:
				state = "WARN"
			else:
				state = "PASS"
			if not v_val == "0" and not "Product" in line and not "IPsec NIC" in line:
				self.add_result(self.title + " - " + v_field, state, v_val)



class check_blades_fg_stat(check):
	page         = "Software Blades.QoS"
	category     = "0verview / Statistics"
	title        = "QoS"
	isFirewall   = True
	isManagement = False
	isBlade      = "qos"
	minVersion   = 8020
	command      = "fgate stat"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if ":" in line:
				data = line.split(':')
			else:
				data = line
			if "Policy Name" in line:
				self.add_result(self.title + " - Policy Name", "INFO", data[1].strip())
			if "Install time" in line:
				self.add_result(self.title + " - Install Time", "INFO", line.replace('Install time:','').strip())
			if "Interfaces Num" in line:
				self.add_result(self.title + " - Interface Count", "INFO", data[1].strip())


class check_blades_fg_iface(check):
	page         = "Software Blades.QoS"
	category     = "Interfaces"
	title        = "QoS"
	isFirewall   = True
	isManagement = False
	isBlade      = "qos"
	minVersion   = 8020
	command      = "fgate stat"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if "|" in line and "Dir" not in line:
				data = line.split('|')
				q_if    = data[1].strip()
				q_dir   = data[2].strip()
				q_limit = data[3].strip()
				q_rate  = data[4].strip()
				q_conn  = data[5].strip()
				q_p_p   = data[6].strip()
				q_p_b   = data[7].strip()
				self.add_result(self.title + " - Interface " + q_if + "/" + q_dir + " Rate/Limit", "INFO", q_rate + " / " + q_limit)
				if q_p_p != "0" or q_p_b != "0":
					self.add_result(self.title + " - Interface " + q_if + "/" + q_dir + " Pending Data!", "WARN", q_p_p + " packets, " + q_p_b + " bytes")



class check_blades_vpn_summary(check):
	page         = "Software Blades.VPN"
	category     = "0verview / Summary"
	title        = ""
	isFirewall   = True
	isManagement = False
	isBlade      = "vpn"
	minVersion   = 8030
	command      = "vpn tu tlist"
	isCommand    = True

	def run_check(self):
		s2s = False
		c2s = False
		for line in self.commandOut:
			if "no tunnels" in line:
				self.add_result(line.strip(), "INFO", "")
			if "Site-to-Site" in line:
				s2s = True
				c2s = False
			if "Clients Are Connected" in line:
				s2s = False
				c2s = True
			if s2s and ("IPSEC" in line or "NAT-T" in line):
				data = line.split()
				v_type  = data[0].strip()
				v_count = data[1].strip()
				self.add_result("Site-2-Site VPN Count / " + v_type, "INFO", "Tunnels: " + v_count)
			if c2s and ("NAT-T" in line or "Visitor" in line or "SSL" in line or "L2TP" in line):
				data = line.split()
				v_type  = data[0].strip()
				if len(data) < 3:
					v_count = data[1].strip()
				else:
					v_type = v_type + " " + data[1].strip()
					v_count = data[2].strip()
				v_count = data[1].strip()
				self.add_result("Client-2-Site VPN Count / " + v_type, "INFO", "Tunnels: " + v_count)


class check_blades_enabled_blades(check):
	page         = "Software Blades.0verview"
	category     = "Enabled Blades"
	title        = "Blade"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "enabled_blades"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut[0].split(" "):
			self.add_result(self.title + ": " + line, "INFO", "active")


class check_blades_ia_pep_conns(check):
	page         = "Software Blades.IA"
	category     = "PEP - Connections"
	title        = ""
	isFirewall   = True
	isManagement = False
	isBlade      = "identityServer"
	minVersion   = 8020
	command      = "pep show pdp all | grep -v 'not running'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if not "-----------" in line and "Command:" not in line and "Direction" not in line:
				data = line.split('|')
				p_dir = data[1].strip()
				p_ip  = data[2].strip()
				p_id  = data[3].strip()
				p_stat= data[4].strip()
				p_user= data[5].strip()
				p_time= data[6].strip()
				title = p_ip + " -> " + p_dir + " (ID: " + p_id + ")"
				detail = p_ip + " / User: " + p_user + " / CTime: " + p_time
				if "Connected" in p_stat:
					state = "PASS"
				else:
					state = "WARN"
				self.add_result(title, state, detail)


class check_blades_ia_pdp_conns(check):
	page         = "Software Blades.IA"
	category     = "PDP - Connections"
	title        = ""
	isFirewall   = True
	isManagement = False
	isBlade      = "identityServer"
	minVersion   = 8020
	command      = "pdp connections pep | grep -v 'not running'"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if not "-------------" in line and "Direction" not in line:
				data = line.split('|')
				p_dir  = data[1].strip()
				p_ip   = data[2].strip()
				p_port = data[3].strip()
				p_name = data[4].strip()
				p_type = data[5].strip()
				p_stat = data[6].strip()
				title = p_name + " -> " + p_dir + " (" + p_type + ")"
				detail = p_ip + " / " + p_port + "/tcp"
				if "Connected" in p_stat:
					state = "PASS"
				else:
					state = "WARN"
				self.add_result(title, state, detail)
				


class check_blades_ssl_enhanced(check):
	page         = "Software Blades.SSL Interception"
	category     = "Enhanced SSL Interception"
	title        = "Enhanced SSL Interception"
	isFirewall   = True
	isManagement = False
	isBlade      = "SSL_INSPECT"
	minVersion   = 8030
	command      = "fw ctl get int enhanced_ssl_inspection | cut -d '=' -f 2"
	isCommand    = True

	def run_check(self):
		out = self.commandOut[0].strip()
		if out == "0":
			self.add_result(self.title, "INFO", "not active")
		else:
			self.add_result(self.title, "WARN", "active")


class check_blades_ssl_enhanced_bypass(check):
	page         = "Software Blades.SSL Interception"
	category     = "Enhanced SSL Interception"
	title        = "Bypass on enhanced SSL Interception"
	isFirewall   = True
	isManagement = False
	isBlade      = "SSL_INSPECT"
	minVersion   = 8030
	command      = "fw ctl get int bypass_on_enhanced_ssl_inspection | cut -d '=' -f 2"
	isCommand    = True

	def run_check(self):
		out = self.commandOut[0].strip()
		if out == "0":
			self.add_result(self.title, "INFO", "not active")
		else:
			self.add_result(self.title, "WARN", "active")




class check_blades_ext_ioc_feeds(check):
	page         = "Software Blades.Other"
	category     = "External IOC Feeds"
	title        = "IOC Feed"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "ioc_feeds show"
	isCommand    = True

	def run_check(self):
		f_name = ""
		f_status = ""
		f_url = ""
		f_action = ""
		for line in self.commandOut:
			if "Feed Name:" in line:
				f_name = line.replace('Feed Name: ','').strip(' ')[5:-4]
			if "Feed is" in line:
				if "Active" in line:		f_status = "Active"
				if "not Active" in line:	f_status = "NOT Active"
			if "Resource:" in line:
				f_url = line.replace('Resource: ','').strip(' ')
			if "Action:" in line:
				f_action = line.replace('Action: ','').strip(' ')
				self.add_result(self.title + " (" + f_name + ")", "INFO", f_status + ", " + f_url)


class check_blades_update_status(check):
	page         = "Software Blades.0verview"
	category     = "Updates"
	title        = "Blade Update Status"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):

		stat = [	["URL Filtering",	"urlf", 0],
				["AntiBot",		"antimalware", 0],
				["AntiVirus",		"antimalware", 1],
				["Application Control",	"appi", 0]]
		i = 0
		oldcmd = ""
		while i < len(stat):
			newcmd = "cpstat -f update_status " + stat[i][1] + " | grep 'Update status'"
			if oldcmd != newcmd:
				out, err = func.execute_command(newcmd)
				oldcmd = newcmd
				data = out.read().split('\n')
			val = stat[i][2]
			line = data[val].split(':')[1].strip(' ').strip('\n')
			state = "FAIL"
			detail = ""
			if line == "-" or line == "":
				state = "INFO"
				detail = "not active"
			if line == "up-to-date":
				state = "PASS"
				detail = "up-to-date"
			self.add_result(self.title + " (" + stat[i][0] + ")", state, detail)
			i = i + 1

class check_blades_status(check):
	page         = "Software Blades.0verview"
	category     = "Status"
	title        = "Blade Status"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "fw stat -b AMW"
	isCommand    = True

	def run_check(self):
		for line in self.commandOut:
			if ":" in line:
				tmp = line.strip('\n').split(":")
				blade  = tmp[0].strip(' ')
				status = tmp[1].strip(' ')
			else:
				blade = ""
				status = ""
			if ("enable" in status.lower() or "disable" in status.lower()) and "fileapp_ctx_enabled" not in status.lower():
				self.add_result(self.title + " (" + blade + ")", "INFO", status.strip().strip('\t'))
				if blade == "IPS" and "enable" in status.lower():
					out, err = func.execute_command('cat $FWDIR/state/local/AMW/local.set | grep -A15 malware_profiles | grep ":name" | awk "{print $2}" | tr -d "()"')
					for l in out:
						self.add_result("Thread Prevention Policy", "INFO", l.strip('\n').replace(':name ', '').strip().strip('\t'))





class check_blades_vpn_ttmfile(check):
	page         = "Software Blades.VPN"
	category     = "trac_client_1.ttm"
	title        = "Syntax trac_client_1.ttm"
	isFirewall   = True
	isManagement = False
	isBlade      = "vpn"
	minVersion   = 8020
	command      = "vpn check_ttm $FWDIR/conf/trac_client_1.ttm"
	isCommand    = True

	def run_check(self):
		for line in self.commandErr:
			if "without any problems" in line:
				self.add_result(self.title, "PASS", "")
				return
			if "ERROR" in line:
				self.add_result(self.title, "FAIL", line.strip())
			if "result:" in line:
				self.add_result(self.title, "FAIL", line.strip())


class check_blades_vpn_ipafile(check):
	page         = "Software Blades.VPN"
	category     = "ipassignment.conf"
	title        = "Syntax ipassignment.conf"
	isFirewall   = True
	isManagement = False
	isBlade      = "vpn"
	minVersion   = 8020
	command      = "vpn ipafile_check $FWDIR/conf/ipassignment.conf"
	isCommand    = True

	def run_check(self):
		found = False
		for line in self.commandOut:
			if not "Reading file records" in line:
				found = True
				self.add_result(self.title, "WARN", line)
		if not found:
			self.add_result(self.title, "PASS", "")


class check_blades_vpn_encryption_domains(check):
	page         = "Software Blades.VPN"
	category     = "VPN"
	title        = "Overlapping Encryption Domains"
	isFirewall   = True
	isManagement = False
	isBlade      = "vpn"
	minVersion   = 8020
	command      = "vpn overlap_encdom"
	isCommand    = True

	def run_check(self):
		found = False
		if len(self.commandOut) == 0:
			self.add_result(self.title, "PASS", "")
			found = True
		for o in self.commandOut:
			if 'No overlapping encryption domain' in o:
				self.add_result(self.title, "PASS", "")
				found = True
		if not found:
			self.add_result(self.title, "FAIL", "please check encryption domains!")





