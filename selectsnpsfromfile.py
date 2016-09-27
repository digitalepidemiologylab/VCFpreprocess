import pandas as pd
import os
import glob

refcsvfile = "./MatchingReferences.csv"
poscsvfile = "./MatchingPositions.csv"


matchingref = pd.read_csv(refcsvfile, sep= "\t")
matchingpos = pd.read_csv(poscsvfile, sep = "\t")


print(matchingpos.head(10))
print(matchingref.head(10))
