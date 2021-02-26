#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

import sys, inspect
import curses
import threading
import func

class content:
	dynamic_load = ['files', 'gaia', 'health', 'blades', 'performance', 'troubleshooting', 'kernel']
	special_pages = [ 'CPme.Log' ]

	debugLevel = 0

	modules = None
	classes = {}
	results = {}
	diags   = {}

	screen = None

	content_templ_row = 7
	content_templ_col = 2

	content_start_row = 7
	content_start_col = 2

	content_fake_row = 7

	window_rows = 4
	window_cols = 4

	scrolling = False
	scrollpos = 0
	scrollout = True

	page = ""

	color_pass = None
	color_warn = None
	color_fail = None
	color_info = None
	color_debug = None

	thread = None
	check_sum = 0
	check_now = 0
	check_cur = ""
	processing = False

	error = False
	error_msg = None

	infobar = False

	search_enabled = False
	search_string = ""

	diag = False
	diag_txt = []

	waitingChecks = False

	def get_window_size(self):
		rows, cols = self.screen.getmaxyx()
		self.window_rows = rows - (self.content_templ_row)
		self.window_cols = cols
		if self.infobar:
			self.window_rows = self.window_rows - 3

	def set_screen(self, screen):
		self.screen = screen
		self.get_window_size()

	def set_colors(self, cpass, cwarn, cfail, cinfo, cdebug):
		self.color_pass = cpass
		self.color_warn = cwarn
		self.color_fail = cfail
		self.color_info = cinfo
		self.color_debug = cdebug

	def __init__(self, debugLevel = 0):
		self.debugLevel = debugLevel
		self.modules = map(__import__, self.dynamic_load)
		i = 0
		for module in self.modules:
			for name, obj in inspect.getmembers(module):
				if inspect.isclass(obj):
					if "check_" in name or "diag_" in name:
						class_ = getattr(module, name)
						self.classes[name] = class_(func.fwVersion(), isFw = func.isFirewall(), isMgmt = func.isManagement(), isCluster = func.isCluster(), debugLevel = self.debugLevel)
						i = i + 1
		self.run_self()

	def run_self(self, runOneTest = False):
		if not self.processing:
			if not runOneTest:
				self.thread = threading.Thread(target=self.run_all_pages, args=())
			else:
				self.thread = threading.Thread(target=self.run_one_page, args=())
			self.thread.daemon = True
			self.thread.start()

	def set_search(self, search_ena = False, search_str = ""):
		self.search_enabled = search_ena
		self.search_string = search_str

	def run_one_page(self):
		tests = []
		for category in self.results[self.page]:
			for test in self.results[self.page][category]:
				tests.append(test)
		self.run_tests(tests)

	def run_all_pages(self):
		tests = []
		for test in sorted(self.classes):
			tests.append(test)
		self.run_tests(tests)

	def run_one_test(self, testname):
		self.check_cur = testname
		try:
			self.classes[testname].clear()
			self.classes[testname].run()
		except Exception as e:
			self.error = True
			self.error_msg = { 'classname': testname, 'commandOut': self.classes[testname].commandOut, 'msg': e }
		page     = self.classes[testname].page
		category = self.classes[testname].category
		if not page in self.results:
			self.results[page] = {}
		if not category in self.results[page]:
			self.results[page][category] = {}
		self.results[page][category][testname] = self.classes[testname].get_results()
		self.results['CPme.Log']['Log File'][testname] = self.classes[testname].get_log()


	def run_tests(self, testArray = []):
		if not 'CPme.Log' in self.results:
			self.results['CPme.Log'] = {}
		if not 'Log File' in self.results['CPme.Log']:
			self.results['CPme.Log']['Log File'] = {}

		self.check_sum = len(testArray)
		self.check_now = 0
		self.processing = True
		for test in testArray:
			if self.classes[test].supported and "check_" in test:
				self.run_one_test(test)
				self.check_now = self.check_now + 1
			if self.classes[test].supported and "diag_" in test:
				self.diags[self.classes[test].page] = test
			self.results['CPme.Log']['Log File'][test] = self.classes[test].get_log()
		self.processing = False


	def set_content(self, page):
		self.page = page

		self.content_start_row = self.content_templ_row
		self.content_start_col = self.content_templ_col
		self.content_fake_row  = self.content_templ_row

		old_category   = ""
		first_category = True

		if self.window_cols > 85:
			lenTitle   = 69
			posResult  = 72
			showDetail = True
			lenDetail  = self.window_cols - 82
		else:
			lenTitle   = self.window_cols - 8
			posResult  = self.window_cols - 6
			showDetail = False
			lenDetail  = 0


		if page in self.results:
			foundWaiting = False
			for category in sorted(self.results[page]):
				for module in self.results[page][category]:
					if not page in self.special_pages and not self.classes[module].runOnStartup:
						self.waitingChecks = True
						foundWaiting = True
					if category != old_category:
						if not first_category:
							if self.content_fake_row >= (self.scrollpos + self.content_templ_row):
								if not self.window_rows < (self.content_start_row - 4):
									self.screen.addstr(self.content_start_row, self.content_start_col, (self.window_cols-4)*"-")
									self.content_start_row = self.content_start_row + 1
							self.content_fake_row = self.content_fake_row + 1
						old_category = category
						if self.content_fake_row >= (self.scrollpos + self.content_templ_row):
							if not self.window_rows < (self.content_start_row - 4):
								self.screen.addstr(self.content_start_row, self.content_start_col, category + ":")
								self.content_start_row = self.content_start_row + 1
							if not self.window_rows < (self.content_start_row - 4):
								self.content_start_row = self.content_start_row + 1
						self.content_fake_row = self.content_fake_row + 2
						first_category = False
					for item in self.results[page][category][module]:
						title  = item['title']
						state  = item['state']
						detail = item['detail']
						if state == "PASS":
							col = self.color_pass
						elif state == "WARN":
							col = self.color_warn
						elif state == "FAIL":
							col = self.color_fail
						elif state == "DEBUG" or state == "WAIT":
							col = self.color_debug
						else:
							col = self.color_info
						if not self.search_enabled or (self.search_string.lower() in title.lower() or self.search_string.lower() in state.lower() or self.search_string.lower() in detail.lower()):
							if self.content_fake_row >= (self.scrollpos + self.content_templ_row):
								if not self.window_rows < (self.content_start_row - 4):
									self.screen.addstr(self.content_start_row, self.content_start_col, title[:lenTitle])
									self.screen.addstr(self.content_start_row, posResult, state, col)
									if showDetail:
										self.screen.addstr(self.content_start_row, posResult + 8, detail[:lenDetail])
									self.content_start_row = self.content_start_row + 1
							self.content_fake_row = self.content_fake_row + 1

			if not page in self.special_pages and not foundWaiting:
				self.waitingChecks = False

		for p in self.diags:
			if p == page:
				self.classes[self.diags[p]].isVisible = True
			else:
				self.classes[self.diags[p]].isVisible = False
				if self.classes[self.diags[p]].thread != None and not self.classes[self.diags[p]].isRunning:
					self.classes[self.diags[p]].thread.join()
					self.classes[self.diags[p]].thread = None

		if page in self.diags:
			rows = self.classes[self.diags[page]].get_content()
			self.diag = self.classes[self.diags[page]].isEnabled
			self.diag_txt = self.classes[self.diags[page]].infoTxt
			if not self.classes[self.diags[page]].isTable:
				for line in rows:
					if self.content_start_row - 5 < self.window_rows:
						self.screen.addstr(self.content_start_row, self.content_start_col, line[:(self.window_cols - 4)])
						self.content_start_row = self.content_start_row + 1
			elif self.classes[self.diags[page]].isTable:
				# determine max cols
				col_size = [ 0 ] * len(rows[0])
				for row in rows:
					col_int = 0
					for col in row:
						if len(str(col)) > col_size[col_int]:
							col_size[col_int] = len(str(col))
						col_int = col_int + 1
				# check if cols fitting into window
				max_cols = 0
				for size in col_size:
					max_cols = max_cols + size + 4
				if max_cols >= (self.window_cols - 4):
					i = 0
					for size in col_size:
						percent = size/max_cols
						columns = round(percent*(self.window_cols-4))
						col_size[i] = columns
						i = i + 1
				# print header and columns
				for row in rows:
					if (self.content_start_row - 4) <= self.window_rows:
						col_int = 0
						for col in row:
							self.screen.addstr(self.content_start_row, self.content_start_col, col[:col_size[col_int]])
							self.content_start_col = self.content_start_col + col_size[col_int] + 3
							if self.content_start_col - 1 < self.window_cols:
								self.screen.addstr(self.content_start_row, self.content_start_col - 2, "|")
							col_int = col_int + 1
						if self.content_start_row == self.content_templ_row:
							self.content_start_row = self.content_start_row + 1
							self.screen.addstr(self.content_start_row, 1, "-"*(self.window_cols-2))
						self.content_start_row = self.content_start_row + 1
						self.content_start_col = self.content_templ_col
						


		if self.content_fake_row > self.content_start_row:
			self.scrolling = True
		else:
			self.scrolling = False


	def get_legend(self):
		if self.page in self.diags:
			return self.classes[self.diags[self.page]].get_legend()
		elif self.page in self.results and self.waitingChecks:
			return "e->run waiting checks"
		else:
			return ""


	def set_keypress(self, key):
		if not self.processing and self.page in self.diags:
			self.classes[self.diags[self.page]].set_keypress_super(key)
		if not self.processing and self.page in self.results:
			for category in self.results[self.page]:
				for test in self.results[self.page][category]:
					if key == ord('e') and not self.classes[test].runOnStartup:
						self.classes[test].set_command()
						self.run_self(runOneTest = True)

