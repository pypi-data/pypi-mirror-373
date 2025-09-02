
import pandas as pd
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt
import sympy as sy

def symsum(lst):
    sm = lst[0]
    for i in lst[1:]:
        sm += i 
    return sm

class errorPropagate():
    """
    A collection of methods to produce the error propagation expression 
    for a given equation
    ----------
    Parameters
    f: The expression to differentiate
    
    dVars: A list of the variables to differentiate with respect to
    
    tex: Whether to output in LaTeX syntax
    
    py: Whether to output in python syntax
    ----------
    
    """
    def __init__(self, f, dVars, tex = True, py = False):
        
        
        function= f[0]
        errorSymbols=[]
        self.fSymbol = sy.symbols(f[1])
        self.dVars = dVars
        
        for dVar in dVars:
            errorSymbols.append(f"{dVar}_e")
            
        self.errors = sy.symbols(errorSymbols)
        
        self.divs = []
        divsE = []
        
        for i in range(len(dVars)):
            div = sy.simplify(sy.diff(function, dVars[i]))
            self.divs.append(div)
            
            divsE.append((div * self.errors[i])**2)
        
        self.errFunc = symsum(divsE)
        
        if tex == True:
            self.tex()
        if py == True:
            self.py()

        
    def tex(self):
        
        expression = f"\\Delta {sy.latex(self.fSymbol)}^{{2}} = "
        
        for i in range(len(self.dVars)):
            
            expression += f"\\left({sy.latex(self.divs[i])}\\right)^{{2}} \\Delta {sy.latex(self.dVars[i])}^2"
            
            if i + 1 != len(self.dVars):
                expression += " + \n"
        
        print(f"\nLatex Expression: \n\n {expression}")
        
    def py(self):
        
        print("\nPython expression(s):\n")
        functions = ["sin", "cos", "tan", "sqrt", "asin", "acos", "atan"]
        
        for i in range(len(self.dVars)):
            
            expression = f"({self.divs[i]}) * {self.dVars[i]}Err"
            
            for function in functions:
                if expression.find(function) != -1:
                    expression = expression.replace(function, f"np.{function}")
            
            print(expression + "\n")
    
    def rtrn(self):
        return sy.sqrt(self.errFunc), self.errors

# =============================================================================
# csv to latex table converter
# =============================================================================

class csv2tab():
    
    def __init__(self, file, caption = "", alignment = ""):

        "Convert a csv file to latex table"
        
        # Reads the csv file
        file = pd.read_csv(file, header=0)
        # Rounds the values such that errors are 1sf and the values match the errors num decimal places
        file = self.numFormat(file)
        
        # initialising strings
        header = ""
        dataStr = ""
        
        # Creating an alignment string if one not entered
        if alignment == "":
            for i in file.columns:
                alignment+="c"
        
        # Creating the header string
        for col in file.columns:
            header += col
            if col != file.columns[len(file.columns)-1]:
                header += " & "
        
        # Creating the data string
        for row in file.index:
            for col in file.columns:
                
                value = file.loc[row,col]
                    
                dataStr += str(value)
                
                if (col != file.columns[-1]):
                    dataStr += " & "
                    
            dataStr += r"\\" + "\n"
        
        # Information that is always included to format the table
        tableStart = r"""\begin{table}[htb]
\centering""" + r"\caption{" + caption + r"}" + r"""
\begin{tabular}{""" + alignment + r"}" + r"""
\toprule
"""
        tableEnd = r"""\bottomrule
\end{tabular}
\label{tab:}
\end{table}"""
        
        # Printing the latex code
        print(tableStart + header + "\\\\\n\\midrule\n" + dataStr + tableEnd)
    
    def sfRound(self, x, sf=1):
        """Round to given significant figures"""
        return float('%s' % float('%.1g' % x))
    
    def numFormat(self, data):
    
        # lists for storage
        newCols = []
        remCols = []
        # Pulling the column headers 
        cols = list(data.columns)
        
        # Looping through the columns and checking if they are errors
        for i in range(len(data.columns)):
            
            # Checking if the column contains errors or data
            if cols[i].find("Error") == -1:
                column = []
                # If the column is at the end of the dataframe, it is saved
                if cols[i] == cols[len(cols)-1]:
                    newCols.append(data[cols[i]])
                # Checking if the adjacent column contains error data
                elif cols[i+1].find("Error") != -1:
                    # Rounding the errors and data
                    for j in data.index:
                        data.loc[j, cols[i+1]] = self.sfRound(data.loc[j, cols[i+1]])
                    data[cols[i+1]] = data[cols[i+1]].astype(str)
                        
                    for j in data.index:
                        rnd = int(('%.0E' % Decimal(data.loc[j,cols[i+1]]))[-2:])
                        
                        data.loc[j, cols[i]] = round(data.loc[j, cols[i]], rnd)
                        
                        column.append(f"${data.loc[j, cols[i]]}\\pm{data.loc[j, cols[i+1]]}$")
                        
                    newCols.append(column)
                    remCols.append(cols[i+1])
                # If previous conditions not passed, the column is just saved
                else:
                    newCols.append(data[cols[i]])
                
            else:
                pass
        # Removing the error columns from the list of headers 
        for col in remCols:
            cols.remove(col)
            
        return pd.DataFrame(np.array(newCols).T, columns=cols)

