using std::cout;
using std::endl;
using std::vector;
using std::string;



/*   Read scaffold/chr name and lengths and save into a map*/
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



//std::map< std::string,std::map< std::string, std::tuple<vector<long int>,vector<long int> > > > 
auto read_als(char* file){
  std::map< std::string,
        std::map< std::string, std::tuple<vector<long int>,vector<long int> > > > pairmap;

  std::ifstream infile(file);
  string line;

  int err=0;
  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, mate;
        int flag;
        long int pos, mate_pos;
        int same_scaff=0;

        ss >> read >> flag >> scaffold >> pos
	   >>  mate >> mate_pos;

        if ( mate == "=" ) continue;  // pair on same scaffold: not interesting
	
	if(pairmap[scaffold].count(mate) && pairmap[mate].count(scaffold) ){
	  if(!err)cout << " Error: duplicate in map " << scaffold << " " << mate << endl;
	  err++;
	}

	if(pairmap[scaffold].count(mate)){ // pair [scaffold][mate] exists already, add one
          vector<long int> pos1 =  std::get<0>(pairmap[scaffold][mate]); //pos
          vector<long int> pos2 =  std::get<1>(pairmap[scaffold][mate]); //mate_pos
         
          pos1.push_back(pos);
          pos2.push_back(mate_pos);
          pairmap[scaffold][mate] = std::make_tuple(pos1,pos2);	  

	} else if ( pairmap[mate].count(scaffold) ){ // otherwise, pair [mate][scaffold]  exists already, add one
	  vector<long int> pos1 =  std::get<0>(pairmap[mate][scaffold]); // mate_pos
          vector<long int> pos2 =  std::get<1>(pairmap[mate][scaffold]); // pos

	  pos1.push_back(mate_pos);
          pos2.push_back(pos);
          pairmap[mate][scaffold] = std::make_tuple(pos1,pos2);	  

	}else{ // new pair
          vector<long int> pos1 = {pos};
          vector<long int> pos2 = {mate_pos};
          pairmap[scaffold][mate] = std::make_tuple(pos1,pos2);
        }
  }
  return pairmap;
}


//std::map< std::string, std::map< std::string, 
//       std::tuple<vector<long int>,vector<long int>,vector<int> > > > 
auto  read_als_training(char* file, std::map<string, int> samechr_map ){

  std::map< std::string, 
    std::map< std::string, std::tuple<vector<long int>,vector<long int>,vector<int> > > > pairmap_training;
  std::ifstream infile(file);
  string line;

  int err=0;
  int ii=0;
  int elim=0;
  int fine=0;
  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, mate;
        int flag;
        long int pos, mate_pos;
        int same_scaff=0;

        ss >> read >> flag >> scaffold >> pos
	   >>  mate >> mate_pos;

	ii++;
	
	if ( mate == "=" ) continue;  // pair on same scaffold: not interesting
	

	fine++;
	// check for bug: //
	if(pairmap_training[scaffold].count(mate) && pairmap_training[mate].count(scaffold) ){
	  if(!err)cout << " Error: duplicate in map " << scaffold << " " << mate << endl; // rpint only once
	  err++;
	}

	if(pairmap_training[scaffold].count(mate)){ // pair [scaffold][mate] exists already, add one
          vector<long int> pos1 =  std::get<0>(pairmap_training[scaffold][mate]); //pos
          vector<long int> pos2 =  std::get<1>(pairmap_training[scaffold][mate]); //mate_pos
	  vector<int> samechr =  std::get<2>(pairmap_training[scaffold][mate]);

          pos1.push_back(pos);
          pos2.push_back(mate_pos);
	  samechr.push_back(samechr_map[read]);
	  pairmap_training[scaffold][mate] = std::make_tuple(pos1,pos2,samechr);

	} else if(pairmap_training[mate].count(scaffold) ){ // otherwise, pair [mate][scaffold]  exists already, add one
	  vector<long int> pos1 =  std::get<0>(pairmap_training[mate][scaffold]); // mate_pos
          vector<long int> pos2 =  std::get<1>(pairmap_training[mate][scaffold]); // pos
	  vector<int> samechr =  std::get<2>(pairmap_training[mate][scaffold]);

	  pos1.push_back(mate_pos);
          pos2.push_back(pos);
	  samechr.push_back(samechr_map[read]);
	  pairmap_training[mate][scaffold] = std::make_tuple(pos1,pos2,samechr);

	}else{ // new pair
          vector<long int> pos1 = {pos};
          vector<long int> pos2 = {mate_pos};
 	  vector<int> samechr = {samechr_map[read]};
	  
	  pairmap_training[scaffold][mate] = std::make_tuple(pos1,pos2,samechr);
        }
  }


  cout << " Total: " << ii <<  " fine: "<< fine << endl;
  return pairmap_training;
}


auto read_refals(char* file){

  std::map<string, int>  samechr_map;  
  std::ifstream infile(file);
  string line;

  int ii=0;
  int fine=0;
  while(getline(infile,line)){
        std::stringstream ss(line);
	string read, chr, mate;
        int flag;
        long int pos, mate_pos;
        int same_scaff=0;

        ss >> read >> flag >> chr >> pos
	   >>  mate >> mate_pos;
     
	ii++;
        if( samechr_map.count(read) ) continue;
        
        if ( mate == "=" ){
          mate = chr;
          same_scaff=1;
	  
	  //if (ii<10) cout << read << endl;
	  fine++;
        }
	samechr_map[read] = same_scaff;
  }

  cout << " Total: " << ii <<  " fine: "<< fine << endl;
  return samechr_map;
}


