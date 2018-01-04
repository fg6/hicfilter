#!/bin/bash



main_folder=$1
myscripts=$mymain/scripts
mysrcs=$main_folder/src
mybin=$main_folder/bin

# srcs to compile:
srcs=( map_reads map_reads_fortraining ) 
errs=0

mkdir -p $mybin

cd $mysrcs
mkdir -p mylibs

#if [[ ! -f  $mybin/bwa ]]; then
#    rm -rf mylibs/bwa
#    cd mylibs
#    git clone https://github.com/lh3/bwa.git
#    cd bwa
#    make 
#    cp bwa $mybin/
#fi
#if [[ ! -f $mybin/bwa ]]; then 
#        echo "  !! Error: bwa not installed properly!"; 
#        errs=$(($errs+1))
#        exit
#fi

### Intalling gzstream (it needs zlib!)
if [[ ! -d  mylibs/gzstream ]]  || [[ ! -f mylibs/gzstream/gzstream.o ]]; then
    
    rm -rf mylibs
    mkdir mylibs
    cd mylibs
    
    wget https://www.cs.unc.edu/Research/compgeom/gzstream/gzstream.tgz 

    if [[ "$?" != 0 ]]; then
	echo "Error downloading gzstream, try again" 
	rm -rf gzstream gzstream.tgz 
	exit
    else
	tar -xvzf gzstream.tgz &> /dev/null
	if [[ "$?" != 0 ]]; then echo " Error during gzstream un-compressing. Exiting now"; exit; fi
	cd gzstream
	make &> /dev/null
	
	if [[ "$?" != 0 ]]; then echo " Error during gzstream compilation. Exiting now"; exit; fi
	test=`make test | grep "O.K" | wc -l`

	if [[ $test == 1 ]]; then echo " "1. gzstream installed; rm ../gzstream.tgz 
	else  echo  " Gzstream test failed. Exiting now"; exit; fi
    fi
fi

cd $mysrcs

errs=0
if [[ ! -f mylibs/gzstream/gzstream.o ]]; then
    echo cannot find gzstream: Error! 
    errs=$(($errs+1))
fi


## Compile sources
cd $mysrcs
for code in "${srcs[@]}"; do 
    cd $mysrcs/$code
  
    if [[ ! -f $code ]] || [[ ! -f $mybin/$code ]] || [[ $mybin/$code -ot $code.cpp ]] \
	|| [[ $code -ot $code.cpp ]] || [[ $code -ot $mysrcs/myinc/map.h ]]; then 
	
	make all 
	rm -f $mybin/$code
	cp $code $mybin/.
    fi

    if [[ ! -f $mybin/$code ]]; then
	errs=$(($errs+1))
        echo Error: cannot find $mybin/$code
    fi
done

echo; echo " All done."; echo " Checking installations:"


## Final checks:
PATH=$mybin/:$PATH
if [  $errs -gt 0 ]; then echo; echo "  ****  Errors occurred! **** "; echo; exit; 
else echo "  Congrats: installations successful!"; fi
