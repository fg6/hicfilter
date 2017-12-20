#!/bin/bash


thisdir=`pwd`
source $thisdir/project.sh

if [ $# -lt 1 ] || [ $1 == '-h' ]; then
    echo; echo "  Usage:" $(basename $0) \<step\> 
    echo "     step: pipeline step to be run. Options: prepals, check "
    echo "      * prepals: prepare alignment file from sam input file"
    echo "      * check: check if alignment ran smoothly"
    exit
fi


step=$1
cd $project


if [ $step == "align" ]; then
    #######################################################
    ###############   ALIGN PIPELINE    ##################
    #######################################################
    $myscripts/pipeline.sh $project $step
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
