# Polybar i3 workspace windows

This script shows all windows in the current i3 workspace in polybar.

## Features

* Focus workspace and window on left mouse button click
* Highlight urgent windows
* Remove unnecessary text from window titles like " - Chromium" for chromium windows to make them shorter
* Icon color supported
* Window name is only shown when there are multiple same applications in the current workspace, or there will only be their class name
* Shorten the bar when there are many windows. They could still overflow, unfortunately.

## Dependencies
* i3-ipc

## Example config

```ini
[module/i3-windows]
type = custom/script
exec = ~/projects/polybar-i3-workspace-windows/module.py
tail = true
```

The scripts expects font-2 to be the font that should be used for icons. You probably want it to have higher size than your regular font. Example:

```ini
font-0 = NotoSans Nerd Font:size=10;2      
font-1 = siji:pixelsize=16;1 
font-2 = NotoSans Nerd Font:size=16;4
```
