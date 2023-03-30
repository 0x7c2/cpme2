#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

from subprocess import Popen, PIPE
import os
import sys
import sqlite3
import time
import ipaddress

#
# variables
#
version = "2.0"

def get_path(env):
        try:
                return os.environ[env]
        except:
                return "/path-not-found/"

# note:
# new file location in r80.40, lets do checkup after loading
# functions.
#
# cpview_database = "/var/log/CPView_history/CPViewDB.dat"
#

cpregistry_file = get_path("CPDIR") + "/registry/HKLM_registry.data"
cpregistry = {}


def info():
	global version
	print("CPme2 - CheckPoint Report/Analytic Tool, " + version + " (by S.Brecht, <https://github.com/0x7c2/cpme2>)")
	print("Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>")
	print("")


def usage():
	print("")
	print("usage: cpme              Run interactive mode")
	print("   or: cpme [arguments]  With arguments, run non interactive mode")
	print("")
	print("Arguments:")
	print("  --update               Try to initiate self-update for CPme")
	print("  --version              Print version and other information")
	print("")


def info_version():
	readme = open('README.md', 'r')
	lines = readme.readlines()
	output = False
	for lineraw in lines:
		line = lineraw.strip('\n').replace('`','')
		if line == "## History":
			output = True
		if line == "## Donation":
			output = False
		if output:
			if "##" in line:
				tmp = line.replace('## ', '')
				print("+" + (len(tmp)+2)*"-" + "+")
				print("| " + tmp + " |")
				print("+" + (len(tmp)+2)*"-" + "+")
			else:
				print(line)


def log_database(sql):
        db = sqlite3.connect("./logfiles.sql")
        dbcur = db.cursor()
        dbcur.execute(sql)
        return dbcur

def gaia_get_value(str, getSingleValue = True):
	retVal = False
	parent = str.split(':')
	parent = parent[0]
	out, err = execute_command("dbget -rv " + parent)
	for o in out:
		if str in o:
			if not getSingleValue and not retVal:
				retVal = []
			if getSingleValue:
				retVal = o.replace(str, '').strip(' ').strip('\n')
			else:
				retVal.append(o.replace(str, '').strip(' ').strip('\n'))
	return retVal


def get_cpregistry(prod, key, returnBool = False):
	global cpregistry
	global cpregistry_file
	inSection = False
	value = "0"
	if prod+"_"+key in cpregistry:
		return cpregistry[prod + "_" + key]
	cmd = Popen("cat " + cpregistry_file, shell=True, stdout=PIPE, universal_newlines=True)
	i = 0
	for line in cmd.stdout:
		i = i + 1
		if ": (" + prod in line:
			inSection = True
		if inSection and ":" + key in line:
			data = line.strip('\n').replace(" ","").replace('\t','')
			value = data.replace(":" + key, "").replace("(", "").replace(")", "")
			break
	if "[4]" in value:
		value = value[4]
	if value != "":
		cpregistry[prod + "_" + key] = value
	if returnBool:
		if value == "0":
			return False
		else:
			return True
	else:
		return value


def execute_command(cmd, waitForMe = False):
	execme = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
	out = execme.stdout
	err = execme.stderr
	if waitForMe:
		execme.wait()
	return out, err


def execute_sqlite_query(sql):
	global cpview_database
	run = True
	while run:
		try:
			db = sqlite3.connect(cpview_database)
			dbcur = db.cursor()
			dbcur.execute(sql)
			run = False
			break
		except:
			time.sleep(0.1)
	return dbcur


def hex2ip(s):
	s = s.strip(' ')
	indices = range(0, 8, 2)
	data = [str(int(s[x:x+2], 16)) for x in indices]
	ipaddr = '.'.join(data)
	return ipaddr

def calc_subnet(firstip, lastip):
	a = ipaddress.IPv4Address(firstip)
	b = ipaddress.IPv4Address(lastip)
	subnets = [ipaddr for ipaddr in ipaddress.summarize_address_range(a, b)]
	for s in subnets:
		return s
	return subnets


def tail_and_head(file, tail = -1, head = -1):
	p = []
	p.append('tail')
	p.append('-n')
	p.append(str(tail))
	p.append(file)
	proc = Popen(p, stdout=PIPE, universal_newlines=True)
	lines = proc.stdout.readlines()
	if head > -1:
		return lines[:head]
	else:
		return lines


def str_pad(val, size, fill = " ", padLeft = False):
	tmp = str(val)
	if padLeft:
		while len(tmp) < size:
			tmp = fill + tmp
	else:
		while len(tmp) < size:
			tmp = tmp + fill
	return tmp


def confirm(cmd):
	print("> Executing command: " + cmd)
	a = input("> Should i really execute command? [y/N] ")
	if a.lower() == "y":
		os.system(cmd)
		return True
	else:
		print("Aborting!")
	return False


def self_update():
	cmd = "curl_cli https://raw.githubusercontent.com/0x7c2/cpme2/main/cpme-install.sh -k | bash"
	print("> Trying self-update routine...")
	print("> Executing command: " + cmd)
	print("")
	print("")
	os.system(cmd)



cache_isFirewall = None
def isFirewall():
	global cache_isFirewall
	if cache_isFirewall == None:
		cache_isFirewall = get_cpregistry("FW1", "FireWall", True)
	return cache_isFirewall

cache_isManagement = None
def isManagement():
	global cache_isManagement
	if cache_isManagement == None:
		cache_isManagement = get_cpregistry("FW1", "Management", True)
	return cache_isManagement

cache_isCluster = None
def isCluster():
	global cache_isCluster
	if cache_isCluster == None:
		cache_isCluster = get_cpregistry("FW1", "HighAvailability", True)
	return cache_isCluster

cache_fwVersion = None
def fwVersion():
	global cache_fwVersion
	if cache_fwVersion == None:
		out, err = execute_command("fw ver | grep -oE '(R[0-9\.]+)'")
		cache_fwVersion = int(out.read().strip('\n').strip(' ').replace('R','').replace('.',''))
	return cache_fwVersion

cache_ipmiInfo = "none"
def ipmiInfo():
	global cache_ipmiInfo
	if cache_ipmiInfo == "none":
		o = []
		out, err = execute_command("ipmitool sensor list")
		for line in out:
			if "Could not open device" in line:
				break
			o.append(line.split('|'))
		cache_ipmiInfo = o
	return cache_ipmiInfo
	
cache_isFWUserMode = "none"
def isFWUserMode():
	global cache_isFWUserMode
	if cache_isFWUserMode == "none":
		if isFirewall:
			out, err = execute_command('lsmod | grep -c "fwmod"')
			ret = bool(int(out.read().strip('\n').strip(' ')))
		else:
			ret = False
		cache_isFWUserMode = ret
	return cache_isFWUserMode

#
# possible values:
# fw vpn urlf av appi ips identityServer SSL_INSPECT anti_bot content_awareness qos mon
#
cache_enabledBlades = []
def enabledBlades():
	global cache_enabledBlades
	if len(cache_enabledBlades) < 1:
		out, err = execute_command('enabled_blades')
		cache_enabledBlades = out.read().strip('\n').split()
	return cache_enabledBlades


if fwVersion() >= 8020 and fwVersion() <= 8030:
	cpview_database = "/var/log/CPView_history/CPViewDB.dat"
if fwVersion() >= 8040:
	cpview_database = "/var/log/opt/CPshrd-R" + str(fwVersion())[:2] + "." + str(fwVersion())[2:] + "/cpview_services/cpview_services.dat"

