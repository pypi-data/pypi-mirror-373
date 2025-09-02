// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core.hpp"

using namespace mlhp;


template<size_t D, size_t P>
void kron_mult( std::array<std::span<const double>, D> NPtrs,
                memory::AlignedVector<double>& dofsVector,  
                memory::AlignedVector<double>& targetVector )
{
    static constexpr auto c_i = P + 1;
    static constexpr auto r_i = P + 1;
    static constexpr auto npadded = memory::paddedLength<double>( P + 1 );

    auto stride = utilities::integerPow( c_i, D - 1 );

    for( size_t axis = 0; axis < D; ++axis )
    {
        auto dofs = memory::assumeAlignedNoalias( dofsVector.data( ) );
        auto target = memory::assumeAlignedNoalias( targetVector.data( ) );
        auto NPtr = memory::assumeAlignedNoalias( NPtrs[D - 1 - axis].data( ) );

        auto size = stride * r_i;

        for( size_t j = 0; j < stride; ++j )
        {
            for( size_t k = 0; k < r_i; ++k )
            {
                target[k * stride + j] = 0.0;

                for( size_t l = 0; l < c_i; ++l )
                {
                    target[k * stride + j] += NPtr[k * npadded + l] * dofs[j * c_i + l];
                }
            }
        }

        std::swap( targetVector, dofsVector );

        stride = size / c_i;
    }
}

// Memory Layout
// [ GLL coordinates                     , padding,
//   GLL weights                         , padding,
//   Lagrange polynomials at GLL point 0 , padding,  // In each row we have all 
//   ...                                 , padding,  // shape functions evaluated 
//   Lagrange polynomials at GLL point P , padding,  // for the coordinate of this
//   Lagrange derivative at GLL point 0  , padding,  // row
//   ...                                 , padding,
//   Lagrange derivative at GLL point P  , padding 
//   Same shape functions, but transposed, padding]  
template<size_t D, size_t P>
struct Lagrange1DEvaluation
{
    memory::AlignedVector<double> data;
    
    static constexpr auto nblocks = memory::paddedNumberOfBlocks<double>( P + 1 );
    static constexpr auto npadded = memory::paddedLength<double>( P + 1 );

    Lagrange1DEvaluation( ) :
        data( ( 4 * ( P + 1 ) + 2 ) * npadded, 0.0 )
    {
        auto rspan = std::span( utilities::begin( data, 0 * npadded ), P + 1 );
        auto wspan = std::span( utilities::begin( data, 1 * npadded ), P + 1 );

        gaussLobattoPoints( P + 1, rspan, wspan );

        for( size_t i = 0; i < P + 1; ++i )
        {
            for( size_t j = 0; j < P + 1; ++j )
            {
                data[( i + 2 + 0 * ( P + 1 ) ) * npadded + j] = polynomial::lagrange( rspan, j, rspan[i], 0 ); // N_j(r_i)
                data[( i + 2 + 1 * ( P + 1 ) ) * npadded + j] = polynomial::lagrange( rspan, j, rspan[i], 1 ); // dN_j(r_i)

                // Same but transposed
                data[( j + 2 + 2 * ( P + 1 ) ) * npadded + i] = data[( i + 2 + 0 * ( P + 1 ) ) * npadded + j]; // N_i(r_j) 
                data[( j + 2 + 3 * ( P + 1 ) ) * npadded + i] = data[( i + 2 + 1 * ( P + 1 ) ) * npadded + j]; // dN_i(r_j)
            }
        }
    }
    
    const auto shapesPtr( size_t index ) const
    {
        return memory::assumeAlignedNoalias( data.data( ) + ( 2 + index * ( P + 1 ) ) * npadded );
    }

    void multiplyN( memory::AlignedVector<double>& target,
                    memory::AlignedVector<double>& tmp ) const
    {
        auto NptrsT = array::make<D>( std::span<const double>( this->shapesPtr( 0 ), this->shapesPtr( 1 ) ) );

        kron_mult<D, P>( NptrsT, target, tmp );
    }

