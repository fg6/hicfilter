import argparse
import os.path
import sys
import utils
from utils import of,tf
from sklearn.externals import joblib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


#def main():

if 0:
    usage="\n %(prog)s -r full_path_to_file ]" 

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-q", action="store_true", dest="quite", default=False,
                        help="don't print status messages to stdout")

    parser.add_argument("-r", dest="filename",
                        help="full path to read_map file") 
  
    args = parser.parse_args()
    if not args.filename:
        print("Some input is missing!")
        parser.print_help()
        #sys.exit(1)            
    if not os.path.exists(args.filename): 
        print("Sorry, file ", args.filename, "does not exists")
        #sys.exit(1)
        
    inputfile = args.filename
    
if 1:
    inputfile = 'wdir/hic_to_scaff_fortraining.als'
    min_size=0

    try:
        df.head()
    except NameError:
        df = utils.read_df(inputfile, min_size, 1)
        df = df.rename(columns={ 0: 'target', 1: 'scaff1', 2: 'scaff2', 3: 'lscaff1', 4: 'lscaff2', 5: 'nlinks'}) # only true for train sample!

    try:
        df0
    except NameError:
        df1 = df.groupby(['target']).get_group(1)
        df0 = df.groupby(['target']).get_group(0)
        groups = df.groupby('target')


    ### nlinks for target==0 and target==1 
    binwidth=50

    print("Target=0 mean nlinks:", df0['nlinks'].mean())
    print("Target=1 mean nlinks:", df1['nlinks'].mean())

    fig, ax = plt.subplots(nrows=2, ncols=2)
    i=0; j=0

    xmax=12000
    bins=range(0, xmax + binwidth, binwidth)
    # Normed
    ax[i,j].hist(df1['nlinks'],  bins=bins, range=[0,xmax], alpha=0.5, normed=True, log= True, label="ON-chr-links", color='blue');
    ax[i,j].hist(df0['nlinks'],  bins=bins, range=[0,xmax], alpha=0.5, normed=True, label="OFF-chr-links", color='orange');
    ax[i,j].set_xlabel('Nlinks'); ax[i,j].set_ylabel('Freq');
    ax[i,j].set_title('Nlinks Frequency: Normed').set_fontsize(10)
    ax[i,j].legend()
    j=1
    # Not normed
    ax[i,j].hist(df1['nlinks'],  bins=bins, range=[0,xmax], alpha=0.5, log= True, label="ON-chr-links", color='blue'); 
    ax[i,j].hist(df0['nlinks'],  bins=bins, range=[0,xmax], alpha=0.5, label="OFF-chr-links", color='orange');
    ax[i,j].set_xlabel('Nlinks'); ax[i,j].set_ylabel('Freq');
    ax[i,j].set_title('Nlinks Frequency: Not Normed').set_fontsize(10)

    i=1; j=0
    xmax=1000
    binwidth=10
    bins=range(0, xmax + binwidth, binwidth)
    # Not normed
    (n1, bb, patches) = ax[i,j].hist(df1['nlinks'],  bins=bins, range=[0,xmax], log= True, label="ON-chr-links", color='blue', alpha=0.5); 
    (n0, bb, patches) = ax[i,j].hist(df0['nlinks'],  bins=bins, range=[0,xmax], alpha=0.5, label="OFF-chr-links", color='orange');
    ax[i,j].set_xlabel('Nlinks'); ax[i,j].set_ylabel('Freq');
    ax[i,j].set_title('Nlinks Frequency: Not Normed, Zoomed').set_fontsize(10)

    j=1
    # total counts:
    nsum = n1 + n0
    #data_perc =  np.nan_to_num(np.divide(n1,n0)) * 100
    data_perc =  np.nan_to_num(np.divide(n1,nsum)) * 100
    ax[i,j].fill_between(x=bb[:-1],y1=data_perc, y2=0, color='blue', step='pre', alpha=0.5)
    ax[i,j].fill_between(x=bb[:-1],y1=100, y2=data_perc, color='orange', step='pre', alpha=0.5)
    ax[i,j].set_xlabel('Nlinks'); ax[i,j].set_ylabel('%');
    ax[i,j].set_title('Nlinks Frequency: Percentage Stacked').set_fontsize(10)
    plt.tight_layout()
    #plt.show()

    fig.savefig("nlinks.pdf")
    #plt.close()

    #ax.set_color_cycle(colors)
    #ax.margins(0.05)
    #for name, group in groups:
    #    plt.plot(group.lscaff1, group.nlinks, marker='o', linestyle='', ms=3, label=name, alpha=0.5) 
    #    plt.title('Nlinks vs. Scaf1 Lenght') #, loc='center')
 
#if __name__ == "__main__":
#    main()
