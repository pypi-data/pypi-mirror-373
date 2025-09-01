/* Fast image metric. */

#define PY_SSIZE_T_CLEAN
#include <complex.h>
#include <math.h>
#include <numpy/arrayobject.h>
#include <omp.h>
#include <Python.h>
#include "cutcutcodec/core/opti/parallel/threading.h"
#include "cutcutcodec/utils.h"


int compute_psnr_float32(
  double* psnr,
  PyArrayObject* im1,
  PyArrayObject* im2,
  PyArrayObject* weights,
  long int threads
) {
  /* Compute the mse for each channel, return the ponderated average. */
  // allocation, precasting
  float mse = 0.0;  // we can not declare *mse in reduction
  float *weights_f32 = malloc(PyArray_DIM(weights, 0) * sizeof(float));
  if ( weights_f32 == NULL ) {
    return EXIT_FAILURE;
  }
  for ( npy_intp k = 0; k < PyArray_DIM(weights, 0); ++k) {
    weights_f32[k] = (float)(*(double *)PyArray_GETPTR1(weights, k));
  }

  // compute mse
  switch ( PyArray_DIM(im1, 2) ) {
    case 1:  // classical case to reduce overhead
      #pragma omp parallel for schedule(static) reduction(+:mse) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(im1, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(im1, 1); ++j ) {
          float diff = *(float *)PyArray_GETPTR3(im1, i, j, 0) - *(float *)PyArray_GETPTR3(im2, i, j, 0);
          mse += diff * diff * weights_f32[0];  // critical for thread safe
        }
      }
      break;
    case 3:  // classical case to reduce overhead
      #pragma omp parallel for schedule(static) reduction(+:mse) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(im1, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(im1, 1); ++j ) {
          for ( npy_intp k = 0; k < 3; ++k ) {
            float diff = *(float *)PyArray_GETPTR3(im1, i, j, k) - *(float *)PyArray_GETPTR3(im2, i, j, k);
            mse += diff * diff * weights_f32[k];  // critical for thread safe
          }
        }
      }
      break;
    default:
      #pragma omp parallel for schedule(static) collapse(2) reduction(+:mse) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(im1, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(im1, 1); ++j ) {
          for ( npy_intp k = 0; k < PyArray_DIM(im1, 2); ++k ) {
            float diff = *(float *)PyArray_GETPTR3(im1, i, j, k) - *(float *)PyArray_GETPTR3(im2, i, j, k);
            mse += diff * diff * weights_f32[k];  // critical for thread safe
          }
        }
      }

  }

  // compute psnr
  free(weights_f32);
  mse /= (float)PyArray_DIM(im1, 0) * (float)PyArray_DIM(im1, 1);
  *psnr = mse > 1.0e-10 ? -10.0*log10((double)mse) : 100.0;
  return EXIT_SUCCESS;
}


int compute_psnr_float64(
  double* psnr,
  PyArrayObject* im1,
  PyArrayObject* im2,
  PyArrayObject* weights,
  long int threads
) {
  /* Compute the mse for each channel, return the ponderated average. */
  double mse = 0.0;  // we can not declare *mse in reduction

  // compute mse
  switch ( PyArray_DIM(im1, 2) ) {
    case 1:  // classical case to reduce overhead
      #pragma omp parallel for schedule(static) reduction(+:mse) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(im1, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(im1, 1); ++j ) {
          double diff = *(double *)PyArray_GETPTR3(im1, i, j, 0) - *(double *)PyArray_GETPTR3(im2, i, j, 0);
          mse += diff * diff * (*(double *)PyArray_GETPTR1(weights, 0));  // critical for thread safe
        }
      }
      break;
    case 3:  // classical case to reduce overhead
      #pragma omp parallel for schedule(static) reduction(+:mse) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(im1, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(im1, 1); ++j ) {
          for ( npy_intp k = 0; k < 3; ++k ) {
            double diff = *(double *)PyArray_GETPTR3(im1, i, j, k) - *(double *)PyArray_GETPTR3(im2, i, j, k);
            mse += diff * diff * (*(double *)PyArray_GETPTR1(weights, k));  // critical for thread safe
          }
        }
      }
      break;
    default:
      #pragma omp parallel for schedule(static) collapse(2) reduction(+:mse) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(im1, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(im1, 1); ++j ) {
          for ( npy_intp k = 0; k < PyArray_DIM(im1, 2); ++k ) {
            double diff = *(double *)PyArray_GETPTR3(im1, i, j, k) - *(double *)PyArray_GETPTR3(im2, i, j, k);
            mse += diff * diff * (*(double *)PyArray_GETPTR1(weights, k));  // critical for thread safe
          }
        }
      }

  }

  // compute psnr
  mse /= (double)PyArray_DIM(im1, 0) * (double)PyArray_DIM(im1, 1);
  *psnr = mse > 1.0e-10 ? -10.0*log10(mse) : 100.0;
  return EXIT_SUCCESS;
}


