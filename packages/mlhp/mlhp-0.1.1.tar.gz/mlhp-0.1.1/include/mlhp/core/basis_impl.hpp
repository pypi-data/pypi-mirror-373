// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_BASIS_IMPL_HPP
#define MLHP_CORE_BASIS_IMPL_HPP

namespace mlhp
{

template<typename BasisType, size_t D> inline
MultilevelHpBasisSharedPtr<D> makeHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                           const PolynomialDegreeTuple& degrees, 
                                           size_t nfields )
{
    return makeHpBasis<BasisType>( grid, UniformGrading { degrees }, nfields );
}

template<typename BasisType, GradingConcept GradingType, size_t D> inline
MultilevelHpBasisSharedPtr<D> makeHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                           const GradingType& grading, 
                                           size_t nfields )
{
    return makeHpBasisFactory<BasisType, D>( grading )( grid, nfields );
}

template<typename BasisType, size_t D> inline
MultilevelHpBasisSharedPtr<D> makeHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                           const PolynomialDegreeDistributor<D>& degrees,
                                           size_t nfields )
{
    return makeHpBasisFactory<BasisType>( degrees )( grid, nfields );
}

template<typename BasisType, size_t D> inline
MultilevelHpBasisFactory<D> makeHpBasisFactory( const PolynomialDegreeTuple& degrees )
{
    return makeHpBasisFactory<BasisType, D>( UniformGrading { degrees } );
}

template<typename BasisType, size_t D, GradingConcept GradingType> inline
MultilevelHpBasisFactory<D> makeHpBasisFactory( const GradingType& grading )
{
    return makeHpBasisFactory<BasisType, D>( PolynomialDegreeDistributor<D> { grading } );
}

template<typename BasisType, size_t D> inline
MultilevelHpBasisFactory<D> makeHpBasisFactory( const PolynomialDegreeDistributor<D>& degrees )
{
    return [=]( const HierarchicalGridSharedPtr<D>& grid, size_t nfields )
    {
        auto basisType = BasisType::template initialMaskProvider<D>( );

        return std::make_shared<MultilevelHpBasis<D>>( grid, degrees( *grid, nfields ), basisType );
    };
}

template<size_t D> inline
std::shared_ptr<BSplineBasis<D>> makeBSplineBasis( std::shared_ptr<const CartesianGrid<D>> grid,
                                                   std::array<size_t, D> degrees,
                                                   std::array<size_t, D> continuities,
                                                   size_t nfields )
{
    return std::make_shared<BSplineBasis<D>>( grid, 
        std::vector<std::array<size_t, D>>( nfields, degrees ), 
        std::vector<std::array<size_t, D>>( nfields, continuities ) );
}

template<size_t D> inline
std::shared_ptr<BSplineBasis<D>> makeBSplineBasis( std::shared_ptr<const CartesianGrid<D>> grid,
                                                   size_t degree,
                                                   size_t continuity,
                                                   size_t nfields )
{
    return makeBSplineBasis( grid, array::make<D>( degree ), array::make<D>( continuity ), nfields );
}

template<size_t D>
struct ElementFilterBasis<D>::Cache
{
    BasisEvaluationCache<D> otherCache;
    MeshMapping<D> mapping;
};

template<size_t D> inline
BasisEvaluationCache<D> ElementFilterBasis<D>::createEvaluationCache( ) const
{
    auto mapping = MeshMapping<D> {  };

    mapping.mesh = mesh_.get( );

    return Cache { basis_->createEvaluationCache( ), std::move( mapping ) };
}

template<size_t D> inline
std::array<size_t, D> ElementFilterBasis<D>::prepareEvaluation( CellIndex ielement,
                                                                size_t maxDiffOrder,
                                                                BasisFunctionEvaluation<D>& shapes,
                                                                BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    cache.mapping.icell = ielement;

    auto orders = basis_->prepareEvaluation( mesh_->unfilteredIndex( ielement ), 
        maxDiffOrder, shapes, cache.otherCache );
    
    shapes.setElementIndex( mesh_->filteredIndex( shapes.elementIndex( ) ) );

    return orders;
}

