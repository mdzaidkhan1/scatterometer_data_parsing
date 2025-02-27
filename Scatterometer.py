#author: Mohammed Zaid Khan
#date: 2022-09-29
#version: 3
#program to open file(s) and extract relevant data
#assumptions:
#the number of incidence angles are all the same in the file

#imports
from tkinter import messagebox
import pandas as pd
import numpy as np
from pandas import ExcelWriter
import os
import math
from numpy import zeros
import tkinter as tk
from tkinter import filedialog
import cmath

#file open window
root=tk.Tk()
root.withdraw()

#counters and flags
infoCount=0
dataCollect=0
rows=0
rowCount=0
fileCount=0
matrixRow=0
matrixCount=0

#list declarations
entryHeaders=[]
elevationList=[]
magList=[]
phaseList=[]
unsortedTable=[]
rhoList=[]
muList=[]
alphaList=[]
HList=[]

# vvValue= []
# hvValue= []
# vhValue= []
# hhValue= []



dataRef= [
    "number of elevation angles:",
    "elevation angles (deg)",
    "Covariance matrix for various elevation angles:",
    "magnitude of HH/VV correlation coefficient:",
    "phase of HH/VV correlation coefficient (deg):",
    "Normalized Radar Cross Section (dBm2/m2) columns with near-field correction: VV, HV, VH, HH; rows: elevations angles :"
] #data to be captured could be added and removed from this list to alter the output you are expecting
#although addition of other parameters to be captured would result in new variables having to be declared
#and development of how they are going to be handled.

#function declaration
def rhoCalculation(Shh, Svv, product ):
    #returns the rho value for the pair of Svv and Shh
    denominator=cmath.sqrt(Svv*Shh)
    result= round(abs(product/denominator), 6)
    return result
#end of rhoCalculation

def muCalculation(Shh, Svv, product, Svh):
    #returns the mu value for the matrix being looked at.
    numerator=2*product.real-Svh
    denominator=Svv+Svh+Shh
    result=denominator
    return result #this equation does not have an abs funciton on it ask professor isleifson whats preferred.

def alphaCalculation(Shh, Svv, ShhSvv, Shv):
    #returns the alpha calculation of the passed matrix.
    delta = pow( Svv - Shh , 2 ) + 4*pow( abs(ShhSvv) , 2)
    matrix1 = np.array([[2*ShhSvv], [0], [Svv - Shh + cmath.sqrt(delta)]])
    matrix2 = np.array([[2*ShhSvv], [0], [Svv - Shh - cmath.sqrt(delta)]])
    lambda1 = 0.5 *(Shh + Svv + cmath.sqrt(pow( Shh - Svv , 2) + 4 *pow( abs(ShhSvv) , 2 )))
    lambda2 = lambda1 - cmath.sqrt(pow( Shh - Svv, 2 ) + 4 *pow( abs(ShhSvv) , 2))
    lambda3 = Shv
    e1 = (1/cmath.sqrt( pow( Svv - Shh + cmath.sqrt(delta), 2) + 4*pow( abs( ShhSvv) , 2)))*matrix1
    e2 = (1/cmath.sqrt( pow( Svv - Shh - cmath.sqrt(delta), 2) + 4*pow( abs( ShhSvv) , 2)))*matrix2
    e3 = np.array([[0], [1], [0]])
    lambdaList = [lambda1, lambda2, lambda3]
    eList = [e1, e2, e3]
    alpha = complex( 0, 0)
    for i in range(len(lambdaList)):
        Pi = lambdaList[i]/sum(lambdaList)
        someVariable = np.clip(np.linalg.norm(eList[i]), -1, 1)
        trigPart = math.acos(someVariable)
        alpha += Pi * trigPart
    return alpha

def HCalculation(Shh, Svv, ShhSvv, Shv):
    lambda1 = 0.5 *(Shh + Svv + cmath.sqrt(pow( Shh - Svv , 2) + 4 *pow( abs(ShhSvv) , 2 )))
    lambda2 = lambda1 - cmath.sqrt(pow( Shh - Svv, 2 ) + 4 *pow( abs(ShhSvv) , 2))
    lambda3 = Shv
    lambdaList = [lambda1, lambda2, lambda3]
    H = complex( 0, 0)
    for i in range(len(lambdaList)):
        Pi = lambdaList[i]/sum(lambdaList)
        result = Pi * math.log( Pi.real, 3)
        H = H - result
    return H
    
