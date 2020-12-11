#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

import os, sys, curses
import datetime

class mymenu:
	screen = None
	menu = {}

	debugLevel = 0

	menu_pos = 1
	menu_sub_pos = 1
	menu_cur = None
	menu_input = ""
	menu_active = False

	menu_val = ""
	menu_sub_val = ""

	menu_entry_templ_row = 3
	menu_entry_templ_col = 2
	menu_entry_start_row = 3
	menu_entry_start_col = 2
	
	focusMenu = True
	focusSub  = False

	infobar = False

	search_enabled = False
	search_string  = ""

	menu_title = ""

	content = ""

	def __init__(self, mycontent, debugLevel = 0):
		self.content = mycontent
		self.debugLevel = debugLevel
		self.build_menu()

	def add_menu(self, menu_name, menu_array):
		self.menu[menu_name] = menu_array

	def build_menu(self):
		if self.debugLevel > 0:
			self.menu['CPme'] = []
			self.menu['CPme'].append('Log')
		for classname in sorted(self.content.classes):
			if self.content.classes[classname].supported:
				pages = self.content.classes[classname].page.split('.')
				page_main = pages[0]
				page_sub  = pages[1]
				if not page_main in self.menu:
					self.menu[page_main] = []
				if not page_sub in self.menu[page_main]:
					self.menu[page_main].append(page_sub)

	def enable_menu(self):
		if not self.menu_active:
			self.screen = curses.initscr()
			curses.noecho()
			curses.cbreak()
			curses.start_color()
			self.screen.keypad(True)
			curses.init_pair(1,curses.COLOR_BLACK , curses.COLOR_WHITE)
			curses.init_pair(2,curses.COLOR_GREEN , curses.COLOR_BLACK)
			curses.init_pair(3,curses.COLOR_RED   , curses.COLOR_BLACK)
			curses.init_pair(4,curses.COLOR_YELLOW, curses.COLOR_BLACK)
			curses.init_pair(5,curses.COLOR_BLUE  , curses.COLOR_BLACK)
			curses.init_pair(6,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
			curses.curs_set(0)
			self.screen.timeout(1000)
		self.menu_active = True
		self.content.set_screen(self.screen)
		self.content.set_colors(curses.color_pair(2), curses.color_pair(4), curses.color_pair(3), curses.color_pair(5), curses.color_pair(6))

	def disable_menu(self):
		if self.menu_active:
			curses.endwin()
		self.menu_active = False


	def make_menu_entry(self, menutxt, menuid, menusel, isFocus = False):
		if isFocus:
			selected = curses.color_pair(1)
		else:
			selected = curses.color_pair(2)
		normal   = curses.A_NORMAL
		if menuid == menusel:
			style = selected
			retval = True
		else:
			style = normal
			retval = False
		txt = menutxt
		self.screen.addstr(self.menu_entry_start_row, self.menu_entry_start_col, txt, style)
		self.menu_entry_start_col = self.menu_entry_start_col + len(txt) + 1
		return retval


	def get_window_size(self):
		rows, cols = self.screen.getmaxyx()
		self.window_rows = rows
		self.window_cols = cols

	def draw_header(self):
		title = "CPme -> " + self.menu_val + " -> " + self.menu_sub_val
		now = datetime.datetime.now()
		timestamp = now.strftime("%H:%M:%S")
		self.screen.addstr(0, 0, "|" + (self.window_cols-2)*"-" + "|")
		self.screen.addstr(1, 0, "| " + title + (self.window_cols-3-len(title))*" " + "|")
		self.screen.addstr(1, (self.window_cols-2-len(timestamp)), timestamp)
		self.screen.addstr(2, 0, "|" + (self.window_cols-2)*"-" + "|")
		self.screen.addstr(3, 0, "|")
		self.screen.addstr(3, self.window_cols-1, "|")
		self.screen.addstr(4, 0, "|" + (self.window_cols-2)*"-" + "|")
		self.screen.addstr(5, 0, "|")
		self.screen.addstr(5, self.window_cols-1, "|")
		self.screen.addstr(6, 0, "|" + (self.window_cols-2)*"-" + "|")
		for i in range(7, self.window_rows-2):
			self.screen.addstr(i, 0, "|")
			self.screen.addstr(i, self.window_cols-1, "|")
		self.screen.addstr(self.window_rows-2, 0, "|" + (self.window_cols-2)*"-" + "|")

	def show_menu(self):
		#
		# check error in content
		#
		if self.content.error:
			self.disable_menu()
			print("Latest FATAL error:")
			print(self.content.error_msg)
			sys.exit()

		#
		# activate menu
		#
		if not self.menu_active:
			self.enable_menu()

		#
		# clear screen
		#
		self.screen.clear()

		#
		# check if infobar is needed
		#
		if self.content.processing:
			self.infobar = True
			self.content.infobar = True
		elif self.search_enabled:
			self.infobar = True
			self.content.infobar = True
		else:
			self.infobar = False
			self.content.infobar = False

		#
		# get new window sizes
		#
		self.get_window_size()
		self.content.get_window_size()

		#
		# reset column and row
		#
		self.menu_entry_start_col = self.menu_entry_templ_col
		self.menu_entry_start_row = self.menu_entry_templ_row

		#
		# build main menu
		#
		i = 0
		for entry in sorted(self.menu):
			i = i + 1
			active = self.make_menu_entry(entry, i, self.menu_pos, self.focusMenu)
			if active:
				self.menu_val = entry


		#
		# build sub menu
		#
		self.menu_entry_start_row = self.menu_entry_templ_row + 2
		self.menu_entry_start_col = self.menu_entry_templ_col
		i = 0
		for entry in sorted(self.menu[self.menu_val]):
			i = i + 1
			active = self.make_menu_entry(entry, i, self.menu_sub_pos, self.focusSub)
			if active:
				self.menu_sub_val = entry


		#
		# build screen layout
		#
		self.draw_header()

		#
		# build content viewer
		#
		self.content.set_search(self.search_enabled, self.search_string)
		self.content.set_content(self.menu_val + "." + self.menu_sub_val)

		#
		# display progress if needed
		#
		if self.infobar:
			self.screen.addstr(self.window_rows-5, 0, "|" + (self.window_cols-2)*"-" + "|")
			if self.content.processing:
				percent = str(round((self.content.check_now / self.content.check_sum) * 100))
				txt = "Running checks in background, please wait: " + percent + "% "
				size = self.window_cols - (len(txt) + 6)
				if size > 4:
					size_1 = round(int(size)/100*int(percent))
					size_2 = round(int(size)-int(size_1))
					txt = txt + "[" + size_1*"#" + size_2*" " + "]"
				self.screen.addstr(self.window_rows-4, 2, txt)
				self.screen.addstr(self.window_rows-3, 2, "Current check: " + self.content.check_cur, curses.color_pair(6))
			if self.search_enabled:
				self.screen.addstr(self.window_rows-4, 2, "Enter search term: (Press backspace to disable)")
				self.screen.addstr(self.window_rows-3, 2, self.search_string)


		#
		# display legend
		#
		if not self.search_enabled and not self.content.processing: 
			legend = "q->quit, r->rerun tests"
			if self.focusSub:
				legend = legend + ", s->search"
		else:
			legend = ""

		#
		# check scrolling module
		#
		if self.content.scrolling:
			if legend != "":
				legend = legend + ", "
			legend = legend + "More information available (Scrolling) " + str(round((self.content.content_start_row + self.content.scrollpos) / self.content.content_fake_row *100)) + "%"

		#
		# print legend and scrolling bar
		#
		self.screen.addstr(self.window_rows-2, 2, legend)

		#
		# request user input
		#
		self.screen.refresh()
		u_input = self.screen.getch()

		if self.search_enabled and not u_input == curses.KEY_DOWN and not u_input == curses.KEY_UP:
			if u_input == curses.KEY_BACKSPACE and self.search_string == "":
				self.search_enabled = False
			elif u_input == curses.KEY_BACKSPACE and self.search_string != "":
				self.search_string = self.search_string[:-1]
			elif u_input != -1 and u_input in range(32, 127):
				self.search_string = self.search_string + chr(u_input)

		elif u_input == curses.KEY_DOWN:
			# key down
			if self.focusSub:
				if self.content.scrolling and self.content.scrollpos < (self.content.content_fake_row - self.content.content_start_row):
					self.content.scrollpos = self.content.scrollpos + 1
			if self.focusMenu:
				self.focusMenu = False
				self.focusSub = True

		elif u_input == curses.KEY_UP:
			# key up
			if self.focusSub and self.content.scrollpos < 1 and not self.search_enabled:
				self.focusSub = False
				self.focusMenu = True
			elif self.focusSub and self.content.scrolling and self.content.scrollpos > 0:
				self.content.scrollpos = self.content.scrollpos - 1

		elif u_input == curses.KEY_PPAGE:
			# page up
			if self.focusSub and self.content.scrolling and self.content.scrollpos > 0:
				if self.content.scrollpos > 8:
					self.content.scrollpos = self.content.scrollpos - 8
				else:
					self.content.scrollpos = 0


		elif u_input == curses.KEY_NPAGE:
			# page down
			if self.focusSub and self.content.scrolling and self.content.scrollpos < (self.content.content_fake_row - self.content.content_start_row):
				if self.content.scrollpos < ((self.content.content_fake_row - self.content.content_start_row) + 8):
					self.content.scrollpos = self.content.scrollpos + 8
				else:
					self.content.scrollpos = (self.content.content_fake_row - self.content.content_start_row)

		elif u_input == curses.KEY_LEFT:
			# key left
			if self.focusMenu:
				self.menu_sub_pos = 1
				self.content.scrollpos = 0
				if self.menu_pos > 1:
					self.menu_pos = self.menu_pos - 1
			if self.focusSub:
				if self.menu_sub_pos > 1:
					self.content.scrollpos = 0
					self.menu_sub_pos = self.menu_sub_pos - 1

		elif u_input == curses.KEY_RIGHT:
			# key right
			if self.focusMenu:
				self.menu_sub_pos = 1
				if self.menu_pos < len(self.menu):
					self.menu_pos = self.menu_pos + 1
			if self.focusSub:
				if self.menu_sub_pos < len(self.menu[self.menu_val]):
					self.content.scrollpos = 0
					self.menu_sub_pos = self.menu_sub_pos + 1

		elif u_input == ord('r'):
			self.content.run_self()

		elif u_input == ord('s'):
			if not self.content.processing and self.focusSub:
				self.content.scrollpos = 0
				self.search_enabled = True

		elif u_input == ord('q') or u_input == 27:
			# escape and or quit
			self.disable_menu()
			sys.exit()









