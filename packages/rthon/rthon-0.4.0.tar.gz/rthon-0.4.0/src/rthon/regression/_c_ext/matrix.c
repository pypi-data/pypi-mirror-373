#include "matrix.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

Matrix* matrix_alloc(int rows, int cols) {
    if (rows <= 0 || cols <= 0) {
        return NULL;
    }
    
    Matrix *mat = malloc(sizeof(Matrix));
    if (!mat) {
        return NULL;
    }
    
    mat->rows = rows;
    mat->cols = cols;
    
    mat->data = malloc(rows * sizeof(double*));
    if (!mat->data) {
        free(mat);
        return NULL;
    }
    
    for (int i = 0; i < rows; i++) {
        mat->data[i] = malloc(cols * sizeof(double));
        if (!mat->data[i]) {
            for (int j = 0; j < i; j++) {
                free(mat->data[j]);
            }
            free(mat->data);
            free(mat);
            return NULL;
        }
    }
    
    return mat;
}

void matrix_free(Matrix *mat) {
    if (!mat) return;
    
    if (mat->data) {
        for (int i = 0; i < mat->rows; i++) {
            free(mat->data[i]);
        }
        free(mat->data);
    }
    free(mat);
}

Matrix* matrix_copy(const Matrix *mat) {
    if (!matrix_is_valid(mat)) {
        return NULL;
    }
    
    Matrix *copy = matrix_alloc(mat->rows, mat->cols);
    if (!copy) {
        return NULL;
    }
    
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            copy->data[i][j] = mat->data[i][j];
        }
    }
    
    return copy;
}

Matrix* matrix_zeros(int rows, int cols) {
    Matrix *mat = matrix_alloc(rows, cols);
    if (!mat) {
        return NULL;
    }
    
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            mat->data[i][j] = 0.0;
        }
    }
    
    return mat;
}

Matrix* matrix_identity(int size) {
    Matrix *mat = matrix_zeros(size, size);
    if (!mat) {
        return NULL;
    }
    
    for (int i = 0; i < size; i++) {
        mat->data[i][i] = 1.0;
    }
    
    return mat;
}

Vector* vector_alloc(int length) {
    if (length <= 0) {
        return NULL;
    }
    
    Vector *vec = malloc(sizeof(Vector));
    if (!vec) {
        return NULL;
    }
    
    vec->length = length;
    vec->data = malloc(length * sizeof(double));
    if (!vec->data) {
        free(vec);
        return NULL;
    }
    
    return vec;
}

void vector_free(Vector *vec) {
    if (!vec) return;
    
    if (vec->data) {
        free(vec->data);
    }
    free(vec);
}

Vector* vector_copy(const Vector *vec) {
    if (!vector_is_valid(vec)) {
        return NULL;
    }
    
    Vector *copy = vector_alloc(vec->length);
    if (!copy) {
        return NULL;
    }
    
    for (int i = 0; i < vec->length; i++) {
        copy->data[i] = vec->data[i];
    }
    
    return copy;
}

Vector* vector_zeros(int length) {
    Vector *vec = vector_alloc(length);
    if (!vec) {
        return NULL;
    }
    
    for (int i = 0; i < length; i++) {
        vec->data[i] = 0.0;
    }
    
    return vec;
}

MatrixErrorCode matrix_multiply(const Matrix *A, const Matrix *B, Matrix *result) {
    if (!matrix_is_valid(A) || !matrix_is_valid(B) || !matrix_is_valid(result)) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    if (A->cols != B->rows) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    if (result->rows != A->rows || result->cols != B->cols) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < A->rows; i++) {
        for (int j = 0; j < B->cols; j++) {
            result->data[i][j] = 0.0;
            for (int k = 0; k < A->cols; k++) {
                result->data[i][j] += A->data[i][k] * B->data[k][j];
            }
        }
    }
    
    return MATRIX_SUCCESS;
}

MatrixErrorCode matrix_transpose(const Matrix *A, Matrix *result) {
    if (!matrix_is_valid(A) || !matrix_is_valid(result)) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    if (result->rows != A->cols || result->cols != A->rows) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < A->rows; i++) {
        for (int j = 0; j < A->cols; j++) {
            result->data[j][i] = A->data[i][j];
        }
    }
    
    return MATRIX_SUCCESS;
}

MatrixErrorCode matrix_vector_multiply(const Matrix *A, const Vector *x, Vector *result) {
    if (!matrix_is_valid(A) || !vector_is_valid(x) || !vector_is_valid(result)) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    if (A->cols != x->length) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    if (result->length != A->rows) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < A->rows; i++) {
        result->data[i] = 0.0;
        for (int j = 0; j < A->cols; j++) {
            result->data[i] += A->data[i][j] * x->data[j];
        }
    }
    
    return MATRIX_SUCCESS;
}

