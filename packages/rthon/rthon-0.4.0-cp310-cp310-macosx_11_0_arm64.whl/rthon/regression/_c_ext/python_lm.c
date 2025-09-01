#include "python_lm.h"
#include "matrix.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double *coefficients;
    double *fitted_values;
    double *residuals;
    double r_squared;
    double residual_std_error;
    int n_obs;
    int n_params;
} CLMResult;

CLMResult* clm_result_alloc(int n_obs, int n_params) {
    CLMResult *result = malloc(sizeof(CLMResult));
    if (!result) return NULL;
    
    result->coefficients = malloc(n_params * sizeof(double));
    result->fitted_values = malloc(n_obs * sizeof(double));
    result->residuals = malloc(n_obs * sizeof(double));
    
    if (!result->coefficients || !result->fitted_values || !result->residuals) {
        free(result->coefficients);
        free(result->fitted_values);
        free(result->residuals);
        free(result);
        return NULL;
    }
    
    result->n_obs = n_obs;
    result->n_params = n_params;
    result->r_squared = 0.0;
    result->residual_std_error = 0.0;
    
    return result;
}

void clm_result_free(CLMResult *result) {
    if (!result) return;
    free(result->coefficients);
    free(result->fitted_values);
    free(result->residuals);
    free(result);
}

MatrixErrorCode gaussian_elimination(Matrix *A, Vector *b, Vector *x) {
    int n = A->rows;
    
    if (A->cols != n || b->length != n || x->length != n) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    for (int i = 0; i < n; i++) {
        int max_row = i;
        for (int k = i + 1; k < n; k++) {
            if (fabs(A->data[k][i]) > fabs(A->data[max_row][i])) {
                max_row = k;
            }
        }
        
        if (max_row != i) {
            for (int j = 0; j < n; j++) {
                double temp = A->data[i][j];
                A->data[i][j] = A->data[max_row][j];
                A->data[max_row][j] = temp;
            }
            double temp = b->data[i];
            b->data[i] = b->data[max_row];
            b->data[max_row] = temp;
        }
        
        if (fabs(A->data[i][i]) < 1e-12) {
            return MATRIX_ERROR_SINGULAR_MATRIX;
        }
        
        for (int k = i + 1; k < n; k++) {
            double factor = A->data[k][i] / A->data[i][i];
            for (int j = i; j < n; j++) {
                A->data[k][j] -= factor * A->data[i][j];
            }
            b->data[k] -= factor * b->data[i];
        }
    }
    
    for (int i = n - 1; i >= 0; i--) {
        x->data[i] = b->data[i];
        for (int j = i + 1; j < n; j++) {
            x->data[i] -= A->data[i][j] * x->data[j];
        }
        x->data[i] /= A->data[i][i];
    }
    
    return MATRIX_SUCCESS;
}

MatrixErrorCode c_linear_regression(const Matrix *X, const Vector *y, CLMResult *result) {
    if (!matrix_is_valid(X) || !vector_is_valid(y) || !result) {
        return MATRIX_ERROR_NULL_POINTER;
    }
    
    int n = X->rows;
    int p = X->cols;
    
    if (n != y->length || n <= p) {
        return MATRIX_ERROR_INVALID_DIMENSIONS;
    }
    
    Matrix *X_t = matrix_alloc(p, n);
    Matrix *X_t_X = matrix_alloc(p, p);
    Vector *X_t_y = vector_alloc(p);
    Vector *coefficients = vector_alloc(p);
    
    if (!X_t || !X_t_X || !X_t_y || !coefficients) {
        matrix_free(X_t);
        matrix_free(X_t_X);
        vector_free(X_t_y);
        vector_free(coefficients);
        return MATRIX_ERROR_MEMORY_ALLOCATION;
    }
    
    matrix_transpose(X, X_t);
    matrix_multiply(X_t, X, X_t_X);
    matrix_vector_multiply(X_t, y, X_t_y);
    
    MatrixErrorCode solve_result = gaussian_elimination(X_t_X, X_t_y, coefficients);
    
    if (solve_result != MATRIX_SUCCESS) {
        matrix_free(X_t);
        matrix_free(X_t_X);
        vector_free(X_t_y);
        vector_free(coefficients);
        return solve_result;
    }
    
    for (int i = 0; i < p; i++) {
        result->coefficients[i] = coefficients->data[i];
    }
    
    for (int i = 0; i < n; i++) {
        result->fitted_values[i] = 0.0;
        for (int j = 0; j < p; j++) {
            result->fitted_values[i] += X->data[i][j] * result->coefficients[j];
        }
        result->residuals[i] = y->data[i] - result->fitted_values[i];
    }
    
    double sum_y = 0.0;
    for (int i = 0; i < n; i++) {
        sum_y += y->data[i];
    }
    double mean_y = sum_y / n;
    
    double tss = 0.0;
    double rss = 0.0;
    for (int i = 0; i < n; i++) {
        tss += (y->data[i] - mean_y) * (y->data[i] - mean_y);
        rss += result->residuals[i] * result->residuals[i];
    }
    
    result->r_squared = 1.0 - (rss / tss);
    result->residual_std_error = sqrt(rss / (n - p));
    
    matrix_free(X_t);
    matrix_free(X_t_X);
    vector_free(X_t_y);
    vector_free(coefficients);
    
    return MATRIX_SUCCESS;
}

