# this script extracts data from an Ansys Fluent .out file
# the data can be converted into a different format and plotted with pyplot

# environment parameters
dataname = "Data"                       # name of subfolder containing data
reffile = "reference_quantities.dat"    # name of file containing reference quantities
ref_delimiter = "?"                     # delimiter used in reffile (caution, only change when explicitly relevant!)

prec = 6                                # numerical precision for statistics

# global plot options
figxsize = 16                           # figure x size
figysize = 9                            # figure y size
linesize = 2                            # data line size
titlefontsize = 28                      # title font size
labelfontsize = 24                      # labels font size
axisfontsize = 20                       # axes font size
legendfontsize = 20                     # legend font size
resolution = 300                        # plot resolution in dpi
plottype = "plot"                       # plot type: lineplot ("plot"), pointplot ("scatter")



############################################################### DO NOT EDIT BELOW ###############################################################
# dependencies
import os                               # operating system operations
import sys                              # system operations
import re                               # regular expressions
import numpy as np                      # numerical python
from matplotlib import pyplot as plt    # python plotting
from colorama import Fore, Style, init          # console output formatting (validated to run on a windows system)


# change to directory containing the script
sourcedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourcedir)
datadir = os.path.join(sourcedir, dataname)



print(f"{Style.BRIGHT}#################################################################### WELCOME ####################################################################{Style.RESET_ALL}")
############################################################## FUNCTION DEFINITION ##############################################################
# returns answer to yes/no query
def ynquery(queryline):
    while True:
        query = input(queryline).lower()

        if query == "y":
            result = True
            break
        elif query == "n":
            result = False
            break
        else:
            print(f"{Fore.RED}Invalid input.\n{Style.RESET_ALL}")
    print()
    return result


# extract all lines from file
def getlines(datafile):
    try:
        with open(datafile, 'r') as file:
            # get file contents
            lines = file.readlines()
            file.close()
    except FileNotFoundError:
        lines = []
    return lines


# extract quantities from file
def getquants(lines):
    # extract quantities
    if len(lines) > 0:
        # find line containing quantitiy names
        quantline = ""
        for index in range(len(lines)):
            if lines[index].startswith("("):
                quantline = lines[index]
                break
        # extract quantity names
        quants = quantline.split('"')[1::2]
    else:
        quants = []
    return quants


# extract data from file
def getdata(lines):
    # extract quantities
    if len(lines) > 0:
        # find line containing quantitiy names
        quantindex = 0
        for index in range(len(lines)):
            if lines[index].startswith("("):
                quantindex = index
                break
        # extract data
        datalines = lines[quantindex+1:]
        data = []
        for line in datalines:
            data.append(line.strip().split())
    else:
        data = []
    return data


# set quantity parameters
def setquantities(quant, type):
    quant.settype(type)

    descr = input("\nEnter description of quantity:\n>>> ")
    quant.setdescr(descr)

    # offset definition
    while True:
        q_offset = input(f"\nDefine global value offset for quantity '{quant.getname()}'.\nLeave blank for no offset.\n>>> (0.0) ")
        try:
            offset = float(q_offset)
            quant.setoffset(offset)
            break
        except ValueError:
            if q_offset == "":
                quant.setoffset(0.0)
                break
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number or leave the prompt blank.")

    # scaling factor definition
    while True:
        q_factor = input(f"\nDefine global value scaling factor for quantity '{quant.getname()}'.\nLeave blank for no scaling.\n>>> (1.0) ")
        try:
            factor = float(q_factor)
            quant.setfactor(factor)
            break
        except ValueError:
            if q_factor == "":
                quant.setfactor(1.0)
                break
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number or leave the prompt blank.")
        break


# get minimum and maximum values from data
def getminmax(sets, datatype):
    for i in range(len(sets)):
        # first entry
        if i == 0:
            if datatype == "xdata":
                data = sets[i].getxdata()
            else:
                data = sets[i].getydata()
            
            min = np.min(data)
            max = np.max(data)

        # further entries
        else:
            if datatype == "xdata":
                data = sets[i].getxdata()
            else:
                data = sets[i].getydata()

            if min > np.min(data):
                min = np.min(data)
            if max < np.max(data):
                max = np.max(data)
    return min, max


# set minimum and maximum values 
def setminmax(descr, min, max):
    while True:
        # min
        while True:
            q_min = input(f"Enter minimum value of quantity '{descr}':\n>>> ({min}) ")

            try:
                min = float(q_min)
                print()
                break
            except ValueError:
                if q_min == "":
                    break
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.\n")

        # max
        while True:
            q_max = input(f"Enter maximum value of quantity '{descr}':\n>>> ({max}) ")

            try:
                max = float(q_max)
                print()
                break
            except ValueError:
                if q_max == "":
                    break
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.\n")

        if min < max:
            break
        else:
            print(f"{Fore.RED}Invalid choice of values.{Style.RESET_ALL} Minimum '{min}' must be smaller than maximum '{max}'.\n")
    return min, max                    


