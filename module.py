#! /usr/bin/python3

import os
import asyncio
import getpass
import i3ipc
import platform
from time import sleep
from collections import Counter

from icon_resolver import IconResolver

#: Max length of single window title
MAX_LENGTH = 70
#: Base 1 index of the font that should be used for icons
ICON_FONT = 3

HOSTNAME = platform.node()
USER = getpass.getuser()

ICONS = [

    ("class=Chromium-browser|Google-chrome" , "\uf268" , "#367dd0") ,
    ("class=TelegramDesktop"                , "\uf3fe" , "#32AADF") ,
    ("class=URxvt|Termite|Tilix"            , "\uf120" , "#772953") ,
    ("class=netease-cloud-music"            , "\uf1bc" , "#C72E2E") ,
    ("class=Spotify"                        , "\uf1bc" , "#1DB954") ,
    ("class=electronic-wechat|Wechat"       , "\uf1d7" , "#B2E281") ,
    ("class=Artha"                          , "\uf02d" , "#835c3b") ,
    ("class=Mailspring"                     , "\uf0e0" , "#F6C12A") ,
    ("class=Nemo|Nautilus"                  , "\uf07c" , "#F7C800") ,
    ("class=Wps"                            , "\uf72b" , "#6090E6") ,
    ("class=MuPDF|Zathura|Foxit"            , "\uf724" , "#F68B1F") ,
    ("class=Et"                             , "\uf71a" , "#387E3F") ,
    ("class=Wpp"                            , "\uf726" , "#ae5831") ,
    ("class=File-roller"                    , "\uf1c6" , "#367BF0") ,
    ("class=Emacs"                          , "\uf2d7" , "#694E7F") ,
    ("class=Gnome-system-monitor"           , "\uf159" , "#689D6A") ,
    ("class=Zeal"                           , "\uf128" , "#D86888") ,
    ("class=Gpick"                          , "\uf5ac" , "#357AF0") ,
    ("class=stacer"                         , "\uf135" , "#212F3C") ,
    ("class=Firefox"                        , "\uf269" , "#FF3729") ,
    ("class=Inkscape"                       , "\uf1fc" , "#5C2E4F") ,
    ("class=electron-ssr"                   , "\uf5d2" , "#51B9C3") ,
    ("class=Matplotlib|Toplevel"            , "\uf200" , "#FF7D3B") ,
    ("class=Steam"                          , "\uf11b" , "#316282") ,
    ("class=Vivaldi"                        , "\uf27d" , "#D73333") ,
    ("class=draw.io"                        , "\uf542" , "#F08705") ,
    ("class=Code"                           , "\ufb0f" , "#007ACC") ,
    ("class=feh|Eog"                        , "\uf03e" , "#74AECE") ,
    ("class=.*"                             , "\uf0c9" , "#ffffff") ,

]

FORMATERS = {
    'Chromium': lambda title: title.replace(' - Chromium', ''),
    'Firefox': lambda title: title.replace(' - Mozilla Firefox', ''),
    'URxvt': lambda title: title.replace('%s@%s: ' % (USER, HOSTNAME), ''),
}

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
COMMAND_PATH = os.path.join(SCRIPT_DIR, 'command.py')

icon_resolver = IconResolver(ICONS)


def main():
    i3 = i3ipc.Connection()

    i3.on('workspace::focus', on_change)
    i3.on('window::focus', on_change)
    i3.on('window', on_change)

    loop = asyncio.get_event_loop()

    loop.run_in_executor(None, i3.main)

    render_apps(i3)

    loop.run_forever()


def on_change(i3, e):
    render_apps(i3)

def dfs(r, con):
    if not r.nodes:
        con.append(r)
    else:
        for n in r.nodes:
            dfs(n, con)
    return

def render_apps(i3):
    tree = i3.get_tree()

    #  import ipdb; ipdb.set_trace()
    focused = tree.find_focused()
    workspace = focused.workspace()
    if workspace is not focused:
        #  while parent is not parent.workspace() and parent.layout != 'tabbed':
        #      parent = parent.parent
        #  apps = workspace.leaves() if workspace is not None else []
        apps = []
        dfs(workspace, apps)
        apps = [app for app in apps if not 'on' in app.floating]
        apps.sort(key=lambda app: app.workspace().name)

        #  out = '%{O12}'.join(format_entry(app) for app in apps)
        klass_counter = Counter([app.window_class for app in apps])
        out = ' '.join(make_title(app, klass_counter, MAX_LENGTH // len(apps)) for app in apps)
    else:
        out = workspace.name

    print(out, flush=True)


def make_title(app, klass_counter, max_length):
    if app.window_class is None:
        out = app.name
    else:
        out = get_prefix(app) + ' '
        f_color = icon_resolver.get_color({'class': app.window_class}) if app.focused else\
            '#e84f4f' if app.urgent else\
            '#ffffff'

        #  if app.focused:
        #  out += '%%{F%s}' % (f_color) + format_title(app, klass_counter, max_length) + '%{F-}'
        out += format_title(app, klass_counter, max_length)
        #  else:
        #      out += format_title(app)

    title = '%%{A1:%s %s:}%s%%{A-}' % (COMMAND_PATH, app.id, out)

    u_color = f_color if app.focused else\
        '#e84f4f' if app.urgent else\
        '#404040'

    return '%%{o%s} %s %%{-o}' % (u_color, title)


def get_prefix(app):
    icon = icon_resolver.resolve({
        'class': app.window_class,
        'name': app.name,
    })

    return ('%%{T%s}%s%%{T-}' % (ICON_FONT, icon))


def format_title(app, klass_counter, max_length):

    title = app.window_class if klass_counter[app.window_class] == 1 else app.name
    #  title = FORMATERS[klass](name) if klass in FORMATERS else name

    if len(title) > max_length:
        title = title[:max_length - 3] + '...'
    else:
        left_padding = (max_length - len(title)) // 2
        right_padding = max_length - len(title) - left_padding
        title = ' ' * left_padding + title + ' ' * right_padding

    return ' ' + title + ''

main()