double vector_dot(const Vector *a, const Vector *b) {
    if (!vector_is_valid(a) || !vector_is_valid(b) || a->length != b->length) {
        return NAN;
    }
    
    double sum = 0.0;
    for (int i = 0; i < a->length; i++) {
        sum += a->data[i] * b->data[i];
    }
    
    return sum;
}

double vector_norm(const Vector *vec) {
    if (!vector_is_valid(vec)) {
        return NAN;
    }
    
    double sum = 0.0;
    for (int i = 0; i < vec->length; i++) {
        sum += vec->data[i] * vec->data[i];
    }
    
    return sqrt(sum);
}

MatrixErrorCode vector_subtract(const Vector *a, const Vector *b, Vector *result) {
    if (!vector_is_valid(a) || !vector_is_valid(b) || !vector_is_valid(result)) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    if (a->length != b->length || result->length != a->length) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < a->length; i++) {
        result->data[i] = a->data[i] - b->data[i];
    }
    
    return MATRIX_SUCCESS;
}

MatrixErrorCode vector_add(const Vector *a, const Vector *b, Vector *result) {
    if (!vector_is_valid(a) || !vector_is_valid(b) || !vector_is_valid(result)) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    if (a->length != b->length || result->length != a->length) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < a->length; i++) {
        result->data[i] = a->data[i] + b->data[i];
    }
    
    return MATRIX_SUCCESS;
}

MatrixErrorCode vector_scale(const Vector *vec, double scalar, Vector *result) {
    if (!vector_is_valid(vec) || !vector_is_valid(result)) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    if (result->length != vec->length) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < vec->length; i++) {
        result->data[i] = scalar * vec->data[i];
    }
    
    return MATRIX_SUCCESS;
}

bool matrix_is_valid(const Matrix *mat) {
    return mat != NULL && mat->data != NULL && mat->rows > 0 && mat->cols > 0;
}

bool vector_is_valid(const Vector *vec) {
    return vec != NULL && vec->data != NULL && vec->length > 0;
}

void matrix_print(const Matrix *mat) {
    if (!matrix_is_valid(mat)) {
        printf("Invalid matrix\n");
        return;
    }
    
    printf("Matrix %dx%d:\n", mat->rows, mat->cols);
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            printf("%10.6f ", mat->data[i][j]);
        }
        printf("\n");
    }
}

void vector_print(const Vector *vec) {
    if (!vector_is_valid(vec)) {
        printf("Invalid vector\n");
        return;
    }
    
    printf("Vector length %d:\n", vec->length);
    for (int i = 0; i < vec->length; i++) {
        printf("%10.6f ", vec->data[i]);
    }
    printf("\n");
}

LinearModelResult* linear_model_result_alloc(int n_obs, int n_params) {
    if (n_obs <= 0 || n_params <= 0) {
        return NULL;
    }
    
    LinearModelResult *result = malloc(sizeof(LinearModelResult));
    if (!result) {
        return NULL;
    }
    
    memset(result, 0, sizeof(LinearModelResult));
    
    result->coefficients.data = malloc(n_params * sizeof(double));
    result->residuals.data = malloc(n_obs * sizeof(double));
    result->fitted_values.data = malloc(n_obs * sizeof(double));
    result->standard_errors = malloc(n_params * sizeof(double));
    
    if (!result->coefficients.data || !result->residuals.data || 
        !result->fitted_values.data || !result->standard_errors) {
        linear_model_result_free(result);
        return NULL;
    }
    
    result->coefficients.length = n_params;
    result->residuals.length = n_obs;
    result->fitted_values.length = n_obs;
    
    result->covariance_matrix.rows = n_params;
    result->covariance_matrix.cols = n_params;
    result->covariance_matrix.data = malloc(n_params * sizeof(double*));
    if (!result->covariance_matrix.data) {
        linear_model_result_free(result);
        return NULL;
    }
    
    for (int i = 0; i < n_params; i++) {
        result->covariance_matrix.data[i] = malloc(n_params * sizeof(double));
        if (!result->covariance_matrix.data[i]) {
            for (int j = 0; j < i; j++) {
                free(result->covariance_matrix.data[j]);
            }
            free(result->covariance_matrix.data);
            linear_model_result_free(result);
            return NULL;
        }
        for (int j = 0; j < n_params; j++) {
            result->covariance_matrix.data[i][j] = 0.0;
        }
    }
    
    result->df_residual = n_obs - n_params;
    result->df_model = n_params - 1;
    
    return result;
}

void linear_model_result_free(LinearModelResult *result) {
    if (!result) return;
    
    if (result->coefficients.data) {
        free(result->coefficients.data);
    }
    if (result->residuals.data) {
        free(result->residuals.data);
    }
    if (result->fitted_values.data) {
        free(result->fitted_values.data);
    }
    if (result->standard_errors) {
        free(result->standard_errors);
    }
    
    if (result->covariance_matrix.data) {
        for (int i = 0; i < result->covariance_matrix.rows; i++) {
            free(result->covariance_matrix.data[i]);
        }
        free(result->covariance_matrix.data);
    }
    free(result);
}