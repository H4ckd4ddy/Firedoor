#!/bin/bash

pyinstaller --hidden-import netifaces --hidden-import scapy --hidden-import scapy.all --hidden-import docker --hidden-import psutil --add-data 'src/:.' --onefile src/firedoor.py