PyArrayObject* gauss_kernel(npy_intp radius, double sigma) {
  /* Create a 2d gaussian kernel. */
  npy_intp shape[2] = {2*radius + 1, 2*radius + 1};
  PyArrayObject* gauss2d;
  double* gauss1d;
  double sum, buff;
  // verifiactions
  if ( radius < 1 ) {
    PyErr_SetString(PyExc_ValueError, "the gaussian radius must be >= 1");
    return NULL;
  }
  if ( sigma <= 0.0 ) {
    PyErr_SetString(PyExc_ValueError, "the variance has to be strictely positive");
    return NULL;
  }
  // allocations
  gauss1d = (double *)malloc((2 * radius + 1) * sizeof(double));
  if ( gauss1d == NULL ) {
    PyErr_NoMemory();
    return NULL;
  }
  gauss2d = (PyArrayObject *)PyArray_EMPTY(2, shape, NPY_DOUBLE, 0);
  if ( gauss2d == NULL ) {
    free(gauss1d);
    PyErr_NoMemory();
    return NULL;
  }

  // compute gaussian
  Py_BEGIN_ALLOW_THREADS
  buff = -1.0 / (2.0 * sigma * sigma);
  #pragma omp simd
  for ( npy_intp i = 1; i < radius + 1; ++i ) {  // compute gaussian 1d
    gauss1d[radius-i] = gauss1d[radius+i] = exp((double)(i*i) * buff);
  }
  gauss1d[radius] = 1.0;
  sum = 0.0;  // compute gaussian 2d
  #pragma omp simd collapse(2) reduction(+:sum)
  for ( npy_intp i = 0; i < shape[0]; ++i ) {
    for ( npy_intp j = 0; j < shape[0]; ++j ) {
      buff = gauss1d[i] * gauss1d[j];
      *(double *)PyArray_GETPTR2(gauss2d, i, j) = buff;
      sum += buff;
    }
  }
  sum = 1.0 / sum;  // normalise
  #pragma omp simd collapse(2)
  for ( npy_intp i = 0; i < shape[0]; ++i ) {
    for ( npy_intp j = 0; j < shape[0]; ++j ) {
      *(double *)PyArray_GETPTR2(gauss2d, i, j) *= sum;
    }
  }
  free(gauss1d);
  Py_END_ALLOW_THREADS
  return gauss2d;
}


