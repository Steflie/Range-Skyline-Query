
//-------------------
//GENERATOR FUNCTIONS
//-------------------

#include <curses.h>
#include <stdio.h>
#include <cstdlib>
#include <time.h>
#include <math.h>
#include <fstream>
#include <iostream>

using namespace std;



const int GENERATORMAXINT = 10000; //set GENERATORMAXINT with the desired range for each coordinate, e.g. put 1000 for [0,1000]
const double SIGMA = 0.20; //s of gaussian distribution in anti-correlated datasets generation [Mamoulis Generator]
const double SIGMAMATLAB = 0.10; //s of gaussian distribution in anti-correlated datasets generation [Borzsonyi Generator]

typedef int* intPtr;
typedef float* floatPtr;
typedef double* doublePtr;




float FindMinFloat(float x, float y)
{
    float FindMin;
    if (x>y)
    {
        FindMin = y;
    }
    else
    {
        FindMin = x;
    }
    return FindMin;
}




//returns random numbers following a gaussian (normal) distribution (Mamoulis Code)
double gaussian(double mean, double sigma)
{
	double v1,v2,s,x;
	do {
		v1 = double(rand()) / RAND_MAX;
		if (rand()%2) v1 = -v1;
		v2 = double(rand()) / RAND_MAX;
		if (rand()%2) v2 = -v2;
		s = v1*v1 + v2*v2;
	} while (s >= 1.);
	x = v1 * sqrt ( -2. * log (s) / s);
	//  x is normally distributed with mean 0 and sigma 1.
	x = x * sigma + mean;
	return x;
}

//returns random numbers following a normal distribution (Borzsonyi method)
double normal(double m, double s)
{
   // normal distribution with mean m and standard deviation s
   double normal_x1,normal_x2;
   double w;                           // radius
   // make two normally distributed variates by Box-Muller transformation
   do {
      normal_x1 = 2. * (double(rand()) / RAND_MAX) - 1.;
      normal_x2 = 2. * (double(rand()) / RAND_MAX) - 1.;
      w = normal_x1*normal_x1 + normal_x2*normal_x2;
   }
   while (w >= 1. || w < 1E-30);
   w = sqrt(log(w)*(-2./w));
   normal_x1 *= w;  normal_x2 *= w;    // normal_x1 and normal_x2 are independent normally distributed variates
   return normal_x1 * s + m;
}

void BorzsonyiDataSetGenerator()
{
	int ds,ns,i,j;
	int xe;
	char fname[20];
	char txtfile[100];
	double r;
	double Ds;
	double diagSize;
	double left,right,sum,uni;
	double x,minX,maxX;

	int rand_seed=0;
	srand(rand_seed);	// initialize random generator

	printf("\nGive the desired File Name:");
	scanf("%s",fname);
	printf("\nEnter the desired number of dimensions:");
	scanf("%d",&ds);
	printf("\nEnter the desired number of data-points:");
	scanf("%d",&ns);

	sprintf(txtfile,"%s",fname);
	FILE* fout=fopen(txtfile,"w");
	fprintf(fout,"%d\t%d\n",ds,ns);


	double** points = new doublePtr[ns];
		for (i=0;i<ns;i++)	{ points[i] = new double[ds+1]; }


	diagSize = sqrt(ds);

	for(i=0;i<ns;i++)
	{
	    points[i][0] = double(i);

		//select a normal distributed value in the space diagonal.
		r = normal(diagSize/2.0,SIGMAMATLAB);
		Ds = double((2.0*r)/sqrt(2.0));

		if (r<=double(sqrt(2.0)/2.0))
		{
			left = 0.0;
			right = double((2.0*r)/sqrt(2.0));
		}
		else
		{
			left = double((2.0*r)/sqrt(2.0) - 1.0);
			right = 1.0;
		}

		//equation of plane: x1 + x2 + ... +x ns = Ds
		//Find values for all dimensions but one.
		sum = 0.0;
		for (j=1;j<ds;j++)
		{
			//get a uniform value in [0,1]
			uni = double(rand()) / RAND_MAX;
       		//scale value to [left,right]
			x = double(left + (right-left)*uni);
			points[i][j] = x;
			sum = sum + x;
		}

		//determine value of the last dimension based on plane equation
		x = Ds - sum;
		points[i][ds] = x;
	}


	//scale dim values to [0,1] (normalization)
	for (j=1;j<=ds;j++)
	{
		minX=0.0;
		maxX=0.0;
		for(i=0;i<ns;i++)
		{
			x=points[i][j];
			//find min and max values
			if (x<minX) minX=x;
			if (x>maxX) maxX=x;
		}
		for(i=0;i<ns;i++)
		{
			points[i][j] = double((points[i][j]-minX)/(maxX-minX));
		}
	}


	//write normalized data to file scaling to the final integer values
	for(i=0;i<ns;i++)
	{
		fprintf(fout,"%d\t",i);
		for (j=1;j<=ds;j++)
		{
			xe = int(GENERATORMAXINT * points[i][j]);
			fprintf(fout,"%d",xe);
			if (j<ds) fprintf(fout,"\t");
		}
		fprintf(fout,"\n");
	}

	fclose(fout);


	for (i=0;i<ns;i++) delete []points[i];
	delete[] points;

    printf("\nData created succesfully.\n\n");
}



