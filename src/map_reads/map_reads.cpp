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

static  vector<int> seqpos;
static  vector<string> seqname;

static  std::ofstream myals;
static gzFile fp;

static  std::map<string, long int> lenmap;
static  std::map<string, long int> refmap;
static  std::map<string, int>  samechr_map;
static  std::map<string, int>  samescaff_map;



static std::map< std::string, 
	  std::map< std::string, std::tuple<vector<long int>,vector<long int>,vector<int> > > > pairmap;

int read_refals(char* file);
int read_draftals(char* file);
std::map<string, long int> readscaff(char* file);
int read_hicmap(string file);

static int step2=0;

int main(int argc, char *argv[])
{   
  if (argc < 5 ) {
    fprintf(stderr, "Usage: %s  <ref_alignments> <chr_lengths> <alignments> <scaffolds_lengths>  \n", argv[0]);   
    return 1;
  }	
  for (int i=0; i<argc; i++){
    if((fp = gzopen(argv[i],"r")) == NULL){ 
      cout << " ERROR main:: missing input file " << i << " !! " << endl;
      return 1;
    }
    gzclose(fp);
  }
  
  //Read Scaffold lengths
  fp = gzopen(argv[4],"r");
  lenmap=readscaff(argv[4]);
  cout << "  Read Chr lengths " << endl;

  //Read Chrs lengths
  fp = gzopen(argv[2],"r");
  refmap=readscaff(argv[2]);
  cout << "  Read Scaffolds lengths " << endl;


  // Map HiC reads to Ref and get samechr_map
  string myname = "hic_to_chr.als";
  if((fp = gzopen(myname.c_str(),"r")) == NULL){ 
    myals.open(myname.c_str()); 
    read_refals(argv[1]);
    myals.close();
    cout <<  " Chr-Map Created and file written" << endl;
  }else{ // hic_to_chr.als file already there! Read that only (it's faster!)
    read_hicmap(myname);
    cout <<  "  Chr-Map Created" << endl;
  }



  // Map HiC reads to Draft
  myname = "hic_to_scaff.als";
  myals.open(myname.c_str()); 
  read_draftals(argv[3]);
  myals.close();

  vector<float> positions;
  int bins=100;
  int val_min= 0;
  int val_max= 100;
  float bin_width = (val_max - val_min) / bins; 
  for (int k=0; k<=bins; k++){
    positions.push_back(k);
  }
  int ii=0;
  static int link_numbers=1;
  vector<int> links;

  
  std::map<std::pair<string, string>, int>  done_map;

  cout << endl;
  myname = "map_n_reads.txt";
  myals.open(myname.c_str()); 
  for(auto const &key1 : pairmap) {
    string scaffold = key1.first;


    for(auto const &key2 : pairmap[scaffold]) {
      string mate = key2.first;
      

      // print each couple only once
      if ( done_map.count(std::make_pair(scaffold, mate))
	   || done_map.count(std::make_pair(mate, scaffold)) ){
	continue;
      }else{
	done_map[std::make_pair(scaffold, mate)] = 1;
	done_map[std::make_pair(mate,scaffold)] = 1;
      }

      vector<long int> pos1 =  std::get<0>(pairmap[scaffold][mate]);
      vector<long int> pos2 =  std::get<1>(pairmap[scaffold][mate]);
      vector<int> samechr =  std::get<2>(pairmap[scaffold][mate]);
      int  nlinks= pos1.size();     
      links.push_back( nlinks );
      

      vector<int> linksmap1(bins, 0);
      vector<int> linksmap2(bins, 0);
      int printout=1;
      
      if ( nlinks  >= link_numbers ){
	int countones = std::count (samechr.begin(), samechr.end(), 1);
	int is_same_chr =0;

	if ( countones*100./nlinks  > 90 )
	  is_same_chr = 1;
	else
	  is_same_chr =0;

	ii++;
	for ( int p: pos1 ) {
	  float thispos=p*100./lenmap[scaffold];
	  //int bin_idx = (int)((value - val_min) / bin_width);
	  int bin_idx = (int)((thispos - val_min) / bin_width);
	  
	  if( thispos < 0  ||  thispos > 100 ) 
	    cout << " Error with bin! " <<  thispos << " " << bin_idx << endl;

	  //linksmap1[bin_idx]+=1;	  
	  linksmap1[bin_idx]++;
	}
	  
	for ( int p: pos2 ) {
	  float thispos=p*100./lenmap[mate];
	  //int bin_idx = (int)((value - val_min) / bin_width);
	  int bin_idx = (int)((thispos - val_min) / bin_width);
	  
	  if( thispos < 0  ||  thispos > 100 ) 
	    cout << " Error with bin! " <<  thispos << " " << bin_idx << endl;

	  //linksmap2[bin_idx]+=1;	  
	  linksmap2[bin_idx]++;
	}
	
	if(printout){
	  myals <<  scaffold << " " << mate << " " 
		<< is_same_chr << " " 
		<< lenmap[scaffold] << " " 
		<< lenmap[mate]<< " " 
		<< nlinks ;
	  for ( int p: linksmap1 )  myals << " " << p ;
	  for ( int p: linksmap2 )  myals  << " " << p;	
	  myals << endl;
	}

      }
    }
  }
  myals.close();

  myname = "number_of_links.txt";
  myals.open(myname.c_str()); 
  for (int l=0; l<links.size(); l++){
    myals << links[l] << endl;
  }
  myals.close();
  
  
  return 0;
}

