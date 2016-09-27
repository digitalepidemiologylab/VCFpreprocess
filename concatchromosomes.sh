	#!/bin/bash 

### Change Zip format before calling split.js



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


############################
#Separate samples using split.js
############################

node split.js



#############################
#Reorganize folders
#############################


mkdir ./bychr
mv ./split/* ./bychr


if [ ! -d ./byusr ]; then
	echo "byusr directory does not exist. Creating it ..."
	mkdir byusr
else

	echo "byusr directory already exists. Cleaning it..."
	rm -rf ./byusr
fi
if [ ! -d ./splitconcatfiles ]; then
	mkdir splitconcatfiles
fi

if [ ! -d ./comments ]; then
	mkdir ./comments
fi


#############################
#Organize the data set by samples
#############################

for _directory in ./bychr/* ; do

	NAMECHR=${_directory##*/}

	for _sample in $_directory/* ; do

		NAMEFILE=${_sample##*/}
		NAMEUSR=$(echo $NAMEFILE | cut -f 1 -d '.')
		if [ ! -d ./byusr/$NAMEUSR ]; then
			mkdir ./byusr/$NAMEUSR
		fi


		####Copy and rename files
		NEWNAME="chr-$NAMECHR-usr-$NAMEUSR.txt.gz"
		echo "Moving chromosome $NAMECHR from usr $NAMEUSR. New name = $NEWNAME"



		#### removes the first row of the _meta files (columns names) before concatenating them. These lines should be removed if split.js changes its output format

		if [ $NAMEFILE == *_meta* ]; then


			echo "Removing header row from $NAMEFILE"
			NAME="$NAMEUSR.txt"
			gunzip $NAMEFILE
			echo `head -5 $NAME`

			sed -i -e "1d" $NAME
			echo `head -4 $NAME`

			gzip $NAME

		fi

		if [ $NAMEFILE == *_comments* ]; then

			cp $_directory/$NAMEFILE ./comments
			mv ./byusr/$NAMEUSR/$NAMEFILE ./byusr/$NAMEUSR/$NEWNAME

		else

			cp $_directory/$NAMEFILE ./byusr/$NAMEUSR
			mv ./byusr/$NAMEUSR/$NAMEFILE ./byusr/$NAMEUSR/$NEWNAME
		fi




	done

done




##############################
#Concatenate the 22 chromosomes in each folder
##############################



for _directory in ./byusr/* ; do

	NUMBERCHROM=$(ls $_directory/ch*.txt.gz | wc -l)
	NAMEUSR=${_directory##*/}
	NAMEOUTPUT="$_directory/chrconcat$NAMEUSR.txt"
	NAMEGZOUTPUT="$NAMEOUTPUT.gz"

	echo "Number of chr. in folder $_directory = $NUMBERCHROM."

	echo "Starting to concatenate chromosomes from user $NAMEUSR"

	for ((_chromosome=1; _chromosome<=$NUMBERCHROM; _chromosome++)); do

		echo "I am in the loop !"

		NAMECHR="$_directory/chr-$_chromosome-usr-$NAMEUSR.txt.gz"
		echo "Concatenating chromosomes from $NAMEUSR : adding chromosome $NAMECHR "

		zcat $NAMECHR>> $NAMEOUTPUT
	done

	gzip $NAMEOUTPUT

	echo "Finished to concatenate chromosomes from user $NAMEUSR. Output : $NAMEGZOUTPUT"


	##########################
	#Control the file and move it to the final directory
	##########################

	LINESNEWFILE=$(zcat $_directory/chrconcat$NAMEUSR.txt | wc -l)
	LINESORIGINALFILES=$(zcat $_directory/chr-*usr*.txt.gz | wc -l)

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