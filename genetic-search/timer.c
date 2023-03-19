//includes
#include "timer.h"
#include <stdio.h>


//functions
void report_times(timer * const atimer)
{
  printf("\n");
  printf("the new timing information");
  printf("%.3f\n",atimer->seconds);
}
