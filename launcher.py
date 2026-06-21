import os
import json
import zipfile
import subprocess
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox
import requests

# Repository Settings
REPO = "kleorr/Worldtscn"
API_URL = f"https://api.github.com/repos/{REPO}/tags" # Tags reliably return ALL versions
CONFIG_FILE = "launcher_config.json"

ctk.set_default_color_theme("blue")

class GameLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Worldtscn Launcher")
        self.geometry("500x350")
        self.resizable(False, False)

        self.config = self.load_config()
        ctk.set_appearance_mode(self.config.get("theme", "dark"))

        self.releases_data = {}
        
        self.create_widgets()
        threading.Thread(target=self.fetch_versions, daemon=True).start()

    def load_config(self):
        default_config = {
            "install_dir": os.path.join(os.path.expanduser("~"), "Worldtscn_Games"),
            "theme": "dark",
            "close_on_launch": True
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for key, val in default_config.items():
                        if key not in loaded:
                            loaded[key] = val
                    return loaded
            except:
                return default_config
        return default_config

    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=25, pady=(20, 10))

        self.title_label = ctk.CTkLabel(self.top_frame, text="Worldtscn", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")

        self.settings_btn = ctk.CTkButton(self.top_frame, text="⚙ Settings", width=100, height=32, 
                                          fg_color=("gray75", "gray25"), text_color=("black", "white"),
                                          hover_color=("gray65", "gray35"), command=self.open_settings)
        self.settings_btn.pack(side="right")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=10)

        self.ver_label = ctk.CTkLabel(self.main_frame, text="Available Game Versions:", font=ctk.CTkFont(size=14))
        self.ver_label.pack(pady=(20, 5))

        self.version_combo = ctk.CTkComboBox(self.main_frame, width=220, state="readonly", values=["Loading..."])
        self.version_combo.pack(pady=5)
        self.version_combo.configure(command=self.check_version_status)

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=300)
        self.progress_bar.pack(pady=(15, 5))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Fetching version list...", text_color="gray")
        self.status_label.pack(pady=2)

        self.action_btn = ctk.CTkButton(self.main_frame, text="Download", width=180, height=40, 
                                        font=ctk.CTkFont(size=15, weight="bold"), state="disabled", 
                                        command=self.on_action_click)
        self.action_btn.pack(pady=(10, 20))

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=25, pady=(5, 10))

        self.github_link = ctk.CTkLabel(self.bottom_frame, text="⚡ GitHub: kleorr", 
                                        font=ctk.CTkFont(size=12, underline=True), text_color="#1f538d", cursor="hand2")
        self.github_link.pack(side="left")
        self.github_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/kleorr"))

        self.dev_label = ctk.CTkLabel(self.bottom_frame, text="kleorr", font=ctk.CTkFont(size=11), text_color="gray")
        self.dev_label.pack(side="right")

    def open_settings(self):
        SettingsWindow(self)

    def fetch_versions(self):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(API_URL, headers=headers)
            
            if response.status_code == 200:
                tags = response.json()
                self.releases_data.clear()

                for tag_data in tags:
                    tag_name = tag_data["name"]
                    
                    if tag_name == "1.0.0-pre-alpha":
                        filename = "game1.0.zip"
                    else:
                        short_version = tag_name.split("-")[0] 
                        if short_version.endswith(".0") and tag_name in ["1.1.0-pre-alpha", "1.2.0-pre-alpha", "1.3.0-pre-alpha"]:
                            short_version = short_version[:-2] 
                        
                        filename = f"Worldtscn.{short_version}.zip"

                    download_url = f"https://github.com/{REPO}/releases/download/{tag_name}/{filename}"
                    self.releases_data[tag_name] = download_url

                if self.releases_data:
                    versions = list(self.releases_data.keys())
                    self.root_update_ui(lambda: self.version_combo.configure(values=versions, state="readonly"))
                    self.root_update_ui(lambda: self.version_combo.set(versions[0]))
                    self.root_update_ui(self.check_version_status)
                    self.root_update_ui(lambda: self.status_label.configure(text="Ready to use", text_color="green"))
                else:
                    self.root_update_ui(lambda: self.status_label.configure(text="No tags found", text_color="red"))
            else:
                self.root_update_ui(lambda: self.status_label.configure(text=f"API Error: {response.status_code}", text_color="red"))
        except Exception as e:
            self.root_update_ui(lambda: self.status_label.configure(text="No internet connection", text_color="red"))

    def root_update_ui(self, func):
        self.after(0, func)

    def get_version_path(self):
        selected_version = self.version_combo.get()
        if not selected_version or selected_version == "Loading...":
            return None
        return os.path.join(self.config["install_dir"], selected_version)

    def find_executable(self, version_path):
        if not os.path.exists(version_path):
            return None
        for root, dirs, files in os.walk(version_path):
            for file in files:
                name_lower = file.lower()
                if name_lower.endswith(".exe") and "worldtscn" in name_lower and "console" not in name_lower:
                    return os.path.join(root, file)
        return None

    def check_version_status(self, choice=None):
        version_path = self.get_version_path()
        if not version_path:
            self.action_btn.configure(state="disabled")
            return

        self.action_btn.configure(state="normal")
        exe_path = self.find_executable(version_path)
        
        if exe_path:
            self.action_btn.configure(text="Play", fg_color="#2fa572", hover_color="#107c41")
        else:
            self.action_btn.configure(text="Download", fg_color="#1f538d", hover_color="#14375e")

    def on_action_click(self):
        current_state = self.action_btn.cget("text")
        if current_state == "Download":
            self.action_btn.configure(state="disabled")
            self.version_combo.configure(state="disabled")
            self.settings_btn.configure(state="disabled")
            threading.Thread(target=self.download_and_extract, daemon=True).start()
        elif current_state == "Play":
            self.launch_game()

    def download_and_extract(self):
        version = self.version_combo.get()
        url = self.releases_data[version]
        target_dir = self.get_version_path()
        
        os.makedirs(target_dir, exist_ok=True)
        zip_path = os.path.join(target_dir, "update.zip")

        try:
            self.root_update_ui(lambda: self.status_label.configure(text=f"Downloading {version}...", text_color="#1f538d"))
            
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code == 200:
                total_length = response.headers.get('content-length')
                
                if total_length is None:
                    self.root_update_ui(self.progress_bar.start)
                    with open(zip_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    self.root_update_ui(self.progress_bar.stop)
                else:
                    total_length = int(total_length)
                    dl = 0
                    with open(zip_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            dl += len(chunk)
                            f.write(chunk)
                            percent = dl / total_length
                            self.root_update_ui(lambda p=percent: self.progress_bar.set(p))
                
                self.root_update_ui(lambda: self.status_label.configure(text="Extracting archive...", text_color="#1f538d"))
                self.root_update_ui(lambda: self.progress_bar.set(0.9))
                
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(target_dir)
                
                os.remove(zip_path)
                self.root_update_ui(lambda: self.progress_bar.set(1.0))
                self.root_update_ui(lambda: self.status_label.configure(text="Installation completed!", text_color="green"))
            else:
                self.root_update_ui(lambda: self.status_label.configure(text="Build archive not found in this release", text_color="red"))
                messagebox.showerror("Error", f"Failed to download build. Please ensure that the release asset filename on GitHub matches correctly for tag {version}")
        except Exception as e:
            self.root_update_ui(lambda: self.status_label.configure(text=f"Error: {str(e)}", text_color="red"))
        
        self.root_update_ui(lambda: self.version_combo.configure(state="readonly"))
        self.root_update_ui(lambda: self.settings_btn.configure(state="normal"))
        self.root_update_ui(self.check_version_status)

    def launch_game(self):
        version_path = self.get_version_path()
        exe_path = self.find_executable(version_path)
        
        if exe_path:
            self.status_label.configure(text="Launching game...", text_color="green")
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
            
            if self.config.get("close_on_launch", True):
                self.destroy()
        else:
            messagebox.showerror("Error", "Game executable not found! Please try downloading the build again.")
            self.check_version_status()


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("Settings")
        self.geometry("440x280")
        self.resizable(False, False)
        
        self.transient(parent)
        self.attributes("-topmost", True) 

        self.create_settings_widgets()

    def create_settings_widgets(self):
        self.path_label = ctk.CTkLabel(self, text="Game Installations Directory:", font=ctk.CTkFont(size=13, weight="bold"))
        self.path_label.pack(anchor="w", padx=25, pady=(15, 2))

        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=25, pady=5)

        self.path_entry = ctk.CTkEntry(self.path_frame, width=280)
        self.path_entry.insert(0, self.parent.config["install_dir"])
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=70, command=self.browse_dir)
        self.browse_btn.pack(side="right")

        self.theme_label = ctk.CTkLabel(self, text="Launcher Visual Theme:", font=ctk.CTkFont(size=13, weight="bold"))
        self.theme_label.pack(anchor="w", padx=25, pady=(15, 2))

        self.theme_switch = ctk.CTkSwitch(self, text="Dark Theme", command=self.toggle_theme)
        self.theme_switch.pack(anchor="w", padx=30, pady=5)
        if self.parent.config["theme"] == "dark":
            self.theme_switch.select()

        self.behavior_label = ctk.CTkLabel(self, text="Launcher Behavior:", font=ctk.CTkFont(size=13, weight="bold"))
        self.behavior_label.pack(anchor="w", padx=25, pady=(15, 2))

        self.close_switch = ctk.CTkSwitch(self, text="Close launcher upon game execution", command=self.toggle_behavior)
        self.close_switch.pack(anchor="w", padx=30, pady=5)
        if self.parent.config["close_on_launch"]:
            self.close_switch.select()

        self.save_btn = ctk.CTkButton(self, text="Done", width=120, command=self.destroy)
        self.save_btn.pack(pady=(20, 10))

    def browse_dir(self):
        directory = filedialog.askdirectory(initialdir=self.parent.config["install_dir"])
        if directory:
            self.parent.config["install_dir"] = directory
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, directory)
            self.parent.save_config()
            self.parent.check_version_status()

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            self.parent.config["theme"] = "dark"
            ctk.set_appearance_mode("dark")
        else:
            self.parent.config["theme"] = "light"
            ctk.set_appearance_mode("light")
        
        self.parent.save_config()
        self.parent.update()
        self.update()

    def toggle_behavior(self):
        self.parent.config["close_on_launch"] = True if self.close_switch.get() == 1 else False
        self.parent.save_config()


if __name__ == "__main__":
    app = GameLauncher()
    app.mainloop()
