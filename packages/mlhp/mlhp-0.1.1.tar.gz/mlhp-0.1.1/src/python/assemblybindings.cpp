// This file is part of the mlhp project. License: See LICENSE

#include "pybind11/pybind11.h"
#include "pybind11/functional.h"
#include "pybind11/stl.h"

#include "src/python/pymlhpcore.hpp"

#include "mlhp/core/assembly.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/integrands.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/mapping.hpp"
#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/boundary.hpp"

namespace mlhp::bindings
{

template<size_t D>
void bindAssemblyDimension( pybind11::module& m )
{
    using MatrixVariant = std::variant<linalg::UnsymmetricSparseMatrix, linalg::SymmetricSparseMatrix>;

    auto allocateSparseMatrixF = []( const AbsBasis<D>& basis,
                                     const DofIndexVector& dirichletDofs,
                                     bool symmetric ) -> MatrixVariant
    {
        if( symmetric ) 
        {
            return allocateMatrix<linalg::SymmetricSparseMatrix>( basis, dirichletDofs );
        }
        else
        {
            return allocateMatrix<linalg::UnsymmetricSparseMatrix>( basis, dirichletDofs );
        }
    };

    m.def( "allocateSparseMatrix", allocateSparseMatrixF, pybind11::arg( "basis" ), 
        pybind11::arg( "dirichletDofs" ) = DofIndexVector { }, pybind11::arg( "symmetric" ) = false );

    using PythonAssemblyTarget = std::variant
    <
        ScalarDouble*,
        DoubleVector*,
        linalg::UnsymmetricSparseMatrix*,
        linalg::SymmetricSparseMatrix*
    >;

    auto convertTargets = []( const std::vector<PythonAssemblyTarget>& pythonTargets )
    { 
        AssemblyTargetVector targets; 

        for( size_t i = 0; i < pythonTargets.size( ); ++i )
        {
            if( pythonTargets[i].index( ) == 0 ) 
                targets.push_back( std::get<ScalarDouble*>( pythonTargets[i] )->get( ) );
            else if( pythonTargets[i].index( ) == 1 ) 
                targets.push_back( std::get<DoubleVector*>( pythonTargets[i] )->get( ) );
            else if( pythonTargets[i].index( ) == 2 )
                targets.push_back( *std::get<linalg::UnsymmetricSparseMatrix*>( pythonTargets[i] ) );
            else if( pythonTargets[i].index( ) == 3 )
                targets.push_back( *std::get<linalg::SymmetricSparseMatrix*>( pythonTargets[i] ) );
        }

        return targets;
    };

    m.def( "integrateOnDomain", [convertTargets]( const AbsBasis<D>& basis,
                                                  const DomainIntegrand<D>& integrand,
                                                  const std::vector<PythonAssemblyTarget>& targets,
                                                  const AbsQuadrature<D>& quadrature,
                                                  const QuadratureOrderDeterminorWrapper<D>& orderDeterminor,
                                                  const DofIndicesValuesPair& boundaryDofs,
                                                  size_t chunksize )
        { 
            return integrateOnDomain( basis, integrand, convertTargets( targets ),
                quadrature, orderDeterminor.get( ), boundaryDofs, chunksize );
        },
        pybind11::arg( "basis" ),
        pybind11::arg( "integrand" ),
        pybind11::arg( "targets" ),
        pybind11::arg( "quadrature" ) = StandardQuadrature<D> { },
        pybind11::arg( "orderDeterminor" ) = QuadratureOrderDeterminorWrapper<D>{ relativeQuadratureOrder<D>( 1 ) },
        pybind11::arg( "dirichletDofs" ) = DofIndicesValuesPair { },
        pybind11::arg( "chunksize" ) = 1
    );
    
    m.def( "projectOnto", []( const AbsBasis<D>& basis,
                              const ScalarFunctionWrapper<D>& function )
           { return DoubleVector ( projectOnto<D>( basis, function ) ); } );
    
    m.def( "projectOnto", []( const AbsBasis<D>& basis,
                              const spatial::VectorFunction<D>& function )
           { return DoubleVector ( projectOnto<D>( basis, function ) ); } );
    
    m.def( "integrateOnDomain", [convertTargets]( const MultilevelHpBasis<D>& basis0,
                                                  const MultilevelHpBasis<D>& basis1,
                                                  const BasisProjectionIntegrand<D>& integrand,
                                                  const std::vector<PythonAssemblyTarget>& globalTargets,
                                                  const AbsQuadrature<D>& quadrature,
                                                  const QuadratureOrderDeterminorWrapper<D>& orderDeterminor,
                                                  const DofIndicesValuesPair& boundaryDofs,
                                                  size_t chunksize )
        { 
            integrateOnDomain( basis0, basis1, integrand, convertTargets( globalTargets ),
                quadrature, orderDeterminor.get( ), boundaryDofs, chunksize );
        },
        pybind11::arg( "basis0" ),
        pybind11::arg( "basis1" ),
        pybind11::arg( "integrand" ),
        pybind11::arg( "targets" ),
        pybind11::arg( "quadrature" ) = StandardQuadrature<D> { },
        pybind11::arg( "orderDeterminor" ) = QuadratureOrderDeterminorWrapper<D>{ relativeQuadratureOrder<D>( 1 ) },
        pybind11::arg( "dirichletDofs" ) = DofIndicesValuesPair { },
        pybind11::arg( "chunksize" ) = 1 
    );

    auto absoluteQuadratureOrderF = []( std::array<size_t, D> orders )
    { 
        return QuadratureOrderDeterminorWrapper<D> { absoluteQuadratureOrder( orders ) };
    };

    m.def( "absoluteQuadratureOrder", absoluteQuadratureOrderF, pybind11::arg( "orders" ), 
           "Disregards input degree and simply returns orders." );

    // Surface support providers
    {
        pybind11::class_<EvaluateQuadraturePartition2<D>, std::shared_ptr<EvaluateQuadraturePartition2<D>>>
            qudraturePartition( m, add<D>( "QuadraturePartition_2_" ).c_str( ) );

        qudraturePartition.def_readwrite( "rst", &EvaluateQuadraturePartition2<D>::rst );
        qudraturePartition.def_readwrite( "xyz", &EvaluateQuadraturePartition2<D>::xyz );
        qudraturePartition.def_readwrite( "weights", &EvaluateQuadraturePartition2<D>::weights );
        qudraturePartition.def_readwrite( "isgrid", &EvaluateQuadraturePartition2<D>::isgrid );
        qudraturePartition.def_readwrite( "normals", &EvaluateQuadraturePartition2<D>::normals );
        qudraturePartition.def_readwrite( "icell", &EvaluateQuadraturePartition2<D>::icell );

        [[maybe_unused]] auto absQuadratureC = pybind11::class_<AbsQuadratureOnMesh<D>, 
            std::shared_ptr<AbsQuadratureOnMesh<D>>>( m, add<D>( "AbsQuadratureOnMesh" ).c_str( ) );
        
        auto evaluateF = pybind11::overload_cast<const AbsQuadratureOnMesh<D>&, const AbsMesh<D>&,
            CellIndex, std::array<size_t, D>>( &evaluateQuadrature<D> );

        absQuadratureC.def( "evaluate", evaluateF, pybind11::arg( "mesh" ),
            pybind11::arg( "icell" ), pybind11::arg( "orders" ) );

        if constexpr ( D <= 3 )
        {
            [[maybe_unused]]
            auto simplexQuadratureC = pybind11::class_<SimplexQuadrature<D>,
                std::shared_ptr<SimplexQuadrature<D>>, AbsQuadratureOnMesh<D>>(
                    m, add<D>( "SimplexQuadrature" ).c_str( ) );

            auto simplexQuadratureF = []( std::shared_ptr<const SimplexMesh<D, D - 1>> mesh,
                                          std::shared_ptr<const SimplexCellAssociation<D>> celldata,
                                          const QuadratureOrderDeterminorWrapper<D>& order )
            { 
                return std::make_shared<SimplexQuadrature<D>>( std::move( mesh ), std::move( celldata ), order.get( ) );
            };

            m.def( "simplexQuadrature", simplexQuadratureF, pybind11::arg( "simplexMesh" ),
                   pybind11::arg( "celldata" ), pybind11::arg( "order" ) = 
                   QuadratureOrderDeterminorWrapper<D>{ relativeQuadratureOrder<D>( 3 ) } );
        }

        [[maybe_unused]] auto meshBoundaryQuadratureC = pybind11::class_<boundary::QuadratureOnMeshFaces<D>, 
            std::shared_ptr<boundary::QuadratureOnMeshFaces<D>>, AbsQuadratureOnMesh<D>>( 
                m, add<D>( "QuadratureOnMeshFaces" ).c_str( ) );

        auto quadratureOnMeshFacesF = []( const AbsMesh<D>& mesh,
                                          const std::vector<size_t>& meshFaces,
                                          const QuadratureOrderDeterminorWrapper<D>& order )
        {
            return std::make_shared<boundary::QuadratureOnMeshFaces<D>>( mesh, meshFaces, order.get( ) );
        };

        m.def( "quadratureOnMeshFaces", quadratureOnMeshFacesF, pybind11::arg( "mesh" ), 
            pybind11::arg( "meshFaces" ), pybind11::arg( "order" ) = 
               QuadratureOrderDeterminorWrapper<D>{ relativeQuadratureOrder<D>( 1 ) } );
    }

    auto integrateOnSurfaceF = [convertTargets]( const AbsBasis<D>& basis,
                                                 const SurfaceIntegrand<D>& integrand,
                                                 const std::vector<PythonAssemblyTarget>& globalTargets,
                                                 const AbsQuadratureOnMesh<D>& quadrature,
                                                 const DofIndicesValuesPair& boundaryDofs,
                                                 size_t chunksize )
    {
        integrateOnSurface( basis, integrand, quadrature,
            convertTargets( globalTargets ), boundaryDofs, chunksize );
    };

    m.def( "integrateOnSurface", integrateOnSurfaceF, pybind11::arg( "basis" ), 
        pybind11::arg( "integrand" ), pybind11::arg( "globalTargets" ), 
        pybind11::arg( "quadrature" ), pybind11::arg( "dirichletDofs" ) = DofIndicesValuesPair { },
        pybind11::arg( "chunksize" ) = 1 );

    [[maybe_unused]] auto surfaceIntegrand = pybind11::class_<SurfaceIntegrand<D>>
        ( m, add<D>( "SurfaceIntegrand" ).c_str( ) );

    // Surface integrands
    {
        auto neumannIntegrandF1 = []( const spatial::VectorFunction<D>& rhs )
        {
            return makeNeumannIntegrand( rhs );
        };

        auto neumannIntegrandF2 = []( const ScalarFunctionWrapper<D>& rhs, size_t ifield )
        {
            return makeNeumannIntegrand( rhs.get( ), ifield );
        };

        auto normalneumannIntegrandF = []( const ScalarFunctionWrapper<D>& rhs )
        {
            return makeNormalNeumannIntegrand( rhs.get( ) );
        };
    
        auto l2BoundaryIntegrandF1 = []( const spatial::VectorFunction<D>& lhs,
                                         const spatial::VectorFunction<D>& rhs )
        {
            return makeL2BoundaryIntegrand( lhs, rhs );
        };

        auto l2BoundaryIntegrandF2 = []( const ScalarFunctionWrapper<D>& lhs,
                                         const ScalarFunctionWrapper<D>& rhs,
                                         size_t ifield )
        {
            return makeL2BoundaryIntegrand( lhs.get( ), rhs.get( ), ifield );
        };

        auto l2BoundaryIntegrandF3 = []( const spatial::VectorFunction<D>& lhs,
                                         const spatial::VectorFunction<D>& rhs,
                                         const DoubleVector& dofs,
                                         bool computeTangent )
        {
            return makeL2BoundaryIntegrand( lhs, rhs, dofs.getShared( ), computeTangent);
        };

        auto l2BoundaryIntegrandF4 = []( const ScalarFunctionWrapper<D>& lhs,
                                         const ScalarFunctionWrapper<D>& rhs,
                                         const DoubleVector& dofs,
                                         size_t ifield,
                                         bool computeTangent )
        {
            return makeL2BoundaryIntegrand( lhs.get( ), rhs.get( ), dofs.getShared( ), ifield, computeTangent );
        };

        auto l2NormalIntegrandF = []( std::optional<ScalarFunctionWrapper<D>> lhs,
                                      std::optional<ScalarFunctionWrapper<D>> rhs,
                                      std::optional<std::shared_ptr<DoubleVector>> dofs )
        {
            using OptionalFunction = std::optional<spatial::ScalarFunction<D>>;

            auto optionalLhs = lhs ? OptionalFunction { lhs->get( ) } : OptionalFunction { std::nullopt };
            auto optionalRhs = rhs ? OptionalFunction { rhs->get( ) } : OptionalFunction { std::nullopt };

            if( !dofs ) // Linear
            {
                return makeL2NormalIntegrand<D>( optionalLhs, optionalRhs );
            }
            else // Nonlinear
            {
                return makeL2NormalIntegrand<D>( optionalLhs, optionalRhs, ( *dofs )->getShared( ) );
            }
        };

        auto nitscheIntegrandF1 = []( std::shared_ptr<const KinematicEquation<D>> kinematics,
                                      std::shared_ptr<const ConstitutiveEquation<D>> constitutive,
                                      const spatial::VectorFunction<D>& function,
                                      double beta, 
                                      std::optional<std::shared_ptr<DoubleVector>> dofs )
        { 
            if( !dofs )
            {
                return makeNitscheIntegrand<D>( kinematics, constitutive, function, beta );
            }
            else
            {
                return makeNitscheIntegrand<D>( kinematics, constitutive, ( *dofs )->getShared( ), function, beta );
            }
        };

        auto reactionForceIntegrandF = []( std::shared_ptr<const KinematicEquation<D>> kinematics,
                                           std::shared_ptr<const ConstitutiveEquation<D>> constitutive,
                                           const DoubleVector& dofs )
        { 
            return makeReactionForceIntegrand<D>( kinematics, constitutive, dofs.getShared( ) );
        };

        auto makeFunctionSurfaceIntegrandF = []( const ScalarFunctionWrapper<D>& function )
        { 
            return makeFunctionSurfaceIntegrand<D>( function.get( ) );
        };

        m.def( "neumannIntegrand", neumannIntegrandF1, pybind11::arg( "rhs" ) );
        m.def( "neumannIntegrand", neumannIntegrandF2, pybind11::arg( "rhs" ), pybind11::arg( "ifield" ) = 0 );
        m.def( "normalNeumannIntegrand", normalneumannIntegrandF, pybind11::arg( "rhs" ) );
        m.def( "l2BoundaryIntegrand", l2BoundaryIntegrandF1, pybind11::arg( "lhs" ), pybind11::arg( "rhs" ) );
        m.def( "l2BoundaryIntegrand", l2BoundaryIntegrandF2, pybind11::arg( "lhs" ), pybind11::arg( "rhs" ),
            pybind11::arg( "ifield" ) = 0 );
        m.def( "l2BoundaryIntegrand", l2BoundaryIntegrandF3, pybind11::arg( "lhs" ), pybind11::arg( "rhs" ),
            pybind11::arg( "dofs" ), pybind11::arg( "computeTangent" ) = true );
        m.def( "l2BoundaryIntegrand", l2BoundaryIntegrandF4, pybind11::arg( "lhs" ), pybind11::arg( "rhs" ),
            pybind11::arg( "dofs" ), pybind11::arg( "ifield" ) = 0, pybind11::arg( "computeTangent" ) = true );
        m.def( "l2NormalIntegrand", l2NormalIntegrandF, pybind11::arg( "lhs" ) = std::nullopt, 
            pybind11::arg( "rhs" ) = std::nullopt, pybind11::arg( "dofs" ) = std::nullopt,
            "Corresponding weak residual: m * <du, n> * (<u, n> - r)" );
        m.def( "nitscheIntegrand", nitscheIntegrandF1, pybind11::arg( "kinematics" ), pybind11::arg( "constitutive" ), 
               pybind11::arg( "function" ) = spatial::VectorFunction<D> { spatial::constantFunction<D>( array::make<D>( 0.0 ) ) },
               pybind11::arg( "beta" ) = 0.0, pybind11::arg( "dofs" ) = std::nullopt );
        m.def( "reactionForceIntegrand", reactionForceIntegrandF, pybind11::arg( "kinematics" ), 
            pybind11::arg( "constitutive" ), pybind11::arg( "dofs" ) );
        m.def( "normalDotProductIntegrand", &makeNormalDotProductIntegrand<D>, pybind11::arg( "function" ) );
        m.def( "functionSurfaceIntegrand", pybind11::overload_cast<const spatial::VectorFunction<D>&>( 
            &makeFunctionSurfaceIntegrand<D> ), pybind11::arg( "function" ) );
        m.def( "functionSurfaceIntegrand", makeFunctionSurfaceIntegrandF, pybind11::arg( "function" ) );
    }

    auto projectGradientF = []( const AbsBasis<D>& basis, 
                                const DoubleVector& dofs, 
                                const AbsQuadrature<D>& quadrature,
                                const ScalarFunctionWrapper<D>& weight )
    { 
        auto solver = linalg::makeCGSolver( 1e-12, 0.0, std::max( static_cast<size_t>( 2 * basis.ndof( ) ), size_t { 5000 } ) );
        auto gradient = projectGradient( basis, dofs.get( ), quadrature, solver, weight.get( ) );
        auto converted = std::array<std::shared_ptr<DoubleVector>, D> { };

        for( size_t axis = 0; axis < D; ++axis )
        {
            converted[axis] = std::make_shared<DoubleVector>( std::move( gradient[axis] ) );
        }

        return converted;
    };

    m.def( "projectGradient", projectGradientF, pybind11::arg( "basis" ), pybind11::arg( "dofs" ),
        pybind11::arg( "quadrature" ) = StandardQuadrature<D> { }, 
        pybind11::arg( "weight" ) = ScalarFunctionWrapper<D> { spatial::constantFunction<D>( 1.0 ) } );
}

template<size_t... D>
void bindAssemblyDimensions( pybind11::module& m, std::index_sequence<D...>&& )
{
    [[maybe_unused]] std::initializer_list<int> tmp { ( bindAssemblyDimension<D + 1>( m ), 0 )... };
}

void bindAssemblyDimensionIndependent( pybind11::module& m )
{
    using QuadratureOrderVariant = DimensionVariant<QuadratureOrderDeterminorWrapper>;

    auto relativeQuadratureOrderF = []( size_t ndim, int offset, double factor )
    { 
        auto create = [&]<size_t D>( ) -> QuadratureOrderVariant {
            return QuadratureOrderDeterminorWrapper<D> { 
                relativeQuadratureOrder<D>( offset, factor ) }; };

        return dispatchDimension( create, ndim );
    };

    m.def( "relativeQuadratureOrder", relativeQuadratureOrderF, pybind11::arg( "ndim" ),
           pybind11::arg( "offset" ), pybind11::arg( "factor" ) = 1.0, 
           "For given input degreee, returns max(ceil(degree * factor) + offset, 0)." );

    m.def( "allocateRhsVector", []( const linalg::AbsSparseMatrix& matrix )
    { 
        return DoubleVector( matrix.size1( ), 0.0 );
    } );
}

void bindCIntegrand( pybind11::module& m )
{
    using DomainIntegrandVariant = DimensionVariant<DomainIntegrand>;

    using CType = void( double**      targets,     double**      shapes,     double**      mapping, 
                        double*       rst,         double*       history,    double*       tmp, 
                        std::int64_t* locationMap, std::int64_t* totalSizes, std::int64_t* fieldSizes,
                        double        detJ,        double        weight,     std::int64_t  ielement );

    auto domainIntegrandFromAddressF = []( size_t ndim, std::uint64_t address,
                                           std::vector<AssemblyType> types,
                                           int diffOrder, size_t tmpdofs )
    { 
        auto create = [&]<size_t D>( ) -> DomainIntegrandVariant
        {
            using Cache = typename DomainIntegrand<D>::Cache;
        
            struct ThisCache
            {
                std::vector<std::int64_t> locationMap;
                std::vector<std::int64_t> fieldSizes;
                std::vector<double*> targetPtrs;
                std::vector<double*> shapesPtrs;
                const MeshMapping<D>* mapping;
                AlignedDoubleVector tmp;
            };

            auto ntargets = types.size( );

            auto createCache = [ntargets]( const AbsBasis<D>& )
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
                    cache.locationMap[idof] = static_cast<std::int64_t>( locationMap[idof] );
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

                    cache.fieldSizes[2 * ifield + 0] = static_cast<std::int64_t>( shapes.ndof( ifield ) );
                    cache.fieldSizes[2 * ifield + 1] = static_cast<std::int64_t>( shapes.ndofpadded( ifield ) );
                }

                auto rst = shapes.rst( );
                auto xyz = shapes.xyz( );
                auto J = cache.mapping->J( rst );
                auto mappingPtrs = std::array<double*, 2> { xyz.data( ), J.data( ) };
                auto totalSizes = std::array { static_cast<std::int64_t>( ndof ), static_cast<std::int64_t>( shapes.ndofpadded( ) ) };
                CType* callback = reinterpret_cast<CType*>( address );
            
                callback( cache.targetPtrs.data( ), cache.shapesPtrs.data( ), mappingPtrs.data( ), rst.data( ), 
                    nullptr, cache.tmp.data( ), cache.locationMap.data( ), totalSizes.data( ),
                    cache.fieldSizes.data( ), 1.0, weightDetJ, static_cast<std::int64_t>( shapes.elementIndex( ) ) );
            };

            return DomainIntegrand<D> { std::move( types ), static_cast<DiffOrders>( diffOrder ), 
                std::move( createCache ), std::move( prepare ), std::move( evaluate ) };
        };

        return dispatchDimension( std::move( create ), ndim );
    };

    m.def( "_domainIntegrandFromAddress", domainIntegrandFromAddressF );
}

void bindAssembly( pybind11::module& m )
{
    bindAssemblyDimensions( m, std::make_index_sequence<config::maxdim>( ) );

    bindAssemblyDimensionIndependent( m );
    bindCIntegrand( m );
}

} // mlhp::bindings

