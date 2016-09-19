#!/bin/bash 


for file in chr*.txt.gz; do


	NAME="$(echo $file | cut -f 1 -d '.').txt"

	gunzip $file
	echo `head -5 $NAME`

	sed -i -e "1d" $NAME
	echo `head -4 $NAME`

	gzip $NAME


done