# create plot
def createplot(plot):
    plt.figure(figsize=(figxsize, figysize))

    # data
    xdatasets = plot.getxdata()
    ydatasets = plot.getydata()
    legend = plot.getlegend()

    # pointplot
    if plottype == "scatter": 
        for i in range(len(xdatasets)):
            plt.scatter(xdatasets[i], ydatasets[i], label = legend[i])
    # lineplot
    else:
        for i in range(len(xdatasets)):
            plt.plot(xdatasets[i], ydatasets[i], label = legend[i], linewidth = linesize)

    # title
    title = plot.gettitle()
    if not title == "":
        plt.title(title + "\n", fontsize = titlefontsize)

    # labels
    plt.xlabel(plot.getxlabel(), fontsize = labelfontsize)
    plt.ylabel(plot.getylabel() + "\n", fontsize = labelfontsize)

    # axis ranges
    plt.xlim(plot.getxmin(), plot.getxmax())
    plt.ylim(plot.getymin(), plot.getymax())

    # axis font
    plt.xticks(fontsize = axisfontsize)
    plt.yticks(fontsize = axisfontsize)

    # legend
    if len(xdatasets) > 1:
        plt.legend(fontsize = legendfontsize)

    # grid
    plt.grid(True)

    # save to file
    filename = plot.getname() + ".png"
    plt.savefig(filename, dpi=resolution)
    plt.close()
    print(f"Created plot '{filename}'")

    

################################################################ CLASS DEFINITION ###############################################################
# dataset class definition
class Dataset:
    # dataset constructor
    def __init__(self, name, quants, data):
        self.name = name                # name of file
        self.quants = quants            # quantities found in file
        self.data = data                # dataset found in file

    # dataset destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):
        return self.name
    def getquants(self):
        return self.quants
    def getdata(self):
        return self.data
    

# quantitiy class definition
class Quantity:
    # quantity constructor
    def __init__(self, name, type, descr, offset, factor):
        self.name = name                # quantity name
        self.count = 1                  # count of datafiles where quantity is included
        self.type = type                # type of quantity (none/xdata/ydata)
        self.descr = descr              # description of quantity
        self.offset = float(offset)     # absolute offset of quantity
        self.factor = float(factor)     # scaling factor for variable

    # quantity destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):
        return self.name
    def getcount(self):
        return self.count
    def gettype(self):
        return self.type
    def getdescr(self):
        return self.descr
    def getoffset(self):
        return self.offset
    def getfactor(self):
        return self.factor
    def getref(self):
        line = self.name
        line += ref_delimiter + self.type
        line += ref_delimiter + self.descr
        line += ref_delimiter + str(self.offset)
        line += ref_delimiter + str(self.factor)
        return line
    
    # setter functions
    def addcount(self):                 # increase count by 1
        self.count += 1
    def settype(self, type):            # set type of quantity
        self.type = type
    def setdescr(self, descr):          # set description of quantity
        self.descr = descr
    def setoffset(self, offset):        # set absolute offset of quantity
        self.offset = float(offset)
    def setfactor(self, factor):        # set scaling factor of quantity
        self.factor = float(factor)


# xydata class definition
class XYdata:
    # xydata constructor
    def __init__(self, header, xquant, yquant, xdata, ydata):
        self.header = header            # header of xydata
        self.xquant = xquant            # x quantity of data
        self.yquant = yquant            # y quantity of data
        self.xdata = xdata              # x data
        self.ydata = ydata              # y data

    # xydata destructor
    def __del__(self):
        pass

    # getter functions
    def getheader(self):
        return self.header
    def getxquant(self):
        return self.xquant
    def getyquant(self):
        return self.yquant
    def getxdata(self):
        return self.xdata
    def getydata(self):
        return self.ydata
    

# plot class definition
class Plot:
    # plot constructor
    def __init__(self, name, title, xlabel, ylabel, xdata, ydata, xmin, xmax, ymin, ymax, legend):
        self.name = name            # name of plot for filename
        self.title = title          # plot title
        self.xlabel = xlabel        # x axis label
        self.ylabel = ylabel        # y axis label
        self.xdata = xdata          # list of plot xdata
        self.ydata = ydata          # list of plot ydata
        self.xmin = xmin            # minimum value on x axis
        self.xmax = xmax            # maximum value in x axis
        self.ymin = ymin            # minimum value on y axis
        self.ymax = ymax            # maximum value in y axis
        self.legend = legend        # legend list

    # surface destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):
        return self.name
    def gettitle(self):
        return self.title
    def getxlabel(self):
        return self.xlabel
    def getylabel(self):
        return self.ylabel
    def getxdata(self):
        return self.xdata
    def getydata(self):
        return self.ydata
    def getxmin(self):
        return self.xmin
    def getxmax(self):
        return self.xmax
    def getymin(self):
        return self.ymin
    def getymax(self):
        return self.ymax
    def getlegend(self):
        return self.legend
    


################################################################# COLLECT FILES #################################################################
outfiles = []


