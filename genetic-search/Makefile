CC = mpicc #-Wall
CFLAGS = -O3 -std=gnu99
LIBS=-lmpi -lm
NCFLAGS = -O2 -g -arch=sm_70 -Xcompiler -fopenmp
NVCC = nvcc

TARGET = perf-ga

$(TARGET): fitness.o ga.o init.o mt_mpi.o report.o
	$(CC)  $^ -o $@ $(LIBS) -lstdc++  -fopenmp
#$(CC)  $^ -o $@ $(LIBS) -lcudart -lcuda -lcusolver -lstdc++  -fopenmp
#$(CC)  $^ -o $@ $(LIBS) -L/usr/local/cuda-10.2/lib64 -lcudart -lcuda -lcusolver -lstdc++  -fopenmp
#-L/usr/local/cuda-10.2/lib64 -L/usr/lib/x86_64-linux-gnu -lstdc++ -lcudart -lcuda -lcusolver 

ga.o: ga.c config.h fitness.h ga.h init.h mt_mpi.h report.h types.h common.h
	$(CC) $(CFLAGS) -c ga.c

fitness.o: fitness.c config.h fitness.h types.h
	$(CC) $(CFLAGS) -c fitness.c

init.o: init.c config.h init.h types.h mt_mpi.h report.h
	$(CC) $(CFLAGS) -c init.c

mt_mpi.o: mt_mpi.c mt_mpi.h
	$(CC) $(CFLAGS) -c mt_mpi.c

report.o: report.c config.h report.h types.h
	$(CC) $(CFLAGS) -c report.c

clean:
	rm *.o $(TARGET)
distclean:
	rm *.o $(TARGET)
