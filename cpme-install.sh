#!/bin/bash

#
# Copyright 2020 by 0x7c2, Simon Brecht.
# All rights reserved.
# This file is part of the Report/Analytic Tool - CPme,
# and is released under the "Apache License 2.0". Please see the LICENSE
# file that should have been included as part of this package.
#

# check running version of check point

found=0

if [ "`fw ver | grep -c "R81.10"`" == "1" ]; then
        echo "Running R81.10, continue installing..."
        found=1
fi

if [ "`fw ver | grep -c "R81.00"`" == "1" ]; then
        echo "Running R81.00, continue installing..."
        found=1
fi

if [ "`fw ver | grep -c "R80.40"`" == "1" ]; then
        echo "Running R80.40, continue installing..."
        found=1
fi

if [ "`fw ver | grep -c "R80.30"`" == "1" ]; then
	echo "Running R80.30, continue installing..."
	found=1
fi

if [ "`fw ver | grep -c "R80.20"`" == "1" ]; then
	echo "Running R80.20, continue installing..."
	found=1
fi

if [ $found -lt 1 ]; then
	echo "Your environment is not supported (yet), exiting."
	exit 1
fi

# download and install
cd
# cleanup old archive
[ -f ./cpme2.tgz ] && rm ./cpme2.tgz

# Added by olejak 
if [ "`host -t A codeload.github.com >/dev/null ; echo $?`" == "0" ]
then
	echo
	echo "Starting download of tgz file from Github..."
	echo
	curl_cli https://codeload.github.com/0x7c2/cpme2/tar.gz/main  -# -k -o cpme2.tgz
	echo
else
	echo
	echo "Can't resolve codeload.github.com"
	echo "Please check DNS settings and/or access to codeload.github.com"
	echo
	exit 1
fi

tar xzvf cpme2.tgz
# cleanup old files
[ -d ./cpme2 ] && rm -r ./cpme2
mv ./cpme2-main ./cpme2
where="`pwd`"
sed -i "1s|.*|#!$FWDIR/Python/bin/python3|" $where/cpme2/cpme.py
echo "#!/bin/bash" > /sbin/cpme
echo "cd $where/cpme2" >> /sbin/cpme
echo "$where/cpme2/cpme.py \$@" >> /sbin/cpme
chmod +x /sbin/cpme
chmod +x $where/cpme2/cpme.py
echo
echo "Installation complete!"
echo "Just type 'cpme' to run the tool..."
echo
