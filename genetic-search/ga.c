/* ========================================================================= */
/* Main GA loop and genetic operator functions								 */
/* ========================================================================= */
#include <math.h>
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "init.h"
#include "fitness.h"
#include "ga.h"
#include "mt_mpi.h"
#include "report.h"
#include "types.h"
#include "common.h"

int main(int argc, char *argv[]) {
	int my_rank;
	double mpi_start_time, mpi_end_time;
	deme *subpop = (deme*) malloc(sizeof(deme));
    
    //idx_t max_cost = atoi(argv[1]);
    //printf("max_cost = %ld\n", max_cost);
    
	MPI_Init(&argc, &argv);
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    //printf("***** init population *****\n");
	init_population(subpop, argc, argv);
	mpi_start_time = MPI_Wtime();
    printf("***** begin iteration *****\n");
	while (!subpop->complete) {
        //printf("***** migration process *****\n");
		migration(subpop);
        //printf("***** reproduction process *****\n");
		reproduction(subpop);
        //printf("***** crossover process *****\n");
		crossover(subpop);
        //printf("***** mutation process *****\n");
		mutation(subpop);
        //printf("***** fitness process *****\n");
        //printf("line 37!\n");
		fitness(subpop);
        update(subpop);
        //printf("line 39!\n");
		//subpop->old_pop = subpop->new_pop;
		subpop->cur_gen++;
        //printf("line 39!\n");
		check_complete(subpop);
		sync_complete(subpop);
        //printf("***** report process *****\n");
		report_all(subpop);
	}
	
	mpi_end_time = MPI_Wtime();
	report_fittest(subpop);
	MPI_Finalize();
	printf("[%i] Elapsed time: %f\n", my_rank, mpi_end_time - mpi_start_time);
	return 0;
}


/* ------------------------------------------------------------------------- */
/* Exchange members with neighboring subpoulations in a ring arrangement.	 */
/* The least fit member of this subpoulation is exchanged with the most fit	 */
/* member of the neighbor to the right. Also, the most fit member of this	 */
/* subpoulation is exchanged with the least fit member of the left neighbor. */
/* ------------------------------------------------------------------------- */
void migration(deme *subpop) {
	MPI_Status	status;
	int my_rank, n_procs;
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
	MPI_Comm_size(MPI_COMM_WORLD, &n_procs);

	int neighbor1 = my_rank, neighbor2 = my_rank;
	if (++neighbor1 == n_procs) neighbor1 = 0;
	if (--neighbor2 == -1) neighbor2 = n_procs - 1;
	
	char old_min[subpop->chr_size];
	char new_min[subpop->chr_size];
	char old_max[subpop->chr_size];
	char new_max[subpop->chr_size];

	// Send the right neighbor the least fit member of this poulation
	strncpy(old_min, subpop->old_pop[subpop->fit_min]->chr,
		subpop->chr_size);
	MPI_Send(old_min, subpop->chr_size, MPI_CHAR, neighbor1, 50,
		MPI_COMM_WORLD);
		
	// Receive the left neighbor's least fit member and add to this population
	MPI_Recv(new_min, subpop->chr_size, MPI_CHAR, neighbor2, 50,
		MPI_COMM_WORLD, &status);
	strncpy(subpop->old_pop[subpop->fit_min]->chr, new_min,
			subpop->chr_size);	
			
	// Send the left neighbor the most fit member of this poulation
	strncpy(old_max, subpop->old_pop[subpop->fit_max]->chr,
		subpop->chr_size);
	MPI_Send(old_max, subpop->chr_size, MPI_CHAR, neighbor2, 50,
		MPI_COMM_WORLD);
		
	// Receive the right neighbor's most fit member and add to this population
	MPI_Recv(new_max, subpop->chr_size, MPI_CHAR, neighbor1, 50,
		MPI_COMM_WORLD, &status);
	strncpy(subpop->old_pop[subpop->fit_max]->chr, new_max,
			subpop->chr_size);			
}


