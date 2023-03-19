#ifndef IO_H
#define IO_H


#include "sptensor.h"
#include "matrixprocess.h"
#include <stdio.h>
#include <stdint.h>


/**
* @brief Open a file.
*
* @param fname The name of the file.
* @param mode The mode for opening.
*
* @return A FILE pointer.
*/
static inline FILE * open_f(
  char const * const fname,
  char const * const mode)
{
  FILE * f;
  if((f = fopen(fname, mode)) == NULL) {
    fprintf(stderr, "SPLATT ERROR: failed to open '%s'\n", fname);
    exit(1);
  }
  return f;
}




/******************************************************************************
 * FILE TYPES
 *****************************************************************************/

/**
* @brief An enum describing the supported input file types.
*/
typedef enum
{
  SPLATT_FILE_TEXT_COORD,      /* plain list of tuples + values */
  SPLATT_FILE_BIN_COORD        /* a binary version of the coordinate format */
} splatt_file_type;


#define get_file_type splatt_get_file_type
/**
* @brief Attempt to determine the type of tensor file based on the extension.
*        NOTE: Defaults to SPLATT_FILE_TEXT_COORD and prints to stderr if
*        unable to determine.
*
* @param fname The filename to analyze.
*
* @return A file type.
*/
splatt_file_type get_file_type(
    char const * const fname);



/******************************************************************************
 * BINARY READS
 *****************************************************************************/


typedef enum
{
  SPLATT_BIN_COORD,
  SPLATT_BIN_CSF
} splatt_magic_type;


/**
* @brief This struct is written to the beginning of any binary tensor file
*        written by SPLATT.
*/
typedef struct
{
  int32_t magic;
  uint64_t idx_width;
  uint64_t val_width;
} bin_header;


#define read_binary_header splatt_read_binary_header
/**
* @brief Populate a binary header from an input file.
*
* @param fin The file to read from.
* @param[OUT] header The header to populate.
*/
void read_binary_header(
    FILE * fin,
    bin_header * header);


#define fill_binary_idx splatt_fill_binary_idx
/**
* @brief Fill an array of idx_t with values from a binary file. 'header' tells
*        us whether we can just fread() the whole array or must read one at a
*        time.
*
* @param buffer The buffer of idx_t to fill.
* @param count The number of entries to read.
* @param header The binary header telling us datatype sizes.
* @param fin The file to read from.
*/
void fill_binary_idx(
    idx_t* const buffer,
    idx_t const count,
    bin_header const * const header,
    FILE * fin);


#define fill_binary_val splatt_fill_binary_val
/**
* @brief Fill an array of val_t with values from a binary file. 'header' tells
*        us whether we can just fread() the whole array or must read one at a
*        time.
*
* @param buffer The buffer of val_t to fill.
* @param count The number of entries to read.
* @param header The binary header telling us datatype sizes.
* @param fin The file to read from.
*/
void fill_binary_val(
    double* const buffer,
    idx_t const count,
    bin_header const * const header,
    FILE * fin);




/******************************************************************************
 * TENSOR FUNCTIONS
 *****************************************************************************/

void tt_get_dims(
    FILE * fin,
    idx_t* const outnmodes,
    idx_t* const outnnz,
    idx_t* outdims,
    idx_t* offset);

void tt_get_dims_binary(
    FILE * fin,
    idx_t* const outnmodes,
    idx_t* const outnnz,
    idx_t* outdims);


sptensor_t * tt_read_file(
  char const * const fname);

sptensor_t * tt_read_binary_file(
  char const * const fname);

void tt_write_file(
  sptensor_t const * const tt,
  FILE * fout);

void tt_write_binary_file(
  sptensor_t const * const tt,
  FILE * fout);

void tt_write(
  sptensor_t const * const tt,
  char const * const fname);

void tt_write_binary(
  sptensor_t const * const tt,
  char const * const fname);


/******************************************************************************
 * DENSE MATRIX FUNCTIONS
 *****************************************************************************/
void mat_write(
  ordi_matrix const * const mat,
  char const * const fname);

void mat_write_file(
  ordi_matrix const * const mat,
  FILE * fout);

void vec_write(
  double const * const vec,
  idx_t const len,
  char const * const fname);

void vec_write_file(
  double const * const vec,
  idx_t const len,
  FILE * fout);


/******************************************************************************
 * SPARSE MATRIX FUNCTIONS
 *****************************************************************************/
void spmat_write(
  spordi_matrix const * const mat,
  char const * const fname);

void spmat_write_file(
  spordi_matrix const * const mat,
  FILE * fout);



#endif