    void multiplyGradN( const memory::AlignedVector<double>& dofs,
                        std::array<memory::AlignedVector<double>, D>& target,
                        memory::AlignedVector<double>& tmp ) const
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            std::copy( dofs.begin( ), dofs.end( ), target[axis].begin( ) );

            auto Nptrs = array::make<D>( std::span<const double>( this->shapesPtr( 0 ), this->shapesPtr( 1 ) ) );

            Nptrs[axis] = std::span<const double>( this->shapesPtr( 1 ), this->shapesPtr( 2 ) );

            kron_mult<D, P>( Nptrs, target[axis], tmp );
        }
    }

    void multiplyNT( memory::AlignedVector<double>& scalar,
                     memory::AlignedVector<double>& tmp ) const
    {
        auto NptrsT = array::make<D>( std::span<const double>( this->shapesPtr( 2 ), this->shapesPtr( 3 ) ) );

        kron_mult<D, P>( NptrsT, scalar, tmp );
    }

    void multiplyGradNT( std::array<memory::AlignedVector<double>, D>& vector,
                         memory::AlignedVector<double>& tmp ) const
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            auto NptrsT = array::make<D>( std::span<const double>( this->shapesPtr( 2 ), this->shapesPtr( 3 ) ) );
            NptrsT[axis] = std::span<const double>( this->shapesPtr( 3 ), this->shapesPtr( 4 ) );

            kron_mult<D, P>( NptrsT, vector[axis], tmp );
        }
    }
};

template<size_t D, size_t P>
struct MatrixFree
{
    static constexpr auto ndofelement = utilities::integerPow( P + 1, D );
    static constexpr auto ndofpadded = memory::paddedLength<double>( ndofelement );
    static constexpr auto sizes = array::makeSizes<D>( P + 1 );

    std::array<size_t, D> nelements, elementStrides, dofStrides;
    std::array<double, D> lengths, origin, halflengths, invHalflengths;
    size_t ndof, chunksize;
    double detJ, deltaT;
    std::int64_t totalElements;

    Lagrange1DEvaluation<D, P> lagrange;

    MatrixFree( std::array<size_t, D> nelements_,
                std::array<double, D> lengths_,
                std::array<double, D> origin_,
                double deltaT_ ) :
        nelements { nelements_ }, elementStrides { nd::stridesFor( nelements ) },
        dofStrides { nd::stridesFor( array::add( array::multiply( nelements, P ), size_t { 1 } ) ) },
        lengths { lengths_ }, origin { origin_ }, 
        halflengths { array::divide( 0.5 * lengths_, array::convert<double>( nelements_ ) ) },
        invHalflengths { array::inverse( halflengths ) }, 
        ndof { array::product( array::add( array::multiply( nelements, P ), size_t { 1 } ) ) },
        detJ { array::product( halflengths ) }, 
        deltaT { deltaT_ },
        totalElements { static_cast<std::int64_t>( array::product( nelements ) ) }
    {
        auto threadlimit = static_cast<size_t>( 0.25 * totalElements / parallel::getMaxNumberOfThreads( ) );

        chunksize = static_cast<size_t>( 2738.0 / ndofelement );         // a couple thousand dofs per chunk
        chunksize -= chunksize % nelements[D - 1];                       // make it muliple of nelements in z
        chunksize += nelements[D - 1] / std::max( size_t { 3 }, P - 1 ); // add 1 / 3 to prevent atomics interfering
        chunksize = std::min( chunksize, threadlimit );                  // At least one chunk per thread
        chunksize = std::max( chunksize, size_t { 1 } );                 // In case chunksize was zero
    }