/* ------------------------------------------------------------------------- */
/* Select an individual in the population by roulette wheel method; a		 */
/* "wheel" is partitioned into sizes proportional to an individual's fitness */
/* relative to the fitness of the rest of the population.					 */
/* ------------------------------------------------------------------------- */
int selection(deme *subpop, int id) {
	int i, my_rank;
    int selection_items[4];
	double current_sum = 0.0;
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
	
	long double rand = mt_rand_real(subpop->fit_tot, my_rank);

    int counter = 0;

    int my_row = id / 4;
    int my_col = id % 4;
    
    if (my_row - 1 >= 0) selection_items[counter++] = id - 4;
    if (my_col - 1 >= 0) selection_items[counter++] = id - 1;
    if (my_col + 1 < 4) selection_items[counter++] = id + 1;
    if (my_row + 1 < 4) selection_items[counter++] = id + 4;
	
	//for (i = 0; i < subpop->pop_size && current_sum <= rand; i++) {
	for (i = 0; i < counter && current_sum <= rand; i++) {
		current_sum += subpop->old_pop[selection_items[i]]->fitness;
        //printf("i=%d, current = %lf, fitneiss = %lf\n", i, current_sum, subpop->old_pop[i]->fitness);
    }

	//printf("return = %d!\n", i-1);
	return selection_items[i-1];
}


/* ------------------------------------------------------------------------- */
/* Randomly pairs individuals, producing from each pair a new pair of		 */
/* offspring. Reproductive probability is determined by relative fitness.	 */
/* Each individual may potentially reproduce zero or more times.			 */
/* ------------------------------------------------------------------------- */
void reproduction(deme *subpop) {
	int i;

	//for (i = 0; i < subpop->pop_size-1; i+=2) {
	for (i = 0; i < subpop->pop_size; i++) {
		// Select two (distinct) parents via roulette wheel
        //printf("before selection!\n");
        //printf("popsize = %d\n", i);
		int p1 = selection(subpop, i);
		int p2 = selection(subpop, i);
        //printf("i=%d, line 139!\n", i);
		while (p1 == p2) p2 = selection(subpop, i);
		// Use these as the parents of two individuals in the next generation
        //printf("i=%d, line 143!\n", i);

		subpop->new_pop[i]->parent1 = p1;
		subpop->new_pop[i]->parent2 = p2;
        //printf("i=%d, line 147!\n", i);

		//subpop->new_pop[i+1]->parent1 = p1;
		//subpop->new_pop[i+1]->parent2 = p2;
	}
}


/* ------------------------------------------------------------------------- */
/* Gives children of the new population attibutes from each of their parents */
/* using two-point crossover.												 */
/* ------------------------------------------------------------------------- */
void crossover(deme *subpop) {
	int i, j, p1, p2, my_rank;
	int xover_pt = subpop->chr_size/2;
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

	for (i = 0; i < subpop->pop_size - 1; i += 2) {
		p1 = subpop->new_pop[i]->parent1;
		p2 = subpop->new_pop[i]->parent2;
		
		if (mt_probability(CROSSOVER_RATE, my_rank)) {
			for (j = 0; j < xover_pt; j++) 
				subpop->new_pop[i]->chr[j] = subpop->old_pop[p1]->chr[j];
			for (j = xover_pt; j < subpop->chr_size; j++)
				subpop->new_pop[i]->chr[j] = subpop->old_pop[p2]->chr[j];
			for (j = 0; j < xover_pt; j++) 
				subpop->new_pop[i+1]->chr[j] = subpop->old_pop[p2]->chr[j];
			for (j = xover_pt; j < subpop->chr_size; j++)
				subpop->new_pop[i+1]->chr[j] = subpop->old_pop[p1]->chr[j];
		}
		else {
			strncpy(subpop->new_pop[i]->chr, subpop->old_pop[p1]->chr,
				subpop->chr_size);
			strncpy(subpop->new_pop[i+1]->chr, subpop->old_pop[p2]->chr,
				subpop->chr_size);
		}
	}
}


/* ------------------------------------------------------------------------- */
/* Mutates bits with a probability defined by MUTATION_RATE					 */
/* For smaller chromosomes, flip a single random bit in each selected string.*/
/* For larger chromosomes, multiple segments of a chromosome have a chance	 */
/* to be mutated.															 */
/* ------------------------------------------------------------------------- */
void mutation(deme *subpop) {
	int i, seg, rand, my_rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

	// Simple fitness function with smaller chromosomes
	if (subpop->ff_type == FF_SIMPLE) {
		for (i = 0; i < subpop->pop_size; i++) {
			if (mt_probability(MUTATION_RATE, my_rank)) {
				rand = mt_rand_int(subpop->chr_size, my_rank);
				if (subpop->new_pop[i]->chr[rand] == '0')
					subpop->new_pop[i]->chr[rand] = '1';
				else subpop->new_pop[i]->chr[rand] = '0';
			}
		}
	}
	
	// Shortest path fitness function with larger chromosomes
	else if (subpop->ff_type == FF_SHPATH) {
		for (i = 0; i < subpop->pop_size; i++) {
			for (seg = 0; seg < subpop->chr_size; seg += COORD_SIZE) {
				if (mt_probability(MUTATION_RATE, my_rank)) {
					rand = seg + mt_rand_int(COORD_SIZE, my_rank);
					if (subpop->new_pop[i]->chr[rand] == '0')
						subpop->new_pop[i]->chr[rand] = '1';
					else subpop->new_pop[i]->chr[rand] = '0';
				}
			}
		}
	}
}


