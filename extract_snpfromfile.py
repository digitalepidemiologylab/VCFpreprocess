# -*-coding:Utf-8 -*

from usefulfunctions import *
###########################
import pandas as pd
import os
import re
import gzip
import subprocess

#######################/!\Works with python 2.7.12 but not 3.5.2 /!\############################


####Clean previous results
subprocess.call("rm -rf "+PATH+"/SelectionofSNPs",shell=True)

####Load list of snp in a dataframe (column 1 = snp ref name, column 2 = chr, column 3 = position)
####Also convert snpref to strings 
refsnps = pd.read_csv(REFSNPFILE, sep = ",")


####Looking at the files present in the directory before working on them

vcffiles = list_vcf_files(PATH)

#### Find the reference SNPs in the actual vcf files
matchingreferences, matchingpositions = find_matches(vcffiles, refsnps)


####Save the list of SNPs found
if not os.path.isdir(PATH+"/SelectionofSNPs") :
	os.mkdir(PATH+"/SelectionofSNPs")
matchingpositions.to_csv(path_or_buf=PATH+"/SelectionofSNPs/MatchingPositions.csv", sep="\t", index=False)
matchingreferences.to_csv(path_or_buf=PATH+"/SelectionofSNPs/MatchingReferences.csv", sep="\t", index=False)


for files in vcffiles :


	print("Starting to process file : {}".format(files))

	chrnb = int(re.sub(BEFORECHRNB,'', re.sub(AFTERCHRNB, '', files)))

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

	lines = gzip.open(files, "r" ).readlines()
	outPOS = open(outputfilePOS, 'a')
	outID = open(outputfileID, 'a')

	print("Extract corresponding positions")
	for linenb in filteredmatchpos["Corresponding row in vcf file"] :

		outPOS.write(lines[linenb-1])
		ITPOS+=1
		print("Information on {0}/{1} matching positions copied".format(ITPOS,matchingpositions.shape[0]))

	print("Extract corresponding references")
	for linenb in filteredmatchref["Corresponding row in vcf file"] :
		outID.write(lines[linenb-1])
		ITID+=1
		print("Information on {0}/{1} matching references copied".format(ITID,matchingreferences.shape[0]))

	outPOS.close()
	outID.close()


	####compress the output file to .gz
	subprocess.call("gzip {}".format(outputfilePOS),shell=True)
	subprocess.call("gzip {}".format(outputfileID),shell=True)