    auto computeInitial( const spatial::ScalarFunction<D>& source,
                         const std::vector<double>& density ) const
    {
        auto massTarget = std::vector<double>( ndof, 0.0 );
        auto sourceTarget = std::vector<double>( ndof, 0.0 );
        auto materialStrides = nd::stridesFor( array::multiply( nelements, P + 1 ) );

        #pragma omp parallel
        {
            auto Me = memory::AlignedVector<double>( ndofpadded, 0.0 );
            auto Fe = memory::AlignedVector<double>( ndofpadded, 0.0 );
            auto tmp = memory::AlignedVector<double>( ndofpadded, 0.0 );

            #pragma omp for schedule(dynamic, chunksize)
            for( std::int64_t ii = 0; ii < totalElements; ++ii )
            {
                auto ijkElement = nd::unravelWithStrides( static_cast<size_t>( ii ), elementStrides );

                std::fill( Me.begin( ), Me.end( ), 1.0 );

                lagrange.multiplyN( Me, tmp );

                // Loop over GLL quadrature points
                nd::executeWithIndex( sizes, [&]( std::array<size_t, D> ijkQP, size_t iQP )
                {      
                    auto multiIndex = array::add( array::multiply( ijkElement, P + 1 ), ijkQP );
                    auto linearIndex = nd::linearIndex( materialStrides, multiIndex );

                    auto weightDetJ = detJ;
                    auto xyz = origin;

                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        weightDetJ *= lagrange.data[lagrange.npadded + ijkQP[axis]];
                        xyz[axis] += ( 2 * ijkElement[axis] + lagrange.data[ijkQP[axis]] + 1 ) * halflengths[axis];
                    }

                    Me[iQP] *= weightDetJ * density[linearIndex];
                    Fe[iQP] = source( xyz ) * weightDetJ;
                } );

                lagrange.multiplyNT( Me, tmp );
                lagrange.multiplyNT( Fe, tmp );

                nd::executeWithIndex( sizes, [&]( std::array<size_t, D> ijkTP, size_t index )
                {
                    auto global = nd::linearIndex( dofStrides, array::add( array::multiply( ijkElement, P ), ijkTP ) );
                
                    #pragma omp atomic
                    massTarget[global] += Me[index];

                    #pragma omp atomic
                    sourceTarget[global] += Fe[index] * deltaT * deltaT;
                } );

            } // for each element
        } // omp parallel

        std::transform( massTarget.begin( ), massTarget.end( ), massTarget.begin( ), []( auto v ) { return 1.0 / v; } );

        return std::tuple { std::move( massTarget ), std::move( sourceTarget ) };
    } 

    auto computeRhs( const std::vector<double>& rhs,
                     const std::vector<double>& density,
                     std::vector<double>& Ktarget )
    {
        auto totalElements = static_cast<std::int64_t>( array::product( nelements ) );
        auto chunksize = std::min( nelements.back( ), 10 * parallel::getNumberOfThreads( ) );
        
        struct Cache
        {
            std::vector<DofIndex> LM;
            memory::AlignedVector<double> T, elementRhs;
            std::array<memory::AlignedVector<double>, D> gradU;

            Cache( size_t ndofpadded ) :
                LM( ndofpadded ), T( ndofpadded ), elementRhs( ndofpadded ),
                gradU { array::make<D>( memory::AlignedVector<double>( ndofpadded ) ) }
            { }
        };

        thread_local auto cache = Cache { ndofpadded };

        auto materialStrides = nd::stridesFor( array::multiply( nelements, P + 1 ) );

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < totalElements; ++ii )
        {
            auto ijkElement = nd::unravelWithStrides( static_cast<size_t>( ii ), elementStrides );
                        
            nd::executeWithIndex( sizes, [&]( std::array<size_t, D> ijkTP, size_t index )
            {
                cache.LM[index] = nd::linearIndex( dofStrides, array::add( array::multiply( ijkElement, P ), ijkTP ) );
                cache.elementRhs[index] = rhs[cache.LM[index]];
            } );

            lagrange.multiplyGradN( cache.elementRhs, cache.gradU, cache.T );

            auto baseIndex = array::multiply( ijkElement, P + 1 );

            // Loop over GLL quadrature points
            nd::executeWithIndex( sizes, [&]( std::array<size_t, D> ijkQP, size_t qpIndex )
            {      
                auto linearIndex = size_t { baseIndex[D - 1] + ijkQP[D - 1] };

                for( size_t axis = 0; axis + 1 < D; ++axis )
                {
                    linearIndex += materialStrides[axis] * ( baseIndex[axis] + ijkQP[axis] );
                }

                auto weightDetJ = detJ * density[linearIndex];
                
                for( size_t axis = 0; axis < D; ++axis )
                {
                    weightDetJ *= lagrange.data[lagrange.npadded + ijkQP[axis]];
                }

                for( size_t axis = 0; axis < D; ++axis )
                {
                    cache.gradU[axis][qpIndex] = cache.gradU[axis][qpIndex] * invHalflengths[axis] * invHalflengths[axis] * weightDetJ;
                }
            } );

            lagrange.multiplyGradNT( cache.gradU, cache.T );

            // Assemble into global vector
            nd::executeWithIndex( sizes, [&]( std::array<size_t, D> ijk, size_t i )
            { 
                auto globalId = cache.LM[i];
                auto value = 0.0;
                
                for( size_t axis = 0; axis < D; ++axis )
                {
                    value += cache.gradU[axis][i];
                }

                #pragma omp atomic
                Ktarget[globalId] += value * deltaT * deltaT;
            } );

        } // for each element
    }
};

