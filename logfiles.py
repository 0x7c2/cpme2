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
import sqlite3
import os.path

class check_log_parser(check):
	page         = "Logfiles.Parser"
	category     = "Logfiles"
	title        = "Log"
	isFirewall   = True
	isManagement = True
	minVersion   = 8020
	command      = "func.log_database('SELECT * FROM log ORDER BY logfile, sk')"
	isCommand    = False

	def run_check(self):
		old_log = ""
		found = False
		for row in self.commandOut:
			# 0 = logfile
			# 1 = sk
			# 2 = message
			# 3 = lastupdate
			if old_log != row[0]:
				if old_log != "" and not found:
					self.add_result(self.title + " [" + old_log + "]", "PASS", "")
				old_log = row[0]
				found = False
			g_out, g_err = func.execute_command("cat " + row[0] + "* | grep -c '" + row[2] + "'")
			counter = g_out.read().strip('\n')
			if counter != "0":
				self.add_result(self.title + " [" + row[0] + "]", "WARN", row[1] + ": " + row[2])
				found = True
		if old_log != "" and not found:
			self.add_result(self.title + " [" + old_log + "]", "PASS", "")