# =============================================================================
# Matplotlib utility
# =============================================================================

class plotter():
    """
    A generaliseable plotting class
    """
    
    # Creation of the figure and axis objects ---------------------------------
    
    def __init__(self, title = None, figsize=(8,5)):
        # Creating the figure and axes objects, setting title
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_title(title)
    
    # General utility methods -------------------------------------------------
    
    def save(self, name):
        self.fig.savefig(name)
    
    # Plotting methods --------------------------------------------------------
    
    def plot(self, data, xyLabels = [None, None], label=None, legendLoc="best"):
        xData, yData = data
        self.ax.plot(xData, yData, label=label) # Plotting the data as a line
        self.ax.set_xlabel(xyLabels[0])         # Setting the x and y axis labels
        self.ax.set_ylabel(xyLabels[1])
        if label != None:
            self.ax.legend(loc=legendLoc)       # Applying a legend to the plot
        
    def scatter(self, data, xyLabels = [None, None], label=None, legendLoc="best", colour=None, markerSize=10, markerStyle = "o"):
        xData, yData = data
        self.ax.scatter(xData, yData, label=label, c=colour, s=markerSize, marker=markerStyle)  # Plotting the data as a scatter
        self.ax.set_xlabel(xyLabels[0])             # Setting the x, y axis labels
        self.ax.set_ylabel(xyLabels[1])
        if label != None:
            self.ax.legend(loc=legendLoc)           # Applying a legend to the plot
    
    def errorbar(self, data, errorbars):
        # Plot errobars
        self.ax.errorbar(data[0], data[1], xerr=errorbars[0], yerr=errorbars[1], fmt="none", capsize=5, elinewidth=2, markeredgewidth=2)
    
    # Formatting methods ------------------------------------------------------
    
    def scales(self, xScale, yScale):
        self.ax.set_xscale(xScale)
        self.ax.set_yscale(yScale)
        
    def limits(self, xLimitD=None, xLimitU=None, yLimitD=None, yLimitU=None):
        # Setting the x and y axes limits
        self.ax.set_xlim(xLimitD, xLimitU)  
        self.ax.set_ylim(yLimitD, yLimitU)
        
    def grid(self, c="k"):
        # Setting the grid of the plot
        self.ax.grid(which='major', color=c, linestyle='-', linewidth=0.6, alpha = 0.6)
        self.ax.grid(which='minor', color=c, linestyle='--', linewidth=0.4, alpha = 0.4)
        self.ax.minorticks_on()     # Turning on minorticks
        self.ax.set_axisbelow(True) # Setting the axis below the data
        
    def aspect(self, aspectRatio="equal"):
        self.ax.set_aspect(aspectRatio) # Setting the aspect ratio of the axes
        
    def invert(self, axis="both"):
        # Invert the axes
        if axis == "both":
            plt.gca().invert_xaxis()
            plt.gca().invert_yaxis()
        if axis == "x":
            plt.gca().invert_xaxis()
        if axis == "y":
            plt.gca().invert_yaxis()
            
    def imshow(self, data, cmap="gray"):
        # Plot an imshow
        im = self.ax.imshow(data, cmap=cmap)
        self.fig.colorbar(im, ax=self.ax)
        
    def legend(self):
        # Applies a legend to the axis
        self.ax.legend()
    
    # Defaults ----------------------------------------------------------------
    
    def defaultPlot(self, data, xyLabels, label=None):
        # Default parameters for quick line plotting
        self.plot(data, xyLabels, label)
        self.grid()
    
    def defaultScatter(self, data, xyLabels, label=None):
        # Default parameters for quick scatter plotting
        self.scatter(data, xyLabels, label)
        self.grid()
        
    # -------------------------------------------------------------------------
