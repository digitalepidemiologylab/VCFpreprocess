#!/bin/bash 

for _directory in ./byusr/* ; do

	NUMBERCHROM=$(ls $_directory/ch*.txt.gz | wc -l)
	NAMEUSR=${_directory##*/}
	NAMEOUTPUT="$_directory/chrconcat$NAMEUSR.txt"
	NAMEGZOUTPUT="$NAMEOUTPUT.gz"

	echo "Number of chr. in folder $_directory = $NUMBERCHROM."

	echo "Starting to concatenate chromosomes from user $NAMEUSR"

	for ((_chromosome=1; _chromosome<=$NUMBERCHROM; _chromosome++)); do

		NAMECHR="$_directory/*chr-$_chromosome-usr-$NAMEUSR.txt.gz"
		echo "Concatenating chromosomes from $NAMEUSR : adding chromosome $NAMECHR "

		zcat $NAMECHR>> $NAMEOUTPUT
	done

	gzip $NAMEOUTPUT

	echo "Finished to concatenate chromosomes from user $NAMEUSR. Output : $NAMEGZOUTPUT"


	##########################
	#Control the file and move it to the final directory
	##########################

	LINESNEWFILE=$(zcat ./byusr/$_directory/chrconcat$NAMEUSR.txt | wc -l)
	LINESORIGINALFILES=$(zcat ./byusr/$_directory/chr*.txt.gz | wc -l)

	if [ $LINESORIGINALFILES != $LINESNEWFILE ]; then

		if [ ! -w ./errors.txt ]; then
			touch errors.txt
		fi
		echo "Error : number of lines not matching in sample $NAMEUSR" >> errors.txt
		echo "----------------------------------------------------------------------" >> errors.txt

	else
		echo "Number of lines between original and new files is matching"
		mv $NAMEGZOUTPUT ./splitconcatfiles

	fi

done