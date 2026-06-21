# Worldtscn Launcher

A modern, lightweight, and autonomous desktop launcher for the **worldtscn** voxel engine. Built with Python and CustomTkinter, it automates version tracking, handles build deployment directly from GitHub, and provides a seamless initialization experience for players.

## 🚀 Key Features

* **Automated Version Tracking:** Dynamically fetches all available tags, pre-alpha, and pre-release builds directly via the GitHub API.
* **Smart Asset Deployment:** Programmatically generates direct download paths to retrieve pre-compiled `.zip` release binaries while completely filtering out raw source code.
* **Real-Time Progress Tracking:** Features a multi-threaded download manager with a visual progress bar that switches to an indeterminate loading state if the server does not provide content-length headers.
* **Automated Extraction & Filtering:** Unpacks downloaded archives into the target directory, scans files to locate the primary game executable, and automatically filters out console variants (`-console` appendics).
* **Context-Aware Execution:** Launches the game with a properly configured Current Working Directory (CWD) to ensure internal game assets and paths resolve correctly.
* **Built-in Configuration Menu:**
  * **Custom Installation Paths:** Easily change the game directory at any time using a native system dialogue window.
  * **Dynamic UI Themes:** Instant on-the-fly switching between Dark and Light visual modes without requiring an application restart.
  * **Post-Launch Behavior:** Toggle between closing the launcher immediately after launching the game or keeping it active in the background.
* **Persistent Settings:** All user preferences (paths, themes, behavior) are automatically serialized into a local JSON configuration file and reloaded upon startup.
* **Standalone Distribution:** Compiled into a single, independent executable via PyInstaller. End-users do not need a Python environment installed.

## 🛠 Tech Stack

* **Core Language:** Python 3.12+
* **User Interface:** CustomTkinter (for a modern, Windows 11-native aesthetic)
* **Networking:** Requests (for GitHub API interactions and binary streaming)
* **System & Concurrency:** `zipfile`, `subprocess`, and `threading` (ensures a responsive UI during heavy I/O operations)

## 📦 Distribution

Pre-compiled standalone binaries can be found in the **Releases** section. Download the executable, place it in your preferred directory, and run.

---
*This launcher is actively maintained alongside the core engine development.*