/* ------------------------------------------------------------------------- */
/* Test if the termination condition has been reached for this sub-population*/
/* ------------------------------------------------------------------------- */
void check_complete(deme *subpop) { // SQX modified
	if (subpop->end_type == M_FIXED_GENERATIONS) {
		if (subpop->cur_gen >= subpop->end_gen) subpop->complete = 1;
	}
	else if (subpop->end_type == M_AVG_FITNESS_THRESHHOLD) {
		if (subpop->fit_avg >= subpop->f_thresh)  subpop->complete = 1;
	}
	else if (subpop->end_type == M_MAX_FITNESS_THRESHHOLD) {
		if (subpop->new_pop[subpop->fit_max]->fitness >= subpop->f_thresh)
			subpop->complete = 1;
	}
	else if (subpop->end_type == M_LOCAL_CONVERGENCE) {
		double difference = fabs(subpop->fit_avg - subpop->fit_prev);
		if (difference < subpop->conv_var) subpop->fit_novar++;
		if (subpop->fit_novar >= subpop->conv_gen) subpop->complete = 1;
	}
    else if (subpop->end_type == M_LOCAL_APPR_THRESHHOLD) {
//        printf("******* CV = %lf ********\n", subpop->fit_cv);
        if (subpop->fit_cv <= subpop->a_thresh) subpop->complete = 1;
    }
    else if (subpop->end_type == M_LOCAL_MCR_THRESHHOLD) {
//        printf("********* MCR = %lf *************\n", subpop->fit_mcr);
        if (subpop->fit_mcr >= subpop->m_thresh) subpop->complete = 1;
    }
}


/* ------------------------------------------------------------------------- */
/* Check if any sub-populations have completed; if so, inform all other		 */
/* processes. This does not apply to runs with fixed generations.			 */
/* ------------------------------------------------------------------------- */
void sync_complete(deme *subpop) {
	MPI_Status status;
	int source, complete, my_rank, n_procs;
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
	MPI_Comm_size(MPI_COMM_WORLD, &n_procs);
	
	if (subpop->end_type == M_FIXED_GENERATIONS) return;
		
	// If any sub-populations have completed, signal process 0
	if (my_rank != 0)
		MPI_Send(&subpop->complete, 1, MPI_INT, 0, 50, MPI_COMM_WORLD);
	else {
		for (source = 1; source < n_procs; source++) {
			MPI_Recv(&complete, 1, MPI_INT, source, 50, MPI_COMM_WORLD,
				&status);
			if (complete) subpop->complete = 1;
		}
	}
	
	// If a completed sub-population has been found, signal all processes
	if (my_rank == 0) {
		for (source = 1; source < n_procs; source++)
			MPI_Send(&subpop->complete, 1, MPI_INT, source, 50,
				MPI_COMM_WORLD);
	}
	else {
		MPI_Recv(&complete, 1, MPI_INT, 0, 50, MPI_COMM_WORLD, &status);
		if (complete) subpop->complete = 1;
	}
}

/**
 * @brief 更新subpop->oldpop
 * 
 * @param subpop 
 */
void update(deme *subpop)
{
	int i = 0;
	for (i = 0; i < DEFAULT_POP_SIZE; i++) {
		org *old_pop = subpop->old_pop[i];
		org *new_pop = subpop->new_pop[i];
		if (new_pop->fitness > old_pop->fitness) {
			old_pop->fitness = new_pop->fitness;
			old_pop->parent1 = new_pop->parent1;
			old_pop->parent2 = new_pop->parent2;
			int j = 0;
			for (j = 0; j < subpop->chr_size; j++) {
				old_pop->chr[j] = new_pop->chr[j];
			}
		}
	}
}

