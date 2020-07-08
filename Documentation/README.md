# BBS
 Branch and Bound algorithm implementation in python language


> It contains **_r\_tree_** submodule, so clone with - - recursive option

	git clone --recursive https://github.com/sudkumar/bbs_implementation

## Usage

	$ python skyline.py < queryfile > < sampleDataFile >

> \# For example

	python skyline.py query2.txt sample2.txt

## Argument files

1. < queryfile >

	>  Two sample query file has been added named query2.txt and sample_query.txt
  
	> First line contains dimensions on which we want to calculate skylines, excluding first column ( id ) and starting from 1

	> Second line contains _page\_size_ on disk

	> Third line contains  _pointer\_size_ and _key\_size_ separated by space

2. < sampleDataFile >

	> sample files are been added named with sample2.txt, sample\_cor.txt, sample\_ind.txt

	> First column must contains id column and this must not be used in finding skylines

	> No restriction on other column but number of column must be greater then maximum dimension specified in queryFile (obviously )

# Range Skyline Query

	A paper from ...
	The implementation of the proposed algorithms in the paper has been done based on the BBS implementation "https://github.com/sudkumar/bbs_implementation"

# Usage

	python single_dimensional_query.py <queryFile> <dataFile>

# Argument Files

1. <queryFile>
	
	> The first line contains the column on which user's range preference is provided
	> The second line contains the user's range preference
		The first tuple is the start of the range(qs), then a space and then the end of the range(qe)

2. <dataFile>

	> Every row represents the features of an object
	> The first column has the id of the object
	> The rest of the columns have the actual features of the object
	> There is no restriction on the number of features an object can have




	
