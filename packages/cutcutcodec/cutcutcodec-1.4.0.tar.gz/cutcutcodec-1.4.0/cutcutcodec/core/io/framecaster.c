/* Fast frame normalization. */

#define PY_SSIZE_T_CLEAN
#include <numpy/arrayobject.h>
#include <omp.h>
#include <Python.h>
#include "cutcutcodec/core/opti/parallel/threading.h"

#define CLAMP(x, low, high)  (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))


#pragma omp declare simd
inline npy_float32 from_y_tv_uint8(npy_uint8 value) {
  /* Inverse of eq (30) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / 219.0f) - (16.0f / 219.0f);
}


#pragma omp declare simd
inline npy_uint8 to_y_tv_uint8(npy_float32 value) {
  /* Eq (30) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint8)CLAMP(219.0f * value + (16.0f + 0.5f), 0.5f, 255.5f);
}


#pragma omp declare simd
inline npy_float32 from_y_tv_uint16(npy_uint16 value) {
  /* Inverse of eq (30) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / (256.0f * 219.0f)) - (16.0f / 219.0f);
}


#pragma omp declare simd
inline npy_uint16 to_y_tv_uint16(npy_float32 value) {
  /* Eq (30) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint16)CLAMP((256.0f * 219.0f) * value + (256.0f * 16.0f + 0.5f), 0.5f, 65535.5f);
}


#pragma omp declare simd
inline npy_float32 from_uv_tv_uint8(npy_uint8 value) {
  /* Inverse of eq (31) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / 224.0f) - (128.0f / 224.0f);
}


#pragma omp declare simd
inline npy_uint8 to_uv_tv_uint8(npy_float32 value) {
  /* Eq (31) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint8)CLAMP(224.0f * value + (128.0f + 0.5f), 0.5f, 255.5f);
}


#pragma omp declare simd
inline npy_float32 from_uv_tv_uint16(npy_uint16 value) {
  /* Inverse of eq (31) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / (256.0f * 224.0f)) - (128.0f / 224.0f);
}


#pragma omp declare simd
inline npy_uint16 to_uv_tv_uint16(npy_float32 value) {
  /* Eq (31) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint16)CLAMP((256.0f * 224.0f) * value + (256.0f * 128.0f + 0.5f), 0.5f, 65535.5f);
}


#pragma omp declare simd
inline npy_float32 from_y_pc_uint8(npy_uint8 value) {
  /* Inverse of eq (36) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / 255.0f);
}


#pragma omp declare simd
inline npy_uint8 to_y_pc_uint8(npy_float32 value) {
  /* Eq (36) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint8)CLAMP(255.0f * value + 0.5f, 0.5f, 255.5f);
}


#pragma omp declare simd
inline npy_float32 from_y_pc_uint16(npy_uint16 value) {
  /* Inverse of eq (36) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / 65535.0f);
}


#pragma omp declare simd
inline npy_uint16 to_y_pc_uint16(npy_float32 value) {
  /* Eq (36) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint16)CLAMP(65535.0f * value + 0.5f, 0.5f, 65535.5f);
}


#pragma omp declare simd
inline npy_float32 from_uv_pc_uint8(npy_uint8 value) {
  /* Inverse of eq (37) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / 255.0f) - (128.0f / 255.0f);
}


#pragma omp declare simd
inline npy_uint8 to_uv_pc_uint8(npy_float32 value) {
  /* Eq (37) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint8)CLAMP(255.0f * value + (128.0f + 0.5f), 0.5f, 255.5f);
}


#pragma omp declare simd
inline npy_float32 from_uv_pc_uint16(npy_uint16 value) {
  /* Inverse of eq (37) of ITU-T H.273 (V4) (07/2024). */
  return (npy_float32)(value) * (1.0f / 65535.0f) - (32768.0f / 65535.0f);
}


#pragma omp declare simd
inline npy_uint16 to_uv_pc_uint16(npy_float32 value) {
  /* Eq (37) of ITU-T H.273 (V4) (07/2024). */
  // +0.5 to avoid rounded down
  return (npy_uint16)CLAMP(65535.0f * value + (32768.0f + 0.5f), 0.0f, 65535.5f);
}


