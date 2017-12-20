#!/bin/bash

step=$1

mymain=$(dirname $0)
if [[ $mymain == "." ]]; then
    mymain=`pwd`
fi
myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin


if [ $# -lt 1 ] || [ $1 == '-h' ]; then
    echo; echo "  Usage:" $(basename $0) \<step\> 
    echo "  step: pipeline step to be run. Options: install, setup"
    echo "  "
    exit
fi


if [ $step == "install" ]; then
  ###################################################
  echo; echo " Installing hicfilter ..."
  ###################################################
  source $myscripts/install.sh  $mymain
fi


if [ $step == "setup" ]; then
  ###################################################
  # echo; echo " Setup for your project in progress..."
  ###################################################
  if [ $# -lt 3 ]  || [ $2 == '-h' ]; then
      echo; echo "  Usage:" $(basename $0) setup  \</full/path/to/draft\>  \</full/path/to/file.sam\>  \</full/path/to/destdir\>
      echo
      echo "   /full/path/to/draft: location of draft assembly (fasta) "
      echo "   /full/path/to/file.sam: location of sam file for HiC reads mapped against the draft assembly " 
      echo "   /full/path/to/destdir: location of your project "
      echo
      exit
  fi
  $myscripts/setup.sh $mymain $2 $3 $4

fi


if [ $step == "test" ]; then
  ###################################################
  echo; echo " Testing with E.coli data"
  ###################################################
  #$myscripts/runtest.sh  $mymain
fi



if [ $step == "suggestions" ]; then
  ###################################################
  echo  Writing some suggestions for parameters  
  ###################################################
    #$myscripts/runsuggestions.sh  
fi