def roundToMultiple(number, multiple):
    #rounds number to closest multiple of variable multiple
    return multiple*round(number/multiple)
#end of roundToMultiple()

def plotToExcel(df_dict):
    #plots dictionary of dataFrames to spreadhseet with multiple sheets
    output_directory=filedialog.askdirectory(title="Choose output file directory")#asking for the directory for the output 
    writer=ExcelWriter(output_directory+r'/Output.xlsx')
    for key in df_dict.keys():
        df_dict[key].to_excel(writer, sheet_name=key)
    #end of for
    writer._save()
#end of plotToExcel()

#actual parsing begins
path_of_directory=filedialog.askdirectory(title="Choose folder containing datasets!")
for someFile in os.listdir(path_of_directory):#iterating through files
    f=os.path.join(path_of_directory, someFile)
    if os.path.isfile(f):#if the file in this directory is an openable file 
        entryHeaders.extend([f.split(".")[0].split("\\")[-1]]) #adding filename to entryHeader list
        fileName=f #can be deleted, assigned in the moment to not have to delete everywhere else
        file=open(fileName, "r")
        for lineRaw in file:
            if lineRaw != "\n": #if not an empty line
                line=str(lineRaw.strip()) #stripping whitespace and new line 
                if dataCollect==1: #data collect is on 
                    if infoCount==1:
                        elevationAngles=int(line);
                        dataCollect=0;
                        if elevationAngles%6==0:
                            rows=elevationAngles/6;
                        #end of if
                        else:
                            rows=(elevationAngles/6)+1;
                        #end of else
                    #end of if
                    if infoCount==2 and fileCount<1: #code is repetitive potentially a function. Also this block only runs for the first file as we assume that the number of elevation 
                        #angles is not going to change in between files
                        #in a future version potentially add it to a list of elevationAngles. AT the end of file iteration find the biggest one and  create the 
                        #2d arrays based on that. condition for the creation of 2d array will be if elevationAngle[i]>max
                        rowCount+=1
                        if rowCount<=rows:
                            strList=line.split()
                            rowList=list(map(float, strList))#mapping to int values
                            elevationList.extend(rowList)
                        #end of if
                        else:#if rowCount is greater than rows, the data capture is done
                            dataCollect=0
                            rowCount=0
                        #end of else
                    #end of if
                    if infoCount==3:
                        matrixRow+=1
                        if(matrixRow <= 4*elevationAngles):
                            matrixLine=line.split(") (")
                            if(matrixRow % 4 == 1 ):
                                newList=matrixLine[0][1:].split(",")
                                Svv=complex( float(newList[0]), float(newList[1]))
                                newList=matrixLine[3][:-1].split(",")
                                SvvShh=complex( float(newList[0]), float(newList[1]))
                            elif(matrixRow % 4 ==2 ):
                                newList=matrixLine[1][:].split(",")
                                Svh=complex( float( newList[0]), float( newList[1]))
                            elif(matrixRow % 4 == 3):
                                newList = matrixLine[2][:].split(",")
                                Shv=complex( float( newList[0]), float( newList[1]))
                            elif( matrixRow % 4 == 0):
                                newList=matrixLine[3][:-1].split(",")
                                Shh=complex(float(newList[0]), float(newList[1]))
                                newList=matrixLine[0][1:].split(",")
                                ShhSvv=complex(float(newList[0]), float(newList[1]))
                                rhoList.append(rhoCalculation(Shh , Svv, SvvShh ))
                                muList.append(muCalculation(Shh, Svv, SvvShh, Svh))
                                alphaList.append(alphaCalculation(Shh, Svv, ShhSvv, Shv))
                                HList.append(HCalculation(Shh, Svv, ShhSvv, Shv))
                                matrixCount+=1
                        else:
                            dataCollect=0
                            matrixRow=0

                    if infoCount==4:#similar to past code. Capturing magnitude
                        rowCount+=1
                        if rowCount<=rows:
                            strList=line.split()
                            rowList=list(map(float, strList))
                            magList.extend(rowList)
                        #end of if
                        else:
                            dataCollect=0
                            rowCount=0
                        #end of else
                    #end of if
                    if infoCount==5:#similar to past code, Capturing phase
                        rowCount+=1
                        if rowCount<=rows:
                            strList=line.split()
                            rowList=list(map(float, strList))
                            phaseList.extend(rowList)
                        #end of if
                        else:
                            dataCollect=0
                            rowCount=0
                        #end of else
                    #end of if  
                    if infoCount==6:#similar to past code but this time creating a 2D array to store the data sets initially.
                        rowCount+=1
                        if rowCount<=elevationAngles:
                            strList=line.split()
                            rowList=list(map(float, strList))
                            unsortedTable.append(rowList)#append and not extend results in workable 2d array.
                        #end of if
                        else:
                            dataCollect=0
                            rowCount=0
                            if fileCount<1:#this code is here as we want all the dataList capturing to be done before we set the referece point for the size of the arrays 
                                vvValue=zeros((len(unsortedTable), len(os.listdir(path_of_directory))))#len(unsortedTable) could be replaced by elevationAngles
                                hvValue=zeros((len(unsortedTable), len(os.listdir(path_of_directory))))
                                vhValue=zeros((len(unsortedTable), len(os.listdir(path_of_directory))))
                                hhValue=zeros((len(unsortedTable), len(os.listdir(path_of_directory))))
                                mag=zeros((len(magList), len(os.listdir(path_of_directory))))
                                phase=zeros((len(phaseList), len(os.listdir(path_of_directory))))
                                mag_calculation=zeros((len(rhoList), len(os.listdir(path_of_directory))))
                                mu_calculation=zeros((len(muList), len(os.listdir(path_of_directory))))
                                H_calculation=zeros((len(HList), len(os.listdir(path_of_directory))))
                                alpha_calculaton=zeros((len(alphaList), len(os.listdir(path_of_directory))))
                            #end of if
                        #end of else
                    #end of if
                #end of if

                for ele in dataRef:#iterating through dataRef elements
                    if line==ele:#to find lines which indicate
                        infoCount+=1
                        dataCollect=1#data collection should be on
                    #end of if
                #end of for
            #end of if
        #end of for

        
        for i in range(len(unsortedTable)):#isolating the collumns
            vvValue[i][fileCount]=unsortedTable[i][0]
            hvValue[i][fileCount]=unsortedTable[i][1]
            vhValue[i][fileCount]=unsortedTable[i][2]
            hhValue[i][fileCount]=unsortedTable[i][3]
            mag[i][fileCount]=magList[i]
            phase[i][fileCount]=phaseList[i]
            mag_calculation[i][fileCount]=rhoList[i]
            mu_calculation[i][fileCount]=abs(muList[i])
            H_calculation[i][fileCount]=abs(HList[i])
            alpha_calculaton[i][fileCount]=abs(alphaList[i])
        #end of for
        #deleting the current iteration of lists so that the next files data can be updated. As well as resetting infoCount and increasing fileCount
        del unsortedTable[:]
        del magList[:]
        del phaseList[:]
        del rhoList[:]
        del muList[:]
        del HList[:]
        del alphaList[:]
        infoCount=0 #reset this counter for next file
        fileCount+=1
    #end of if
