#!/bin/sh
emacs --daemon &
emacsclient -c -a 'emacs' &
brave &
nitrogen --restore &
picom --config $HOME/.config/picom/picom.conf &
if [ -x /usr/bin/nm-applet ]; then
    nm-applet &
fi
