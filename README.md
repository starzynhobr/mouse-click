# AutoClicker Pro

AutoClicker Pro is a lightweight Windows auto-clicker with a modern CustomTkinter interface and a low-level mouse hook for precise physical-click detection.

The app supports two click modes:

* **Hold-to-click:** enable the auto-clicker, hold a mouse button, and it clicks continuously until you release it.
* **Burst mode:** enable burst mode, press a mouse button once, and it fires a configured number of clicks as fast as possible.

## Features

* **Modern desktop UI:** Built with CustomTkinter.
* **Hold-to-click mode:** Continuous clicking only while the physical button is held.
* **Burst mode:** One physical click can trigger up to 500 injected clicks.
* **High-burst warning:** The UI warns when the burst count is above 50 clicks, since very high values can behave unpredictably in some target apps.
* **CPS control:** The CPS slider controls the continuous hold-to-click mode.
* **Full-speed burst behavior:** Burst mode ignores CPS and dispatches the configured clicks as quickly as possible.
* **Low-level mouse hook:** Uses `WH_MOUSE_LL` and ignores injected events with `LLMHF_INJECTED`, preventing the auto-clicker from reacting to its own clicks.
* **Middle-click toggle:** Toggle the auto-clicker with the scroll button.
* **Keyboard shortcut:** Default shortcut is `<ctrl>+<shift>+a`, shown in the UI as `Ctrl+Shift+A`.
* **Right-click support:** Optional auto-clicking for the right mouse button.
* **System tray support:** Optional minimize-to-tray behavior.
* **Localization:** Minimal `PT` and `EN` language selector in the top-right corner.

## How To Use

1. Download `gui.exe` from the repository releases.
2. Run `gui.exe`.
3. Use the scroll button or `Ctrl+Shift+A` to enable or disable the auto-clicker.
4. In default mode, hold the left mouse button to click continuously.
5. Enable right-click support if you also want the right mouse button to trigger clicks.
6. Enable burst mode if you want one physical click to fire a fixed number of clicks.
7. Adjust `Clicks per burst` to choose how many clicks each burst sends.

Running as administrator is recommended when you need the mouse hook to work across elevated programs or apps that capture input more aggressively.

## Behavior Notes

### Hold-To-Click

The `Clicks per Second` slider controls the interval between clicks:

```text
click_interval = 1 / cps
```

For example, `50 CPS` means roughly one click every `0.02` seconds while the button is held.

### Burst Mode

Burst mode is independent from CPS. It sends the configured number of clicks in a tight loop with no intentional delay between clicks.

This makes small bursts feel almost instant, but very large bursts can still take noticeable time depending on the target app, Windows scheduling, and how quickly the target processes input events.

Some apps may drop, merge, throttle, or react unpredictably to very fast injected input. That is expected behavior for high burst counts and is not usually a hardware limitation.

## Developer Setup

This project targets Windows and uses Python.

1. Clone the repository:

    ```bash
    git clone https://github.com/starzynhobr/mouse-click.git
    cd mouse-click
    ```

2. Create and activate a virtual environment:

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

3. Install dependencies:

    ```powershell
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```

4. Run the app:

    ```powershell
    python gui.py
    ```

If your virtual environment was created without `pip`, bootstrap it with:

```powershell
.\.venv\Scripts\python.exe -m ensurepip --upgrade
```

## Building With Nuitka

Install Nuitka and its recommended helpers:

```powershell
python -m pip install nuitka zstandard ordered-set
```

Build a single-file executable:

```powershell
python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-package=customtkinter --include-data-file="config.json=config.json" --output-dir=dist gui.py
```

If your machine does not have a C compiler available, or if you are using a newer Python version where Nuitka recommends Zig, use:

```powershell
python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-package=customtkinter --include-data-file="config.json=config.json" --output-dir=dist --assume-yes-for-downloads --zig gui.py
```

The generated one-file executable will be:

```text
dist/gui.exe
```

The generated `gui.exe` is the file intended for distribution. Nuitka may also leave build folders such as `gui.build`, `gui.dist`, and `gui.onefile-build` for inspection; those folders are not needed by end users when distributing the one-file executable.

## Distribution Notes

Without code signing, Windows SmartScreen or antivirus tools may warn users because the executable is new and unsigned. This can happen with Nuitka, PyInstaller, or any other unsigned Windows executable.

For simple GitHub Releases, the recommended artifact is the one-file `dist/gui.exe`. For maximum compatibility, you can also provide a zipped standalone build in addition to the one-file build.

## Licensing

This project is available under dual licensing:

* **Community use (GPLv3):** Suitable for open-source usage, learning, and community projects. Derivative code must remain open under GPL-compatible terms.
* **Commercial use:** A commercial license is required if you want to integrate AutoClicker Pro into proprietary software, sell it as part of a closed product, or use it commercially without GPLv3 obligations.

For commercial licensing or partnership questions, contact: `starzynhobr@gmail.com`.
