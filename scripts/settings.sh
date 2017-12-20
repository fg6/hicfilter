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
project=MYDESTDIR


myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin

# Aligner
mybwa=$mybin/bwa
wdir=$project/wdir
alfile=$wdir/sam.als
draftdir=$wdir/draft

hicdir=$wdir/hicmaps
hictoscaff=$hicdir/hic_to_scaff.als