static PyObject* py_from_rgb(PyObject* Py_UNUSED(self), PyObject* args) {
  /* Convert a frame from the RGB space to float32 RGB frame. */
  PyArrayObject *frame, *out = NULL;
  int is_tv, not_implemented = 1;
  long int threads = 0;

  // parse input
  if ( !PyArg_ParseTuple(
    args, "O!p|ll",
    &PyArray_Type, &frame, &is_tv, &threads
    )
  ) {
    return NULL;
  }

  // case grayscale, add a leading channel dimension
  if ( PyArray_NDIM(frame) == 2 ) {
    npy_intp ptr[] = {PyArray_DIM(frame, 0), PyArray_DIM(frame, 1), 1};
    PyArray_Dims shape = {ptr, 3};
    if ( PyArray_Resize(frame, &shape, 0, NPY_ANYORDER) == NULL ) {
      return PyErr_NoMemory();
    }
  } else {
    if ( PyArray_NDIM(frame) != 3 ) {
      PyErr_SetString(PyExc_ValueError, "'frame' requires 3 dimensions");
      return NULL;
    }
  }

  // allocate the output array
  out = (PyArrayObject *)PyArray_EMPTY(3, PyArray_SHAPE(frame), NPY_FLOAT32, 0);
  if ( out == NULL ) {
    return PyErr_NoMemory();
  }

  // set context
  threads = get_num_threads(threads);

  // cast and convert
  Py_BEGIN_ALLOW_THREADS
  switch ( PyArray_TYPE(frame) ) {
    case NPY_UINT8:
      not_implemented = 0;
      if ( is_tv ) {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
        #pragma GCC ivdep
        for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
          *(npy_float32 *)PyArray_GETPTR3(out, i, j, k) = from_y_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, k));
        }}}
      } else {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
        #pragma GCC ivdep
        for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
          *(npy_float32 *)PyArray_GETPTR3(out, i, j, k) = from_y_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, k));
        }}}
      }
      break;
    case NPY_UINT16:
      not_implemented = 0;
      if ( is_tv ) {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
        #pragma GCC ivdep
        for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
          *(npy_float32 *)PyArray_GETPTR3(out, i, j, k) = from_y_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, k));
        }}}
      } else {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
        #pragma GCC ivdep
        for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
          *(npy_float32 *)PyArray_GETPTR3(out, i, j, k) = from_y_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, k));
        }}}
      }
      break;
    case NPY_FLOAT32:  // simple copy
      not_implemented = 0;
      #pragma omp parallel for schedule(static) num_threads(threads)
      for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
      for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
      #pragma GCC ivdep
      for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
        *(npy_float32 *)PyArray_GETPTR3(out, i, j, k) = *(npy_float32 *)PyArray_GETPTR3(frame, i, j, k);
      }}}
      break;
  }
  Py_END_ALLOW_THREADS

  // finalyse
  if ( not_implemented ) {
    Py_DECREF(out);
    PyErr_SetString(PyExc_NotImplementedError, "this input frame format is not yet supported");
    return NULL;
  }
  return (PyObject*)out;
}


