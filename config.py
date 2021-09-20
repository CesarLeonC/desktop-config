# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import inspect, os, subprocess, re
from libqtile.backend import base
from libqtile import bar, layout
from libqtile import extension, hook, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

CONFIG_DIR = "~/.config/qtile"
START = "start.sh"
RESTART = "restart.sh"
SHUTDOWN = "shutdown.sh"

my_window_margin = 15
font_kwargs = {
    "letters": {
        "font": "SauceCodePro Nerd Font",
        "fontsize": 13
            },
    "icons": {
        "font": "NotoSansMono Nerd Font",
        "fontsize": 22
            },
        }

my_terminal = "alacritty"
my_ide = "emacsclient -c -a 'emacs'"
my_browser = "brave"
my_recorder = "obs"
my_vmanager = "VirtualBox"

class_names = {
    0 : ["Pavucontrol"],
    1 : ["Alacritty"],
    2 : ["Emacs"],
    3 : ["libreoffice-startcenter"],
    4 : ["VirtualBox Manager"],
    5 : ["vlc"],
    6 : ["Nitrogen"],
    7 : ["Brave-browser"],
    8 : ["obs"]
            }

my_colors = {
    "focus": "#46d9ff",
    "unfocus": "#ffffff",
    "background": "#000e35",
    "foreground": "#002282"
            }

winkey = "mod4"
alt = "mod1"
shift = "shift"
control = "control"

my_workspaces = [
    ("welcome",""),
    ("term",""),
    ("ide",""),
    ("doc",""),
    ("vbox",""),
    ("video","嗢"),
    ("nitr",""),
    ("web",""),
    ("obs","辶"),
            ]

for file in [START, RESTART, SHUTDOWN]:
    os.chmod(
        path=os.path.expanduser(CONFIG_DIR + "/" + file),
        mode=0o755
            )

@hook.subscribe.startup_once
def qtile_startup():
    executable = CONFIG_DIR + "/" + START
    executable = os.path.expanduser(executable)
    subprocess.call([executable])

@hook.subscribe.restart
def qtile_restarts():
    executable = CONFIG_DIR + "/" + RESTART
    executable = os.path.expanduser(executable)
    subprocess.call([executable])

def window_keys():
    keys = [
        Key([winkey],"space",lazy.next_layout()),
        Key([winkey],"Left",lazy.screen.prev_group()),
        Key([winkey],"Right",lazy.screen.next_group()),
        Key([winkey],"Home",lazy.next_screen()),
        Key([winkey],"End",lazy.prev_screen()),
        Key([winkey],"Tab",lazy.layout.next()),
        Key([winkey],"Return",lazy.layout.swap_main())
            ]
    return keys

def mgmt_keys():
    keys = [
        Key([winkey,"shift"],"c",lazy.window.kill()),
        Key([winkey],"r",lazy.restart()),
        Key([winkey],"q",lazy.shutdown()),
        Key([winkey],"d",lazy.run_extension(
            extension.DmenuRun(
                dmenu_prompt="Run:",
                **font_kwargs["letters"]
            ))),
            ]
    return keys

def apps_keys():
    keys =[
        Key([winkey],"b",lazy.spawn(my_browser)),
        Key([winkey],"e",lazy.spawn(my_ide)),
        Key([winkey],"t",lazy.spawn(my_terminal)),
        Key([winkey],"v",lazy.spawn(my_vmanager)),
        Key([winkey],"o",lazy.spawn(my_recorder)),
            ]
    return keys

def workspace_keys(groups):
    keys = list()
    keys.extend([
        Key(
            [winkey],str(i+1),
            lazy.group[ws.name].toscreen()
        ) for i,ws in enumerate(groups)
            ])
    keys.extend([
        Key(
            [winkey,"shift"],str(i+1),
            lazy.window.togroup(ws.name,switch_group=True)
        ) for i,ws in enumerate(groups)
    ])
    return keys

