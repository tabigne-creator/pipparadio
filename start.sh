#!/bin/bash
icecast2 -c /etc/icecast2/icecast.xml &
sleep 3
python3 /streamer.py
