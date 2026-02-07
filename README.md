# Sleep Chart Extractor
A Python tool designed to extract sleep stage data (N1, N2, N3, REM, Wake) from generated sleep chart images. It scans pixel colors and visual grids to convert graphical charts into a time-series sequence.
## Features
- **Automated Stage Detection**: Identifies sleep stages based on specific RGB color codes.
- **REM Support**: Detects REM stages displayed above the baseline.
- **Timeline Calculation**: Uses vertical grid lines to determine the time scale automatically.
- **Data Compression**: Merges consecutive identical stages for a cleaner output.
## Color Mapping
The script recognizes the following color coding:
- **N1**: Yellow `(255, 255, 0)`
- **N2**: Green `(0, 128, 0)`
- **N3**: Teal `(0, 128, 128)`
- **REM**: Dark Red `(128, 0, 0)`
- **Wake**: Gray/Default background
## Installation
1. Clone the repository.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
