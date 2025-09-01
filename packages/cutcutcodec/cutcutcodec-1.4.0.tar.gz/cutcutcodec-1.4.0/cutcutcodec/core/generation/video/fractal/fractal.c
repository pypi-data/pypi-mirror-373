/* Fast generation of fractal. */

#define PY_SSIZE_T_CLEAN
#include <numpy/arrayobject.h>
#include <omp.h>
#include <complex.h>
#include <Python.h>
#include "cutcutcodec/core/opti/parallel/threading.h"


float compute_mandelbrot_longdouble(
  long double cst_real,  // real part of the constant
  long double cst_imag,  // imag part of the constant
  const long int iter_max,  // maximum number of iterations
  const float inv_iter_max  // 1.0 / (float)iter_max
) {
  /*
    Compute the mathematical suite Zn+1 = Zn**2 + C, Z0 = 0.
    Return the divergence speed in [0, 1]
  */
  long int i;
  long double real, imag, real_square, imag_square;
  real = cst_real, imag = cst_imag;
  real_square = real*real, imag_square = imag*imag;
  for ( i = 0; i < iter_max && real_square + imag_square <= 4.0L; ++i ) {
    imag = 2.0L*real*imag + cst_imag;
    real = real_square - imag_square + cst_real;
    real_square = real*real, imag_square = imag*imag;
  }
  return (float)i * inv_iter_max;
}


float compute_mandelbrot_double(double cst_real, double cst_imag, const long int iter_max, const float inv_iter_max) {
  /* Same as compute_mandelbrot_longdouble for double. */
  long int i;
  long double real, imag, real_square, imag_square;
  { // simd
    real = cst_real, imag = cst_imag;
    real_square = real*real, imag_square = imag*imag;
  };
  for ( i = 0; i < iter_max && real_square + imag_square <= 4.0; ++i ) {
    imag = 2.0*real*imag + cst_imag;
    real = real_square - imag_square + cst_real;
    real_square = real*real, imag_square = imag*imag;  // simd
  }
  return (float)i * inv_iter_max;
}


int mandelbrot_converge_longdouble(const long double cst_real, const long double cst_imag) {
  /*
    Return 1 if the point is in the main carioid or in the main disque.
    Return 0 if we don't know.
  */
  long double imag_square;
  long double complex cst;

  // tests if c in circle of center -1, radius 1/4
  imag_square = cst_imag*cst_imag;
  if ( cst_real * (cst_real + 2.0L) + imag_square <= -0.9375L ) {  // (x+1)**2 + y**2 <= (1/4)**2
    return 1;
  }

  // Optional test to return faster, consits in bounding the cardioid with 2 circles.
  // The circle of center -1/4, radius 1/2 is contained in the cardioid.
  // For the second excluded, not yet implemented.
  if ( cst_real * (cst_real + 0.5L) + imag_square <= 0.1875L ) {  // (x+1/4)**2 + y**2 <= (1/2)**2
    return 1;
  }
  // |1 - sqrt(1 - 4*c)| <= 1
  cst = cst_real + cst_imag * I;
  cst *= -4.0L;
  cst += 1.0L;
  cst = csqrtl(cst);
  cst -= 1.0L;
  if ( creall(cst)*creall(cst) + cimagl(cst)*cimagl(cst) <= 1.0L ) {
    return 1;
  }
  return 0;
}


int mandelbrot_converge_double(const double cst_real, const double cst_imag) {
  /* Same as mandelbrot_converge_longdouble for double */
  double real_square, imag_square, cst_square_norm;
  double complex cst;
  real_square = cst_real*cst_real, imag_square = cst_imag*cst_imag;  // simd
  cst_square_norm = real_square + imag_square;
  if (  // group the tests for simd
    cst_square_norm + 2.0*cst_real <= -0.9375
    || cst_square_norm + 0.5*cst_real <= 0.1875
  ) {
    return 1;
  }
  cst = cst_real + cst_imag * I;
  cst *= -4.0;
  cst += 1.0;
  cst = csqrt(cst);
  cst -= 1.0;
  if ( creal(cst)*creal(cst) + cimag(cst)*cimag(cst) <= 1.0L ) {
    return 1;
  }
  return 0;
}


#pragma GCC optimize ("-fno-finite-math-only")
int isnan_longdouble(const long double x) {
  return isnan(x);
}


#pragma GCC optimize ("-fno-finite-math-only")
int isnan_double(const double x) {
  return isnan(x);
}


