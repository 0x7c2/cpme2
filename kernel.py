#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func

class check_kernel_fw(check):
	page         = "Kernel.Firewall"
	category     = "Kernel Parameter - Firewall"
	title        = "kern/fw/int"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "modinfo -p $FWDIR/boot/modules/fw_kern*.o | sort -u | grep int | cut -d ':' -f1"
	isCommand    = True
	runOnStartup = False

	def run_check(self):
		for o in self.commandOut:
			if "=" in o:
				data = o.split("=")
				self.add_result(self.title + ": " + str(data[0]).strip(), 'INFO', str(data[1]).strip())
			else:
				self.add_result(self.title + ": " + str(o), 'WAIT', '')

	def set_command(self):
		self.command = "modinfo -p $FWDIR/boot/modules/fw_kern*.o | sort -u | grep int | cut -d ':' -f1 | xargs -n1 fw ctl get int"


class check_kernel_sim(check):
	page         = "Kernel.SIM"
	category     = "Kernel Parameter - SIM"
	title        = "kern/sim/int"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "modinfo -p $PPKDIR/boot/modules/sim_kern*.o | sort -u | grep int | cut -d ':' -f1"
	isCommand    = True
	runOnStartup = False

	def run_check(self):
		for o in self.commandOut:
			if "=" in o:
				data = o.split("=")
				self.add_result(self.title + ": " + str(data[0]).strip(), 'INFO', str(data[1]).strip())
			else:
				self.add_result(self.title + ": " + str(o), 'WAIT', '')

	def set_command(self):
		self.command = "modinfo -p $PPKDIR/boot/modules/sim_kern*.o | sort -u | grep int | cut -d ':' -f1 | xargs -n1 fw ctl get int"


