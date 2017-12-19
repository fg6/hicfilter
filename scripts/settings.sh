#### Parameters to set: ####
aligner=bwa
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
myfastq1=MYFQ1
myfastq2=MYFQ2
project=MYDESTDIR

myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin

# Aligner
mybwa=$mybin/bwa
wdir=$project/$aligner\_temp
draftdir=$wdir/draft
aldir=$wdir/align
alfile=$aldir/bwa.sam

hicdir=$wdir/hicmaps
hictoscaff=$hicdir/hic_to_scaff.als
#sortedhictoscaff=$hicdir/hic_to_scaff_sorted.als