PyObject* convert_list_to_matrix(PyObject *list_obj, Matrix **matrix) {
    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list for matrix");
        return NULL;
    }
    
    Py_ssize_t rows = PyList_Size(list_obj);
    if (rows == 0) {
        PyErr_SetString(PyExc_ValueError, "Matrix cannot be empty");
        return NULL;
    }
    
    PyObject *first_row = PyList_GetItem(list_obj, 0);
    if (!PyList_Check(first_row)) {
        PyErr_SetString(PyExc_TypeError, "Expected matrix to be list of lists");
        return NULL;
    }
    
    Py_ssize_t cols = PyList_Size(first_row);
    if (cols == 0) {
        PyErr_SetString(PyExc_ValueError, "Matrix rows cannot be empty");
        return NULL;
    }
    
    *matrix = matrix_alloc((int)rows, (int)cols);
    if (!*matrix) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate matrix");
        return NULL;
    }
    
    for (Py_ssize_t i = 0; i < rows; i++) {
        PyObject *row = PyList_GetItem(list_obj, i);
        if (!PyList_Check(row) || PyList_Size(row) != cols) {
            matrix_free(*matrix);
            PyErr_SetString(PyExc_ValueError, "All matrix rows must have same length");
            return NULL;
        }
        
        for (Py_ssize_t j = 0; j < cols; j++) {
            PyObject *item = PyList_GetItem(row, j);
            if (!PyFloat_Check(item) && !PyLong_Check(item)) {
                matrix_free(*matrix);
                PyErr_SetString(PyExc_TypeError, "Matrix elements must be numbers");
                return NULL;
            }
            (*matrix)->data[i][j] = PyFloat_AsDouble(item);
        }
    }
    
    Py_RETURN_NONE;
}

PyObject* convert_list_to_vector(PyObject *list_obj, Vector **vector) {
    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list for vector");
        return NULL;
    }
    
    Py_ssize_t length = PyList_Size(list_obj);
    if (length == 0) {
        PyErr_SetString(PyExc_ValueError, "Vector cannot be empty");
        return NULL;
    }
    
    *vector = vector_alloc((int)length);
    if (!*vector) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate vector");
        return NULL;
    }
    
    for (Py_ssize_t i = 0; i < length; i++) {
        PyObject *item = PyList_GetItem(list_obj, i);
        if (!PyFloat_Check(item) && !PyLong_Check(item)) {
            vector_free(*vector);
            PyErr_SetString(PyExc_TypeError, "Vector elements must be numbers");
            return NULL;
        }
        (*vector)->data[i] = PyFloat_AsDouble(item);
    }
    
    Py_RETURN_NONE;
}

static void PythonLMResult_dealloc(PythonLMResult *self) {
    free(self->coefficients);
    free(self->fitted_values);
    free(self->residuals);
    free(self->standard_errors);
    Py_XDECREF(self->column_names);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject* PythonLMResult_get_coefficients(PythonLMResult *self, void *closure) {
    PyObject *list = PyList_New(self->n_params);
    for (int i = 0; i < self->n_params; i++) {
        PyList_SetItem(list, i, PyFloat_FromDouble(self->coefficients[i]));
    }
    return list;
}

static PyObject* PythonLMResult_get_fitted_values(PythonLMResult *self, void *closure) {
    PyObject *list = PyList_New(self->n_obs);
    for (int i = 0; i < self->n_obs; i++) {
        PyList_SetItem(list, i, PyFloat_FromDouble(self->fitted_values[i]));
    }
    return list;
}

static PyObject* PythonLMResult_get_residuals(PythonLMResult *self, void *closure) {
    PyObject *list = PyList_New(self->n_obs);
    for (int i = 0; i < self->n_obs; i++) {
        PyList_SetItem(list, i, PyFloat_FromDouble(self->residuals[i]));
    }
    return list;
}

static PyObject* PythonLMResult_get_r_squared(PythonLMResult *self, void *closure) {
    return PyFloat_FromDouble(self->r_squared);
}

static PyObject* PythonLMResult_get_residual_std_error(PythonLMResult *self, void *closure) {
    return PyFloat_FromDouble(self->residual_std_error);
}

static PyGetSetDef PythonLMResult_getsetters[] = {
    {"coefficients", (getter)PythonLMResult_get_coefficients, NULL, "Regression coefficients", NULL},
    {"fitted_values", (getter)PythonLMResult_get_fitted_values, NULL, "Fitted values", NULL},
    {"residuals", (getter)PythonLMResult_get_residuals, NULL, "Residuals", NULL},
    {"r_squared", (getter)PythonLMResult_get_r_squared, NULL, "R-squared", NULL},
    {"residual_std_error", (getter)PythonLMResult_get_residual_std_error, NULL, "Residual standard error", NULL},
    {NULL}
};

PyTypeObject PythonLMResultType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "rthon.regression._c_ext.LinearModelResult",
    .tp_doc = "Linear model result from C implementation",
    .tp_basicsize = sizeof(PythonLMResult),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor) PythonLMResult_dealloc,
    .tp_getset = PythonLMResult_getsetters,
};

