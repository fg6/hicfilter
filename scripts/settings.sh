#### Parameters to set: ####
debug=1

# lfs jobs parameters:
lfsjobs=1  
myqueue=normal
maxjobs=50  #maximum number of jobs to run at a time
myjobmem=5000
myncpus=15

########################
mymain=MYMAIN
mydraft=MYDRAFT
samfile=MYSAM
samref=MYREFSAM
project=MYDESTDIR


myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin

# Aligner
mybwa=$mybin/bwa
wdir=$project/wdir
alfile=$wdir/sam.als
refals=$wdir/ref.als

hictoscaff=$wdir/hic_to_scaff.als
hictochr=$wdir/hic_to_scaff_fortraining.als

