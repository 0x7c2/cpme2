#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

import func
import sys
from datetime import datetime

class check:
	#
	# define cpme output page
	#
	page = ""

	#
	# define category of check
	#
	category = ""

	#
	# define check title
	# 
	title  = ""

	#
	# is check for firewall and/or management
	#
	isFirewall = False
	isManagement = False
	isClusterXL = False

	#
	# minimum version
	#
	minVersion = 8020
	supported  = False

	#
	# executeCommand
	#
	isCommand = False
	command   = ""
	commandOut = ""
	commandErr = ""

	#
	# predefine results
	#
	results = []

	#
	# predefine debug log
	#
	debug_log = {}

	def __init__(self, version, isFw = False, isMgmt = False, isCluster = False, debugLevel = 0):
		if version >= self.minVersion:
			if self.isFirewall and self.isFirewall == isFw:
				if self.isClusterXL and self.isClusterXL == isCluster:
					self.supported = True
				if not self.isClusterXL:
					self.supported = True
			if self.isManagement and isMgmt == self.isManagement:
				self.supported = True
		self.debugLevel = debugLevel
		self.debug(2, '-----------------------------')
		self.debug(1, "Class supported: " + str(self.supported))
		self.debug(2, '-----------------------------')
		self.debug(2, 'Environment:')
		self.debug(2, "minVersion  = " + str(self.minVersion)  + ", version   = " + str(version))
		self.debug(2, "isFirewall  = " + str(self.isFirewall)  + ", firewall  = " + str(isFw))
		self.debug(2, "isClusterXL = " + str(self.isClusterXL) + ", cluster   = " + str(isCluster))
		self.debug(2, "isManagement= " + str(self.isManagement)+ ", management= " + str(isMgmt))

	def clear(self):
		self.debug(2, "Cleaning results")
		self.results    = []
		self.commandOut = ""

	def get_command(self):
		if self.isCommand:
			return command
		else:
			return False

	def get_version(self):
		return self.minVersion

	def get_results(self):
		return self.results

	def run(self):
		if self.supported:
			self.debug(2, 'Class is supported, running check..')
			if self.commandOut == "":
				if self.isCommand:
					out, err = func.execute_command(self.command)
					self.commandOut = out.read().split('\n')
					self.commandErr = err.read().split('\n')
				else:
					self.commandOut = eval(self.command)
			if isinstance(self.commandOut, list):
				self.commandOut = list(filter(None, self.commandOut))
				self.debug(4, '-----------------------------')
				self.debug(4, 'commandOut:')
				for o in self.commandOut:
					self.debug(5, str(o))
				self.debug(4, '-----------------------------')
			if isinstance(self.commandErr, list):
				self.commandErr = list(filter(None, self.commandErr))
				self.debug(5, 'commandErr:')
				for o in self.commandErr:
					self.debug(5, str(o))
				self.debug(5, '-----------------------------')
			self.run_check()
			return self.results
		else:
			return self.supported

	def set_commandOut(self, temp):
		self.commandOut = temp

	def add_result(self, title, state, detail = ""):
		self.debug(3, 'Adding results to array, state: ' + state)
		self.results.append( { 'title': title, 'state': state, 'detail': detail } )

	def debug(self, level, msg):
		timestamp = datetime.now()
		classname = self.__class__.__name__
		if not self.__class__.__name__ in self.debug_log:
			self.debug_log[self.__class__.__name__] = []
		if self.debugLevel >= level:
			self.debug_log[self.__class__.__name__].append( { 'title': str(timestamp) + " " + classname, 'state': 'DEBUG', 'detail': msg } )

	def get_log(self):
		return self.debug_log[self.__class__.__name__]