template<size_t D>
auto initializeDensity( const ImplicitFunction<D>& domain,
                        std::array<size_t, D> nelements, 
                        std::array<double, D> lengths,
                        std::array<double, D> origin,
                        size_t degree,
                        double inside,
                        double outside )
{
    auto nvoxels = array::multiply( nelements, array::make<D>( degree + 1 ) );
    auto halflengths = array::divide( 0.5 * lengths, array::convert<double>( nvoxels ) );
    auto data = std::vector<double>( array::product( nvoxels ) );

    nd::executeWithIndex( nvoxels, [&]( std::array<size_t, D> ijk, size_t index ) 
    {
        auto xyz = origin;

        for( size_t axis = 0; axis < D; ++axis )
        {
            xyz[axis] += ( 2 * ijk[axis] + 1 ) * halflengths[axis];
        }

        data[index] = domain( xyz ) ? inside : outside;
    } );

    return data;
}

template<size_t D, size_t P>
void postprocessSolution( std::string filename,
                          std::array<size_t, D> nelements,
                          std::array<double, D> lengths,
                          std::array<double, D> origin,
                          const std::vector<double>& dofs );

int main( )
{
    using namespace mlhp;

    static constexpr size_t D = 2;
    static constexpr size_t P = 5;

    auto origin = array::make<D>( 0.0 );
    auto lengths = array::make<D>( 2.0 );
    auto nelements = array::makeSizes<D>( 12 );

    auto duration = 3.0;
    auto nsteps = 500;
    auto deltaT = duration / nsteps;
    
    auto postprocess = false;
    auto interval = size_t { 20 };

    std::function sourceX = []( std::array<double, D> xyz )
    {
        auto sigmaS = 0.06;

        return 10 * std::exp( -spatial::normSquared( xyz ) / ( 2 * sigmaS * sigmaS ) );
    };
    
    std::function sourceT = [=]( double t )
    {   
        auto frequency = 4.0;
        auto t0 = 1.0 / frequency;
        auto sigmaT = 1.0 / ( 2.0 * std::numbers::pi * frequency );

        return -( t - t0 ) / ( std::sqrt( 2.0 * std::numbers::pi ) * sigmaT * sigmaT * sigmaT ) * 
            std::exp( -( t - t0 ) * ( t - t0 ) / ( 2 * sigmaT * sigmaT ) );
    };

    auto matrixFree = MatrixFree<D, P>( nelements, lengths, origin, deltaT );

    std::cout << "ndim = " << D << ", p = " << P << std::endl;
    std::cout << array::product( nelements ) << " elements" << std::endl;
    std::cout << matrixFree.ndof << " dofs" << std::endl;
    std::cout << nsteps << " time steps" << std::endl;
    std::cout << deltaT << " delta T" << std::endl;
    
    auto Ktarget = std::vector<double>( matrixFree.ndof, 0.0 );
    auto u1 = std::vector<double>( matrixFree.ndof, 0.0 );
    auto u2 = std::vector<double>( matrixFree.ndof, 0.0 );

    auto domain = implicit::invert( implicit::sphere<D>( origin + lengths / 2.0, 0.3 * array::minElement( lengths ) ) );
    auto density = initializeDensity<D>( domain, nelements, lengths, origin, P, 1.0, 0.1 );
    
    auto initial = matrixFree.computeInitial( sourceX, density );
	
    auto& invMass = std::get<0>( initial );
    auto& fs = std::get<1>( initial );
	
    auto checkpoint = utilities::tic( );

    if( postprocess )
    {
        std::cout << "Writing step " << 0 << std::endl;

        postprocessSolution<D, P>( "outputs/matrix_free_0", nelements, lengths, origin, u2 );
    }

    #pragma omp parallel
    {
        for( size_t istep = 0; istep < nsteps; ++istep )
        {
            auto ft = sourceT( ( istep + 1 ) * deltaT );

            matrixFree.computeRhs( u2, density, Ktarget );

            #pragma omp for schedule(static)
            for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( matrixFree.ndof ); ++ii )
            {
                auto idof = static_cast<size_t>( ii );

                u1[idof] = 2 * u2[idof] - u1[idof] + invMass[idof] * ( ft * fs[idof] - Ktarget[idof] );
                Ktarget[idof] = 0.0;
            }

            #pragma omp barrier
            { }

            #pragma omp single
            {
                std::swap( u1, u2 );
            }

            if( postprocess && ( istep + 1 ) % interval == 0 )
            {
                #pragma omp single
                {
                    std::cout << "Writing step " << istep + 1 << std::endl;

                    auto filename = "outputs/matrix_free_" + std::to_string( ( istep + 1 ) / interval );

                    postprocessSolution<D, P>( filename, nelements, lengths, origin, u2 );
                }
            }
        }
    }

    auto seconds = utilities::toc( checkpoint );

    std::cout << "Took " << seconds << " seconds" << std::endl;
    std::cout << "Dofs / second: " << nsteps * u2.size( ) / seconds << std::endl;
}

