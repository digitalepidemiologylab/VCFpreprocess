#!/usr/bin/python2.7.12
# -*-coding:Utf-8 -*
import pandas as pd
import os
import glob
import re
import gzip
import subprocess

#####VARIABLES TO DECLARE AT THE BEGINNING OF THE COMPLETE SCRIPT
###############################################
####Strings to remove to extract chromosome number
PATH = "./"
BEFORECHRNB = ""
AFTERCHRNB = ".QC.vcf.gz.vcf.gz"

subprocess.call("rm -rf"+PATH+"/SelectionofSNPs",shell=True)
###############################################


####TO BE REMOVED WHEN MERGED WITH THE REST OF THE SCRIPT
###############################################
refcsvfile = "./MatchingReferences.csv"
poscsvfile = "./MatchingPositions.csv"

matchingreferences = pd.read_csv(refcsvfile, sep= "\t")
matchingpositions = pd.read_csv(poscsvfile, sep = "\t")

print(matchingpositions.head(5))
print(matchingreferences.head(5))
import extract_snpfromfile
vcffiles = extract_snpfromfile.list_vcf_files(PATH)
###############################################



for files in vcffiles :


	print("Starting to process file : {}".format(files))

	chrnb = int(re.sub(BEFORECHRNB, '', re.sub(AFTERCHRNB, '', files)))


	if not os.path.isdir(PATH+"/SelectionofSNPs") :
		os.mkdir(PATH+"/SelectionofSNPs")
	if not os.path.isdir(PATH+"/SelectionofSNPs/ID") :
		os.mkdir(PATH+"/SelectionofSNPs/ID")
	if not os.path.isdir(PATH+"/SelectionofSNPs/POS") :
		os.mkdir(PATH+"/SelectionofSNPs/POS")

	outputfileID = PATH+"/SelectionofSNPs/ID/"+str(chrnb)+".subset_ID.vcf"
	outputfilePOS = PATH+"/SelectionofSNPs/POS/"+str(chrnb)+".subset_POS.vcf"

	#####Copy header and column labels in a subset file (<chrnb>.subset_<type of selction criteria>.vcf) in PATH/SelectionofSNPs
	with gzip.open(files, "r") as fi:
		with open(outputfileID, "w") as fo:
			for line in fi:
				if line.startswith("#"):
					fo.write(line)
				else :
					break
	subprocess.call("cp {0} {1}".format(outputfileID, outputfilePOS), shell=True)

 	#####Filter dataframe to have only snps corresponding to the file

	filteredmatchpos = matchingpositions[ matchingpositions.CHROM == chrnb ]
	filteredmatchref = matchingreferences[ matchingreferences.CHROM == chrnb ]

	#### Use awk to get directly to the line of interest (faster)
	print("Extract corresponding positions")
	for line in filteredmatchpos["Corresponding row in vcf file"] :
		subprocess.call("zcat {0} | awk 'NR=={1} {{print;exit}}' >> {2}".format(files,line,outputfilePOS), shell=True)

	print("Extract corresponding references")
	for line in filteredmatchref["Corresponding row in vcf file"] :
		subprocess.call("zcat {0} | awk 'NR=={1} {{print;exit}}' >> {2}".format(files,line,outputfileID), shell=True)


	####compress the output file to .gz
 	subprocess.call("gzip {}".format(outputfilePOS),shell=True)
 	subprocess.call("gzip {}".format(outputfileID),shell=True)