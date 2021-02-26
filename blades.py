#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func


class check_blades_vpn_summary(check):
	page         = "Software Blades.VPN"
	category     = "Summary"
	title        = ""
	isFirewall   = True
	isManagement = False
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
				data = line.split(" ")
				v_type  = data[0].strip()
				v_count = data[1].strip()
				self.add_result("Site-2-Site VPN Count / " + v_type, "INFO", "Tunnels: " + v_count)
			if c2s and ("NAT-T" in line or "Visitor" in line or "SSL" in line or "L2TP" in line):
				data = line.split(" ")
				v_type  = data[0].strip()
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
	minVersion   = 8020
	command      = "pep show pdp all"
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
	minVersion   = 8020
	command      = "pdp connections pep"
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
				f_name = line.replace('Feed Name: ','').strip(' ')[6:-4]
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
	minVersion   = 8020
	command      = "vpn ipafile_check /opt/CPsuite-R80.40/fw1/conf/ipassignment.conf"
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





