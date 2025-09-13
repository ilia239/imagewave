# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an image processing application that converts images into stencils for eau-forte (etching). The core concept is converting images into sine wave patterns where wave frequency reflects the brightness of corresponding image areas.

### Architecture
- **Backend**: Python Flask server with modular image processing pipeline
- **Frontend**: HTML/CSS/JavaScript web interface with synchronized dual-view
- **Core Algorithm**: Line-based segmentation with intensity-to-frequency mapping

## Development Commands

### Server Setup
```bash
cd server
pip install -r requirements.txt
python app.py
```
Server runs on http://localhost:5001

### Project Structure
```
server/
├── app.py                    # Flask API server
├── image_processor.py        # Line-based image segmentation
├── frequency_mapper.py       # CSV intensity-to-frequency mapping
├── sine_generator.py         # Sine wave calculation per line
├── svg_generator.py          # SVG path creation
├── config/frequency_map.csv  # Default intensity mapping
└── requirements.txt

web/
├── index.html               # Main interface
├── style.css               # Styling
├── script.js               # Upload and API handling
└── viewer.js               # Dual-view zoom/pan synchronization
```

## Core Algorithm

1. **Image Segmentation**: Split input image into horizontal lines (default: 8px height)
2. **Intensity Analysis**: Calculate average pixel intensity for each row within each line
3. **Frequency Mapping**: Convert intensity values to sine wave frequencies using CSV lookup table
4. **Wave Generation**: Generate sine waves for each line with intensity-based frequency
5. **SVG Export**: Convert wave coordinates to SVG path elements

### Configuration
- Line height: Configurable via `/config` endpoint (default: 8 pixels)
- Frequency mapping: Editable in `server/config/frequency_map.csv`
- Wave amplitude: Configurable amplitude factor

## Web Interface Features
- Drag & drop image upload
- Side-by-side original/SVG comparison
- Synchronized zoom and pan between views
- SVG download functionality
- Real-time conversion progress