# first check for .out files in specified data directory
if os.path.exists(datadir) and os.path.isdir(datadir):
    # collect all outfiles
    outfiles = [file for file in os.listdir(datadir) if file.endswith(".out")]
    
    # check if files were found
    if len(outfiles) > 0:
        print(f"Found {len(outfiles)} .out file(s) in the /{dataname} directory.")
        currentdir = datadir
    else:
        print(f"{Fore.RED}No .out files found in the specified data directory /{dataname}.{Style.RESET_ALL}\nChecking current directory instead.")
else:
    print(f"{Fore.RED}The specified data directory /{dataname} does not exist in the current directory.{Style.RESET_ALL}\nChecking current directory instead.")


# if no files were found in the specified date directory, check script source folder instead
if len(outfiles) == 0:
    # collect all outfiles
    outfiles = [file for file in os.listdir(sourcedir) if file.endswith(".out")]
    
    #check if files were found
    if len(outfiles) > 0:
        currentdir = sourcedir
        print(f"\nFound {len(outfiles)} .out file(s) in the current directory.")
    else:
        # exit program if no .out files were found 
        print(f"{Fore.RED}\nNo .out files found in the current directory.{Style.RESET_ALL}\nPlease provide post processing files either in the current directory or in the specified data subfolder: /{dataname}.")
        print(f"{Fore.RED}\n\nExiting program.{Style.RESET_ALL}")
        sys.exit()
    

# list all found outfiles  
for i in range(len(outfiles)):
    print(f"{i+1}: {outfiles[i]}")



################################################################# FILE PROCESSING ################################################################
print(f"{Style.BRIGHT}\n\n################################################################# FILE PROCESSING ################################################################{Style.RESET_ALL}")
# change to directory with data
os.chdir(currentdir)


# query to process all found files  
q_all = ynquery("Automatically process all data files at once? (y/n):\n>>> ")

# process all files at once
if q_all:
    files = outfiles

# process specific files
else:
    while True:
        # get numbers of files
        filenums = input("Enter the numbers of datafiles to be processed, separated by spaces:\n>>> ").strip().split()
        files = []

        print()

        # add valid files
        for i in range(len(filenums)):
            try:
                entry = int(filenums[i])

                # number has to match outfile list entry
                if entry <= len(outfiles):
                    # add to empty list
                    if len(files) == 0:
                        files.append(outfiles[entry-1])
                    
                    # check for double entries
                    else:
                        included = False
                        
                        for file in files:
                            if file == outfiles[entry-1]:
                                included = True
                                print(f"Number {Fore.RED}'{filenums[i]}'{Style.RESET_ALL} has multiple entries. File added only once to current selection.")
                                break
                        
                        if not included:
                            files.append(outfiles[entry-1])

                # number does not match list entries
                else:
                    print(f"Number {Fore.RED}'{filenums[i]}'{Style.RESET_ALL} is invalid.")    

            # not a valid number, number conversion failed
            except ValueError:
                print(f"Number {Fore.RED}'{filenums[i]}'{Style.RESET_ALL} is invalid.")    
        
        if len(files) > 0:
            break


# datasets including quantities collected from files
datasets = []

# get quantities and data from all found outfiles
print(f"\nProcessing {len(files)} datafile(s):")
for file in files:
    # get lines from file, extract quantities and data
    lines = getlines(file)
    quants = getquants(lines)
    data = getdata(lines)

    # add dataset
    if len(quants) > 0 and len(data) > 0:
        name = file.replace(".out", "")
        datasets.append(Dataset(name, quants, data))
        print(f"Extracted data from file {os.path.relpath(file, sourcedir)}")

    # skip file in no usable data has been found
    else:
        print(f"{Fore.RED}File {os.path.relpath(file, sourcedir)} is not in the correct format or could not be opened.\n{Style.RESET_ALL}")

input("\n\nPress 'Enter' to continue...")



############################################################## QUANTITY PROCESSING ##############################################################
print(f"{Style.BRIGHT}\n\n############################################################## QUANTITY PROCESSING ##############################################################{Style.RESET_ALL}")
# change to source directory
os.chdir(sourcedir)

# definition of quantities
quantities = []

# extact quantities from datasets
for dataset in datasets:
    quants = dataset.getquants()

    # empty quantity list
    if len(quantities) == 0:
        for quant in quants:
            quantities.append(Quantity(quant, None, None, 0.0, 1.0))

    # quantity list with prior entries
    else:
        for quant in quants:
            included = False

            for ref in quantities:
                # if quantity is already included, incement count by one
                if quant == ref.getname():
                    ref.addcount()
                    included = True
                    break
                
            # if a found quantity was not included, append it
            if not included:
                quantities.append(Quantity(quant, None, None, 0.0, 1.0))

# exit if no data was found
if len(quantities) == 0:
    print(f"{Fore.RED}No quantities were found in the provided datafiles.{Style.RESET_ALL}")
    print(f"{Fore.RED}\n\nExiting program.{Style.RESET_ALL}")
    sys.exit()


# list found quantities
print(f"Found {len(quantities)} quantities in the datafiles:")
for quant in quantities:
    print(f"- '{quant.getname()}' included in {quant.getcount()} datafiles.")

