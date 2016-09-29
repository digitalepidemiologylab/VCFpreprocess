# -*-coding:Utf-8 -*

import VCF
from usefulfunctions import *
import VCF
####################################################
import pandas as pd
import glob
import os
import re
import gzip


nbsharedvariantsintotal = 0
nbdiffvariantsintotal = 0

vcffiles = list_vcf_files(PATH+"SelectionofSNPs/ID/")

for files in vcffiles :

	nbsharedvariantsinfile = 0
	nbdiffvariantsinfile = 0

	chrdf = pd.read_csv(files, header=6, compression="gzip", sep="\t").drop(["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"], 1)

	for index, row in chrdf.iterrows():
		if len(row.unique()) == 1 :
			nbsharedvariantsinfile +=1
		else :
			nbdiffvariantsinfile +=1

	nbsharedvariantsintotal += nbsharedvariantsinfile
	nbdiffvariantsintotal += nbdiffvariantsinfile

	print("{0} variants and {1} shared position in file {2}".format(nbdiffvariantsinfile, nbsharedvariantsinfile, files))