#ifndef COMMON_H
#define COMMON_H
#define MAX_CF 10
#define INF 1.0e99
#define EPS 1.0e-14
#define E  2.7182818284590452353602874713526625
#define PI 3.1415926535897932384626433832795029

typedef struct genetic_array {
//  void *m_d10;
//  void *m_d20;
//  void *m_d30;
//  void *m_d40;
//  void *m_d50;
//  void *m_d60;
//  void *m_d70;
//  void *m_d80;
//  void *m_d90;
//  void *m_d100;
  void *m_d;
  void *OShift;
  void *x;
  void *f;
  int n;
  int m;
  int func_num;
} genetic_array;
#endif