void MamoulisDataSetFileGenerator()
{
	int ds,ns,i,j;
	int x;
	char fname[20];
	char txtfile[100];
	char gen_code;
	double value;
	double newval;
	double range;
	double pold;

	int rand_seed=0;
	srand(rand_seed);	// initialize random generator
	srand(rand_seed);


	// printf("\nDo you want an Anti-Correlated Dataset using Borzsonyi Generator (y/n)?");
	// gen_code=getch();
	// if (gen_code=='y')
	// {
	// 	BorzsonyiDataSetGenerator();
	// 	return;
	// }


	printf("\nGive the desired File Name:");
	scanf("%s",fname);
	printf("\nEnter the desired number of dimensions:");
	scanf("%d",&ds);
	printf("\nEnter the desired number of data-points:");
	scanf("%d",&ns);
	printf("\nGive the desired Distribution (i/c/a):");
	gen_code='c'; //getch();
	printf("%c\n",gen_code);

	sprintf(txtfile,"%s",fname);

	FILE* fout=fopen(txtfile,"w");

	fprintf(fout,"%d\t%d\n",ds,ns);

	for(i=0;i<ns;i++)
	{
		fprintf(fout,"%d\t",i);
		for (j=0;j<ds;j++)
		{
			if (gen_code=='i') //create independent points
			{
				x=int(GENERATORMAXINT * ( (double) rand()/RAND_MAX));
			}
			else if (gen_code=='c') //create correlated points
			{
				if (j==0)
				{
					value=double(rand())/RAND_MAX;
					x=int(GENERATORMAXINT*value);
				}
				else
				{
					newval=gaussian(value,0.05);
					while (newval<0 || newval>1) newval=gaussian(value,0.05);
					value=newval;
					x=int(GENERATORMAXINT*value);
				}
			}
			else if (gen_code=='a') //create anti-correlated points
			{
				if (j==0)
				{
					range=0.5*ds + gaussian(0,SIGMA);
					pold=(double(rand()) / RAND_MAX)*FindMinFloat(1.0,range);
					x=int(GENERATORMAXINT*pold);
				}
				else
				{
					range=range-pold;
					pold=(double(rand()) / RAND_MAX)*FindMinFloat(1.0,range);
					x=int(GENERATORMAXINT*pold);
					if (j==ds-1)
					{
						pold=FindMinFloat(1.0,range);
						x=int(GENERATORMAXINT*pold);
					}
					if(x==GENERATORMAXINT)     //<---correction that avoids many points with same GENERATORMAXINT x value
					{
						x = x - int(100 * ( (double) rand()/RAND_MAX));
					}
				}
			}
			fprintf(fout,"%d",x);
			if (j<ds-1) fprintf(fout,"\t");
		}
		fprintf(fout,"\n");
	}

	fclose(fout);

    printf("\nData created succesfully.\n\n");

}


int main(void)
{
	// For correlated distrubution
	printf("Correlated Data: \n");
	MamoulisDataSetFileGenerator();
	// For anti-correlated distribution
	printf("Anti-Correlated Data: \n");
	BorzsonyiDataSetGenerator();

	return 0;
}



