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

for files in glob.glob('*.vcf.gz'):
	IT+=1
	vcffiles.append(files)
	print("File found at {0} : {1}".format(PATH,files))

print("Number of files found in {0} : {1}".format(PATH, IT))

###Naturally sort the files so that the chromosomes are processed in the roght order
vcffiles = natural_sort(vcffiles)

####
for file in vcffiles:

	print("Loading file {} in a dataframe ...".format(file))
	chromosomefile = VCF.dataframe(file).drop(["ALT", "REF", "QUAL", "FILTER", "INFO"], 1)
	skip = VCF._count_comments(file)+2
	chromosomefile["Row"] = range(skip,chromosomefile.shape[0]+skip)
	
	print("Searching for matches with the reference dataframes...")
	newmatchingreferences = pd.concat((matchingreferences, chromosomefile[chromosomefile['ID'].isin(refids)]))
	newmatchingpositions = pd.concat((matchingpositions, chromosomefile[chromosomefile["POS"].isin(refpositions)]))

	print("{0} ref matching and {1} positions matching in {2}".format(newmatchingreferences.shape[0] - matchingreferences.shape[0], newmatchingpositions.shape[0] - matchingpositions.shape[0], file))

	matchingreferences = newmatchingreferences
	matchingpositions = newmatchingpositions
print("We found {} matching ref of snps.".format(matchingreferences.shape[0]))

print("We found {} matching positions of snps.".format(matchingpositions.shape[0]))

matchingpositions.to_csv(path_or_buf="./MatchingPositions.csv", sep="\t", index=False)
matchingreferences.to_csv(path_or_buf="./MatchingReferences.csv", sep="\t", index=False)