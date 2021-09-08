#!/bin/sh
emacs --daemon &
emacsclient -c -a 'emacs' &
brave &
picom --config $HOME/.config/picom/picom.conf &
nitrogen --restore &
nm-applet &