void iterate_mandelbrot_longdouble(
  PyArrayObject* fractal,  // the output float 32 fractal
  const PyArrayObject* cpx_plan,  // the initial complex values
  const long int iter_max,  // maximum number of iterations
  const int inper2  // true to perform prior test
) {
  /*
    Compute the mandelbrot suite for all pixels.
  */
  long int shape[2] = {(long int)PyArray_DIM(fractal, 0), (long int)PyArray_DIM(fractal, 1)};
  float inv_iter_max = 1.0f / (float)iter_max;
  #pragma omp parallel for schedule(dynamic)
  for ( long int i = 0; i < shape[0]; ++i ) {
    for ( long int j = 0; j < shape[1]; ++j ) {
      long double complex cst = *(long double complex *)PyArray_GETPTR2(cpx_plan, i, j);
      if ( isnan_longdouble(creall(cst)) ) continue;
      if ( inper2 && mandelbrot_converge_longdouble(creall(cst), cimagl(cst)) ) {
        *(float *)PyArray_GETPTR2(fractal, i, j) = 1.0L;
      } else {
        *(float *)PyArray_GETPTR2(fractal, i, j) = compute_mandelbrot_longdouble(
          creall(cst), cimagl(cst), iter_max, inv_iter_max
        );
      }
    }
  }
}


void iterate_mandelbrot_double(PyArrayObject* fractal, const PyArrayObject* cpx_plan, const long int iter_max, const int inper2) {
  long int shape[2] = {(long int)PyArray_DIM(fractal, 0), (long int)PyArray_DIM(fractal, 1)};
  float inv_iter_max = 1.0f / (float)iter_max;
  #pragma omp parallel for schedule(dynamic)
  for ( long int i = 0; i < shape[0]; ++i ) {
    for ( long int j = 0; j < shape[1]; ++j ) {
      double complex cst = *(double complex *)PyArray_GETPTR2(cpx_plan, i, j);
      if ( isnan_double(creal(cst)) ) continue;
      if ( inper2 && mandelbrot_converge_double(creal(cst), cimag(cst)) ) {
        *(float *)PyArray_GETPTR2(fractal, i, j) = 1.0;
      } else {
        *(float *)PyArray_GETPTR2(fractal, i, j) = compute_mandelbrot_double(
          creal(cst), cimag(cst), iter_max, inv_iter_max
        );
      }
    }
  }
}


void mandelbrot_longdouble(float* iters, long double* cst_reals, long double* cst_imags, const npy_intp dim, const long int iter_max) {
  npy_intp i, j;
  const float iter_max_float=(float)iter_max;
  #pragma omp parallel for schedule(dynamic)
  for ( i = 0; i < dim; ++i ) {
    long double real, imag, cst_real, cst_imag, real_square, imag_square;
    cst_real = cst_reals[i], cst_imag = cst_imags[i];
    real = cst_real, imag = cst_imag;
    real_square = real*real, imag_square = imag*imag;
    for ( j = 0; j < iter_max && real_square + imag_square <= 4.0L; ++j ) {
      imag = 2.0L*real*imag + cst_imag;
      real = real_square - imag_square + cst_real;
      real_square = real*real, imag_square = imag*imag;
    }
    iters[i] = (float)j / iter_max_float;
  }
}


void mandelbrot_double(float* iters, double* cst_reals, double* cst_imags, const npy_intp dim, const long int iter_max) {
  npy_intp i, j;
  const float iter_max_float=(float)iter_max;
  #pragma omp parallel for schedule(dynamic)
  for ( i = 0; i < dim; ++i ) {
    double real, imag, cst_real, cst_imag, real_square, imag_square;
    { // simd
      cst_real = cst_reals[i], cst_imag = cst_imags[i];
      real = cst_real, imag = cst_imag;
      real_square = real*real, imag_square = imag*imag;
    };
    for ( j = 0; j < iter_max && real_square + imag_square <= 4.0; ++j ) {
      imag = 2.0*real*imag + cst_imag;
      real = real_square - imag_square + cst_real;
      real_square = real*real, imag_square = imag*imag; // simd
    }
    iters[i] = (float)j / iter_max_float;
  }
}


