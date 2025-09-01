Hi!

Functions:

ChangeWallpaper(path)
Changes the desktop wallpaper.
⚠️ Works only on Windows.
Example: ChangeWallpaper("C:/Images/wallpaper.jpg")
-------------------------------------------

RunCommand(command)
Runs a system command.
⚠️ Won't work if CMD is blocked.
Example: RunCommand("echo hi")
------------------
StartFile(file)
Opens or runs a file.
Example: StartFile("taskmgr.exe")
------------
OpenURL(url)
Opens a website in your default browser.
Example: OpenURL("https://www.google.com")
----------
BlockCmd()
Blocks the command prompt.
⚠️ Windows only.
-------------
BlockTaskmgr()
Blocks Task Manager.
⚠️ Windows only.
-----
Shutdown(seconds)
Shuts down the PC after the specified number of seconds.
Example: Shutdown(5) ⏳
-----
Restart(seconds)
Restarts the PC after waiting for the specified number of seconds.
Example: Restart(5) 
---
BlackScreen(seconds)
Displays a black screen for the specified number of seconds.
Example: BlackScreen(5) ⚫
----
IP()
Displays the IP address of the user. For fun/scaring the user. 
----
FakeBsod()
Displays a fake BSOD and then restarts the PC. Only for scaring. 
-----
Flash(times)
Flashes the screen from black to white as much as you want. ⚡
Just for scaring the user.
Example: Flash(10) # Flashes the screen 10 times
----
MouseChaos(times)
Fixes the cursor at random positions on the screen.
Example: MouseChaos(100) 
-----
Messagebox(title, message, image)
Shows a messagebox.
Example: Messagebox("LMAO", "you've got hacked", "info")
Images: "error", "warning", "info"

what's new in 0.3.1?
- Fixed the Flash bug
