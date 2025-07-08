## Setup

### Download & Install Dependencies
1. Download [MC Anti-Raid](https://github.com/xanzinfl/Projects/raw/refs/heads/main/MC-Anti-Raid/MC%20Anti-Raid.exe?download=), [Region Finder](https://github.com/xanzinfl/Projects/raw/refs/heads/main/MC-Anti-Raid/Region%20Finder.exe?download=), [MPOS](https://sourceforge.net/projects/mpos/)

2. Download and install [Tesseract](https://github.com/UB-Mannheim/tesseract/releases/latest)
- Add `C:\Program Files\Tesseract-OCR` to your system PATH

### Configuring OCR Capture
3. Run MPOS and place your mouse in the top left of where your subtitles are and save the "Physical" x and y positions

4. Run Region Finder and input the x and y values from MPOS and set the width and height 300 to start, then press preview to see what its capturing

5. Adjust the x,y,w,h values till it captures the entierty of your subtitles
  > Keep a bit of overhang on the capture area since some subtitles are longer

6. Once your capture area is the correct size for your monitors resolution click the copy button.

7. Launch MC Anti-Raid and paste the values from Region Finder into "OCR Region"


## Notes
You can change the audio by specifying your own path, or replacing alert.mp3 in `%YourUser\Documents\MCAnti-Raid\%`