int compute_ssim_float32(
  double* ssim,
  PyArrayObject* im1,  // float32
  PyArrayObject* im2,  // float32
  PyArrayObject* weights,  // double
  PyArrayObject* kernel,  // double
  double data_range,
  long int stride,
  long int threads
) {
  /*
    100% pure C fonction to compute ssim.
    Assumptions:
      The kernel is symetric
      The kernel is square
      The kernel has odd shape
      The sum of the kernel coefs is 1
      The image shape is bigger than the kernel shape
  */
  npy_intp kernel_size = PyArray_DIM(kernel, 0);
  npy_intp radius = kernel_size / 2;  // rigorously (s - 1) / 2
  double local_ssim = 0.0;
  float c1 = 0.01 * (float)data_range, c2 = 0.03 * (float)data_range;
  c1 *= c1, c2 *= c2;

  // copy kernel weights to cast only once
  float* weights_data = malloc(kernel_size * kernel_size * sizeof(float));
  if ( weights_data == NULL ) {
    return EXIT_FAILURE;
  }
  for ( npy_intp i = 0; i < kernel_size; ++i ) {
    #pragma GCC ivdep
    for ( npy_intp j = 0; j < kernel_size; ++j ) {
      weights_data[j + i*kernel_size] = (float)(*(double *)PyArray_GETPTR2(kernel, i, j));
    }
  }

  // iterate on the patch center position
  #pragma omp parallel for schedule(static) collapse(2) reduction(+:local_ssim) num_threads(threads)
  for ( npy_intp i0 = radius; i0 < PyArray_DIM(im1, 0)-radius; i0 += stride ) {
  for ( npy_intp j0 = radius; j0 < PyArray_DIM(im1, 1)-radius; j0 += stride ) {
    npy_intp shift[2] = {i0-radius, j0-radius};
    for ( npy_intp k = 0; k < PyArray_DIM(im1, 2); ++k ) {  // repeat on each channel
      // iterate within each patch
      float mu1 = 0.0, mu2 = 0.0, s12 = 0.0, s11 = 0.0, s22 = 0.0;
      float patch_ssim, m11, m22, m12;
      for ( npy_intp i = 0; i < kernel_size; ++i ) {
        for ( npy_intp j = 0; j < kernel_size; ++j ) {
          npy_intp i_im = i + shift[0], j_im = j + shift[1];
          float x1, x2, x1w, x2w, weight;
          weight = weights_data[j + i * kernel_size];
          x1 = *(float *)PyArray_GETPTR3(im1, i_im, j_im, k),
          x2 = *(float *)PyArray_GETPTR3(im2, i_im, j_im, k);
          x1w = x1 * weight, x2w = x2 * weight;
          mu1 += x1w, mu2 += x2w;
          s11 += x1 * x1w, s22 += x2 * x2w, s12 += x1 * x2w;
        }
      }
      m11 = mu1 * mu1, m22 = mu2 * mu2, m12 = mu1 * mu2;
      s11 -= m11, s22 -= m22, s12 -= m12;
      patch_ssim = (  // the ssim of the patch
        (2.0 * m12 + c1) * (2.0 * s12 + c2)
      ) / (
        (m11 + m22 + c1) * (s11 + s22 + c2)
      );
      patch_ssim *= (float)(*(double *)PyArray_GETPTR1(weights, k));  // normalise by the channel weight
      local_ssim += (double)patch_ssim;
    }
  }}
  free(weights_data);
  local_ssim /= (double)(
    (1 + (PyArray_DIM(im1, 0) - 2*radius - 1) / stride) * (1 + (PyArray_DIM(im1, 1) - 2*radius - 1) / stride)
  );
  *ssim = local_ssim;
  return EXIT_SUCCESS;
}