static PyObject* py_mandelbrot(PyObject* Py_UNUSED(self), PyObject* args, PyObject* kwargs) {
  // declaration
  static char *kwlist[] = {"cpx_plan", "iterations", "inper2", "threads", "out", NULL};
  PyArrayObject *cpx_plan, *fractal = NULL;
  long int iterations = 256, threads = 0;
  int inper2 = 1;
  npy_intp shape[2];

  // parse and check
  if ( !PyArg_ParseTupleAndKeywords(
    args, kwargs, "O!|l$plO!", kwlist,
    &PyArray_Type, &cpx_plan, &iterations, &inper2, &threads, &PyArray_Type, &fractal
    )
  ) {
    return NULL;
  }
  if ( PyArray_NDIM(cpx_plan) != 2 ) {
    PyErr_SetString(PyExc_ValueError, "'cpx_plan' requires 2 dimensions");
    return NULL;
  }
  if ( iterations < 1 ) {
    PyErr_SetString(PyExc_ValueError, "'iteration' has to be >= 1");
    return NULL;
  }

  // set omp nbr threads
  set_num_threads(threads);

  // alloc fractal
  if ( fractal == NULL ) {
    shape[0] = PyArray_DIM(cpx_plan, 0), shape[1] = PyArray_DIM(cpx_plan, 1);
    fractal = (PyArrayObject *)PyArray_EMPTY(2, shape, NPY_FLOAT32, 0);
    if ( fractal == NULL ) {
      return PyErr_NoMemory();
    }
  } else {
    if ( PyArray_NDIM(fractal) != 2 ) {
      PyErr_SetString(PyExc_ValueError, "'out' requires 2 dimensions");
      return NULL;
    }
    if ( PyArray_DIM(cpx_plan, 0) != PyArray_DIM(fractal, 0) || PyArray_DIM(cpx_plan, 1) != PyArray_DIM(fractal, 1) ) {
      PyErr_SetString(PyExc_ValueError, "'out' has to be same shape as 'cpx_plan'");
      return NULL;
    }
    if ( PyArray_TYPE(fractal) != NPY_FLOAT32 ) {
      PyErr_SetString(PyExc_TypeError, "'out' must be of typs float32");
      return NULL;
    }
    Py_INCREF(fractal);
  }

  // compute suite
  switch ( PyArray_TYPE(cpx_plan) ) {
    case NPY_COMPLEX128:
      Py_BEGIN_ALLOW_THREADS
      iterate_mandelbrot_double(fractal, cpx_plan, iterations, inper2);
      Py_END_ALLOW_THREADS
      break;
    case NPY_COMPLEX256:
      Py_BEGIN_ALLOW_THREADS
      iterate_mandelbrot_longdouble(fractal, cpx_plan, iterations, inper2);
      Py_END_ALLOW_THREADS
      break;
    default:
      PyErr_SetString(PyExc_TypeError, "only the types complex128 and complex256 are accepted");
      Py_DECREF(fractal);
      return NULL;
  }

  // cast and return result
  return (PyObject *)fractal;
}


static PyMethodDef fractalMethods[] = {
  {
    "mandelbrot", (PyCFunction)py_mandelbrot, METH_VARARGS | METH_KEYWORDS,
    R"(Compute a mandelbrot grayscale image in C language.

    For each pixel, given by a complex point :math:`c`, compute :math:`n` iterations of the suite:

    .. math::

        \begin{cases}
            z_0 = 0 \\
            z_{n+1} = z_n^2 + c \\
        \end{cases}

    Parameters
    ----------
    cpx_plan : np.ndarray
        The 2d complex plane that associates the constant :math:`c` to each pixel.
        If the real part is ``nan``, The corresponding pixel will not be initialized.
        This array doesn't has to be c contiguous.
    iterations : int, default=256
        The maximum number of iterations before declaring that the sequence does not diverge.
        It must be >= 1 and <= 2147483647.
    inper2 : boolean, default=True
        If True (default), performs a test for each pixel to determine whether
        the pixel in question is in the cardioid or in the main disk.
        If False, calculates the sequence directly without prior testing.
    threads : int, optional
        Defines the number of threads.
        The value -1 means that the function uses as many calculation threads as there are cores.
        The default value (0) allows the same behavior as (-1) if the function
        is called in the main thread, otherwise (1) to avoid nested threads.
        Any other positive value corresponds to the number of threads used.
    out : np.ndarray[np.float32], optional
        If provided, set the result in this array and return it.
        This array doesn't has to be c contiguous.

    Returns
    -------
    fractal : np.ndarray[np.float32]
        The convergence speed of the suite in [0, 1].
        1 means it converges and 0 it diverges.
        The shape is the same as ``cpx_plan``.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.generation.video.fractal.fractal import mandelbrot
    >>> y, x = np.meshgrid(
    ...     np.linspace(1, -1, 2000, dtype=np.float128),  # imaginary part, -y axis
    ...     np.linspace(-2, 1, 3000, dtype=np.float128),  # real part, x axis
    ...     indexing="ij",
    ... )
    >>> cpx_plan = x + 1j*y
    >>> fractal = mandelbrot(cpx_plan)
    >>>
    )"
  },
  {NULL, NULL, 0, NULL}
};


static struct PyModuleDef fractal = {
  .m_base = PyModuleDef_HEAD_INIT,
  .m_name = "fractal",
  .m_doc = "This module, implemented in C, offers functions for calculating fractals.",
  .m_size = -1,
  .m_methods = fractalMethods,
  .m_slots = NULL,
  .m_traverse = NULL,
  .m_clear = NULL,
  .m_free = NULL,
};


PyMODINIT_FUNC PyInit_fractal(void)
{
  import_array();
  if ( PyErr_Occurred() ) {
    return NULL;
  }
  return PyModule_Create(&fractal);
}
