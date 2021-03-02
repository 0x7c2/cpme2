#!/opt/CPsuite-R80.40/fw1/Python/bin/python3
#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

import menu
import content
import sys
import func

#
# set debug level,
#   0     : disabled debug
#   [...]
#   5     : max debug output
#
debug = 0

mycontent = content.content(debugLevel = debug)
mymenu = menu.mymenu(mycontent, debugLevel = debug)

def loopme():
	while True:
		mymenu.show_menu()


if len(sys.argv) < 2:
	func.info()
	loopme()
else:
	if sys.argv[1] == "--version":
		func.info()
		func.info_version()
	elif sys.argv[1] == "--update":
		func.info()
		func.self_update()
	else:
		func.info()
		func.usage()

