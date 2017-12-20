#!/bin/bash


if [ $# -lt 2 ] || [ $1 == '-h' ]; then
    echo; echo " Some errors in your launch.sh script!"
    exit
fi

project=$1
step=$2

source $project/project.sh
cd $project


if [ $step == "prepals" ]; then
    err=0
    if [ ! -f $samfile ]; then echo; echo "Could not find samfile file in" $samfile;  echo "error";err=$(($err+1)); fi    
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi
 
    samtools view -f 0x40 -F 4 -F 0x900 $samfile | awk '{print $1, $2, $3, $4, $7, $8}' > $alfile

fi

if [ $step == "align" ]; then
    #######################################################
    ###############   ALIGN PIPELINE    ##################
    #######################################################
    err=0
    if [ ! -f $myref ]; then echo; echo "Could not find reference assembly in" $myref;  echo "error"; err=$(($err+1)); fi
    if [ ! -f $mydraft ]; then echo; echo "Could not find draft assembly in" $mydraft;  echo "error"; err=$(($err+1)); fi
    if [ ! -f $samfile ]; then echo; echo "Could not find hic fastq1 file in" $myfastq1;  echo "error";err=$(($err+1)); fi
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; 
    else echo; echo " All input files found! Proceeding with pipeline.."; echo; fi
    
    $myscripts/runalign.sh $project $2>&1 
fi


#if [ $whattodo == "report" ]; then
    #######################################################
    ##################  CREATE REPORT  ###################
    #######################################################
#fi


if [ $step == "check" ]; then
  ###################################################
  echo; echo " Looking for possible issues... "
  ###################################################

  #if [[ ! -f $workdir/$thirdal.al ]]; then
   #   echo; echo " Error: cannot find file with alignments " $workdir/$thirdal.al
    #  exit
  #fi

  #$myscripts/runcheck.sh 
fi
