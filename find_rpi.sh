#!/bin/bash

# arp -a | awk '/b8:27:eb/{ print substr($2, 2, length($2)-2); exit; }'
# "enp0s31f6"
sudo nmap -sP $(ip -o -f inet addr show | grep "wlp4s0" | awk '/scope global/ {print $4}') | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'