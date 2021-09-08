import os, json, re, subprocess
from libqtile.backend import base
from libqtile import bar, layout
from libqtile import extension, hook, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

CONFIG_DIR = "~/.config/qtile"
START = "start.sh"
RESTART = "restart.sh"
my_fontfamily = {
    "icons": "NotoSansMono Nerd Font",
    "letters": "SauceCodePro Nerd Font"
            }
my_fontsize = {
    "icons": 17,
    "letters": 15
            }

my_window_margin = 15

my_terminal = "alacritty"
my_ide = "emacsclient -c -a 'emacs'"
my_browser = "brave"
my_recorder = "obs"
my_vmanager = "VirtualBox"

class_names = {
    0 : ["Pavucontrol"],
    1 : ["Alacritty"],
    2 : ["Emacs"],
    3 : ["Libre Office"],
    4 : ["VirtualBox Manager"],
    5 : ["vlc"],
    6 : ["Nitrogen"],
    7 : ["Brave-browser"],
    8 : ["obs"]
            }

my_baropacity= 0.70
my_colors = {
    "focus": "#46d9ff",
    "unfocus": "#ffffff",
    "background": "#000e35",
    "foreground": "#002282"
            }

mod = "mod4"

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

for file in [START, RESTART]:
    os.chmod(
        path=os.path.expanduser(CONFIG_DIR + "/" + file),
        mode=0o755
            )

@hook.subscribe.startup_once
def qtile_startup():
    executable = CONFIG_DIR + "/" + START
    executable = os.path.expanduser(executable)
    subprocess.call([executable])

@hook.subscribe.startup
def qtile_restarts():
    executable = CONFIG_DIR + "/" + RESTART
    executable = os.path.expanduser(executable)
    subprocess.call([executable])

def window_keys():
    keys = [
        Key([mod],"Return",lazy.layout.swap_main()),
        Key([mod],"space",lazy.next_layout()),
        Key([mod],"Tab",lazy.window.toggle_floating()),
        Key([mod],"Left",lazy.screen.prev_group()),
        Key([mod],"Right",lazy.screen.next_group()),
            ]
    return keys

def mgmt_keys():
    keys = [
        Key([mod,"shift"],"c",lazy.window.kill()),
        Key([mod],"r",lazy.restart()),
        Key([mod],"q",lazy.shutdown()),
        Key([mod],"d",lazy.run_extension(
            extension.DmenuRun(
                dmenu_prompt="Run:",
                font=my_fontfamily["letters"],
                fontsize=my_fontsize["letters"]
            ))),
            ]
    return keys

def apps_keys():
    keys =[
        Key([mod],"b",lazy.spawn(my_browser)),
        Key([mod],"e",lazy.spawn(my_ide)),
        Key([mod],"t",lazy.spawn(my_terminal)),
        Key([mod],"v",lazy.spawn(my_vmanager)),
        Key([mod],"o",lazy.spawn(my_recorder)),
            ]
    return keys

def workspace_keys(groups):
    keys = list()
    keys.extend([
        Key(
            [mod],str(i+1),
            lazy.group[ws.name].toscreen()
        ) for i,ws in enumerate(groups)
            ])
    keys.extend([
        Key(
            [mod,"shift"],str(i+1),
            lazy.window.togroup(ws.name,switch_group=True)
        ) for i,ws in enumerate(groups)
    ])
    return keys

def init_calendar():
    return widget.Clock(
        format = " %a %d-%b-%Y"
            )

def init_clock():
    return widget.Clock(
        format = " %H:%M"
            )

def init_currentlayout():
     return widget.CurrentLayoutIcon(
         font = my_fontfamily["icons"],
         fontsize = my_fontsize["icons"],
         scale = 0.75
            )

def init_delimiter():
    return widget.TextBox(
        text = "|",
        font = my_fontfamily["icons"],
        fontsize = my_fontsize["icons"]+7,
        foreground = "#FFFFFF"
            )

def init_groupbox():
    return widget.GroupBox(
        font = my_fontfamily["icons"],
        fontsize = my_fontsize["icons"]+5,
        highlight_method = "line",
        active = my_colors["focus"],
        inactive = my_colors["unfocus"]
            )

def init_logo():
    return widget.TextBox(
        text = "",
        font = my_fontfamily["icons"],
        fontsize = my_fontsize["icons"]+5,
        foreground = my_colors["focus"]
            )

def init_misc():
    return widget.WidgetBox(
        widgets=[
            widget.Net(),
            widget.Battery(),
            widget.Volume()
            ])

def init_systray():
    return widget.Systray(
        icon_size = my_fontsize["icons"]
            )

def init_bar():
    new_bar = bar.Bar(
        widgets=[
            init_logo(),
            init_delimiter(),
            init_groupbox(),
            widget.Spacer(),
            init_currentlayout(),
            init_delimiter(),
            init_calendar(),
            init_delimiter(),
            init_clock()
            ],
        size=28,
        background = "#00000000",
        opacity = my_baropacity
            )
    return new_bar

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

widget_defaults = dict(
    font=my_fontfamily["letters"],
    fontsize=my_fontsize["letters"],
    padding=3,
)

extension_defaults = widget_defaults.copy()

primary_bar = init_bar()
secondary_bar = init_bar()

screens = [
    Screen(top=secondary_bar),
    Screen(top=primary_bar)
]

mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
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

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
