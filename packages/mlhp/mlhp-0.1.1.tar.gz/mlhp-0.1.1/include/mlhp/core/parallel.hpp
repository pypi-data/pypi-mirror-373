// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_PARALLEL_HPP
#define MLHP_CORE_PARALLEL_HPP

#include "mlhp/core/config.hpp"
#include "mlhp/core/coreexport.hpp"

#ifdef MLHP_MULTITHREADING_OMP
#include <omp.h>
#endif

namespace mlhp::parallel
{

#ifdef MLHP_MULTITHREADING_OMP
    using Lock = omp_lock_t;
#else
    using Lock = std::uint8_t;
#endif

MLHP_EXPORT 
size_t getMaxNumberOfThreads( );

MLHP_EXPORT 
size_t getNumberOfThreads( );

MLHP_EXPORT 
void setNumberOfThreads( size_t nthreads );

MLHP_EXPORT 
size_t getThreadNum( );

MLHP_EXPORT 
void initialize( Lock& lock );

MLHP_EXPORT 
void aquire( Lock& lock );

MLHP_EXPORT 
void release( Lock& lock );

//! Given the total size, determine the chunksize between [1, chunkLimit], such that
//! one chunk is not larger than size / (threadFactor * maxThreads). For example:
//! 16 threads with size = 1000, chunkLimit = 20, threadFactor = 1  -->  20 (from chunkLimit)
//! 64 threads with size = 1000, chunkLimit = 20, threadFactor = 1  -->  15 (from 1000 // 64)
//! 64 threads with size = 1000, chunkLimit = 20, threadFactor = 2  -->  7  (from 1000 // (2 * 64))
//! 64 threads with size = 1000, chunkLimit = 20, threadFactor = 4  -->  3  (from 1000 // (4 * 64))
//! 64 threads with size = 10, chunkLimit = 20, threadFactor = 4    -->  1  (at least 1)
MLHP_EXPORT std::uint64_t clampChunksize( std::uint64_t size, std::uint64_t chunkLimit, size_t threadFactor = 4 );

} // namespace mlhp::parallel

#endif // MLHP_CORE_PARALLEL_HPP
