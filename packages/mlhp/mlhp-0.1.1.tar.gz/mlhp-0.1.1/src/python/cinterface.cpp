// This file is part of the mlhp project. License: See LICENSE

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "src/python/helper.hpp"

#include "mlhp/core/integrands.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/mapping.hpp"

namespace mlhp::bindings
{

void bindIntegrands( pybind11::module& m )
{
    pybind11::enum_<AssemblyType>( m, "AssemblyType" )
        .value( "Scalar", AssemblyType::Scalar )
        .value( "Vector", AssemblyType::Vector )
        .value( "UnsymmetricMatrix", AssemblyType::UnsymmetricMatrix );

    using DomainIntegrandVariant = DimensionVariant<DomainIntegrand>;

    auto domainIntegrandFromAddressF = []( size_t ndim, std::uint64_t address,
                                           std::vector<AssemblyType> types,
                                           int diffOrder, size_t tmpdofs )
    { 
        auto create = [&]<size_t D>( ) { return [&]( ) -> DomainIntegrandVariant
        {
            using CType = void( double** targets,     double** shapes,     double** mapping, 
                                double*  rst,         double*  history,    double*  tmp, 
                                size_t*  locationMap, size_t*  totalSizes, size_t*  fieldSizes,
                                double   detJ,        double   weight,     size_t   ielement );

            using Cache = typename DomainIntegrand<D>::Cache;
        
            struct ThisCache
            {
                std::vector<size_t> locationMap;
                std::vector<size_t> fieldSizes;
                std::vector<double*> targetPtrs;
                std::vector<double*> shapesPtrs;
                const MeshMapping<D>* mapping;
                AlignedDoubleVector tmp;
            };

            auto ntargets = types.size( );

            auto createCache = [ntargets]( )
            { 
                auto cache = ThisCache { };

                cache.targetPtrs.resize( ntargets );

                return Cache { std::move( cache ) };
            };

            auto prepare = [tmpdofs]( Cache& anyCache, 
                                      const MeshMapping<D>& mapping, 
                                      const LocationMap& locationMap )
            {
                auto& cache = utilities::cast<ThisCache>( anyCache );

                cache.tmp.resize( tmpdofs * memory::paddedLength<double>( locationMap.size( ) ) );
                cache.locationMap.resize( locationMap.size( ) );
                cache.mapping = &mapping;

                for( size_t idof = 0; idof < locationMap.size( ); ++idof )
                {
                    cache.locationMap[idof] = static_cast<size_t>( locationMap[idof] );
                }
            };

            auto evaluate = [address, ntargets]( Cache& anyCache, const BasisFunctionEvaluation<D>& shapes,
                                                 AlignedDoubleVectors& targets, double weightDetJ )
            { 
                auto& cache = utilities::cast<ThisCache>( anyCache );
            
                auto ndof = static_cast<size_t>( shapes.ndof( ) );
                auto nfields = shapes.nfields( );

                if( cache.shapesPtrs.empty( ) )
                {
                    cache.shapesPtrs.resize( nfields );
                    cache.fieldSizes.resize( nfields * 2 );
                }
     
                for( size_t itarget = 0; itarget < ntargets; ++itarget )
                {
                    cache.targetPtrs[itarget] = targets[itarget].data( );
                }

                for( size_t ifield = 0; ifield < nfields; ++ifield )
                {
                    cache.shapesPtrs[ifield] = const_cast<double*>( shapes.get( ifield, 0 ) );

                    cache.fieldSizes[2 * ifield + 0] = shapes.ndof( ifield );
                    cache.fieldSizes[2 * ifield + 1] = shapes.ndofpadded( ifield );
                }

                auto rst = shapes.rst( );
                auto xyz = shapes.xyz( );
                auto J = cache.mapping->J( rst );
                auto mappingPtrs = std::array<double*, 2> { xyz.data( ), J.data( ) };
                auto totalSizes = std::array { ndof, static_cast<size_t>( shapes.ndofpadded( ) ) };
                auto callback = reinterpret_cast<CType*>( address );
            
                callback( cache.targetPtrs.data( ), cache.shapesPtrs.data( ), mappingPtrs.data( ), rst.data( ), 
                    nullptr, cache.tmp.data( ), cache.locationMap.data( ), totalSizes.data( ), 
                    cache.fieldSizes.data( ), 1.0, weightDetJ, static_cast<size_t>( shapes.elementIndex( ) ) );
            };

            return DomainIntegrand<D> { std::move( types ), static_cast<DiffOrders>( diffOrder ), 
                std::move( createCache ), std::move( prepare ), std::move( evaluate ) };
        }; };

        return createDimensionDispatch( std::move( create ) )( ndim )( );
    };

    m.def( "_domainIntegrandFromAddress", domainIntegrandFromAddressF );
}

} // mlhp::bindings

