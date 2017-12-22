#!/bin/bash


if [ $# -lt 2 ] || [ $1 == '-h' ]; then
    echo; echo " Some errors in your launch.sh script!"
    exit
fi

project=$1
step=$2

source $project/project.sh
mkdir -p $wdir
cd $wdir


#if [ $step == "prepals" ]; then
    
    err=0
    if [ ! -f $samfile ]; then echo; echo "Could not find samfile file in" $samfile;  echo "error";err=$(($err+1)); fi    
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi
 
    if [[ ! -s $alfile ]]; then
	samtools view -f 0x40 -F 4 -F 0x900 $samfile | awk '{print $1, $2, $3, $4, $7, $8}' > $alfile
    fi

    if [[ ! -s $alfile ]]; then  echo; echo "Could not create the alignment file!";  echo "error"; err=$(($err+1)); fi    
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi
    
    echo; echo "1. Alignment file is ready!"

#fi

#if [ $step == "prepdraft" ]; then

    
    if [ ! -f $mydraft ]; then echo; echo "Could not find draft assembly in" $mydraft;  echo "error"; err=$(($err+1)); fi
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi


    already_there="Yes"
    if [[ ! -s $wdir/myn50.dat ]] || [[ ! -s $wdir/scaffolds_lenghts.txt ]]; then 
	$mysrcs/n50/n50 $mydraft '>' $wdir/myn50.dat
	already_there="No"
    fi

    if [[ ! -s $wdir/myn50.dat ]] || [[ ! -s $wdir/scaffolds_lenghts.txt ]]; then 
	echo; echo "Could not analyze draft assembly";  echo "error"; err=$(($err+1)); 
    fi
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi

    
    echo "2. Draft Stats checked and scaffold_lengths printed"


#fi

#if [ $step == "map" ]; then
    already_there="Yes"
    if [ ! -f $hictoscaff ]; then 
	already_there="No"
	$mysrcs/map_reads/map_reads $wdir/scaffolds_lenghts.txt  $alfile
	echo
    fi
    
#    if [ ! -f  $hictochr  ] || [ ! -f $hictoscaff ]; then 
#	echo "  Error: Something went wrong during map_reads"
#	echo "  (Already there?" $already_there")"
#	exit 
#   fi
    

#fi 