#end of for


#rounding the elevationList values
for _ in range(len(elevationList)):
    elevationList[_]=roundToMultiple(elevationList[_], 5)
#end of for


#making the dictionary of dataframes with their keys being the data that is saved in respective dataframes which will also be used as 
df_dict={'VV': pd.DataFrame(vvValue, columns=entryHeaders, index=elevationList),
                    'HV': pd.DataFrame(hvValue, columns=entryHeaders, index=elevationList),
                    'VH': pd.DataFrame(vhValue, columns=entryHeaders, index=elevationList),
                    'HH': pd.DataFrame(hhValue, columns=entryHeaders, index=elevationList),
                    'Phase': pd.DataFrame(phase, columns=entryHeaders, index=elevationList),
                    'Rho': pd.DataFrame(mag, columns=entryHeaders, index=elevationList),
                    'Rho Calculated': pd.DataFrame(mag_calculation, columns=entryHeaders, index=elevationList),
                    'Mu': pd.DataFrame(mu_calculation, columns=entryHeaders, index=elevationList),
                    'Alpha': pd.DataFrame(alpha_calculaton, columns=entryHeaders, index=elevationList),
                    'H': pd.DataFrame(H_calculation, columns=entryHeaders, index=elevationList),
                    }

#plotting the dictionary
plotToExcel(df_dict)

print("Program has run successfully and the output file has been created in the chosen directory!")

#program ends
