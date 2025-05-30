# MusiCarol - Local music manager and organizer
Copyright (C) 2025 Laura Gómez Panizo

```
         		█████████                       
                     █████████████████                   
                   █████████████████████                 
                 █████████████████████████               
                ███████████████████████████              
              ██████████████████████████████             
              ███████████████████████████████            
             ████████████████████████████████            
            ██████████████████████████████████           
            ██████████████████████████████████           
            ███████ █████████████████████████████        
         ██████████  ███████████ ████████████████████    
     █████████████     █████████  █████████████████  ██  
   ███████████████████ █████████   ████████████████   ██ 
 ███  ████████████    ██████████  ████     ████████    ██
██ ██ █████████ ██      ██████████    ██    ████████   ██
██ █ █  ███████ ███████   ██████       ███  ████████   ██
██ █ █ ██ █████ ███ ████   █████ █████  ████  ██████   ██
██ █ █ █  ████████  █████   ████  █████   ██  █  ██   ██ 
 █     █  ████████   ████   ██     ███  ██  █ █  █████  
  ██      █████████         █ █        ██ █ █ █  █       
    ██       █████  █████████  ███████ █  █ █ █ ██       
     ███      ██████                  ██  ███   █        
        ██    ████████      ███     ███       ██         
         ██   ████████████   ██  ████       ███          
      ████    ███████████████████████     ███   ██       
      ████    ██       ██  ██████████   ████  ████       
      ████                   ████████   ██████████       
       ███                     ██████   ██████████       
                                █████   ████████         
                                 ████   ██████                    
```

This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 2 of the License, or (at your option) any later 
version.

This program is distributed in the hope that it will be useful, but WITHOUT 
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more 
details.

You should have received a copy of the GNU General Public License along with 
this program; if not, write to the Free Software Foundation, Inc., 675 Mass 
Ave, Cambridge, MA 02139, USA.

------------
[2025-05-30] VERSION: 1.0.0 (For Windows 10/11)
------------

Welcome to MusiCarol, an mp3 file manager and organizer!

Visit us at: https://github.com/lauragomezp/musicarol

Feel welcome to share bug reports, feature requests, development ideas or general discussion.

If you have any questions, read the FAQ in out GitHub repo first <3

------------
Features
------------

- **MP3 format:** MusiCarol supports the main music format and will soon include support for FLAC.
- **Mutagen:** MusiCarol uses the well-known Python library Mutagen to manage the file's metadata, in which all versions of ID3v2 are supported, and all standard ID3v2.4 frames are parsed.
- **Open source:** MusiCarol is licensed under the GNU General Public License 2.0 or later, and is hosted on GitHub where it is actively developed.
- **API implementation**: MusiCarol implements the MusicBrainz API to complete some missing metadata tags.

-----------
Installation guide
-----------

To properly run MusiCarol, make sure you have **Python 3.7 or higher** installed, as well as **pip**, Python’s package manager.

## How to install Python and pip

- **Python 3.7+**

  Download and install Python from the official website:
  [https://www.python.org/downloads/](https://www.python.org/downloads/)

  Make sure to download a version **3.7 or higher** for your operating system (Windows, macOS, Linux).

- **pip** (usually comes bundled with Python)

  To check if pip is installed, open your terminal and run:

  ```bash
  pip --version
  ```

  If pip is not installed, follow the instructions here:
  [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)

---

After making sure both Python 3.7 and pip are properly installed, follow the next step-by-step instructions:

## Clone the repository

Open your terminal (PowerShell on Windows, or bash on Linux/macOS), navigate to the folder where you want to save the project, then run:

```bash
git clone https://github.com/lauragomezp/musicarol.git
cd musicarol
```

## Install all dependencies

Then run the following command, it will install all the dependecies necessary to run MusiCarol automatically.

```bash
pip install -r requirements.txt
```

## Run the app

```bash
python musicarol.py
```

MusiCarol should open next to it's help window!

------------
FAQ
------------

- Which file formats does it support?

As of today, MusiCarol only supports .mp3 formatted files.

- Does it require internet conexion?

No, only when the functions related to the API are used.

- Where can I find a download page with the executables?

There's no download page yet, but you can follow the installation guide to run the program on your computer as long as you have Python 3.7 or higher installed.

- How stable is it? Can it work with huge music batches?

MusiCarol has been tested with up to 2000 MP3 files without any issues, and no specific performance limit has been identified.
