#!/bin/bash
#Shinobu Startup Script

if [ -e "/etc/shinobu/Shinobu.py" ];then
	cd /etc/shinobu
	python Shinobu.py
else
	git clone http://github.com/3jackdaws/ShinobuBot
	mv ShinobuBot/* shinobu/
	cd shinobu
	rm start_shinobu.sh
	mkdir resources
	python Shinobu.py
fi