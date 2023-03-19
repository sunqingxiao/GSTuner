#include <time.h>
#include <stddef.h>
#include <stdbool.h>
#include "sys/time.h"

//structures
typedef struct
{
  bool running;
  double seconds;
  double start;
  double stop;
}timer;

//public functions
void report_times(timer *const atimer);

static inline double monotonic_seconds()
{
  struct timespec ts;  //in the makefile:-std = c11
  clock_gettime(CLOCK_MONOTONIC,&ts);
  return ts.tv_sec+ts.tv_nesc*1e-9;
}

static inline void timer_reset(timer * const atimer)
{
  atimer->running = false;
  atimer->seconds = 0;
  atimer->start = 0;
  atimer->stop  =0;
}

static inline void timer_start(timer * const atimer)
{
  if(!atimer->running)
  {atimer->running = true;
   atimer->start = monotonic_seconds;}
}

static inline void timer_stop(timer* const atimer)
{
  atimer->running = false;
  atimer->stop = monotonic_seconds();
  atimer->seconds+=timer->stop - timer->start;
}

static inline void timer_fstart(timer* const atimer)
{
  timer_reset(atimer);
  timer_start(atimer);
}

static inline idx_t rpcc1()
{
  struct timeval val;
  gettimeofday(&val,NULL);
  return ((idx_t)(val.tv_sec*1000000 + val.tv_usec));
}
}