int write_data( auto pairmap, auto lenmap, string filename)
{
  std::ofstream myals;
  myals.open(filename.c_str()); 

  std::map<std::pair<string, string>, int>  done_map;
  int minlinks=10; // minimum number of links
  int bins=100;
  int val_min= 0;
  int val_max= 100;
  float bin_width = (val_max - val_min) / bins; 


  int err=0;
  for(auto const &key1 : pairmap) {
    string scaffold = key1.first;
  
    for(auto const &key2 : pairmap[scaffold]) {
      string mate = key2.first;
      
      
      if ( done_map.count(std::make_pair(scaffold, mate))
	   || done_map.count(std::make_pair(mate, scaffold)) ){
	if(!err) cout << " Error: duplication in write_data! " << endl;
	err++;
	continue;
      }else{
	done_map[std::make_pair(scaffold, mate)] = 1;
	done_map[std::make_pair(mate,scaffold)] = 1;
      }
      
      vector<long int> pos1 =  std::get<0>(pairmap[scaffold][mate]);
      vector<long int> pos2 =  std::get<1>(pairmap[scaffold][mate]);
      
      int  nlinks= pos1.size();     
           
      vector<int> linksmap1(bins, 0);  // vector of position in scaf1 (percentage of scaffold1 length)
      vector<int> linksmap2(bins, 0);  // vector of position in scaf2 (percentage of scaffold2 length)

      if ( nlinks  >= minlinks ){  // min links
	// fill vector of positions for scaffold 
	for ( int p: pos1 ) {
	  float thispos=p*100./lenmap[scaffold];
	  int bin_idx = (int)((thispos - val_min) / bin_width); // bin
	  
	  if( thispos < 0  ||  thispos > 100 ){
	    cout << " Error with bin! Not found or larger than max: " 
		 <<  thispos << " " << bin_idx << endl;
	    return 0;
	  }

	  linksmap1[bin_idx]++;
	}
	  
	// fill vector of positions for mate 
	for ( int p: pos2 ) {
	  float thispos=p*100./lenmap[mate];
	  int bin_idx = (int)((thispos - val_min) / bin_width);
	  
	  if( thispos < 0  ||  thispos > 100 ){
	    cout << " Error with bin! Not found or larger than max: " 
		 <<  thispos << " " << bin_idx << endl;
	    return 0;
	  }
	  linksmap2[bin_idx]++;
	}


	// write info to file
	myals << scaffold << " " << mate << " " 
	      << lenmap[scaffold] << " " 
	      << lenmap[mate]<< " " 
	      << nlinks ;
	for ( int p: linksmap1 )  myals << " " << p ;
	for ( int p: linksmap2 )  myals  << " " << p;	
	myals << endl;


      }// min number of links     
    }
  }
  myals.close();

}


int write_data_training( auto pairmap, auto lenmap, string filename)
{
  std::ofstream myals;
  myals.open(filename.c_str()); 

  std::map<std::pair<string, string>, int>  done_map;
  int minlinks=10; // minimum number of links
  int bins=100;
  int val_min= 0;
  int val_max= 100;
  float bin_width = (val_max - val_min) / bins; 
  int is_same_chr;

  int err=0;
  for(auto const &key1 : pairmap) {
    string scaffold = key1.first;
  
    for(auto const &key2 : pairmap[scaffold]) {
      string mate = key2.first;
      
      
      if ( done_map.count(std::make_pair(scaffold, mate))
	   || done_map.count(std::make_pair(mate, scaffold)) ){
	if(!err) cout << " Error: duplication in write_data! " << endl;
	err++;
	continue;
      }else{
	done_map[std::make_pair(scaffold, mate)] = 1;
	done_map[std::make_pair(mate,scaffold)] = 1;
      }
      
      vector<long int> pos1 =  std::get<0>(pairmap[scaffold][mate]);
      vector<long int> pos2 =  std::get<1>(pairmap[scaffold][mate]);
      vector<int> samechr =  std::get<2>(pairmap[scaffold][mate]);
      int  nlinks= pos1.size();     
      
      // check if same chr: 
      int countones = std::count (samechr.begin(), samechr.end(), 1);
      int is_same_chr =0;

      if ( countones*100./nlinks  > 90 )
	is_same_chr = 1;
      else
	is_same_chr =0;

           
      vector<int> linksmap1(bins, 0);  // vector of position in scaf1 (percentage of scaffold1 length)
      vector<int> linksmap2(bins, 0);  // vector of position in scaf2 (percentage of scaffold2 length)

      if ( nlinks  >= minlinks ){  // min links

	// fill vector of positions for scaffold 
	for ( int p: pos1 ) {
	  float thispos=p*100./lenmap[scaffold];
	  int bin_idx = (int)((thispos - val_min) / bin_width); // bin
	  
	  if( thispos < 0  ||  thispos > 100 ){
	    cout << " Error with bin! Not found or larger than max: " 
		 <<  thispos << " " << bin_idx << endl;
	    return 0;
	  }

	  linksmap1[bin_idx]++;
	}
	  
	// fill vector of positions for mate 
	for ( int p: pos2 ) {
	  float thispos=p*100./lenmap[mate];
	  int bin_idx = (int)((thispos - val_min) / bin_width);
	  
	  if( thispos < 0  ||  thispos > 100 ){
	    cout << " Error with bin! Not found or larger than max: " 
		 <<  thispos << " " << bin_idx << endl;
	    return 0;
	  }
	  linksmap2[bin_idx]++;
	}


	// write info to file
	myals  << is_same_chr << " " 
	       <<  scaffold << " " << mate << " " 
	       << lenmap[scaffold] << " " 
	       << lenmap[mate]<< " " 
	       << nlinks ;
	for ( int p: linksmap1 )  myals << " " << p ;
	for ( int p: linksmap2 )  myals  << " " << p;	
	myals << endl;


      }// min number of links     
    }
  }
  myals.close();
}