template<size_t D> inline
void ElementFilterBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                                   BasisEvaluationCache<D>& cache ) const
{
    basis_->prepareGridEvaluation( rst, utilities::cast<Cache>( cache ).otherCache );
}

template<size_t D> inline
void ElementFilterBasis<D>::evaluateGridPoint( std::array<size_t, D> ijk,
                                               BasisFunctionEvaluation<D>& shapes,
                                               BasisEvaluationCache<D>& cache ) const
{
    shapes.setElementIndex( mesh_->unfilteredIndex( shapes.elementIndex( ) ) );

    basis_->evaluateGridPoint( ijk, shapes, utilities::cast<Cache>( cache ).otherCache );
    
    shapes.setElementIndex( mesh_->filteredIndex( shapes.elementIndex( ) ) );
}

template<size_t D> inline
void ElementFilterBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                                 BasisFunctionEvaluation<D>& shapes,
                                                 BasisEvaluationCache<D>& cache ) const
{
    shapes.setElementIndex( mesh_->unfilteredIndex( shapes.elementIndex( ) ) );

    basis_->evaluateSinglePoint( rst, shapes, utilities::cast<Cache>( cache ).otherCache );
    
    shapes.setElementIndex( mesh_->filteredIndex( shapes.elementIndex( ) ) );
}

template<size_t D> inline
const MeshMapping<D>& ElementFilterBasis<D>::mapping( BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );
    auto& filteredMapping = basis_->mapping( cache.otherCache );

    cache.mapping.mapping = filteredMapping.mapping;
    cache.mapping.type = filteredMapping.type;

    return cache.mapping;
}

template<size_t D> inline
void ElementFilterBasis<D>::locationMap( CellIndex ielement,
                                         LocationMap& locationMap ) const
{
    auto begin = locationMap.size( );

    basis_->locationMap( mesh_->unfilteredIndex( ielement ), locationMap );

    for( auto index = begin; index < locationMap.size( ); ++index )
    {
        locationMap[index] = reductionMap_[locationMap[index]];

        MLHP_CHECK_DBG( locationMap[index] != NoDof, "Eliminated dof part of location map." );
    }
}

template<size_t D> inline
DofIndex ElementFilterBasis<D>::faceDofs( CellIndex ielement,
                                          size_t iface,
                                          size_t ifield,
                                          std::vector<size_t>& localDofs ) const
{
    return basis_->faceDofs( mesh_->unfilteredIndex( ielement ), iface, ifield, localDofs );
}

template<size_t D> inline
std::array<size_t, D> ElementFilterBasis<D>::maxdegrees( CellIndex ielement ) const
{
    return basis_->maxdegrees( mesh_->unfilteredIndex( ielement ) );
}

template<size_t D> inline
DofIndex ElementFilterBasis<D>::ndof( ) const
{
    return ndof_;
}

template<size_t D> inline
CellIndex ElementFilterBasis<D>::nelements( ) const
{
    return mesh_->ncells( );
}

template<size_t D> inline
DofIndex ElementFilterBasis<D>::ndofelement( CellIndex ielement ) const
{
    return basis_->ndofelement( mesh_->unfilteredIndex( ielement ) );
}

template<size_t D> inline
DofIndex ElementFilterBasis<D>::ndofelement( CellIndex ielement, size_t fieldIndex ) const
{
    return basis_->ndofelement( mesh_->unfilteredIndex( ielement ), fieldIndex );
}


template<size_t D> inline
size_t ElementFilterBasis<D>::nfields( ) const
{
    return basis_->nfields( );
}

template<size_t D> inline
const AbsMesh<D>& ElementFilterBasis<D>::mesh( ) const
{
    return *mesh_;
}

template<size_t D> inline
const AbsFilteredMesh<D>& ElementFilterBasis<D>::filteredMesh( ) const
{
    return *mesh_;
}

template<size_t D> inline
const AbsBasis<D>& ElementFilterBasis<D>::unfilteredBasis( ) const
{
    return *basis_;
}

