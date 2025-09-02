// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/parallel.hpp"

namespace mlhp::parallel
{

#ifdef MLHP_MULTITHREADING_OMP

size_t getMaxNumberOfThreads( )
{
    return static_cast<size_t>( omp_get_max_threads( ) );
}

size_t getNumberOfThreads( )
{
    return static_cast<size_t>( omp_get_num_threads( ) );
}

void setNumberOfThreads( [[maybe_unused]]size_t nthreads )
{
    omp_set_num_threads( static_cast<int>( nthreads ) );
}

size_t getThreadNum( )
{
    return static_cast<size_t>( omp_get_thread_num( ) );
}

void initialize( Lock& lock )
{
    omp_init_lock( &lock );
}

void aquire( Lock& lock )
{
    omp_set_lock( &lock );
}

void release( Lock & lock )
{
    omp_unset_lock( &lock );
}

#else

size_t getNumberOfThreads( ) { return 1; }
size_t getMaxNumberOfThreads( ) { return 1; }
size_t getThreadNum( ) { return 0; }

void setNumberOfThreads( size_t ){ }
void initialize( Lock& ) { }
void aquire( Lock& ) { }
void release( Lock& ) { }

#endif

std::uint64_t clampChunksize( std::uint64_t size, std::uint64_t chunkLimit, size_t threadFactor )
{
    auto threadLimit = static_cast<std::uint64_t>( size / ( threadFactor * getMaxNumberOfThreads( ) ) );

    return std::max( std::min( chunkLimit, threadLimit ), std::uint64_t { 1 } );
}

} // namespace mlhp::parallel
