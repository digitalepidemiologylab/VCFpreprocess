import VCF
import pandas as pd
import glob
import os
import re

#######################Works with python 2.7.12 but not 3.5.2

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


###################################################################
PATH = "./"
REFSNPFILE= "./snpslinkedwithheight.csv"
IT = 0
NBCORPOS = 0
NBCORID = 0
vcffiles = []
matchingreferences = pd.DataFrame()
matchingpositions = pd. DataFrame()


####Load list of snp in a dataframe (column 1 = snp ref name, column 2 = chr, column 3 = position)
####Also convert snpref to strings 
refsnps = pd.read_csv(REFSNPFILE, sep = ",")
refids = refsnps["SNP"].tolist()
refpositions = refsnps["Position"].tolist()

####Looking at the files present in the directory before working on them

for files in sorted(glob.glob('*.vcf.gz')):
	IT+=1
	vcffiles.append(files)
	print("File found at {0} : {1}".format(PATH,files))

print("Number of files found in {0} : {1}".format(PATH, IT))
vcffiles = natural_sort(vcffiles)

####
for file in vcffiles:

	print("Loading file {} in a dataframe ...".format(file))
	chromosomefile = VCF.dataframe(file).drop(["ALT", "REF", "QUAL", "FILTER", "INFO"], 1)
	print(chromosomefile.head(5))

	chromosomefile["Row"] = range(1,chromosomefile.shape[0]+1)
	
	matchingreferences = pd.concat((matchingreferences, chromosomefile[chromosomefile['ID'].isin(refids)]))
	matchingpositions = pd.concat((matchingpositions, chromosomefile[chromosomefile["POS"].isin(refpositions)]))


print("We found {} matching ref of snps.".format(matchingreferences.shape[0]))

print("We found {} matching positions of snps.".format(matchingpositions.shape[0]))

matchingpositions.to_csv(path_or_buf="./MatchingPositions.csv", sep="\t")
matchingreferences.to_csv(path_or_buf="./MatchingReferences.csv", sep="\t")