#!/bin/sh
killall nm-applet
if [ -x /usr/bin/nm-applet ]; then
    nm-applet &
fi