static PyObject* py_from_yuv(PyObject* Py_UNUSED(self), PyObject* args) {
  /* Convert a frame from the YUV space to float32 frame in the Y'PbPr space. */
  PyArrayObject *frame, *out = NULL;
  int is_tv, not_implemented = 1;
  long int threads = 0;

  // parse input
  if ( !PyArg_ParseTuple(
    args, "O!p|ll",
    &PyArray_Type, &frame, &is_tv, &threads
    )
  ) {
    return NULL;
  }

  // case grayscale, add a leading channel dimension
  if ( PyArray_NDIM(frame) == 2 ) {
    npy_intp ptr[] = {PyArray_DIM(frame, 0), PyArray_DIM(frame, 1), 1};
    PyArray_Dims shape = {ptr, 3};
    if ( PyArray_Resize(frame, &shape, 0, NPY_ANYORDER) == NULL ) {
      return PyErr_NoMemory();
    }
  } else {
    if ( PyArray_NDIM(frame) != 3 ) {
      PyErr_SetString(PyExc_ValueError, "'frame' requires 3 dimensions");
      return NULL;
    }
  }

  // allocate the output array
  out = (PyArrayObject *)PyArray_EMPTY(3, PyArray_SHAPE(frame), NPY_FLOAT32, 0);
  if ( out == NULL ) {
    return PyErr_NoMemory();
  }

  // set context
  threads = get_num_threads(threads);

  // cast and convert
  switch ( PyArray_TYPE(frame) ) {
    case NPY_UINT8:
      Py_BEGIN_ALLOW_THREADS
      switch ( PyArray_DIM(frame, 2) ) {
        case 1:
          not_implemented = 0;
          if ( is_tv ) {  // uint8 y tv
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 0));
            }}
          } else {  // uint8 y pc
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, pc
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 0));
            }}
          }
          break;
        case 3:
          not_implemented = 0;
          if ( is_tv ) {  // uint8 yuv tv
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 2));
            }}
          } else {  // uint8 yuv pc
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, pc
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 2));
            }}
          }
          break;
        case 4:
          not_implemented = 0;
          if ( is_tv ) {  // uint8 yuva tv
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 2));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 3) = from_y_tv_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 3));
            }}
          } else {  // uint8 yuva pc
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, pc
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 2));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 3) = from_y_pc_uint8(*(npy_uint8 *)PyArray_GETPTR3(frame, i, j, 3));
            }}
          }
          break;
      }
      Py_END_ALLOW_THREADS
      break;
    case NPY_UINT16:
      Py_BEGIN_ALLOW_THREADS
      switch ( PyArray_DIM(frame, 2) ) {
        case 1:
          not_implemented = 0;
          if ( is_tv ) {  // uint16 y tv
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint16, y, tv
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 0));
            }}
          } else {  // uint16 y pc
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint16, y, pc
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 0));
            }}
          }
          break;
        case 3:
          not_implemented = 0;
          if ( is_tv ) {  // uint16 yuv tv
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint16, y, tv
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 2));
            }}
          } else {  // uint16 yuv pc
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint16, y, pc
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 2));
            }}
          }
          break;
        case 4:
          not_implemented = 0;
          if ( is_tv ) {  // uint16 yuva tv
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint16, y, tv
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 2));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 3) = from_y_tv_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 3));
            }}
          } else {  // uint16 yuva pc
            #pragma omp parallel for schedule(static) num_threads(threads)
            for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint16, y, pc
            #pragma GCC ivdep
            for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 0) = from_y_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 0));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 1) = from_uv_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 1));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 2) = from_uv_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 2));
              *(npy_float32 *)PyArray_GETPTR3(out, i, j, 3) = from_y_pc_uint16(*(npy_uint16 *)PyArray_GETPTR3(frame, i, j, 3));
            }}
          }
          break;
      }
      Py_END_ALLOW_THREADS
      break;
    case NPY_FLOAT32:  // simple copy
      not_implemented = 0;
      if ( PyArray_CopyInto(out, frame) ) {
        Py_DECREF(out);
        PyErr_SetString(PyExc_RuntimeError, "failed to copy frame");
        return NULL;
      }
      break;
  }

  // finalyse
  if ( not_implemented ) {
    Py_DECREF(out);
    PyErr_SetString(PyExc_NotImplementedError, "this input frame format is not yet supported");
    return NULL;
  }
  return (PyObject*)out;
}


