#!/usr/bin/python3
from immucellai2.myclasses import CLASS_FOR_RUN
from immucellai2.myfunction3 import ObtainCellTypeCateogry
import pandas
import os
import re
import sys
import multiprocessing as mp
from importlib.resources import files 

def SelectGeneForDeconvolution(DFReferenceProfile, FileCoveredGenes="", Method="UsedMarker"):
   print("Select the gene for the following deconvolution...")
   GeneUsedForDeconvolution = []
   DFReferenceProfileGenes = DFReferenceProfile.index.values
   print(f"[DEBUG] reference genes: {len(DFReferenceProfileGenes)}")
   print(f"[DEBUG] head: {DFReferenceProfileGenes[:5]}")
   if Method == "UsedMarker":
      if FileCoveredGenes == "": 
         try:
            marker_path = files("immucellai2.myconfig").joinpath("MarkerUsedDeconvolution.txt")
            FileCoveredGenes = str(marker_path)
         except Exception as e:
            import os, sys, re
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            FileCoveredGenes = os.path.join(script_dir, "immucellai2/myconfig/MarkerUsedDeconvolution.txt")
            print(f"[WARNING] Using fallback path: {FileCoveredGenes}")
      try:
         print(f"[DEBUG] getwd: {FileCoveredGenes}")
         GeneUsedForDeconvolution0 = pandas.read_table(FileCoveredGenes, sep="\t", header=None).iloc[1].tolist()
         print(f"[DEBUG] head:\n list(islice(GeneUsedForDeconvolution0, 3))")
         GeneUsedForDeconvolution = list(set(GeneUsedForDeconvolution0).intersection(set(DFReferenceProfileGenes)))
         print(f"Successfully loaded {len(GeneUsedForDeconvolution)} marker genes")
      except FileNotFoundError:
         print(f"Error: Marker file not found - {FileCoveredGenes}")
         print("Please check:")
         print("1. Package is installed correctly (pip install --upgrade immucellai2)")
         print("2. Environment variable IMMUCELLAI_CONFIG_DIR is set")
         return [] 
      except Exception as e:
         print(f"Error reading marker file: {str(e)}") 
         return [] 
   return GeneUsedForDeconvolution

def Obtainmyconfigpath():
   script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
   return os.path.join(script_dir, "immucellai2", "myconfig", "")

def CelltypeCategoryCheck(FileCellTypeCategory = "", celltypelist = [] ):
   print("Check the Celltype covered by configfile")
   if FileCellTypeCategory == "":
      try:
         with resources.path("immucellai2.myconfig", "Celltype.category") as config_path:
            FileCellTypeCategory = str(config_path)
      except Exception as e:
         FileCellTypeCategory = Obtainmyconfigpath() + "Celltype.category"
         print(f"[WARNING] Using fallback path for config file: {FileCellTypeCategory}")
   try:
      obtaincontent = ObtainCellTypeCateogry(FileCellTypeCategory)
   except Exception as e:
      print(f"Error reading cell type config: {str(e)}")
      raise
   Allcelltype = []
   for keyword, oneCellTypeNode in obtaincontent.items():
      Allcelltype += [ keyword ] + oneCellTypeNode["AlsoKnownAs"] + oneCellTypeNode["RelatedNode"]["HisChidNode"]
   for onecelltype in celltypelist:
      if onecelltype not in Allcelltype:
         raise ValueError( "EEROR: reference matrix celltpe'{0}' NOT IN configfile, please CHECK...".format(onecelltype))
   return FileCellTypeCategory
   
def InitialCellTypeRatioCheck(InitialCellTypeRatio, FileInitialCellTypeRatio = "", ncelltype = 0):
   print("Check the celltype ratio initialization method...")
   if InitialCellTypeRatio[1] != "prior":
      return
   if FileInitialCellTypeRatio == "":
      FileInitialCellTypeRatio = Obtainmyconfigpath() + "myCellTypeRatio.initial"
   Expactedcelltypenum = (pandas.read(FileInitialCellTypeRatio, sep = "\t", header = 0, index_col = 0)).shape[1]
   if Expactedcelltypenum <1:
      raise ValueError("FAILED") 
   elif Expactedcelltypenum in [ ncelltype, ncelltype -1 ]:
      return FileInitialCellTypeRatio
   else:
      InitialCellTypeRatio = 'randn'    

def PrepareData(FileReferenceProfile , 
   FileSampleExpressionProfile , 
   EnvironmentConfig = "" ,
   FileCoveredGenes = "" ,
   FileCellTypeCategory = "" ,
   FileInitialCellTypeRatio = "" , 
   InitialCellTypeRatio = ('Normone', 'randn')):
   print("prepare for RunObject...")
   if FileReferenceProfile.shape[1] < 2: 
      print("warning: When open Reference File, might sep = ' ' not '\t'")
   print("celltype reference raw matrix:\n", FileReferenceProfile.iloc[0:4, 0:4]) 
   ReferenceCelltype = {} 
   for oneCellType in FileReferenceProfile.columns.values.tolist():
      numbertail = re.findall("\.[0-9]*$", oneCellType)
      oneCellType0 = oneCellType
      if numbertail != []: oneCellType = oneCellType[:-len(numbertail)]
      if oneCellType in ReferenceCelltype.keys(): 
         ReferenceCelltype[oneCellType].append(ReferenceCelltype[oneCellType])
      else: ReferenceCelltype[oneCellType] = [oneCellType0]
   DFReferenceProfile = pandas.DataFrame(columns = list(ReferenceCelltype.keys()),
       index = FileReferenceProfile.index.values)
   for celltype in  DFReferenceProfile.columns.values:
        DFReferenceProfile[celltype] = (  
           FileReferenceProfile.loc[:, ReferenceCelltype[celltype] ]).mean(axis = 1)
   print("celltype reference matrix:\n", DFReferenceProfile.iloc[0:4, 0:4])
   DFSampleExpressionProfile = pandas.read_table(FileSampleExpressionProfile, sep = "\t", header = 0, index_col = 0)
   print(" initialize a Object For running...") 
   print("environment config(threads): ", EnvironmentConfig)
   GeneUsedForDeconvolution = SelectGeneForDeconvolution(DFReferenceProfile)
   #FileCellTypeCategory = CelltypeCategoryCheck(FileCellTypeCategory, celltypelist = list(ReferenceCelltype.keys()))
   FileInitialCellTypeRatio = InitialCellTypeRatioCheck(InitialCellTypeRatio, FileInitialCellTypeRatio, ncelltype = DFReferenceProfile.shape[1]) 
   DFReferenceProfile0 = DFReferenceProfile.loc[GeneUsedForDeconvolution, ]
   DFReferenceProfile0 = DFReferenceProfile0[DFReferenceProfile0.index.isin(DFSampleExpressionProfile.index)]   
   selected_DFSampleExpressionProfile = DFSampleExpressionProfile.loc[DFReferenceProfile0.index]
   selected_DFSampleExpressionProfile = selected_DFSampleExpressionProfile.transpose() 
   SampleList = list(selected_DFSampleExpressionProfile.index) 
   return CLASS_FOR_RUN(
      DFReferenceProfile0, 
      selected_DFSampleExpressionProfile, 
      SampleList,
      EnvironmentConfig,
      InitialCellTypeRatio = InitialCellTypeRatio,
      FileCellTypeCategory = FileCellTypeCategory,
      FileInitialCellTypeRatio = FileInitialCellTypeRatio,) 








