#!/bin/bash
export PYTHONPATH=$myscripts/:$PYTHONPATH


if [ $# -lt 2 ] || [ $1 == '-h' ]; then
    echo; echo " Some errors in your launch.sh script!"
    exit
fi

# cases:
# train : needs scaffold.als, chr.als, map_training, python_train
# predict : needs model_from_python, scaffold.als, map, python_predict
# loop train : test accuracy on various scaffold lengths 

project=$1
step=$2
model=$3
optimize=$4


source $project/project.sh
mkdir -p $wdir
cd $wdir
###### Check input files ######

err=0
if [ ! -f $samfile ]; then echo; echo "Could not find samfile file in" $samfile; err=$(($err+1)); fi    
if [ ! -f $mydraft ]; then echo; echo "Could not find draft assembly in" $mydraft; err=$(($err+1)); fi
if [[ ! -f $samref ]] && [[ $step == 'train' ]]; then 
    echo; echo "Could not find ref samfile in" $samref; err=$(($err+1)); 
elif [[ $step == 'predict' ]]; then
    if [[ $model == '' ]]; then
    	echo; echo " Please specify which model to load: randfor, xgboost, both  or /full/path/to/model.sav"; 
    	err=$(($err+1)); 
    fi

    if [[ ! -s $model ]]; then   # it's not a file or does not exists	
	if [[ ! -s $wdir/$model.sav ]]; then    # it's either both or  does not exists
	    if [[ ! $model = "both" ]]; then
		echo; echo "Could not find model for prediction in" $model;
		echo; echo " Please specify which model to load: randfor, xgboost, both  or /full/path/to/model.sav"; 
		err=$(($err+1))
	    fi
	fi
   
    fi
fi
if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi

### common_steps.sh
######### 1. Prepare alignment file for scaffold #########
already_there="(Already there)"
if [[ ! -s $alfile ]]; then
    samtools view -f 0x40 -F 4 -F 0x900 $samfile | grep -v "=" | awk '{print $1, $2, $3, $4, $7, $8}' > $alfile
    already_there="New"
fi
if [[ ! -s $alfile ]]; then  echo; echo "Could not create the alignment file!";  echo "error"; err=$(($err+1)); fi    
if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi
    
echo; echo "1. Scaffold alignment file is ready!" $already_there

  
######### 2. Prepare scaffold stats and lengths ########
already_there="(Already there)"
if [[ ! -s $wdir/myn50.dat ]] || [[ ! -s $wdir/scaffolds_lenghts.txt ]]; then 
    $mysrcs/n50/n50 $mydraft '>' $wdir/myn50.dat
    already_there="New"
fi
if [[ ! -s $wdir/myn50.dat ]] || [[ ! -s $wdir/scaffolds_lenghts.txt ]]; then 
    echo; echo "Could not analyze draft assembly";  echo "error"; err=$(($err+1)); 
fi
echo "2. Draft Stats checked and scaffold_lengths printed" $already_there


if [ $step == "train" ] || [ $step == "looptrain" ]; then

    ### move to train.sh

    ######### 1. Prepare alignment file for chr #########
    already_there="(Already there)"
    if [[ ! -s $refals ]]; then
	samtools view -f 0x40 -F 4 -F 0x900 $samref | grep "=" | awk '{print $1, $2, $3, $4, $7, $8}' > $refals
	already_there="New"
    fi
    if [[ ! -s $refals ]]; then  echo; echo "Could not create the alignment file!"; err=$(($err+1)); fi    
    if [ ! $err -eq 0 ]; then echo; echo " ****  Error! Something is wrong! Giving up! **** "; echo; exit; fi
    
    echo; echo "Train 1. Chr alignment file is ready!" $already_there



    ######### 2. Map reads to scaffolds and keep infop on same_chr 
    already_there="(Already there)"
    if [ ! -f $hictochr ]; then 
	already_there="New"
	$mysrcs/map_reads_fortraining/map_reads_fortraining $wdir/scaffolds_lenghts.txt  $alfile  $refals
    fi    
    if [ ! -f $hictochr ]; then 
	echo "  Error: Something went wrong during map_reads_fortraining"
	exit 
    fi
    echo "Train 2. HiC reads scaffold map plus same_chr printed"  $already_there

    python $myscripts/train_or_predict.py -r $hictochr -f $model -o $optimize -m $step

    # train_or_predict.py  need to modify
    ### Add python script to train and printout model
fi


if [ $step == "predict" ]; then

    ### move to predict.sh
    ######### 1. Map reads to scaffolds 
    already_there="(Already there)"
    if [ ! -f $hictoscaff ]; then 
	already_there="New"
	$mysrcs/map_reads/map_reads $wdir/scaffolds_lenghts.txt  $alfile
	echo
    fi    
    if [ ! -f $hictoscaff ]; then 
	echo "  Error: Something went wrong during map_reads"
	echo "  (Already there?" $already_there")"
	exit 
    fi
    echo; echo "Predict 1. HiC reads scaffold map printed "

    python $myscripts/train_or_predict.py -r $hictoscaff -f $model -o $optimize -m predict
    

    # train_or_predict.py  need to modify
    ### Add python script to read model and print out list of read pair with predicted real connection
    ### Filter original sam file with predicted real connection only, and run Arima again
    echo "Predict 2. Prediction done"

fi 

