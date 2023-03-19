#ifndef UTIL_H
#define UTIL_H

//includes
#include "base.h"
#include "csf.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


//functions
//void cal_modereferencesize(idx_t* Moderefernce, idx_t rank);
//void cal_blocksize(idx_t* blocksize, csf_sptensor* atensor);
void quicksort(idx_t* sortarray, idx_t* noarray0, idx_t* noarray1, double* value, idx_t begin, idx_t end);


#endif