input("\n\nPress 'Enter' to continue...")


# get reference quantites from file
ref_quantities = []
try:
    with open(reffile, "r") as file:
        lines = file.readlines()
        
        for line in lines:
            entries = line.strip().split(ref_delimiter)
            
            # add reference quantity if its entries are valid
            if len(entries) == 5:
                ref_quantities.append(Quantity(entries[0], entries[1], entries[2], entries[3], entries[4]))

        file.close()
except FileNotFoundError:
    print(f"{Fore.RED}\n\nCould not find or open reference file {reffile}.{Style.RESET_ALL}")

print()

# check for matches between current and reference quantities
if len(ref_quantities) > 0:
    for quant in quantities:
        for ref_quant in ref_quantities:
            if quant.getname() == ref_quant.getname():
                print(f"\nFound references for quantity '{quant.getname()}':")
                print(f"- type:           {ref_quant.gettype()}")
                print(f"- description:    {ref_quant.getdescr()}")
                print(f"- offset:         {ref_quant.getoffset()}")
                print(f"- scaling factor: {ref_quant.getfactor()}\n")
                

                # query to use reference
                q_useref = ynquery(f"Use references for quantity '{quant.getname()}'? (y/n)\n>>> ")

                # copy reference parameters
                if q_useref:
                    quant.settype(ref_quant.gettype())
                    quant.setdescr(ref_quant.getdescr())
                    quant.setoffset(ref_quant.getoffset())
                    quant.setfactor(ref_quant.getfactor())
                break


# enter attributes of remaining quantities
for quant in quantities:
    if quant.gettype() == None:
        while True:
            q_type = input(f"\nDefine type of quantity '{quant.getname()}': none/xdata/ydata or n/x/y\n>>> ").lower()

            # quantity not to be plotted
            if q_type == "none" or q_type == "n":
                quant.settype("none")
                quant.setdescr("none")
                quant.setoffset(0.0)
                quant.setfactor(0.0)
                break

            # xdata definition
            elif q_type == "xdata" or q_type == "x":
                setquantities(quant, "xdata")
                break

            # ydata definition
            elif q_type == "ydata" or q_type == "y":
                setquantities(quant, "ydata")
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")

        print()
        newline = quant.getref()
        
        # check if references for current quantity exist
        refmatch = False
        for ref_quant in ref_quantities:
            if quant.getname() == ref_quant.getname():
                refmatch = True
                break
        
        # no references have been found
        if not refmatch:
            # add new quantity to references
            q_addref = ynquery(f"Add settings for new quantity '{quant.getname()}' to reference file '{reffile}'? (y/n)\n>>> ")
            
            if q_addref:
                # add to existing file
                try:
                    # add a line to the file
                    with open(reffile, "a") as file:
                        file.write(newline + "\n")
                        file.close()
                    print(f"{Style.BRIGHT}Added settings for new quantity '{quant.getname()}.{Style.RESET_ALL}")

                except FileNotFoundError:
                    # if the file doesn't exist, create it and add a line
                    with open(reffile, "w") as file:
                        file.write(newline + "\n")
                        file.close()
                    print(f"{Style.BRIGHT}The file '{reffile}' didn't exist. Created a new file.{Style.RESET_ALL}")


        # references have been found
        else:
            # update quantity in references
            q_addref = ynquery(f"Update settings for existing quantity '{quant.getname()}' in reference file '{reffile}'? (y/n)\n>>> ")
            
            if q_addref:
                # get all lines from file
                with open(reffile, "r") as file:
                    # add a line to the file
                    lines = file.readlines()
                    file.close()

                # find and replace line of quantity
                for index in range(len(lines)):
                    if lines[index].startswith(quant.getname()):
                        lines[index] = newline + "\n"
                        break

                # update existing file
                with open(reffile, "w") as file:
                    # add a line to the file
                    file.writelines(lines)
                    file.close()
                
                print(f"{Style.BRIGHT}Updated settings for existing quantity '{quant.getname()}'.{Style.RESET_ALL}")
            

# check if a least one xdata quantity and ydata quantity exist
xquantexists = False
yquantexists = False

for quant in quantities:
    if quant.gettype() == "xdata":
        xquantexists = True
    elif quant.gettype() == "ydata":
        yquantexists = True

if not (xquantexists and yquantexists):   
    print(f"{Fore.RED}\nAt least one xdata quantity and one ydata quantity have to be defined for data evaluation.{Style.RESET_ALL}")
    print(f"{Fore.RED}\n\nExiting program.{Style.RESET_ALL}")
    sys.exit()


print(f"\nOverview over all {len(quantities)} current quantities:")
for quant in quantities:
    print(f"- Settings for quantity '{quant.getname()}':")
    print(f"    - type:           {quant.gettype()}")
    print(f"    - description:    {quant.getdescr()}")
    print(f"    - offset:         {quant.getoffset()}")
    print(f"    - scaling factor: {quant.getfactor()}\n")

input("\nPress 'Enter' to continue...")