int read_draftals(char* file){
  std::ifstream infile(file);
  string line;

  int readnum=0, sscaffnum=0, schrnum=0;
  int not_found_in_chr=0;
  int same_chr_diff_scaff = 0;

  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, cigar, mate;
	int flag, mapq;
	long int pos, mate_pos, insert;
	int same_scaff=0;

        ss >> read >> flag >> scaffold >> pos 
	   >> mapq >> cigar >> mate >> mate_pos >> insert;
	
	readnum++;  // read num (not read-pairs)

	if( samescaff_map.count(read) ) continue; // read pair already accounted for

	if( !samechr_map.count(read) ) {  // read not found in ref
	  not_found_in_chr++;
	  continue;
	}

	if ( mate == "=" ){
	  mate = scaffold;
	  same_scaff=1;
	  sscaffnum++;
	}else{
	  if(samechr_map[read]) 
	    same_chr_diff_scaff++;
	}
	
	schrnum+=samechr_map[read];       

	// filter on flag and mapq?
	samescaff_map[read] = same_scaff;
	  
	myals << read << " " << scaffold << " " <<  pos << " " 
	      << mate<< " " << mate_pos<< " " << insert << " " 
	      << same_scaff << " " << samechr_map[read] << endl; 


	if(scaffold == mate) continue;
	
	if( pairmap.count(scaffold) &&  pairmap[scaffold].count(mate)) {
	  // pair existing already! Add element
	  vector<long int> pos1 =  std::get<0>(pairmap[scaffold][mate]);
	  vector<long int> pos2 =  std::get<1>(pairmap[scaffold][mate]);
	  vector<int> samechr =  std::get<2>(pairmap[scaffold][mate]);
	  
	  pos1.push_back(pos);
	  pos2.push_back(mate_pos);
	  samechr.push_back(samechr_map[read]);	    
	  pairmap[scaffold][mate] = std::make_tuple(pos1,pos2,samechr);

	}else{ // new pair
	  vector<long int> pos1 = {pos};
	  vector<long int> pos2 = {mate_pos};
	  vector<int> samechr = {samechr_map[read]};
	  pairmap[scaffold][mate] = std::make_tuple(pos1,pos2,samechr);
	}	    

	if (pairmap.count(mate) && pairmap[mate].count(scaffold) ){
	  // pair existing already! Add element
	  vector<long int> pos1 =  std::get<0>(pairmap[mate][scaffold]);
	  vector<long int> pos2 =  std::get<1>(pairmap[mate][scaffold]);
	  vector<int> samechr =  std::get<2>(pairmap[mate][scaffold]);
	  
	  pos1.push_back(mate_pos);
	  pos2.push_back(pos);
	  samechr.push_back(samechr_map[read]);	    
	  pairmap[mate][scaffold] = std::make_tuple(pos1,pos2,samechr);
	  
	}else{
	  // new pair
	  vector<long int> pos1 = {mate_pos};
	  vector<long int> pos2 = {pos};
	  vector<int> samechr = {samechr_map[read]};
	  pairmap[mate][scaffold] = std::make_tuple(pos1,pos2,samechr);
	}	 
	
  }
	



  cout << " Mapping done, I found: " 
       << readnum << " reads, " 
       << not_found_in_chr << " read-pairs which were not mapped to the Ref (at least one)" <<  not_found_in_chr*100./(readnum/2) <<  "%) \n"
       << "  " << schrnum << " read-pairs mapping to the same chromosome (" <<  schrnum*100./(readnum/2) <<  "%) \n"
       << "  " << sscaffnum << " read-pairs mapped to the same scaffold (" <<  sscaffnum*100./(readnum/2) <<  "%) \n"
       << "  " << same_chr_diff_scaff << " read-pairs mapped to same chr but different scaffolds (" <<  same_chr_diff_scaff*100./readnum <<  "%)"
       << endl;
}


std::map<string, long int>  readscaff(char* file){
  std::ifstream infile(file);
  string line;
  std::map<string, long int> tempmap;

  while(getline(infile,line)){
    std::stringstream ss(line);
    string scaff;
    long int length;
    ss >> scaff >> length;
    tempmap[scaff] = length;
  }
  return tempmap;
}

int read_hicmap(string file){  
  std::ifstream infile(file.c_str());
  string line;

  while(getline(infile,line)){
    std::stringstream ss(line);
    string read, scaffold, cigar, mate;
    int flag, mapq;
    long int pos, mate_pos, insert;
    int same_scaff;
    ss >> read >> scaffold >> pos >>
      mate >> mate_pos >> insert >> same_scaff ;

    //if ( scaffold == mate )  same_scaff = 1;
    samechr_map[read] = same_scaff;
  }
 
  return 0;
}




int read_refals(char* file){
  std::ifstream infile(file);
  string line;

  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, cigar, mate;
	int flag, mapq;
	long int pos, mate_pos, insert;
	int same_scaff=0;

        ss >> read >> flag >> scaffold >> pos 
	   >> mapq >> cigar >> mate >> mate_pos >> insert;

	if( samechr_map.count(read) ) continue;
	
	if ( mate == "=" ){
	  mate = scaffold;
	  same_scaff=1;
	}
	
	// filter on flag and mapq?
	//std::tuple<string,long int, string, long int, long int, long int, long int > 
	// thistuple=std::make_tuple(scaffold, pos, mate, mate_pos, insert, lenmap[scaffold], lenmap[mate]);
	
	samechr_map[read] = same_scaff;
	  
	myals << read << " " << scaffold << " " <<  pos << " " 
	      << mate<< " " << mate_pos<< " " << insert << " " << same_scaff << endl; 
	

  }
}

