import pandas as pd
import os
import glob
import re

#####VARIABLES TO DECLARE AT THE BEGINNING OF THE COMPLETE SCRIPT
###############################################
####Strings to remove to extract chromosome number
BEFORECHRNB = ""
AFTERCHRNB = ".QC.vcf.gz.vcf.gz"
###############################################


####TO BE REMOVED WHEN MERGED WITH THE REST OF THE SCRIPT
###############################################
refcsvfile = "./MatchingReferences.csv"
poscsvfile = "./MatchingPositions.csv"

matchingreferences = pd.read_csv(refcsvfile, sep= "\t")
matchingpositions = pd.read_csv(poscsvfile, sep = "\t")

print(matchingpositions.head(5))
print(matchingreferences.head(5))
PATH = "./"
import extract_snpfromfile
vcffiles = extract_snpfromfile.list_vcf_files(PATH)
###############################################

for files in vcffiles :

	if not os.path.isdir(PATH+"/SelectionofSNPs") :
		os.mkdir(PATH+"/SelectionofSNPs")


	#####Copy header and column labels in a subset file (<chrnb>.subset.vcf) in PATH/SelectionofSNPs


 	#####Filter dataframe to have only snps corresponding to the file
	chrnb = int(re.sub(BEFORECHRNB, '', re.sub(AFTERCHRNB, '', files)))


	####Loop through the indexes of the filtered df

		####Check that pos and ref are ok

			####Add line to subset file 



	####compress the output file to .gz
 	
