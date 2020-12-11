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
	dynamic_load = ['files', 'gaia', 'health', 'performance']

	debugLevel = 0

	modules = None
	classes = {}
	results = {}

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
					if "check_" in name:
						class_ = getattr(module, name)
						self.classes[name] = class_(func.fwVersion(), isFw = func.isFirewall(), isMgmt = func.isManagement(), isCluster = func.isCluster(), debugLevel = self.debugLevel)
						i = i + 1
		self.run_self()

	def run_self(self):
		if not self.processing:
			self.thread = threading.Thread(target=self.run_tests, args=())
			self.thread.daemon = True
			self.thread.start()

	def set_search(self, search_ena = False, search_str = ""):
		self.search_enabled = search_ena
		self.search_string = search_str

	def run_tests(self):
		if not 'CPme.Log' in self.results:
			self.results['CPme.Log'] = {}
		if not 'Log File' in self.results['CPme.Log']:
			self.results['CPme.Log']['Log File'] = {}

		self.check_sum = len(self.classes)
		self.check_now = 0
		self.processing = True
		for test in sorted(self.classes):
			if self.classes[test].supported:
				self.check_cur = test
				self.check_now = self.check_now + 1
				try:
					self.classes[test].clear()
					self.classes[test].run()
				except Exception as e:
					self.error = True
					self.error_msg = { 'classname': test, 'commandOut': self.classes[test].commandOut, 'msg': e }
				
				page     = self.classes[test].page
				category = self.classes[test].category
				if not page in self.results:
					self.results[page] = {}
				if not category in self.results[page]:
					self.results[page][category] = {}
				self.results[page][category][test] = self.classes[test].get_results()
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


		for pages in self.results:
			if pages == page:
				for category in sorted(self.results[pages]):
					for module in self.results[pages][category]:
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
						for item in self.results[pages][category][module]:
							title  = item['title']
							state  = item['state']
							detail = item['detail']
							if state == "PASS":
								col = self.color_pass
							elif state == "WARN":
								col = self.color_warn
							elif state == "FAIL":
								col = self.color_fail
							elif state == "DEBUG":
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

		if self.content_fake_row > self.content_start_row:
			self.scrolling = True
		else:
			self.scrolling = False