int compute_ssim_float64(
  double* ssim,
  PyArrayObject* im1,  // double
  PyArrayObject* im2,  // double
  PyArrayObject* weights,  // double
  PyArrayObject* kernel,  // double
  double data_range,
  long int stride,
  long int threads
) {
  /*
    100% pure C fonction to compute ssim.
    Assumptions:
      The kernel is symetric
      The kernel is square
      The kernel has odd shape
      The sum of the kernel coefs is 1
      The image shape is bigger than the kernel shape
  */
  npy_intp radius = PyArray_DIM(kernel, 0) / 2;  // rigorously (s - 1) / 2
  double local_ssim = 0.0;
  double c1 = 0.01 * data_range, c2 = 0.03 * data_range;
  c1 *= c1, c2 *= c2;
  // iterate on the patch center position
  long int count = 0;
  #pragma omp parallel for schedule(static) collapse(2) reduction(+:local_ssim) num_threads(threads)
  for ( npy_intp i0 = radius; i0 < PyArray_DIM(im1, 0)-radius; i0 += stride ) {
  for ( npy_intp j0 = radius; j0 < PyArray_DIM(im1, 1)-radius; j0 += stride ) {
    npy_intp shift[2] = {i0-radius, j0-radius};
    ++count;
    for ( npy_intp k = 0; k < PyArray_DIM(im1, 2); ++k ) {  // repeat on each channel
      double mu1 = 0.0, mu2 = 0.0, s11 = 0.0, s22 = 0.0, s12 = 0.0;
      float patch_ssim, m11, m22, m12, weight;
      for ( npy_intp i = 0; i < PyArray_DIM(kernel, 0); ++i ) {
      for ( npy_intp j = 0; j < PyArray_DIM(kernel, 1); ++j ) {
        float x1, x2, x1w, x2w;
        weight = *(double *)PyArray_GETPTR2(kernel, i, j);
        x1 = *(double *)PyArray_GETPTR3(im1, i+shift[0], j+shift[1], k),
        x2 = *(double *)PyArray_GETPTR3(im2, i+shift[0], j+shift[1], k);
        x1w = x1 * weight, x2w = x2 * weight;
        mu1 += x1w, mu2 += x2w;
        s11 += x1 * x1w, s22 += x2 * x2w, s12 += x1 * x2w;
      }}
      m11 = mu1 * mu1, m22 = mu2 * mu2, m12 = mu1 * mu2;
      s11 -= m11, s22 -= m22, s12 -= m12;
      patch_ssim = (
        (2.0 * mu1 * mu2 + c1) * (2.0 * s12 + c2)
      ) / (
        (mu1 * mu1 + mu2 * mu2 + c1) * (s11 + s22 + c2)
      );
      patch_ssim *= *(double *)PyArray_GETPTR1(weights, k);
      local_ssim += patch_ssim;
    }
  }}
  local_ssim /= (double)(
    (1 + (PyArray_DIM(im1, 0) - 2*radius - 1) / stride) * (1 + (PyArray_DIM(im1, 1) - 2*radius - 1) / stride)
  );
  *ssim = local_ssim;
  return EXIT_SUCCESS;
}


