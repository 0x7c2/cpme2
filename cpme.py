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

#
# set debug level,
#   0     : disabled debug
#   [...]
#   5     : max debug output
#
debug = 5

mycontent = content.content(debugLevel = debug)
mymenu = menu.mymenu(mycontent, debugLevel = debug)

while True:
	mymenu.show_menu()
