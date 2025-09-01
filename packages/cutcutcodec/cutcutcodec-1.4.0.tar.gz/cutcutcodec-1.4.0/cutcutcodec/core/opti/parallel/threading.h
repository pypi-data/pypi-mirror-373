/* Multithreading tools. */

#include <omp.h>
#include <unistd.h>
#include <sys/syscall.h>
#ifndef SYS_gettid
#error 'SYS_gettid unavailable on this system'
#endif
#define gettid() ((pid_t)syscall(SYS_gettid))


long int get_num_threads(long int threads) {
  /* Return the number of threads. */
  if ( threads == 0 ) {
    if ( gettid() == getpid() ) {  // if we are in the main thread
      threads = omp_get_num_procs() / 2;
      return threads < 2 ? 2 : threads;
    }
    return 1;
  } else if ( threads < 0 ) {
    threads = omp_get_num_procs() / 2;
    return threads < 2 ? 2 : threads;
  }
  return threads;
}


long int set_num_threads(long int threads) {
  /* Set the number of thread for the openmp directives. */
  long int ncpu = get_num_threads(threads);
  omp_set_num_threads(ncpu);
  return ncpu;
}
