import VCF
import pandas as pd
import glob
import os
import re
import gzip
import subprocess

#######################/!\Works with python 2.7.12 but not 3.5.2 /!\############################

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def list_vcf_files(PATH):
	vcffiles = []
	iterator = 0
	for files in glob.glob('*.vcf.gz'):
		iterator+=1
		vcffiles.append(files)
		print("File found at {0} : {1}".format(PATH,files))

	print("Number of files found in {0} : {1}".format(PATH, iterator))

	####Naturally sort the files so that the chromosomes are processed in the roght order
	vcffiles = natural_sort(vcffiles)
	return vcffiles

def find_matches(vcffiles, refsnps) :

	refids = refsnps["SNP"].tolist()
	refpositions = refsnps["Position"].tolist()	
	matchingreferences = pd.DataFrame()
	matchingpositions = pd. DataFrame()

	for file in vcffiles:

		print("Loading file {} in a dataframe ...".format(file))
		chromosomefile = VCF.dataframe(file).drop(["ALT", "REF", "QUAL", "FILTER", "INFO"], 1)
		###Number of lines to shift to make dataframe index correspond with lines in actual vcf file (comments + 1 (dataframe index starts at 0)) 
		skip = VCF._count_comments(file)+1
		chromosomefile["Corresponding row in vcf file"] = range(skip,chromosomefile.shape[0]+skip)
		
		print("Searching for matches with the reference dataframes...")
		newmatchingreferences = pd.concat((matchingreferences, chromosomefile[chromosomefile['ID'].isin(refids)]))
		newmatchingpositions = pd.concat((matchingpositions, chromosomefile[chromosomefile["POS"].isin(refpositions)]))

		print("{0} ref matching and {1} positions matching in {2}".format(newmatchingreferences.shape[0] - matchingreferences.shape[0], newmatchingpositions.shape[0] - matchingpositions.shape[0], file))

		matchingreferences = newmatchingreferences
		matchingpositions = newmatchingpositions
	print("We found {} matching ref of snps.".format(matchingreferences.shape[0]))

	print("We found {} matching positions of snps.".format(matchingpositions.shape[0]))
	return matchingreferences, matchingpositions


###################################################################
PATH = "./"
REFSNPFILE= "./snpslinkedwithheight.csv"
BEFORECHRNB = ""
AFTERCHRNB = ".QC.vcf.gz.vcf.gz"
IT = 0
NBCORPOS = 0
NBCORID = 0

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

	chrnb = int(re.sub(BEFORECHRNB, '', re.sub(AFTERCHRNB, '', files)))

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