# OpenModelica-GUI-Runner-Batch-Version
PyQt6 GUI application to run OpenModelica simulations using batch (.bat) launcher with result visualization

# OpenModelica GUI Runner - Batch Version

This repository contains the OpenModelica-generated simulation files used by the PyQt6 GUI runner project.

## Purpose

The files in this repository are the runtime output produced by OpenModelica for the `TwoConnectedTanks` model.  
They are kept separately so the GUI project stays clean and easy to use.

## Repository Contents

- `TwoConnectedTanks.bat`
- `TwoConnectedTanks.exe`
- `TwoConnectedTanks.log`
- `TwoConnectedTanks_info.json`
- `TwoConnectedTanks_init.xml`
- generated runtime files
- simulation output files

## How to Use

1. Download or clone this repository.
2. Keep the generated files together in the same folder.
3. Open the main GUI project repository.
4. Run `main.py`.
5. In the GUI, browse and select the `TwoConnectedTanks.bat` file from this folder.
6. Enter the start time and stop time.
7. Click **Run Simulation**.

## Notes

- Do not move the `.bat` file away from its generated support files.
- The `.bat` file is the recommended entry point for running the simulation correctly.
- The simulation output `.mat` file is created during execution and used by the GUI for plotting.

## Author

Rishit Sutar