################################################################ DATA PROCESSING ################################################################
print(f"{Style.BRIGHT}\n\n################################################################ DATA PROCESSING ################################################################{Style.RESET_ALL}")
# xy data
xydata = []

print("Available yx datasets:")
# obtain valid xy data from datasets
for dataset in datasets:
    # get data
    data = dataset.getdata()
    
    # get quantities from dataset
    xquants = []
    yquants = []
    quants = dataset.getquants()
    
    # go through current quantities
    for quant in quants:
        # go through defined quantities
        for quantity in quantities:
            # get quantity parameters for dataset
            if quant == quantity.getname():
                # get x quantities
                if quantity.gettype() == "xdata":
                    xquants.append(quantity)
                
                # get y quantities
                if quantity.gettype() == "ydata":
                    yquants.append(quantity)


    # check if dataset contains a single set of xy data
    if len(xquants) == 1 and len(yquants) == 1:
        singleset = True
    else:
        singleset = False
    
    # valid xy data only if at least one xquant and one yquant have been found
    if len(xquants) > 0 and len(yquants) > 0:
        print(f"- Dataset '{dataset.getname()}':")

        # counting number of xydata sets in current dataset
        datacount = 1
        
        # go through all x quantities
        for xquant in xquants:
            # go through all yquantites
            for yquant in yquants:
                # find index of x quantity 
                for i in range(len(quants)):
                    if quants[i] == xquant.getname():
                        # extract x data at index position
                        xdata = []
                        for j in range(len(data)):
                            # format and scale xdata
                            xdata.append(xquant.getfactor()*(float(data[j][i]) + xquant.getoffset()))
                        break

                # find index of y quantity 
                for i in range(len(quants)):
                    if quants[i] == yquant.getname():
                        # extract y data at index position
                        ydata = []
                        for j in range(len(data)):
                            ydata.append(yquant.getfactor()*(float(data[j][i]) + yquant.getoffset()))
                        break

                # define xy data header
                if singleset:
                    header = dataset.getname()
                else:
                    header = f"{dataset.getname()}-{datacount}"
                
                # define xy dataset
                xydata.append(XYdata(header, xquant, yquant, xdata, ydata))
                
                print(f"    - {header}:\n        - x: {xquant.getname()}\n        - y: {yquant.getname()}")
                datacount += 1
        print()

    # invalid dataset
    else:
        print(f"{Fore.RED}Skipping dataset '{dataset.getname()}'.{Style.RESET_ALL} No valid xy data has been found.\n")


print(f"{Style.BRIGHT}\nCreated {len(xydata)} xy dataset(s) from {len(datasets)} dataset(s) found in {len(files)} file(s).{Style.RESET_ALL}")
input("\n\nPress 'Enter' to continue...")



################################################################## FILE OUTPUT ##################################################################
print(f"{Style.BRIGHT}\n\n################################################################## FILE OUTPUT ##################################################################{Style.RESET_ALL}")
# create files for xy datasets
q_datatofile = ynquery("Write xy datasets to .txt files? (y/n)\nExisting files of these datasets will be overwritten.\n>>> ")

# file configuration
if q_datatofile:       
    while True:
        q_format = input("\nSpecify format of data to be written (m/o):\n    - m: Maple format: [[x1,y1],[x2,y2],...] in single line\n    - o: other format: pairs of x and y data in each line, separated by a delimiter\n>>> ").lower()

        # maple format
        if q_format == "m":
            print("")
            
            # write all xydata to file
            for data in xydata:
                # filename
                filename = data.getheader() + ".txt"
                
                # build lines
                lines = []
                lines.append(f"{data.getxquant().getname()}: {data.getxquant().getdescr()}\n")
                lines.append(f"{data.getyquant().getname()}: {data.getyquant().getdescr()}\n")

                # data lines
                xdata = data.getxdata()
                ydata = data.getydata()
                dataline = "["
                for i in range(len(xdata) - 1):
                    dataline += f"[{xdata[i]},{ydata[i]}],"
                dataline += f"[{xdata[-1]},{ydata[-1]}]]\n"

                lines.append(dataline)

                # write to file
                with open(filename, "w") as file:
                    # add a line to the file
                    file.writelines(lines)
                    file.close()

                print(f"Created file '{filename}'")
            print()
            break


        # other format
        elif q_format == "o":
            
            while True:
                q_delim = input("\nSpecify delimiter between x and y data:\nGood options are a space, a comma or any common delimiter. Can only be a single character.\n>>> ")
            
                # check for single character delimiter
                if len(q_delim) == 1:
                    break

                else:
                    print(f"{Fore.RED}Invalid delimiter.{Style.RESET_ALL}")
            
            # write all xydata to file
            for data in xydata:
                # filename
                filename = data.getheader() + ".txt"
                
                # build lines
                lines = []
                lines.append(f"{data.getxquant().getname()}{q_delim}{data.getyquant().getname()}\n")
                lines.append(f"{data.getxquant().getdescr()}{q_delim}{data.getyquant().getdescr()}\n")
                
                # data lines
                xdata = data.getxdata()
                ydata = data.getydata()

                for i in range(len(xdata)):
                    lines.append(f"{xdata[i]}{q_delim}{ydata[i]}\n")
                
                # write to file
                with open(filename, "w") as file:
                    # add a line to the file
                    file.writelines(lines)
                    file.close()

                print(f"Created file '{filename}'")
            print()
            break

        else:
            print(f"{Fore.RED}Invalid input. Please enter one of the provided options.{Style.RESET_ALL}")



