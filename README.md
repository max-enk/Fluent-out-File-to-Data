# Fluent .out File to Data

## Introduction

This project aims to automate the post processing of multiple .out files created during the runtime of any Ansys Fluent simulation. Extracted data can be formatted, written to different data formats and directly plotted using the Python plotting library.

As of October 2024, this package is no longer supported by updates and is published to GitHub for public access.


## Prerequisites

### Install and configure Python

To run the scripts, make sure to have a suitable Python environment installed on your machine. The latest version of Python can be downloaded [here](https://www.python.org/downloads/) or via the Microsoft Store. To ensure maximum compatibility, installing Python version 3.11 from the sources is recommended. Using Python 3.12 may cause errors as some of the string formatting works differently.

Additionally, install all the required packages via the windows command line, if not installed already.

```
python -m pip install package
```

Replace "package" with the desired package to be installed.
Required packages:
- os
- sys
- re
- numpy
- matplotlib
- colorama (tested for Windows 11, Visual Studio Code CLI)

In case you are using a version of Python different to the one provided in the Microsoft Store, replace the command line executable "python" with the path to your python.exe, usually in the form of C:/Users/(username)/AppData/Local/Programs/Python/PythonXXX/python.exe when installing from the sources.

### Script Environment

The script will look for files ending on ".out". In the root folder where the script is located, it will first check the specified /Data subdirectory and only read from this folder in case suitable files have been found. If no files are found in the /Data subdirectory or it does not exist, it will check the the script root folder instead. Example files are provided in the /Data directory. The user can change the name of this folder at the top of the script, along with global plot options and other settings.


## Script Functionality and Capabilities

1. __File Setup:__
   - If suitable .out files were found, the user must select the files to be processed. The user can either choose to process all or enter a selection of files. 
2. __Data Extraction:__
   - If the file setup matches Fluent .out files, the raw data and corresponding quantities will be extracted from the file.
3. __Quantity Setup:__
   - A quantity has the following attributes:
      - __name:__ name as found in the datafiles.
      - __description:__ Description of quantity. Will serve as axis label when creating plots. Can contain dimension of quantity in the form of "\[...\]".
      - __offset:__ Global value offset of quantity in the unit of the raw data.
      - __scaling factor:__ Global factor applied to the raw data. Used for unit conversion, e.g. conversion from \[m\] to \[mm\].
      - the final data values are computed for each quantity by 
      ```
      scaling_factor*(value + offset)
      ```
   - __Reference File Operations:__
      - If the file "reference_quantities.dat" exists in the script root directory, the quantities of the current files will be matched with the ones found in the reference file. The settings in the reference file can be copied to the current set.
      - The reference file can be created, extended and updated with this script. The user can also manually edit the file in an editor.
      - It is recommended to move the reference file with the script when post processing and expanding it when new quantities are introduced.
4. __Dataset Creation:__
   - Creation of datasets per file. The scaling factor and offset for each quantity will be applied in this step. If more than one x quantity or y quantity are found in the file, several datasets will be created. An example for this would be the inclusion of different sensors "probe1" and "probe2" in the file to be plotted over the physical simulated time. The sensors are recognized as different quantities, meaning two datasets would be created for this file.
5. __Write to File:__
   - The user has the option to write all datasets to individual files. The following formats are available:
      - Maple: Write x and y data to a single line in the format:
      ```
      [[x1, y1], [x2, y2], ...]
      ```
      - other: Write individual x and y data to multiple lines. A delimiter has to be specified, good options would be " " (space) or "," (comma). When using a comma, the output would be
      ```
      x1,y1
      x2,y2
      :,:
      ```
6. __Plot Creation:__
   - __Individual Plots:__
   Create individual plots for all datasets. These are sorted based on their x and y quantities. Options:
      - Include title in plot. Can be automatically or manually defined.
      - Match axis spacings between all plots with matching quantities. This option is intended to have a better comparability between the individual plots. The minimum and maximum values out of all suitable datasts will be computed. When not matching axis spacings, the local minimum and maximum values will be used. The user can adjust any of these values before creating the plots. 
   - __Combined Plots:__
   Create combined plots from all datasets with matching quantities or descriptions. Options:
      - Include title in plot. Can be automatically or manually defined.
      - Use or adjust computed axis ranges in the same way as for the individual plots.
      - Create combined plots with all datasets found with matching quantities.
      - Create additional plots with selected datasets. This is only possible if the descriptions of the included quantities match. The quantity names can be different here. This setting is intended to be used in the situation, where different variables are written to files during simulation in Fluent, e.g. "probe1" and "probe2". These probes will be recognized as different quantities. If they share the same description or dimension, e.g. "Distance to liquid inlet \[mm\]" measured at two different points in the simulation domain, these datasets can still be combined in one plot.
