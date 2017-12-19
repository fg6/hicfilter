#!/bin/bash


mymain=$1
mydraft=$2
mysam=$3
project=$4

if [ $# -lt 4 ]; then
    echo; echo " Something wrong in your setup.sh script!"
    exit
fi

myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin

mkdir -p $project
mkdir -p $project/history

sub1="s#MYMAIN#$mymain#g"
sub2="s#MYDRAFT#$mydraft#g"
sub3="s#MYSAM#$mysam#g"
sub5="s#MYDESTDIR#$project#g"

sed $sub1 $myscripts/settings.sh | sed $sub2 | sed $sub3 | sed $sub4 > $project/project.sh
cp $myscripts/launch.sh $project/launch.sh


# Saving setup information
setup_time=`date | awk '{print $6$2$3"_"$4}' | sed 's#:#.#g'`
echo $mymain/launchme.sh setup $2 $3 $4  > $project/history/$setup_time.txt
rm -f $project/setupas.txt
ln -sf $project/history/$setup_time.txt $project/setupas.txt



chmod +x $project/*.sh
echo; echo  " Your new project is set in folder: " $project
echo " Modify relevant paramters in " $project/project.sh