static PyObject* py_to_rgb(PyObject* Py_UNUSED(self), PyObject* args) {
  /* Convert a frame from the float32 rgb space to uint8 frame in the RGB space. */
  PyArrayObject *frame, *out = NULL;
  int to_tv = 0;
  long int threads = 0;

  // parse input
  if ( !PyArg_ParseTuple(
    args, "O!|pll",
    &PyArray_Type, &frame, &to_tv, &threads
    )
  ) {
    return NULL;
  }

  // verification
  if ( PyArray_NDIM(frame) != 3 ) {
    PyErr_SetString(PyExc_ValueError, "'frame' requires 3 dimensions");
    return NULL;
  }
  if ( PyArray_TYPE(frame) != NPY_FLOAT32 ) {
    PyErr_SetString(PyExc_ValueError, "'frame' has to be in float32");
    return NULL;
  }

  // allocate the output array
  out = (PyArrayObject *)PyArray_EMPTY(3, PyArray_SHAPE(frame), NPY_UINT8, 0);
  if ( out == NULL ) {
    return PyErr_NoMemory();
  }

  // set context
  threads = get_num_threads(threads);

  // cast and convert
  Py_BEGIN_ALLOW_THREADS
  if ( to_tv ) {
    #pragma omp parallel for schedule(static) num_threads(threads)
    for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
    for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
    #pragma GCC ivdep
    for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
      *(npy_uint8 *)PyArray_GETPTR3(out, i, j, k) = to_y_tv_uint8(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, k));
    }}}
  } else {
    #pragma omp parallel for schedule(static) num_threads(threads)
    for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {
    for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
    #pragma GCC ivdep
    for ( npy_intp k = 0; k < PyArray_DIM(frame, 2); ++k ) {
      *(npy_uint8 *)PyArray_GETPTR3(out, i, j, k) = to_y_pc_uint8(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, k));
    }}}
  }
  Py_END_ALLOW_THREADS

  return (PyObject*)out;
}


static PyObject* py_to_yuv(PyObject* Py_UNUSED(self), PyObject* args) {
  /* Convert a frame from the Y'PbPr space to uint16 frame in the YUV tv space. */
  PyArrayObject *frame, *out = NULL;
  int not_implemented = 1;
  int to_tv = 1;
  long int threads = 0;

  // parse input
  if ( !PyArg_ParseTuple(
    args, "O!|pll",
    &PyArray_Type, &frame, &to_tv, &threads
    )
  ) {
    return NULL;
  }

  // verification
  if ( PyArray_NDIM(frame) != 3 ) {
    PyErr_SetString(PyExc_ValueError, "'frame' requires 3 dimensions");
    return NULL;
  }
  if ( PyArray_TYPE(frame) != NPY_FLOAT32 ) {
    PyErr_SetString(PyExc_ValueError, "'frame' has to be in float32");
    return NULL;
  }

  // allocate the output array
  out = (PyArrayObject *)PyArray_EMPTY(3, PyArray_SHAPE(frame), NPY_UINT16, 0);
  if ( out == NULL ) {
    return PyErr_NoMemory();
  }

  // set context
  threads = get_num_threads(threads);

  // cast and convert
  Py_BEGIN_ALLOW_THREADS
  switch ( PyArray_DIM(frame, 2) ) {
    case 1:
      not_implemented = 0;
      if ( to_tv ) {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
        #pragma GCC ivdep
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 0) = to_y_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 0));
        }}
      } else {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
        #pragma GCC ivdep
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 0) = to_y_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 0));
        }}
      }
      break;
    case 3:
      not_implemented = 0;
      if ( to_tv ) {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
        #pragma GCC ivdep
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 0) = to_y_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 0));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 1) = to_uv_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 1));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 2) = to_uv_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 2));
        }}
      } else {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
        #pragma GCC ivdep
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 0) = to_y_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 0));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 1) = to_uv_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 1));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 2) = to_uv_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 2));
        }}
      }
      break;
    case 4:
      not_implemented = 0;
      if ( to_tv ) {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
        #pragma GCC ivdep
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 0) = to_y_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 0));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 1) = to_uv_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 1));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 2) = to_uv_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 2));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 3) = to_y_tv_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 3));
        }}
      } else {
        #pragma omp parallel for schedule(static) num_threads(threads)
        for ( npy_intp i = 0; i < PyArray_DIM(frame, 0); ++i ) {  // uint8, y, tv
        #pragma GCC ivdep
        for ( npy_intp j = 0; j < PyArray_DIM(frame, 1); ++j ) {
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 0) = to_y_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 0));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 1) = to_uv_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 1));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 2) = to_uv_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 2));
          *(npy_uint16 *)PyArray_GETPTR3(out, i, j, 3) = to_y_pc_uint16(*(npy_float32 *)PyArray_GETPTR3(frame, i, j, 3));
        }}
      }
      break;
  }
  Py_END_ALLOW_THREADS

  // finalyse
  if ( not_implemented ) {
    Py_DECREF(out);
    PyErr_SetString(PyExc_NotImplementedError, "this input frame dim is not yet supported");
    return NULL;
  }
  return (PyObject*)out;
}