static PyObject* py_ssim(PyObject* Py_UNUSED(self), PyObject* args, PyObject* kwargs) {
  // declaration
  static char *kwlist[] = {"im1", "im2", "data_range", "weights", "sigma", "stride", "threads", NULL};
  PyArrayObject *im1, *im2, *weights = NULL;
  double ssim, data_range = 1.0, sigma = 1.5;
  long int stride = 1, threads = 0;
  int error = EXIT_SUCCESS;

  // parse and check
  if ( !PyArg_ParseTupleAndKeywords(
    args, kwargs, "O!O!|dO&d$ll", kwlist,
    &PyArray_Type, &im1, &PyArray_Type, &im2, &data_range, &parse_double_array, &weights, &sigma, &stride, &threads
    )
  ) {
    return NULL;
  }
  if ( PyArray_NDIM(im1) != 3 ) {
    PyErr_SetString(PyExc_ValueError, "'im1' requires 3 dimensions");
    return NULL;
  }
  if ( PyArray_NDIM(im2) != 3 ) {
    PyErr_SetString(PyExc_ValueError, "'im2' requires 3 dimensions");
    return NULL;
  }
  if ( PyArray_DIM(im1, 0) != PyArray_DIM(im2, 0) ) {
    PyErr_SetString(PyExc_ValueError, "'im1' and 'im2' must have the same height");
    return NULL;
  }
  if ( PyArray_DIM(im1, 1) != PyArray_DIM(im2, 1) ) {
    PyErr_SetString(PyExc_ValueError, "'im1' and 'im2' must have the same width");
    return NULL;
  }
  if ( PyArray_DIM(im1, 2) != PyArray_DIM(im2, 2) ) {
    PyErr_SetString(PyExc_ValueError, "'im1' and 'im2' must have the same channels");
    return NULL;
  }
  if ( PyArray_TYPE(im1) != PyArray_TYPE(im2) ) {
    PyErr_SetString(PyExc_TypeError, "'im1' and 'im2' are not the same type");
    return NULL;
  }
  if ( data_range <= 0.0 ) {
    PyErr_SetString(PyExc_ValueError, "'data_range' must be > 0");
    return NULL;
  }
  if ( stride <= 0 ) {
    PyErr_SetString(PyExc_ValueError, "'stride' must be >= 1");
    return NULL;
  }

  // default values
  if ( weights == NULL ) {
    npy_intp dims[1] = {PyArray_DIM(im1, 2)};
    weights = (PyArrayObject *)PyArray_EMPTY(1, dims, NPY_DOUBLE, 0);
    if ( weights == NULL ) {
      PyErr_NoMemory();
      return NULL;
    }
    #pragma omp simd
    for ( npy_intp i = 0; i < PyArray_DIM(weights, 0); ++i ) {
      *(double *)PyArray_GETPTR1(weights, i) = 1.0;
    }
  } else if ( PyArray_DIM(weights, 0) != PyArray_DIM(im1, 2) ) {
    PyErr_SetString(PyExc_ValueError, "the length of weights must match the number of channels");
    return NULL;
  }

  // get omp nbr threads
  threads = get_num_threads(threads);

  // normalise weights
  ssim = 0.0;
  for ( npy_intp i = 0; i < PyArray_DIM(weights, 0); ++i ) {
    ssim += *(double *)PyArray_GETPTR1(weights, i);
  }
  for ( npy_intp i = 0; i < PyArray_DIM(weights, 0); ++i ) {
    *(double *)PyArray_GETPTR1(weights, i) /= ssim;
  }

  // get gaussian kernel
  npy_intp radius = (npy_intp)(3.5 * sigma + 0.5);
  PyArrayObject* kernel = gauss_kernel(radius, sigma);  // radius sigma
  if ( kernel == NULL ) {
    Py_DECREF(weights);
    return NULL;
  }
  if ( PyArray_DIM(kernel, 0) > PyArray_DIM(im1, 0) || PyArray_DIM(kernel, 1) > PyArray_DIM(im1, 1) ) {
    PyErr_SetString(PyExc_ValueError, "sigma is to big for the image size");
    Py_DECREF(weights);
    Py_DECREF(kernel);
    return NULL;
  }

  // compute ssim
  switch ( PyArray_TYPE(im1) ) {
    case NPY_FLOAT32:
      Py_BEGIN_ALLOW_THREADS
      error = compute_ssim_float32(&ssim, im1, im2, weights, kernel, data_range, stride, threads);
      Py_END_ALLOW_THREADS
      break;
    case NPY_DOUBLE:
      Py_BEGIN_ALLOW_THREADS
      error = compute_ssim_float64(&ssim, im1, im2, weights, kernel, data_range, stride, threads);
      Py_END_ALLOW_THREADS
      break;
    default:
      PyErr_SetString(PyExc_TypeError, "only the types float32 and float64 are accepted");
      error = EXIT_FAILURE;
  }
  Py_DECREF(weights);
  Py_DECREF(kernel);

  // return and manage error
  if ( error == EXIT_FAILURE ) {
    if ( !PyErr_Occurred() ) {
      PyErr_NoMemory();
    }
    return NULL;
  }
  return Py_BuildValue("d", ssim);
}