PyObject* python_lm_matrix_interface(PyObject *X_list, PyObject *y_list) {
    Matrix *X = NULL;
    Vector *y = NULL;
    CLMResult *result = NULL;
    
    if (convert_list_to_matrix(X_list, &X) == NULL) {
        return NULL;
    }
    
    if (convert_list_to_vector(y_list, &y) == NULL) {
        matrix_free(X);
        return NULL;
    }
    
    result = clm_result_alloc(X->rows, X->cols);
    if (!result) {
        matrix_free(X);
        vector_free(y);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result");
        return NULL;
    }
    
    MatrixErrorCode error = c_linear_regression(X, y, result);
    
    if (error != MATRIX_SUCCESS) {
        matrix_free(X);
        vector_free(y);
        clm_result_free(result);
        
        switch (error) {
            case MATRIX_ERROR_INVALID_DIMENSIONS:
                PyErr_SetString(PyExc_ValueError, "Invalid matrix dimensions");
                break;
            case MATRIX_ERROR_SINGULAR_MATRIX:
                PyErr_SetString(PyExc_ValueError, "Matrix is singular");
                break;
            case MATRIX_ERROR_MEMORY_ALLOCATION:
                PyErr_SetString(PyExc_MemoryError, "Memory allocation failed");
                break;
            default:
                PyErr_SetString(PyExc_RuntimeError, "Unknown error in linear regression");
                break;
        }
        return NULL;
    }
    
    PythonLMResult *py_result = (PythonLMResult *)PyObject_New(PythonLMResult, &PythonLMResultType);
    if (!py_result) {
        matrix_free(X);
        vector_free(y);
        clm_result_free(result);
        return NULL;
    }
    
    py_result->coefficients = result->coefficients;
    py_result->fitted_values = result->fitted_values;
    py_result->residuals = result->residuals;
    py_result->standard_errors = NULL;
    py_result->r_squared = result->r_squared;
    py_result->residual_std_error = result->residual_std_error;
    py_result->f_statistic = 0.0;
    py_result->n_obs = result->n_obs;
    py_result->n_params = result->n_params;
    py_result->df_residual = result->n_obs - result->n_params;
    py_result->df_model = result->n_params - 1;
    py_result->column_names = Py_None;
    Py_INCREF(Py_None);
    
    free(result);
    matrix_free(X);
    vector_free(y);
    
    return (PyObject *)py_result;
}

static PyObject* clinalg_lm(PyObject *self, PyObject *args) {
    PyObject *X_list, *y_list;
    
    if (!PyArg_ParseTuple(args, "OO", &X_list, &y_list)) {
        return NULL;
    }
    
    return python_lm_matrix_interface(X_list, y_list);
}

static PyMethodDef rthon_regression_c_methods[] = {
    {"lm", clinalg_lm, METH_VARARGS, "Linear regression using C implementation"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef rthon_regression_c_module = {
    PyModuleDef_HEAD_INIT,
    "rthon.regression._c_ext",
    "C-based linear algebra for regression",
    -1,
    rthon_regression_c_methods
};

PyMODINIT_FUNC PyInit__c_ext(void) {
    PyObject *m;
    
    if (PyType_Ready(&PythonLMResultType) < 0)
        return NULL;
    
    m = PyModule_Create(&rthon_regression_c_module);
    if (m == NULL)
        return NULL;
    
    Py_INCREF(&PythonLMResultType);
    if (PyModule_AddObject(m, "LinearModelResult", (PyObject *) &PythonLMResultType) < 0) {
        Py_DECREF(&PythonLMResultType);
        Py_DECREF(m);
        return NULL;
    }
    
    return m;
}