static PyMethodDef framecasterMethods[] = {
  {
    "from_yuv", (PyCFunction)py_from_yuv, METH_VARARGS,
    R"(Convert a frame from the YUV space to float32 frame in the Y'PbPr space.

    * add 1 leading channel to grayscale frame (h x w -> h x w x 1)
    * cast into float32
    * convert limited range to full range (based on UIT-R)

    Parameters
    ----------
    frame : np.ndarray
        The float32, uint8 or uint16 video frame of shape (height, width, [channels]),
        with optional channel dimension in {1, 3, 4}.
    is_tv : bool
        If True, consider the input as a limited range coding.
    threads : int, default=0
        Number of threads used.

    Returns
    -------
    normalized : np.ndarray[np.float32, np.float32, np.float32]
        The normalized frame with [y, u, v] in [0, 1] x [-1/2, 1/2]**2.

    Notes
    -----
    * It is optimized for C contiguous array.
    * This function makes a safe copy of the input frame, no modification inplace.
    )"
  },
  {
    "from_rgb", (PyCFunction)py_from_rgb, METH_VARARGS,
    R"(Convert a frame from the RGB space to float32 frame in the RGB space.

    * add 1 leading channel to grayscale frame (h x w -> h x w x 1)
    * cast into float32
    * convert limited range to full range (based on UIT-R)

    Parameters
    ----------
    frame : np.ndarray
        The float32, uint8 or uint16 video frame of shape (height, width, [channels]).
    is_tv : bool
        If True, consider the input as a limited range coding.
    threads : int, default=0
        Number of threads used.

    Returns
    -------
    normalized : np.ndarray[np.float32, np.float32, np.float32]
        The normalized frame with [r, g, b] in [0, 1]**3.

    Notes
    -----
    * It is optimized for C contiguous array.
    * This function makes a safe copy of the input frame, no modification inplace.
    )"
  },
  {
    "to_yuv", (PyCFunction)py_to_yuv, METH_VARARGS,
    R"(Convert a frame from the Y'PbPr float32 space to uint16 frame in the YUV tv space.

    Parameters
    ----------
    frame : np.ndarray[np.float32, np.float32, np.float32]
        The float32 video frame of shape (height, width, channels).
    to_tv : bool, default=True
        If False, convert the frame in full range, default is limited range.
    threads : int, default=0
        Number of threads used.

    Returns
    -------
    out : np.ndarray[np.uint16]
      The YUV frame in limited range.

    Notes
    -----
    * It is optimized for C contiguous array.
    * This function makes a safe copy of the input frame, no modification inplace.
    )"
  },
  {
    "to_rgb", (PyCFunction)py_to_rgb, METH_VARARGS,
    R"(Convert a frame from the RGB float32 space to uint8 frame in rgb24.

    Parameters
    ----------
    frame : np.ndarray[np.float32, np.float32, np.float32]
        The float32 video frame of shape (height, width, channels).
    to_tv : bool, default=False
        If True, convert the frame in limited range, default is full range.
    threads : int, default=0
        Number of threads used.

    Returns
    -------
    out : np.ndarray[np.uint8]
        The YUV frame in limited range.

    Notes
    -----
    * It is optimized for C contiguous array.
    * This function makes a safe copy of the input frame, no modification inplace.
    )"
  },
  {NULL, NULL, 0, NULL}
};


static struct PyModuleDef framecaster = {
  .m_base = PyModuleDef_HEAD_INIT,
  .m_name = "framecaster",
  .m_doc = "This module, implemented in C, offers functions to normalize frames.",
  .m_size = -1,
  .m_methods = framecasterMethods,
  .m_slots = NULL,
  .m_traverse = NULL,
  .m_clear = NULL,
  .m_free = NULL,
};


PyMODINIT_FUNC PyInit_framecaster(void)
{
  import_array();
  if ( PyErr_Occurred() ) {
    return NULL;
  }
  return PyModule_Create(&framecaster);
}
