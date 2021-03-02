#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func
import datetime
import json


def mgmt_fetch_uid_firewall_properties():
	if func.isManagement():
		out, err = func.execute_command('mgmt_cli show-generic-objects name "firewall_properties" -r true -f json --unsafe true')
		data = json.load(out)
		return data['objects'][0]['uid']
	else:
		return "-1"


class check_mgmt_global_properties_general(check):
	page         = "Management.Global Properties"
	category     = "General"
	title        = "Global/General"
	isFirewall   = False
	isManagement = True
	minVersion   = 8020
	command      = "mgmt_cli show generic-object uid '" + mgmt_fetch_uid_firewall_properties() + "' -r true -f json --unsafe true"
	isCommand    = True

	check = []
	check.append([	"fwDropOutOfStateIcmp",		True,	"WARN",	"Drop Out of State: ICMP"	])
	check.append([	"fwDropOutOfStateUdp",		True,	"WARN",	"Drop Out of State: UDP"	])
	check.append([	"fwAllowOutOfStateTcp",		0,	"WARN",	"Drop Out of State: TCP"	])
	check.append([	"fwDropOutOfStateSctp",		True,	"WARN",	"Drop Out of State: SCTP"	])
	check.append([	"logImpliedRules",		True,	"INFO",	"Log implied Rules"		])
	check.append([	"natAutomaticArp",		True,	"INFO",	"Automatic NAT - ARP"		])
	check.append([	"natAutomaticRulesMerge",	True,	"INFO",	"Merge manual NAT Rules"	])
	check.append([	"natDstClientSide",		True,	"FAIL",	"Translate DST on Client Side"	])
	check.append([	"udpreply",			True,	"WARN",	"Accept statful UDP replies"	])
	check.append([	"allowDownloadContent",		True,	"INFO",	"Allow Download Content"	])
	check.append([	"allowUploadContent",		False,	"INFO",	"Improve product experience.."	])
	check.append([	"fw1enable",			True,	"WARN",	"Imp.Rules: Control Connections"])
	check.append([	"raccessenable",		True,	"WARN",	"Imp.Rules: RAS Connections"	])
	check.append([	"outgoing",			True,	"WARN", "Imp.Rules: Outgoing from GW"	])
	check.append([	"acceptOutgoingToCpServices",	True,	"WARN", "Imp.Rules: Gateway to CP"	])

	def run_check(self):
		config = json.loads('\n'.join(self.commandOut))
		for c in self.check:
			if config[c[0]] == c[1]:
				state = "PASS"
				detail = str(c[1])
			else:
				state = c[2]
				detail = str(config[c[0]])
			self.add_result(self.title + " [" + c[3] + "]", state, detail)


class check_mgmt_global_properties_si(check_mgmt_global_properties_general):
	category      = "Stateful Inspection"
	title         = "Global/Stateful"
	check = []
	check.append([	"tcpstarttimeout",		25,	"WARN",	"TCP start timeout"			])
	check.append([	"tcptimeout",			3600,	"WARN",	"TCP session timeout"			])
	check.append([	"tcpendtimeout",		20,	"WARN",	"TCP end timeout"			])
	check.append([	"tcpendtimeoutCern",		5,	"WARN",	"TCP end timeout, R80.20 and higher"	])
	check.append([	"udptimeout",			40,	"WARN",	"UDP virtual session timeout"		])
	check.append([	"icmptimeout",			30,	"WARN",	"ICMP virtual session timeout"		])
	check.append([	"othertimeout",			60,	"WARN",	"Other Protocol session timeout"	])
	check.append([	"sctpstarttimeout",		30,	"WARN",	"SCTP start timeout"			])
	check.append([	"sctptimeout",			3600,	"WARN",	"SCTP session timeout"			])
	check.append([	"sctpendtimeout",		20,	"WARN",	"SCTP end timeout"			])

