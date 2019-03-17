#!/bin/bash
# ssh_rpi:
#   Connect to first found RaspberryPi device


PROGNAME=$(basename $0)
error_exit() {
	echo -e "\e[1m\e[31mError (${PROGNAME}): ${1:-"Unknown Error"}" 1>&2
	exit 1
}

echo -e "\e[33mSearching for RaspberryPi Device...\e[0m"
ip=$(./find_rpi.sh)

if [ ! -z "$ip" ]
    then
    if ping -c1 -W1 -q $ip &>/dev/null
        then
        echo -e "\e[32mFound $ip\e[0m"
        echo -e "\e[32mConnecting to RPI\n\e[0m"
        ssh pi@$ip
        else
            error_exit "RaspberryPi cannot be connected"
    fi
    else
        error_exit "RaspberryPi cannot be found on local network"
fi