#################################################################### PLOTTING ###################################################################
print(f"{Style.BRIGHT}\n#################################################################### PLOTTING ###################################################################{Style.RESET_ALL}")
# create plots for xy datasets
q_datatoplot = ynquery("Create plots for xy datasets? (y/n)\nExisting plots of these datasets will be overwritten.\n>>> ")

if not q_datatoplot:
    print(f"{Style.BRIGHT}{Fore.GREEN}\n##################################################################### DONE ######################################################################{Style.RESET_ALL}")
    sys.exit()


# sort xy datasets by quantities
xydatasets = []

# find matching datasets
for data in xydata:
    # first entry
    if len(xydatasets) == 0:
        xydatasets.append([data])

    # prior entries
    else:
        # quantities of current xy dataset
        xquant = data.getxquant().getname()
        yquant = data.getyquant().getname()
        
        # look in entries of xydatasets for the same quantities
        included = False
        
        for index in range(len(xydatasets)):
            # quantities in reference xy dataset in matches
            refxquant = xydatasets[index][0].getxquant().getname()
            refyquant = xydatasets[index][0].getyquant().getname()

            # entry in matches already present
            if xquant == refxquant and yquant == refyquant:
                # add dataset to matches
                xydatasets[index].append(data)
                included = True
                break

        # add new dataset if not included
        if not included:
            xydatasets.append([data])

# multiple datasets with matching quantities
multisets = False

# print sorted datasets           
print("\nSorted xy datasets by matching quantities:")
for i in range(len(xydatasets)):
    # x and y quantities of datasets
    xquant = xydatasets[i][0].getxquant().getname()
    yquant = xydatasets[i][0].getyquant().getname()

    # check for multiple datasets with matching quantities
    if len(xydatasets[i]) > 1:
        multisets = True
    
    print(f"- {len(xydatasets[i])} set(s) with x quantity '{xquant}' and y quantity '{yquant}':")
    for j in range(len(xydatasets[i])):
        print(f"    - {xydatasets[i][j].getheader()}")
    print()
print()


# promt to create individual plots
q_iplot = ynquery("Create individual plots for all xy datasets? (y/n)\n>>> ")

# individual plot configuration
if q_iplot:
    # title inclusion query
    q_ititle = ynquery("Include title for individual plots? (y/n)\n>>> ")
    
    # title customization query
    if q_ititle:
        q_ititle_auto = ynquery("Auto-assign xy dataset name as title? (y/n)\n>>> ")
    else: 
        q_ititle_auto = False 
    
    # match axes in case of multiple datasets
    if multisets:
        q_matchaxes = ynquery("Match axis ranges between datasets with matching quantities? (y/n)\n>>> ")    
    else:
        q_matchaxes = False


    # individual plot list
    iplots = []


    # create individual plots
    for i in range(len(xydatasets)):
        # x and y quantities of datasets
        xquant = xydatasets[i][0].getxquant().getname()
        yquant = xydatasets[i][0].getyquant().getname()
        xdescr = xydatasets[i][0].getxquant().getdescr()
        ydescr = xydatasets[i][0].getyquant().getdescr()


        print(f"\nPlot configuration for plots with x quantity '{xquant}' and y quantity '{yquant}':")
        

        # global axis ranges
        if q_matchaxes:
            # compute global ranges
            # x values
            xmin, xmax = getminmax(xydatasets[i], "xdata")

            # y values
            ymin, ymax = getminmax(xydatasets[i], "ydata")

            # output ranges
            print("Computed axis range boundaries of set:")
            print(f"- xmin: {xmin}\n- xmax: {xmax}")
            print(f"- ymin: {ymin}\n- ymax: {ymax}\n")


            # use computed ranges
            q_bounds = ynquery("Use computed ranges? (y/n)\n>>> ")
            
            # manual input of ranges
            if not q_bounds:
                # set x values
                xmin, xmax = setminmax(xdescr, xmin, xmax)

                # set y values
                ymin, ymax = setminmax(ydescr, ymin, ymax)


            # create plots
            for j in range(len(xydatasets[i])):
                # data
                xdatasets = [xydatasets[i][j].getxdata()]
                ydatasets = [xydatasets[i][j].getydata()]

                # legend
                legend = [xydatasets[i][j].getheader()]

                # title
                if q_ititle:
                    if q_ititle_auto:
                        title = xydatasets[i][j].getheader()
                    else:
                        title = input(f"\nEnter title of plot {xydatasets[i][j].getheader()}:\n>>> ")
                        print()
                else:
                    title = ""

                # name
                if title == "":
                    name = xydatasets[i][j].getheader()
                else:
                    name = xydatasets[i][j].getheader().replace(" ", "-")

                iplots.append(Plot(name, title, xdescr, ydescr, xdatasets, ydatasets, xmin, xmax, ymin, ymax, legend))
            print()
        

        # individual axis ranges
        else:
            # define global ranges
            q_bounds = ynquery(f"Automatically use computed axis ranges for plots with x quantity '{xquant}' and y quantity '{yquant}'? (y/n)\n>>> ")
            
            # define plots individually
            for j in range(len(xydatasets[i])):
                # compute ranges
                # x values
                xmin, xmax = getminmax([xydatasets[i][j]], "xdata")

                # y values
                ymin, ymax = getminmax([xydatasets[i][j]], "ydata")


                # manual input of ranges
                if not q_bounds:
                    print(f"Enter axis ranges for plot {xydatasets[i][j].getheader()}:")
                    
                    # set x values
                    xmin, xmax = setminmax(xdescr, xmin, xmax)

                    # set y values
                    ymin, ymax = setminmax(ydescr, ymin, ymax)


                # create plot
                # data
                xdatasets = [xydatasets[i][j].getxdata()]
                ydatasets = [xydatasets[i][j].getydata()]

                # legend
                legend = [xydatasets[i][j].getheader()]

                # title
                if q_ititle:
                    if q_ititle_auto:
                        title = xydatasets[i][j].getheader()
                    else:
                        title = input(f"\nEnter title of plot {xydatasets[i][j].getheader()}:\n>>> ")
                        print()
                else:
                    title = ""

                # name
                if title == "":
                    name = xydatasets[i][j].getheader()
                else:
                    name = xydatasets[i][j].getheader().replace(" ", "-")

                iplots.append(Plot(name, title, xdescr, ydescr, xdatasets, ydatasets, xmin, xmax, ymin, ymax, legend))
            print()


    # output individual plots to file
    print("Creating individual plots:")
    for plot in iplots:
        createplot(plot)
    print()
    print()


