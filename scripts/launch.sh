#!/bin/bash


thisdir=`pwd`
source $thisdir/project.sh

if [ $# -lt 1 ] || [ $1 == '-h' ]; then
    echo; echo "  Usage:" $(basename $0) \<step\>   '('\<full/path/to/model.sav\>')'
    echo "     step: pipeline step to be run. Options: train or predict " 
    echo "      * train: train model on alignment to scaffolds and info on same_chr"
    echo "      * predict: use saved model to predict which connections are true"
    echo "      * full/path/to/model.sav: for the predict step provide location of model to be used for predicition"
    exit
elif [  $# -lt 2 ] && [ $1 == 'predict' ]; then
    echo; echo "  Usage:" $(basename $0) \<step\>  '('\<full/path/to/model.sav\>')'
    echo "     step: pipeline step to be run. Options: train or predict " 
    echo "      * train: train model on alignment to scaffolds and info on same_chr"
    echo "      * predict: use saved model to predict which connections are true"
    echo "      * full/path/to/model.sav: for the predict step provide location of model to be used for predicition"
    exit
fi


step=$1
model=$2
optimize=$3
if [[ $optimize == "" ]]; then optimize=0; fi
cd $project



#######################################################
###############  PIPELINE    ##################
#######################################################
$myscripts/pipeline.sh $project $step $model $optimize





if [ $step == "check" ]; then
  ###################################################
  #echo; echo " Looking for possible issues... "
  ###################################################
  echo " not implemented yet..."

  #if [[ ! -f $workdir/$thirdal.al ]]; then
   #   echo; echo " Error: cannot find file with alignments " $workdir/$thirdal.al
    #  exit
  #fi

  #$myscripts/runcheck.sh 
fi
