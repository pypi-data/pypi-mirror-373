#ifndef MATRIX_H
#define MATRIX_H

#include <stddef.h>
#include <stdbool.h>

typedef struct {
    double **data;
    int rows;
    int cols;
} Matrix;

typedef struct {
    double *data;
    int length;
} Vector;

typedef struct {
    Vector coefficients;
    Vector residuals;
    Vector fitted_values;
    double r_squared;
    double residual_std_error;
    double *standard_errors;
    Matrix covariance_matrix;
    int df_residual;
    int df_model;
    double f_statistic;
    double f_pvalue;
} LinearModelResult;

typedef enum {
    MATRIX_SUCCESS = 0,
    MATRIX_ERROR_NULL_POINTER = 1,
    MATRIX_ERROR_INVALID_DIMENSIONS = 2,
    MATRIX_ERROR_MEMORY_ALLOCATION = 3,
    MATRIX_ERROR_SINGULAR_MATRIX = 4,
    MATRIX_ERROR_RANK_DEFICIENT = 5
} MatrixErrorCode;

Matrix* matrix_alloc(int rows, int cols);
void matrix_free(Matrix *mat);
Matrix* matrix_copy(const Matrix *mat);
Matrix* matrix_zeros(int rows, int cols);
Matrix* matrix_identity(int size);

Vector* vector_alloc(int length);
void vector_free(Vector *vec);
Vector* vector_copy(const Vector *vec);
Vector* vector_zeros(int length);

MatrixErrorCode matrix_multiply(const Matrix *A, const Matrix *B, Matrix *result);
MatrixErrorCode matrix_transpose(const Matrix *A, Matrix *result);
MatrixErrorCode matrix_vector_multiply(const Matrix *A, const Vector *x, Vector *result);

double vector_dot(const Vector *a, const Vector *b);
double vector_norm(const Vector *vec);
MatrixErrorCode vector_subtract(const Vector *a, const Vector *b, Vector *result);
MatrixErrorCode vector_add(const Vector *a, const Vector *b, Vector *result);
MatrixErrorCode vector_scale(const Vector *vec, double scalar, Vector *result);

bool matrix_is_valid(const Matrix *mat);
bool vector_is_valid(const Vector *vec);
void matrix_print(const Matrix *mat);
void vector_print(const Vector *vec);

LinearModelResult* linear_model_result_alloc(int n_obs, int n_params);
void linear_model_result_free(LinearModelResult *result);

#endif