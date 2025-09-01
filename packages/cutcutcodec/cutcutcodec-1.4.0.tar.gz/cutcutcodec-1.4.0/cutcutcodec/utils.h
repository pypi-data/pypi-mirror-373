/* Various C utils. */

#include <numpy/arrayobject.h>
#include <Python.h>


int parse_double_array(PyObject *obj, void *addr) {
  /* Convert a pyobject sequence into an array of double. */
  if (!PySequence_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "it is expected to be a sequence");
    return 0;
  }

  npy_intp dims[1] = {(npy_intp)PySequence_Length(obj)};
  PyArrayObject* array = (PyArrayObject *)PyArray_EMPTY(1, dims, NPY_DOUBLE, 0);
  if ( array == NULL ) {
    PyErr_NoMemory();
    return 0;
  }

  for ( npy_intp i = 0; i < PyArray_DIM(array, 0); ++i ) {
    PyObject *item = PySequence_GetItem(obj, (Py_ssize_t)i);
    *(double *)PyArray_GETPTR1(array, i) = PyFloat_AsDouble(item);  // try to convert in float
    if ( PyErr_Occurred() ) {
      Py_DECREF(array);
      return 0;
    }
    Py_DECREF(item);
  }

  *(PyArrayObject **)addr = array;
  return 1;
}
