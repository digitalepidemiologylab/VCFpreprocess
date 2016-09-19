#!/bin/bash 

###########################
#Change the compression format of the dataset from .vcf.gz to .vcf.zip
###########################
NUMBEROFFILES=$(ls *.vcf.gz | wc -l)
ITER=0

for _file in *.vcf.gz; do

	ITER=$((ITER+1))

	NAME="${_file%.*}"
	echo $NAME
	NAMEZIP="$NAME.zip"

	echo "unzipping $_file ($ITER / $NUMBEROFFILES)"
	gunzip $_file

	echo "rezipping $NAME to $NAMEZIP"
	zip -r $NAMEZIP $NAME

	echo "erasing $NAME"
	rm $NAME
done
