# scatterometer_data_parsing
This script can be used to parse Scatterometer data, as obtained from L-Band and C-Band Scatterometer's to an excel spreadsheet 

**INTRODUCTION**
This program is a script to parse C-Band and L-Band Scatterometer files to excel spreadsheets to aid in data processing and representation.

**RUNNING THE CODE**
The Scatterometer.py file is the main function and can be run by downloading any dependencies not parsed by the Python compiler using pip, then clicking run.

The program will prompt the user for the directory where the scatterometer files are, and upon chosing the directory the program will parse the data, and further prompt the user to chose the output directory. Upon chosing this directory, an output file called 'Output.xlsx' will be made in the output directory.
**NOTE: The code is setup to parse multiple files in a directory, hence the user need not chose a single file, unless a single file is all that in the chosen directory**

The Output file will contain polarization coefficients: hh, vv, vh, hv and rho, rho_calculated, mu, alpha, and H.
