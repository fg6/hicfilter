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


#include<map.h>

int main(int argc, char *argv[])
{   
  gzFile fp;
  if (argc < 3 ) {
    fprintf(stderr, "Usage: %s  <scaffolds_lengths> <alignments>  \n", argv[0]);   
    return 1;
  }	
  for (int i=0; i<argc; i++){
    if((fp = gzopen(argv[i],"r")) == NULL){ 
      cout << " ERROR main:: missing input file " 
	   << i << " !! " << endl;
      return 1;
    }
    gzclose(fp);
  }

  std::map<string, long int> lenmap;
 
  //Read Scaffold lengths
  fp = gzopen(argv[1],"r");
  lenmap=readscaff(argv[1]);

  // Read and create Map for pair of alignments
  std::map< std::string, std::map< std::string, std::tuple<vector<long int>,vector<long int> > > > pairmap;
  pairmap = read_als(argv[2]);
 
 
  // Write map and alignment positions
  string myname = "map_n_reads.txt";
  write_data(pairmap,lenmap,myname);

  return 0;
}
