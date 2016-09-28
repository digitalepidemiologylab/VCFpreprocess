#!/usr/bin/python2.7.12
# -*-coding:Utf-8 -*
import pandas as pd
import os
import glob
import re
import gzip

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

	chrnb = int(re.sub(BEFORECHRNB, '', re.sub(AFTERCHRNB, '', files)))


	if not os.path.isdir(PATH+"/SelectionofSNPs") :
		os.mkdir(PATH+"/SelectionofSNPs")
	if not os.path.isdir(PATH+"/SelectionofSNPs/ID") :
		os.mkdir(PATH+"/SelectionofSNPs/ID")
	if not os.path.isdir(PATH+"/SelectionofSNPs/POS") :
		os.mkdir(PATH+"/SelectionofSNPs/POS")
	if not os.path.isdir(PATH+"/SelectionofSNPs/HEADER") :
		os.mkdir(PATH+"/SelectionofSNPs/HEADER")

	outputfileID = PATH+"/SelectionofSNPs/ID/"+str(chrnb)+".subset_ID.vcf"
	outputfilePOS = PATH+"/SelectionofSNPs/POS/"+str(chrnb)+".subset_POS.vcf"
	outputfileHEADER = PATH+"/SelectionofSNPs/HEADER/"+str(chrnb)+".subset_HEADER.vcf"


	#####Copy header and column labels in a subset file (<chrnb>.subset_<type of selction criteria>.vcf) in PATH/SelectionofSNPs
	with gzip.open(files, "r") as fi:
		with open(outputfileID, "w") as fo:
			for line in fi:
				if line.startswith("#"):
					fo.write(line)
				else :
					break




 	#####Filter dataframe to have only snps corresponding to the file

	filteredmatchpos = matchingpositions[ matchingpositions.CHROM == chrnb ]
	filteredmatchref = matchingreferences[ matchingreferences.CHROM == chrnb ]

	#### Use awk to get directly to the line of interest (faster)
	for line in filteredmatchpos["Corresponding row in vcf file"] :
		os.system("zcat {0} | awk 'NR=={1} {{print;exit}}' >> {2}".format(files,line,outputfilePOS))


	####Loop through the indexes of the filtered df

		####Check that pos and ref are ok

			####Add line to subset file 



	####compress the output file to .gz
 	
