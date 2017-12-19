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


using std::cout;
using std::endl;
using std::vector;
using std::string;

static gzFile fp;
static  vector<int> rlen;
static  vector<string> rseq;
static  vector<string> rqual;
static  vector<string> rname;
static  vector<string> rcomment;

static std::ofstream myfile;

int calc(void);
std::pair<std::string, std::string>  getname(std::string str);
int fasttype(char* file);
int readfasta(char* file);
int readfastq(char* file);


int main(int argc, char *argv[])
{ 

  if (argc == 1) {
   fprintf(stderr, "Usage: %s <reads.fq/fa>\n", argv[0]);
   return 1;
  }	
  if((fp = gzopen(argv[1],"r")) == NULL){ 
    printf("ERROR main:: missing input file  !! \n");
    return 1;
  }

  int err=1;

  // File type	
  int isfq=fasttype(argv[1]);


  string myname="scaffolds_lenghts.txt";
  myfile.open(myname.c_str());

  if(!isfq)
     err=readfasta(argv[1]); // save info (contig names and length) in vectors
  else
     err=readfastq(argv[1]);
  myfile.close();

  if(!err)calc();  

  return 0;
}
// ---------------------------------------- //
int calc()
// ---------------------------------------- //
{
  sort(rlen.begin(),  rlen.end(), std::greater<int>());

  int n=rlen.size();
  int max=rlen[0];                 	
  float bases = accumulate(rlen.begin(), rlen.end(), 0.0);
  float mean = bases / n;

  int n50=0,l50=0;
  int done=0;
  long int t50=0;
  int ii=0;
  while(done<1){
    t50+=rlen[ii];
    if(t50 > bases*0.5) 
      done=1;
    ii++;
   }

  n50=ii;
  l50=rlen[n50-1];  //counting from 0
  
  std::cout << std::fixed << std::setprecision(0) <<  "Bases= " << bases << " contigs= "<< n << " mean_length= " 
	<< mean << " longest= " << max << " N50= "<< l50 << " n= " << n50   //counting from 1
	<< std::endl;  

  return 0;
}



// ---------------------------------------- //
int fasttype(char* file)
// ---------------------------------------- //
{ 
  char fq[5]={"@"};
  char fa[5]={">"};
  string ttname;
  int isfq=0;
  igzstream infile(file);

  getline(infile,ttname);
  string ftype=ttname.substr(0,1);
  if(ftype==fa) isfq=0;
  else isfq=1;

  return(isfq);
}


// ---------------------------------------- //
int readfastq(char* file)
// ---------------------------------------- //
{ 
  igzstream infile(file);
  char fq[5]={"@"};
  char plus[5]={"+"};
  int nseq=0;
 
  rlen.reserve(100000);

  string read;
  int seqlen=0;
  int quallen=0;
  int seqlines=0;


  int stop=1;
  while(stop){
    getline(infile,read);
    
    if(read.substr(0,1)==fq){  // name
      nseq++;

      if(nseq>1) {// previous
	rlen.push_back(seqlen);
	if(seqlen != quallen) cout << " Error! seqlen != qual-len"
				 << seqlen << " " << quallen << endl;
      }

      //reset
      seqlen=0;
      seqlines=0;
      quallen=0;

    }else if(read.substr(0,1)==plus){ // + and qual
      for(int ll=0; ll<seqlines; ll++){
	getline(infile,read);
	quallen+=read.size();
      }
    }else{ // sequence 
      seqlines++;
      seqlen+=read.size();
    }
 
    // EOF
    if(infile.eof()){ // previous
      rlen.push_back(seqlen);
      stop=0;
    }

  }//read loop
 
  return 0;
}


// ---------------------------------------- //
int readfasta(char* file)
// ---------------------------------------- //
{ 
  igzstream infile(file);
  char fa[5]={">"};
  int nseq=0;

  rlen.reserve(100000);
 
  string read;
  string old_name, old_comment;
  int seqlen=0;

  int stop=1;
  while(stop){
    getline(infile,read);
    
    if(read.substr(0,1)==fa){  // name
      nseq++;

      if(nseq>1) { // previous
	rlen.push_back(seqlen);
	myfile <<  old_name << " " << seqlen << endl;
      }

      
      //reset
      std::tie(old_name,old_comment) = getname(read); 
      //old_name=read;
      seqlen=0;

    }else{ // sequence 
      seqlen+=read.size();
    }
 
    // EOF
    if(infile.eof()){ // previous
      rlen.push_back(seqlen);
      myfile <<  old_name << " " << seqlen << endl;
      stop=0;
    }
  }//read loop
 
  return 0;
}

std::pair<string, string>  getname(string str){
  size_t ns=0;
  size_t nt=0;
  ns=str.find(" ");
  nt=str.find("\t");

  string name="";
  string comment="";

  if(ns!=std::string::npos) { 
    name=str.substr(1,ns-1);
    comment=str.substr(ns+1,str.size());
  }else if(nt!=std::string::npos) {
    name=str.substr(1,nt-1);
    comment=str.substr(nt+1,str.size());
  }else{
    name=str.erase(0,1);
  }

  return std::make_pair(name,comment);
}