def init_misc():
    return widget.WidgetBox(
        widgets=[
            widget.Net(),
            widget.Battery(),
            widget.Volume(),
            widget.Systray(icon_size = font_kwargs["icons"]["fontsize"])
            ])

keys = list()
for set in [apps_keys(),mgmt_keys(),window_keys()]:
    keys.extend(set)

groups = [Group(name=ws,label=l) for ws,l in my_workspaces]
ws_keys = workspace_keys(groups)
keys.extend(ws_keys)

@hook.subscribe.client_new
def arrangement(app):
    name = app.window.get_wm_class()[1]
    for i,ws in enumerate(groups):
        if name in class_names[i]:
            group_name = ws.name
            app.togroup(group_name,switch_group=True)

layout_types = [
    layout.MonadTall,
    layout.MonadWide,
    layout.Matrix,
    layout.Max
            ]

layout_kwargs = {
    "border_focus":my_colors["focus"],
    "margin": my_window_margin
            }

layouts = [l(**layout_kwargs) for l in layout_types]

widget_list = [
    (widget.TextBox, {"text": "","foreground":my_colors["focus"]}, font_kwargs["icons"]),
    (widget.TextBox, {"text": "|"}, font_kwargs["icons"]),
    (widget.GroupBox, {"active":my_colors["focus"],"inactive": my_colors["unfocus"], "highlight_method":"line"}, font_kwargs["icons"]),
    (widget.Spacer, {}, {}),
    (widget.KeyboardLayout, {"configured_keyboards":['us','latam']}, font_kwargs["letters"]),
    (widget.TextBox, {"text": "|"}, font_kwargs["icons"]),
    (widget.CurrentLayoutIcon, {"scale": 0.75}, font_kwargs["icons"]),
    (widget.TextBox, {"text": "|"}, font_kwargs["icons"]),
    (widget.TextBox, {"text": ""}, font_kwargs["icons"]),
    (widget.Clock, {"format": "%a %d-%b-%Y"}, font_kwargs["letters"]),
    (widget.TextBox, {"text": "|"}, font_kwargs["icons"]),
    (widget.TextBox, {"text": ""}, font_kwargs["icons"]),
    (widget.Clock, {"format": "%H:%M"}, font_kwargs["letters"]),
            ]

widget_set = [
    [w_object(**w_only,**w_general) for w_object, w_only, w_general in widget_list[:4]],
    [w_object(**w_only,**w_general) for w_object, w_only, w_general in widget_list[4:]],
    [init_misc()]
            ]

widget_kwargs = {"padding": 3}
widget_kwargs.update(font_kwargs["letters"])

extension_defaults = widget_kwargs.copy()

n_monitors = os.popen("xrandr --listmonitors").read()
n_monitors = int(re.split(" ",re.search("Monitors.+",n_monitors)[0])[1])

def init_bar(my_widgets):
    return bar.Bar(
        widgets = my_widgets,
        size = 28,
        background = "#00000000"
    )

screen_widgets = [
    widget_set[0] + widget_set[monitor+1]
    for monitor in range(n_monitors)
            ]
if n_monitors == 1:
    screen_widgets = [
        widget_set[0]
        + widget_set[1]
        + widget_set[2]
            ]

screen_bars = [init_bar(w_set) for w_set in screen_widgets]
screens = [Screen(top=bar) for bar in screen_bars]

mouse = [
    Drag([winkey], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([winkey], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([winkey], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False

floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
])

auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize
# themselves when losing focus
# should we respect this or not?
auto_minimize = True

# XXX: Gasp! We're lying here. In fact, nobody really uses
# or cares about this string besides java UI toolkits;
# you can see several discussions on the mailing lists
# GitHub issues, and other WM documentation that
# suggest setting this string if your java app
# doesn't work correctly.

# We may as well just lie and say that
# we're a working one by default.

# We choose LG3D to maximize irony:
#  - It is a 3D non-reparenting WM written in java
#    that happens to be on java's whitelist.
wmname = "LG3D"
