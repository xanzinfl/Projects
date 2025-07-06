## 420 Finder

### Downloads
[Download Latest Version](https://github.com/xanzinfl/Projects/raw/refs/heads/main/420Finder/dist/420%20Finder.exe?download=)

### Manual Build

1. Download [420Finder.py](https://github.com/xanzinfl/Projects/blob/main/420Finder/420%20Finder.py)

2. Run pip install pyinstaller pytz pystray plyer pywin32

2. pyinstaller --onefile --noconsole --hidden-import=plyer.platforms.win.notification '420 Finder.py'