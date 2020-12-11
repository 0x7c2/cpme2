#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from templates import check
import func

import os, hashlib

class check_files_management(check):
	page         = "GAiA.Filesystem"
	category     = "Management Related"
	title        = "File"
	isFirewall   = False
	isManagement = True
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):

		PPKDIR = func.get_path("PPKDIR")
		FWDIR = func.get_path("FWDIR")

		results = []

		# user.def
		files_fwm = [	[FWDIR + "/lib/user.def", "e4c4b057826ed24937a92cf16541b8ee"] ]
		# crypt.def
		files_fwm.append([FWDIR + "/lib/crypt.def", "45acf726e29970add148df6816f313ba"])


		# table.def
		if func.fwVersion() >= 8020 and func.fwVersion() <= 8030:
			files_fwm.append([FWDIR + "/lib/table.def", "1b3268539fb3c5711891edc49bce57ee"])
		if func.fwVersion() == 8040:
			files_fwm.append([FWDIR + "/lib/table.def", "ac179cc481dd7b6d18dcb21abe47ddef"])


		# implied_rules.def
		if func.fwVersion() == 8020 or func.fwVersion() == 8030:
			files_fwm.append([FWDIR + "/lib/implied_rules.def", "43e98a9595e479f1a7d879f9ba9e38ff"])
		if func.fwVersion() == 8040:
			files_fwm.append([FWDIR + "/lib/implied_rules.def", "d1cf4d23e544060c26ff8f77bcd3864a"])	

		i = 0	
		while i < len(files_fwm):
			state = "PASS"
			detail = files_fwm[i][1]
			if detail == "1":
				detail = "File shoud not exist"
			try:
				with open(files_fwm[i][0], "rb") as f:
					bytes = f.read()
					fhash = hashlib.md5(bytes).hexdigest()
				if fhash != files_fwm[i][1]:
					state = "WARN"
					detail = "Wrong Hash: " + str(fhash)
			except:
				if files_fwm[i][1] != "1":
					state = "FAIL"
					detail = "not found!"
			self.add_result(self.title + " (" + files_fwm[i][0] + ")", state, detail)
			i = i + 1



class check_files_firewall(check):
	page         = "GAiA.Filesystem"
	category     = "Firewall Related"
	title        = "File"
	isFirewall   = True
	isManagement = False
	minVersion   = 8020
	command      = "ls"
	isCommand    = True

	def run_check(self):

		PPKDIR = func.get_path("PPKDIR")
		FWDIR = func.get_path("FWDIR")

		results = []

		# fwkern.conf
		files_fwd = [	[FWDIR + "/boot/modules/fwkern.conf", "1"] ]

		# fwaffinity.conf
		files_fwd.append([FWDIR + "/conf/fwaffinity.conf", "a1603a26029ebf4aba9262fa828c4685"])

		# simkern.conf
		files_fwd.append([PPKDIR + "/boot/modules/simkern.conf", "5e93554515a637726c4832adee9095ce"])

		# simkern.conf
		files_fwd.append([PPKDIR + "/conf/simkern.conf", "1"])

		# trac_client_1.ttm
		files_fwd.append([FWDIR + "/conf/trac_client_1.ttm", "9d898b072aa5e0d3646ce81829c45453"])

		# ipassignment.conf
		files_fwd.append([FWDIR + "/conf/ipassignment.conf", "4564f2ffd76c72c5503d4a74420f0ef7"])

		# discntd.if
		files_fwd.append([FWDIR + "/conf/discntd.if", "1"])	
	
		i = 0
		while i < len(files_fwd):
			state = "PASS"
			detail = files_fwd[i][1]
			if detail == "1":
				detail = "File shoud not exist"
			try:
				with open(files_fwd[i][0], "rb") as f:
					bytes = f.read()
					fhash = hashlib.md5(bytes).hexdigest()
				if fhash != files_fwd[i][1]:
					state = "WARN"
					detail = "Wrong Hash: " + str(fhash)
			except:
				if files_fwd[i][1] != "1":
					state = "FAIL"
					detail = "not found!"
			self.add_result(self.title + " (" + files_fwd[i][0] + ")", state, detail)
			i = i + 1


