#ifndef PYTHON_LM_H
#define PYTHON_LM_H

#include <Python.h>
#include "matrix.h"

typedef struct {
    PyObject_HEAD
    double *coefficients;
    double *fitted_values;
    double *residuals;
    double *standard_errors;
    double r_squared;
    double residual_std_error;
    double f_statistic;
    int n_obs;
    int n_params;
    int df_residual;
    int df_model;
    PyObject *column_names;
} PythonLMResult;

extern PyTypeObject PythonLMResultType;

PyObject* python_lm_matrix_interface(PyObject *X_list, PyObject *y_list);

PyObject* convert_list_to_matrix(PyObject *list_obj, Matrix **matrix);
PyObject* convert_list_to_vector(PyObject *list_obj, Vector **vector);
PyObject* convert_matrix_to_list(const Matrix *matrix);
PyObject* convert_vector_to_list(const Vector *vector);

#endif