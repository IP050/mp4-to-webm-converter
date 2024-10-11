# MP4 to WebM Converter

A simple and efficient GUI application to batch convert MP4 video files to WebM format using FFmpeg. This tool provides an easy-to-use interface for customizing conversion settings, including video quality, target size, resolution, and audio options.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-green.svg)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Install FFmpeg](#install-ffmpeg)
  - [Install Python Dependencies](#install-python-dependencies)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Building an Executable with PyInstaller](#building-an-executable-with-pyinstaller)

## Features

- **Batch Conversion**: Convert multiple MP4 files to WebM format simultaneously.
- **Quality Control**: Adjust video quality using CRF (Constant Rate Factor) values.
- **Target File Size**: Specify the desired output file size per video.
- **Resolution Settings**: Set custom resolutions for output videos.
- **Audio Options**: Include or exclude audio, and set custom audio bitrate.
- **Advanced Parameters**: Add custom FFmpeg parameters for advanced users.
- **Progress Monitoring**: Real-time progress bar and status updates during conversion.
- **Cross-Platform Support**: Works on Windows, macOS, and Linux.
- **Standalone Executable**: Build a standalone executable using PyInstaller.

## Requirements

- **Python 3.6 or higher**
- **Tkinter**: Standard GUI library for Python (usually comes pre-installed).
- **FFmpeg**: Must be installed and added to your system's PATH environment variable.
- **PyInstaller** (optional): For building a standalone executable.

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/mp4-to-webm-converter.git
cd mp4-to-webm-converter
```

###  Running the Application
To run the application directly with Python:

```bash
python mp4_to_webm_converter.py
``` 

### Building an Executable with PyInstaller
You can build a standalone executable of the application using PyInstaller. This allows you to run the application on systems without requiring Python to be installed.

#### Install PyInstaller
If you don't have PyInstaller installed, you can install it using pip:

```bash
pip install pyinstaller
```

#### Build the Executable 
From the project directory:

```bash
pyinstaller --onefile --windowed mp4_to_webm_converter.py
```