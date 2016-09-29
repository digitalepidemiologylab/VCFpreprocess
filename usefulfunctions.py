# -*-coding:Utf-8 -*


import VCF
#######################
import glob
import pandas as pd
import re

#################################################################################
#################################################################################

PATH = "./"#FichiersVCF/"
REFSNPFILE= "./snpslinkedwithheight.csv"
BEFORECHRNB = PATH+""
AFTERCHRNB = ".QC.vcf.gz.vcf.gz"
ITID = 0
ITPOS = 0
NBCORPOS = 0
NBCORID = 0


#################################################################################



####Sort a list by natural order and returns it
def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


####Parse the folder indicated in PATH and return a list of the files in the <file.vcf.gz>
def list_vcf_files(PATH):
	vcffiles = []
	iterator = 0
	print(PATH)
	for files in glob.glob(PATH+'*.vcf.gz'):
		iterator+=1
		vcffiles.append(files)
		print("File found at {0} : {1}".format(PATH,files))

	print("Number of vcf files found in {0} : {1}".format(PATH, iterator))

	####Naturally sort the files so that the chromosomes are processed in the roght order
	vcffiles = natural_sort(vcffiles)
	return vcffiles

####Look at all the files in the list vcffiles and see if any snp in the refsnp dataframe is present
def find_matches(vcffiles, refsnps) :

	matchingreferences = pd.DataFrame()
	matchingpositions = pd. DataFrame()

	for file in vcffiles:


		####Filter by chromosome to avoid testing all references on all files + prevent from picking the same position for different chromosomes
		chrnb = int(re.sub(BEFORECHRNB,'', re.sub(AFTERCHRNB, '', file)))
		filteredrefsnps = refsnps[ refsnps.Chr == chrnb ]
		refids = filteredrefsnps["SNP"].tolist()
		refpositions = filteredrefsnps["Position"].tolist()	

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


	#####Modified version of the one from VCF.py, allow to load a complete file into a dataframe. /!\ Don't load unfiltered vcf files with this function !
	def dataframe(filename,large=True):
		if large:
			# Set the proper argument if the file is compressed.
			comp = 'gzip' if filename.endswith('.gz') else None
			# Count how many comment lines should be skipped.
			comments = _count_comments(filename)
			# Return a simple DataFrame without splitting the INFO column.
			return pd.read_table(filename, compression=comp, skiprows=comments,
							names=VCF_HEADER, usecols=range(8))

		# Each column is a list stored as a value in this dict. The keys for this
		# dict are the VCF column names and the keys in the INFO column.
		result = OrderedDict()
		# Parse each line in the VCF file into a dict.
		for i, line in enumerate(lines(filename)):
			for key in line.keys():
				# This key has not been seen yet, so set it to None for all
				# previous lines.
				if key not in result:
					result[key] = [None] * i
			# Ensure this row has some value for each column.
			for key in result.keys():
				result[key].append(line.get(key, None))

		return pd.DataFrame(result)