template<size_t D> inline
DofOffsetBasis<D>::DofOffsetBasis( BasisPtr basis, DofIndex offset, DofIndex ndof ) :
    basis_ { basis }, offset_ { offset }, 
    ndof_ { ndof == NoDof ? basis->ndof( ) + offset : ndof }
{ }

template<size_t D> inline
const AbsBasis<D>& DofOffsetBasis<D>::basis( ) const
{
    return *basis_;
}

template<size_t D> inline
const AbsMesh<D>& DofOffsetBasis<D>::mesh( ) const
{
    return basis_->mesh( );
}

template<size_t D> inline
DofIndex DofOffsetBasis<D>::offset( ) const
{
    return offset_;
}

template<size_t D> inline
CellIndex DofOffsetBasis<D>::nelements( ) const
{
    return basis_->nelements( );
}

template<size_t D> inline
DofIndex DofOffsetBasis<D>::ndof( ) const
{
    return ndof_;
}

template<size_t D> inline
DofIndex DofOffsetBasis<D>::ndofelement( CellIndex ielement ) const
{
    return basis_->ndofelement( ielement );
}

template<size_t D> inline
DofIndex DofOffsetBasis<D>::ndofelement( CellIndex ielement, size_t ifield ) const
{
    return basis_->ndofelement( ielement, ifield );
}

template<size_t D> inline
size_t DofOffsetBasis<D>::nfields( ) const
{
    return basis_->nfields( );
}

template<size_t D> inline
std::array<size_t, D> DofOffsetBasis<D>::maxdegrees( CellIndex ielement ) const
{
    return basis_->maxdegrees( ielement );
}

template<size_t D> inline
void DofOffsetBasis<D>::locationMap( CellIndex ielement,
                                     LocationMap& locationMap ) const
{
    auto begin = locationMap.size( );

    basis_->locationMap( ielement, locationMap );

    for( auto index = begin; index < locationMap.size( ); ++index )
    {
        locationMap[index] += offset_;
    }
}

template<size_t D> inline
DofIndex DofOffsetBasis<D>::faceDofs( CellIndex ielement,
                                      size_t iface, 
                                      size_t ifield,
                                      std::vector<size_t>& localDofs ) const
{
    return basis_->faceDofs( ielement, iface, ifield, localDofs );
}

template<size_t D> inline
BasisEvaluationCache<D> DofOffsetBasis<D>::createEvaluationCache( ) const
{       
    return basis_->createEvaluationCache( );
}

template<size_t D> inline
std::array<size_t, D> DofOffsetBasis<D>::prepareEvaluation( CellIndex ielement,
                                                            size_t maxDiffOrder,
                                                            BasisFunctionEvaluation<D>& shapes,
                                                            BasisEvaluationCache<D>& anyCache ) const
{
    return basis_->prepareEvaluation( ielement, maxDiffOrder, shapes, anyCache );
}

template<size_t D> inline
void DofOffsetBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                             BasisFunctionEvaluation<D>& shapes,
                                             BasisEvaluationCache<D>& anyCache ) const
{
    return basis_->evaluateSinglePoint( rst, shapes, anyCache );
}

template<size_t D> inline
void DofOffsetBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                               BasisEvaluationCache<D>& anyCache ) const
{
    return basis_->prepareGridEvaluation( rst, anyCache );
}

template<size_t D> inline
void DofOffsetBasis<D>::evaluateGridPoint( std::array<size_t, D> ijk,
                                           BasisFunctionEvaluation<D>& shapes,
                                           BasisEvaluationCache<D>& anyCache ) const
{
    return basis_->evaluateGridPoint( ijk, shapes, anyCache );
}

template<size_t D> inline
const MeshMapping<D>& DofOffsetBasis<D>::mapping( BasisEvaluationCache<D>& anyCache ) const
{
    return basis_->mapping( anyCache );
}

} // namespace mlhp

#endif // MLHP_CORE_BASIS_IMPL_HPP
