#include <iomanip>  //setprecision
#include <algorithm>    // sort, reverse
#include <gzstream.h>
#include <vector>  //setprecision
#include <tuple> // C++11, for std::tie
#include <numeric> // accumulate
#include <zlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <tuple> // C++11, for std::tie

using std::cout;
using std::endl;
using std::vector;
using std::string;

static std::ofstream myals;

#include<map.h>

static int step2=0;

int main(int argc, char *argv[])
{   
  gzFile fp;
  if (argc < 3 ) {
    fprintf(stderr, "Usage: %s  <scaffolds_lengths> <alignments>  \n", argv[0]);   
    return 1;
  }	
  for (int i=0; i<argc; i++){
    if((fp = gzopen(argv[i],"r")) == NULL){ 
      cout << " ERROR main:: missing input file " << i << " !! " << endl;
      return 1;
    }
    gzclose(fp);
  }

  std::map<string, long int> lenmap;
 
  // for training case only
  //std::map<string, long int> refmap;
  //std::map<string, int>  samechr_map;  
  //std::map< std::string, 
  //	  std::map< std::string, std::tuple<vector<long int>,vector<long int>,vector<int> > > > pairmap_training;

  
  //Read Scaffold lengths
  fp = gzopen(argv[1],"r");
  lenmap=readscaff(argv[1]);

  /* Need to rewrite following and read_refals function to read and same map of read-links same chr yes or no:
     // fill  samechr_map!!

  // Map HiC reads to Ref and get samechr_map
  string myname = "hic_to_chr.als";
  if((fp = gzopen(myname.c_str(),"r")) == NULL){ 
    myals.open(myname.c_str()); 
    read_refals(argv[1]);  // this for creating chr map?? update though
    myals.close();
    cout <<  " Chr-Map Created and file written" << endl;
  }else{ // hic_to_chr.als file already there! Read that only (it's faster!)
    read_hicmap(myname);
    cout <<  "  Chr-Map Created" << endl;
  }
  */

  // Read and create Map for pair of alignments
  std::map< std::string, 
    std::map< std::string, std::tuple<vector<long int>,vector<long int>,vector<int> > > > pairmap_training;
  pairmap_training = read_als_training(argv[2 , samechr_map]);
 
 
  // Write map and alignment positions plus same chr yes or no column
  string myname = "map_n_reads_training.txt";
  write_data_training(pairmap_training,lenmap,myname);

  return 0;
}