static PyObject* py_psnr(PyObject* Py_UNUSED(self), PyObject* args, PyObject* kwargs) {
  // declaration
  static char *kwlist[] = {"im1", "im2", "weights", "threads", NULL};
  PyArrayObject *im1, *im2, *weights = NULL;
  double psnr;
  long int threads = 0;
  int error = EXIT_SUCCESS;

  // parse and check
  if ( !PyArg_ParseTupleAndKeywords(
    args, kwargs, "O!O!|O&$l", kwlist,
    &PyArray_Type, &im1, &PyArray_Type, &im2, &parse_double_array, &weights, &threads
    )
  ) {
    return NULL;
  }
  if ( PyArray_NDIM(im1) != 3 ) {
    PyErr_SetString(PyExc_ValueError, "'im1' requires 3 dimensions");
    return NULL;
  }
  if ( PyArray_NDIM(im2) != 3 ) {
    PyErr_SetString(PyExc_ValueError, "'im2' requires 3 dimensions");
    return NULL;
  }
  if ( PyArray_DIM(im1, 0) != PyArray_DIM(im2, 0) ) {
    PyErr_SetString(PyExc_ValueError, "'im1' and 'im2' must have the same height");
    return NULL;
  }
  if ( PyArray_DIM(im1, 1) != PyArray_DIM(im2, 1) ) {
    PyErr_SetString(PyExc_ValueError, "'im1' and 'im2' must have the same width");
    return NULL;
  }
  if ( PyArray_DIM(im1, 2) != PyArray_DIM(im2, 2) ) {
    PyErr_SetString(PyExc_ValueError, "'im1' and 'im2' must have the same channels");
    return NULL;
  }
  if ( PyArray_TYPE(im1) != PyArray_TYPE(im2) ) {
    PyErr_SetString(PyExc_TypeError, "'im1' and 'im2' are not the same type");
    return NULL;
  }

  // default values
  if ( weights == NULL ) {
    npy_intp dims[1] = {PyArray_DIM(im1, 2)};
    weights = (PyArrayObject *)PyArray_EMPTY(1, dims, NPY_DOUBLE, 0);
    if ( weights == NULL ) {
      PyErr_NoMemory();
      return NULL;
    }
    #pragma omp simd
    for ( npy_intp i = 0; i < PyArray_DIM(weights, 0); ++i ) {
      *(double *)PyArray_GETPTR1(weights, i) = 1.0;
    }
  }

  // get omp nbr threads
  threads = get_num_threads(threads);

  // normalise weights
  psnr = 0.0;
  for ( npy_intp i = 0; i < PyArray_DIM(weights, 0); ++i ) {
    psnr += *(double *)PyArray_GETPTR1(weights, i);
  }
  for ( npy_intp i = 0; i < PyArray_DIM(weights, 0); ++i ) {
    *(double *)PyArray_GETPTR1(weights, i) /= psnr;
  }

  // compute psnr
  switch ( PyArray_TYPE(im1) ) {
    case NPY_FLOAT32:
      Py_BEGIN_ALLOW_THREADS
      error = compute_psnr_float32(&psnr, im1, im2, weights, threads);
      Py_END_ALLOW_THREADS
      break;
    case NPY_DOUBLE:
      Py_BEGIN_ALLOW_THREADS
      error = compute_psnr_float64(&psnr, im1, im2, weights, threads);
      Py_END_ALLOW_THREADS
      break;
    default:
      PyErr_SetString(PyExc_TypeError, "only the types float32 and float64 are accepted");
      error = EXIT_FAILURE;
  }
  Py_DECREF(weights);

  // return and manage error
  if ( error == EXIT_FAILURE ) {
    return NULL;
  }
  return Py_BuildValue("d", psnr);
}


static PyMethodDef metricMethods[] = {
  {
    "psnr", (PyCFunction)py_psnr, METH_VARARGS | METH_KEYWORDS,
    R"(Pure C implementation of :py:func:`cutcutcodec.core.analysis.video.metric.psnr`.

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric.metric import psnr
    >>> np.random.seed(0)
    >>> im1 = np.random.random((720, 1080, 3))
    >>> im2 = 0.8 * im1 + 0.2 * np.random.random((720, 1080, 3))
    >>> round(psnr(im1, im2), 1)
    21.8
    >>>
    )"
  },
  {
    "ssim", (PyCFunction)py_ssim, METH_VARARGS | METH_KEYWORDS,
    R"(Pure C implementation of :py:func:`cutcutcodec.core.analysis.video.metric.ssim`.

    This fonction is nearly equivalent to these functions:

    Examples
    --------
    >>> import numpy as np
    >>> from cutcutcodec.core.analysis.video.metric.metric import ssim
    >>> np.random.seed(0)
    >>> im1 = np.random.random((720, 1080, 3))
    >>> im2 = 0.8 * im1 + 0.2 * np.random.random((720, 1080, 3))
    >>> round(ssim(im1, im2), 2)
    0.95
    >>>
    )"
  },
  {NULL, NULL, 0, NULL}
};


static struct PyModuleDef metric = {
  .m_base = PyModuleDef_HEAD_INIT,
  .m_name = "metric",
  .m_doc = "This module, implemented in C, offers functions for image metric calculation.",
  .m_size = -1,
  .m_methods = metricMethods,
  .m_slots = NULL,
  .m_traverse = NULL,
  .m_clear = NULL,
  .m_free = NULL,
};


PyMODINIT_FUNC PyInit_metric(void)
{
  import_array();
  if ( PyErr_Occurred() ) {
    return NULL;
  }
  return PyModule_Create(&metric);
}