// Hack for postprocessing results though multilevel-hp basis
template<size_t D, size_t P>
void postprocessSolution( std::string filename,
                          std::array<size_t, D> nelements,
                          std::array<double, D> lengths,
                          std::array<double, D> origin,
                          const std::vector<double>& dofs )
{
    auto mesh = makeRefinedGrid( nelements, lengths, origin );
    auto basis = makeHpBasis<TensorSpace>( mesh, P );
    auto GLL = gaussLobattoPoints( P + 1 )[0];

    PolynomialBasis polynomialBasis = [=]( size_t p, size_t maxDiff, double r, double* target )
    {
        MLHP_CHECK( p == P && maxDiff == 0, "Inconsistent degree or diff order." );

        target[0] = polynomial::lagrange( GLL, 0, r, 0 );
        target[1] = polynomial::lagrange( GLL, P, r, 0 );

        for( size_t i = 1; i < P; ++i )
        {
            target[i + 1] = polynomial::lagrange( GLL, i, r, 0 );
        }
    };

    basis->setPolynomialBases( array::make<D>( polynomialBasis ) );

    auto transformedDofs = std::vector<double>( basis->ndof( ), 0.0 );
    auto basisLM = LocationMap { };
    auto dofStrides = nd::stridesFor( array::add( array::multiply( nelements, P ), size_t { 1 } ) );

    nd::executeWithIndex( nelements, [&]( std::array<size_t, D> ijkElement, size_t ielement )
    {
        basis->locationMap( static_cast<CellIndex>( ielement ), utilities::resize0( basisLM ) );

        nd::executeWithIndex(  array::makeSizes<D>( P + 1 ), [&]( std::array<size_t, D> ijkTP, size_t index )
        {
            // Move right nodal shape function (index 1) to P, shift others to the left
            for( size_t axis = 0; axis < D; ++axis )
            {
                auto ind = ijkTP[axis];

                if( ind == 1 ) ijkTP[axis] = P;
                if( ind > 1 ) ijkTP[axis] -= 1;
            }   

            auto matrixFreeIndex = nd::linearIndex( dofStrides, array::add( array::multiply( ijkElement, P ), ijkTP ) );

            transformedDofs[basisLM[index]] = dofs[matrixFreeIndex];
        } );
    } );

    auto resolution = cellmesh::grid<D>( array::makeSizes<D>( P > 1 ? P + 3 : 1 ) );

    writeOutput( *basis, resolution, makeSolutionProcessor<D>( transformedDofs ), PVtuOutput { filename } );
}