# promt to create combined plots
enoughsets = False
for datasets in xydatasets:
    if len(datasets) > 1:
        enoughsets = True

if enoughsets:
    q_mplot = ynquery("Create combined plots with multiple xy datasets? (y/n)\n>>> ")
else:
    print(f"{Fore.RED}Not enough datasets to create combined plots.{Style.RESET_ALL}")
    q_mplot = False


# combined plot configuration
if q_mplot:
    # title inclusion query
    q_mtitle = ynquery("Include title for combined plots? (y/n)\n>>> ")

    # title customization query
    if q_mtitle:
        q_mtitle_auto = ynquery("Auto-assign 'Comparison of...' as title? (y/n)\n>>> ")
    else: 
        q_mtitle_auto = False 


    # combined plot list
    mplots = []


    # all plots with matching quantities
    if multisets:
        # check if more than one dataset exist per x quantity and y quantity combination
        for i in range(len(xydatasets)):
            if len(xydatasets[i]) > 1:
                # x and y quantities of datasets
                xquant = xydatasets[i][0].getxquant().getname()
                yquant = xydatasets[i][0].getyquant().getname()
                xdescr = xydatasets[i][0].getxquant().getdescr()
                ydescr = xydatasets[i][0].getyquant().getdescr()
                
                # output datasets
                print(f"Datasets with x quantity '{xquant}' and y quantity '{yquant}':")
                for j in range(len(xydatasets[i])):
                    print(f"- {xydatasets[i][j].getheader()}")
                print()

                # create plots with multiple datasets
                q_multi = ynquery("Create a combined plot with all of the above xy datasets? (y/n)\n>>> ")

                if q_multi:
                    # compute global ranges
                    # x values
                    xmin, xmax = getminmax(xydatasets[i], "xdata")

                    # y values
                    ymin, ymax = getminmax(xydatasets[i], "ydata")

                    # output ranges
                    print("Computed axis range boundaries of set:")
                    print(f"- xmin: {xmin}\n- xmax: {xmax}")
                    print(f"- ymin: {ymin}\n- ymax: {ymax}\n")


                    # use computed ranges
                    q_bounds = ynquery("Use computed ranges? (y/n)\n>>> ")
                    
                    # manual input of ranges
                    if not q_bounds:
                        # set x values
                        xmin, xmax = setminmax(xdescr, xmin, xmax)

                        # set y values
                        ymin, ymax = setminmax(ydescr, ymin, ymax)


                    # create plot
                    # data
                    xdatasets = []
                    ydatasets = []

                    # legend
                    legend = []

                    for j in range(len(xydatasets[i])):
                        xdatasets.append(xydatasets[i][j].getxdata())
                        ydatasets.append(xydatasets[i][j].getydata())
                        legend.append(xydatasets[i][j].getheader().replace(f"-{yquant}", "").replace(f"{yquant}", ""))

                    # title
                    if q_mtitle:
                        if q_mtitle_auto:
                            title = f"Comparison of {ydescr}"
                        else:
                            title = input(f"\nEnter title of plot with x quantity '{xquant}' and y quantity '{yquant}':\n>>> ")
                            print()
                    else:
                        title = ""

                    # name
                    if title == "":
                        name = f"Comparison of {ydescr}"
                        name = name.replace(" ", "-")
                        name = re.sub(re.compile(r"-\[.*?\]"), "", name)
                    else:
                        name = title.replace(" ", "-")
                        name = re.sub(re.compile(r"-\[.*?\]"), "", name)

                    mplots.append(Plot(name, title, xdescr, ydescr, xdatasets, ydatasets, xmin, xmax, ymin, ymax, legend))
                print()


    # other combinations of data
    count = 0
    
    while True:        
        q_other = ynquery("Create other combinations of xy datasets? (y/n)\nThe descriptions of all quantities must match in order to be plotted together.\n>>> ")
        
        if q_other:
            print("\nAvailable xy datasets:")
            for i in range(len(xydata)):
                print(f"- {i+1}: {xydata[i].getheader()}")
            print()
            
            # get numbers of datasets
            datanums = input("Enter the numbers of xy datasets for plotting, separated by spaces:\n>>> ").strip().split()
            sets = []

            print()

            # add valid files
            for i in range(len(datanums)):
                try:
                    entry = int(datanums[i])

                    # number has to match outfile list entry
                    if entry <= len(xydata):
                        # add to empty list
                        if len(sets) == 0:
                            sets.append(xydata[entry-1])
                            
                            # quantities of reference list entry
                            setxdescr = sets[0].getxquant().getdescr()
                            setydescr = sets[0].getyquant().getdescr()
                        
                        # check for double entries
                        else:
                            included = False
                            
                            for set in sets:
                                if set.getheader() == xydata[entry-1].getheader():
                                    included = True
                                    print(f"Number {Fore.RED}'{datanums[i]}'{Style.RESET_ALL} has multiple entries. Dataset added only once to current selection.")
                                    break
                            
                            if not included:
                                # quantities of current entry
                                xdescr = xydata[entry-1].getxquant().getdescr()
                                ydescr = xydata[entry-1].getyquant().getdescr()
                                
                                # check for matching quantity descriptions
                                if xdescr == setxdescr and ydescr == setydescr:
                                    sets.append(xydata[entry-1])
                                else:
                                    print(f"Number {Fore.RED}'{datanums[i]}'{Style.RESET_ALL} does not match set quantities.")

                    # number does not match list entries
                    else:
                        print(f"Number {Fore.RED}'{datanums[i]}'{Style.RESET_ALL} is invalid.")    

                # not a valid number, number conversion failed
                except ValueError:
                    print(f"Number {Fore.RED}'{datanums[i]}'{Style.RESET_ALL} is invalid.")    
                    

            # create plot
            if len(sets) > 1:
                count += 1
                
                # compute global ranges
                # x values
                xmin, xmax = getminmax(sets, "xdata")

                # y values
                ymin, ymax = getminmax(sets, "ydata")

                # output ranges
                print("Computed axis range boundaries of set:")
                print(f"- xmin: {xmin}\n- xmax: {xmax}")
                print(f"- ymin: {ymin}\n- ymax: {ymax}\n")


                # use computed ranges
                q_bounds = ynquery("Use computed ranges? (y/n)\n>>> ")
                
                # manual input of ranges
                if not q_bounds:
                    # set x values
                    xmin, xmax = setminmax(setxdescr, xmin, xmax)

                    # set y values
                    ymin, ymax = setminmax(setydescr, ymin, ymax)


                # create plot
                # data
                xdatasets = []
                ydatasets = []

                # legend
                legend = []

                for i in range(len(sets)):
                    xdatasets.append(sets[i].getxdata())
                    ydatasets.append(sets[i].getydata())
                    yquant = sets[i].getyquant().getname()
                    legend.append(sets[i].getheader().replace(f"-{yquant}", "").replace(f"{yquant}", ""))

                # title
                if q_mtitle:
                    if q_mtitle_auto:
                        title = f"Comparison of {setydescr}"
                    else:
                        title = input(f"\nEnter title of plot:\n>>> ")
                        print()
                else:
                    title = ""

                # name
                if title == "":
                    name = f"Comparison of {setydescr}"
                    name = name.replace(" ", "-")
                    name = re.sub(re.compile(r"-\[.*?\]"), "", name)
                    name += f"-set{count}"
                else:
                    name = title.replace(" ", "-")
                    name = re.sub(re.compile(r"-\[.*?\]"), "", name)
                    name += f"-set{count}"

                mplots.append(Plot(name, title, xdescr, ydescr, xdatasets, ydatasets, xmin, xmax, ymin, ymax, legend))
                print()

            else:
                print(f"{Fore.RED}Found less than 2 plottable datasets.{Style.RESET_ALL} Skipping creation of combined plot.\n\n")
        else:
            break

    # output combined plots to file
    print("\nCreating combined plots:")
    for plot in mplots:
        createplot(plot)

print(f"{Style.BRIGHT}{Fore.GREEN}\n\n##################################################################### DONE ######################################################################{Style.RESET_ALL}")