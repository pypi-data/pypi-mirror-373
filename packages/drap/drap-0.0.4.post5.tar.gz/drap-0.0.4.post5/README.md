# Droplet Computer program

This package allows the analysis of videos and images in EDF format to extract 
physical parameters of droplets in acoustic levitation or other experimental techniques. 
The graphical user interface provides:

- Region of interest cropping  
- Morphological analysis  
- Polynomial fitting of data  
- PDF report generation  

## How to use

Install:

    python -m venv venv

    source venv/bin/activate (Linux) or venv\Scripts\activate (windows)

    pip install drap

Use:

    drap -o 1 (Gui interface)

    drap -o 2 (Terminal interface)

    drap -o 3  (Automatic file: name_videos.dat)