// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_BASIS_HPP
#define MLHP_CORE_BASIS_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/ndarray.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/alias.hpp"

#include <type_traits>

namespace mlhp
{

template<size_t D>
using BasisEvaluationCache = utilities::Cache<AbsBasis<D>>;

template<size_t D>
class AbsBasis : utilities::DefaultVirtualDestructor
{
public:
    virtual const AbsMesh<D>& mesh( ) const = 0;
    virtual MeshConstSharedPtr<D> meshPtr( ) const = 0;

    virtual CellIndex nelements( ) const = 0;
    
    virtual DofIndex ndof( ) const = 0;
    virtual DofIndex ndofelement( CellIndex ielement ) const = 0;
    virtual DofIndex ndofelement( CellIndex ielement, size_t ifield ) const = 0;

    virtual size_t nfields( ) const = 0;

    //! Highest polynomial orders in each local coordinate direction
    virtual std::array<size_t, D> maxdegrees( CellIndex ielement ) const = 0;

    //! Append the global dof indices for all element dofs. Does not clear previous entries in locationMap.
    virtual void locationMap( CellIndex ielement,
                              LocationMap& locationMap ) const = 0;

    //! Append indices of local dofs that are non-zero on the given face. Returns the offset 
    //! for the given field component. Does not clear previous entries in localDofs.
    virtual DofIndex faceDofs( CellIndex ielement,
                               size_t iface, 
                               size_t ifield,
                               std::vector<size_t>& localDofs ) const = 0;

    // ---------------------------------------------------------------------

    //! 1. Create cache once (per thread)
    virtual BasisEvaluationCache<D> createEvaluationCache( ) const = 0;

    //! 2. Prepare cache and shape function container for an element and return polynomial degrees
    virtual std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                                     size_t maxDiffOrder,
                                                     BasisFunctionEvaluation<D>& shapes,
                                                     BasisEvaluationCache<D>& cache ) const = 0;

    //! 3. Option 1: Evaluate single point
    virtual void evaluateSinglePoint( std::array<double, D> rst,
                                      BasisFunctionEvaluation<D>& shapes,
                                      BasisEvaluationCache<D>& cache ) const = 0;

    //! 3. Option 2: First, prepare for evaluating on a grid of local coordinates 
    virtual void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                        BasisEvaluationCache<D>& cache ) const = 0;

    //! 3. Option 2: Then, evaluate one point in the grid prepared in prepareGridEvaluation
    virtual void evaluateGridPoint( std::array<size_t, D> ijk,
                                    BasisFunctionEvaluation<D>& shapes,
                                    BasisEvaluationCache<D>& cache ) const = 0;
    
    //! Obtain geometric mapping from evaluation cache (after calling prepareEvaluation). 
    //! The reference must be valid until cache is overwritten or its lifetime ends.
    virtual const MeshMapping<D>& mapping( BasisEvaluationCache<D>& cache ) const = 0;

    //! Number of owned dynamically allocated bytes excluding shared objects.
    virtual size_t memoryUsage( ) const = 0;
};

template<size_t D>
class MultilevelHpBasis final : public AbsBasis<D>
{

public:

    MLHP_EXPORT 
    MultilevelHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                       const AnsatzTemplateVector& polynomialDegrees,
                       const InitialMaskProvider<D>& ansatzSpace );
                
    MLHP_PURE 
    DofIndex ndof( ) const override { return ndof_; }
    
    MLHP_PURE 
    size_t nfields( ) const override { return nfields_; }
    
    MLHP_PURE 
    CellIndex nelements( ) const override { return grid_->nleaves( ); }

    MLHP_EXPORT MLHP_PURE 
    DofIndex ndofelement( CellIndex ielement ) const override;
    
    MLHP_EXPORT MLHP_PURE 
    DofIndex ndofelement( CellIndex ielement, size_t fieldIndex ) const override;

    //! Dynamic memory usage. Excludes grid and sizeof( *this )
    MLHP_EXPORT MLHP_PURE 
    size_t memoryUsage( ) const override;

    // ---------------------------------------------------------------------

    MLHP_EXPORT BasisEvaluationCache<D> createEvaluationCache( ) const override;

    MLHP_EXPORT std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                                         size_t maxDiffOrder,
                                                         BasisFunctionEvaluation<D>& shapes,
                                                         BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT void evaluateSinglePoint( std::array<double, D> rst,
                                          BasisFunctionEvaluation<D>& shapes,
                                          BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                            BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT void evaluateGridPoint( std::array<size_t, D> ijk,
                                        BasisFunctionEvaluation<D>& shapes,
                                        BasisEvaluationCache<D>& anyCache ) const  override;

    MLHP_EXPORT MLHP_PURE 
    const MeshMapping<D>& mapping( BasisEvaluationCache<D>& anyCache ) const override;

    // ---------------------------------------------------------------------

    MLHP_EXPORT void locationMap( CellIndex ielement,
                                  LocationMap& target ) const override;
    
    MLHP_EXPORT DofIndex faceDofs( CellIndex ielement,
                                   size_t iface, 
                                   size_t ifield,
                                   std::vector<size_t>& localDofs ) const override;

    MLHP_EXPORT void tensorProductIndices( CellIndex fullIndex,
                                           size_t fieldIndex,
                                           TensorProductIndicesVector<D>& target ) const;

    MLHP_EXPORT MLHP_PURE 
    std::array<size_t, D> maxdegrees( CellIndex ielement ) const override;

    MLHP_EXPORT 
    void setPolynomialBases( const std::array<PolynomialBasis, D>& bases );

    const AbsMesh<D>& mesh( ) const override { return *grid_; }
    const AbsHierarchicalGrid<D>& hierarchicalGrid( ) const { return *grid_; }
    HierarchicalGridSharedPtr<D> hierarchicalGridPtr( ) const { return grid_; }
    
    MeshConstSharedPtr<D> meshPtr( ) const override { return grid_; };

private:
    struct EvaluationImpl;

    size_t nfields_;
    DofIndex ndof_;

    HierarchicalGridSharedPtr<D> grid_;

    std::array<PolynomialBasis, D> bases1D_;
    
    // Data structure of MultilevelHpBasis:
    // * All data exists for each cell in the hierarcy, not only for leaves
    // * locationMaps_ contains the global indices for all dofs of all cells
    //   in a linearized fashion, so one after another in a big vector.
    // * tensorProductIndices_ has the same size as locationMaps_, but instead 
    //   contains the basis function indices for the D axes. For example 
    //   (1, 0, 2) corresponds to N_1(r) * N_0(s) * N_2(t).
    // * indices_ contains the indices for each field component of each 
    //   element in the previous two vectors. 
    //   So the location map of field 2 of element 7 would be in the range
    //   [ indices_[7 * nfields + 2], indices_[7 * nfields + 2 + 1] ).
    //   The location map for all field components of element 7 would be in
    //   [ indices_[7 * nfields], indices_[8 * nfields] ).
    DofIndexVector indices_;
    DofIndexVector locationMaps_;
    TensorProductIndicesVector<D> tensorProductIndices_;
};

template<size_t D> MLHP_EXPORT
void print( const MultilevelHpBasis<D>& basis, std::ostream& os );


template<size_t D>
class BSplineBasis final : public AbsBasis<D>
{

public:

    //! One degree tuple and continuity tuple per solution field component
    MLHP_EXPORT 
    BSplineBasis( std::shared_ptr<const CartesianGrid<D>> grid,
                  std::vector<std::array<size_t, D>> degrees,
                  std::vector<std::array<size_t, D>> continuities );

    MLHP_EXPORT MLHP_PURE
    DofIndex ndof( ) const override;

    size_t nfields( ) const override { return degrees_.size( ); }
    CellIndex nelements( ) const override { return grid_->ncells( ); }

    MLHP_EXPORT MLHP_PURE 
    DofIndex ndofelement( CellIndex ielement ) const override;
    
    MLHP_EXPORT MLHP_PURE 
    DofIndex ndofelement( CellIndex ielement, size_t fieldIndex ) const override;

    //! Dynamic memory usage. Excludes grid and sizeof( *this )
    MLHP_EXPORT MLHP_PURE 
    size_t memoryUsage( ) const override;

    // ---------------------------------------------------------------------

    MLHP_EXPORT BasisEvaluationCache<D> createEvaluationCache( ) const override;

    MLHP_EXPORT std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                                         size_t maxDiffOrder,
                                                         BasisFunctionEvaluation<D>& shapes,
                                                         BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT void evaluateSinglePoint( std::array<double, D> rst,
                                          BasisFunctionEvaluation<D>& shapes,
                                          BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                            BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT void evaluateGridPoint( std::array<size_t, D> ijkPoint,
                                        BasisFunctionEvaluation<D>& shapes,
                                        BasisEvaluationCache<D>& cache ) const  override;

    MLHP_EXPORT MLHP_PURE 
    const MeshMapping<D>& mapping( BasisEvaluationCache<D>& cache ) const override;

    // ---------------------------------------------------------------------

    MLHP_EXPORT void locationMap( CellIndex ielement,
                                  LocationMap& target ) const override;
    
    MLHP_EXPORT DofIndex faceDofs( CellIndex ielement,
                                   size_t iface, 
                                   size_t ifield,
                                   std::vector<size_t>& localDofs ) const override;

    MLHP_EXPORT MLHP_PURE 
    std::array<size_t, D> maxdegrees( CellIndex ielement ) const override;

    const AbsMesh<D>& mesh( ) const override { return *grid_; }
    MeshConstSharedPtr<D> meshPtr( ) const override { return grid_; };

private:
    struct EvaluationCache;

    std::shared_ptr<const CartesianGrid<D>> grid_;
    std::vector<std::array<size_t, D>> degrees_;
    std::vector<std::array<size_t, D>> continuities_;
    std::vector<std::vector<double>> knotVectors_;
};

template<size_t D> MLHP_EXPORT
void print( const BSplineBasis<D>& basis, std::ostream& os );

// Filters elements after creating a basis. This means that the basis
// functions were created with respect to the unfiltered mesh. Instead,
// you can also create a basis defined directly on a filtered mesh.
template<size_t D>
class ElementFilterBasis final : public AbsBasis<D>
{
public:
    struct Cache;

    MLHP_EXPORT
    ElementFilterBasis( const BasisConstSharedPtr<D>& basis,
                        const FilteredMeshSharedPtr<D>& mesh );

    MLHP_PURE const AbsMesh<D>& mesh( ) const override;
    MLHP_PURE const AbsFilteredMesh<D>& filteredMesh( ) const;
    MLHP_PURE const AbsBasis<D>& unfilteredBasis( ) const;
    
    MeshConstSharedPtr<D> meshPtr( ) const override { return mesh_; };

    std::array<size_t, D> maxdegrees( CellIndex ielement ) const override;

    CellIndex nelements( ) const override;

    DofIndex ndof( ) const override;
    DofIndex ndofelement( CellIndex ielement ) const override;
    DofIndex ndofelement( CellIndex ielement, size_t fieldIndex ) const override;
    
    size_t nfields( ) const override;

    void locationMap( CellIndex ielement,
                      LocationMap& target ) const override;

    DofIndex faceDofs( CellIndex ielement,
                       size_t iface, 
                       size_t ifield,
                       std::vector<size_t>& localDofs ) const override;

    BasisEvaluationCache<D> createEvaluationCache( ) const override;

    std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                             size_t maxDiffOrder,
                                             BasisFunctionEvaluation<D>& shapes,
                                             BasisEvaluationCache<D>& cache ) const override;

    void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                BasisEvaluationCache<D>& cache ) const override;

    void evaluateGridPoint( std::array<size_t, D> ijk,
                            BasisFunctionEvaluation<D>& shapes,
                            BasisEvaluationCache<D>& cache ) const override;

    void evaluateSinglePoint( std::array<double, D> rst,
                              BasisFunctionEvaluation<D>& shapes,
                              BasisEvaluationCache<D>& cache ) const override;

    const MeshMapping<D>& mapping( BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT MLHP_PURE
    size_t memoryUsage( ) const override;

    MLHP_EXPORT 
    std::vector<DofIndex> reductionMap( ) const;
    
    MLHP_EXPORT 
    std::vector<DofIndex> expansionMap( ) const;

private:
    const BasisConstSharedPtr<D> basis_;
    const FilteredMeshSharedPtr<D> mesh_;

    DofIndex ndof_;

    // Reduced index if exists, NoDof otherwise
    DofIndexVector reductionMap_; 
};

template<size_t D>
class FieldFilterBasis final : public AbsBasis<D>
{
public:
    struct Cache;

    MLHP_EXPORT
    FieldFilterBasis( memory::vptr<const AbsBasis<D>> basis, size_t ifield );

    // invert = false : index in original basis --> index in filtered basis (NoDof if filtered)
    // invert = true  : index in filtered basis --> index in original basis
    MLHP_EXPORT std::vector<DofIndex> dofIndexMap( bool invert = false ) const;

    MLHP_EXPORT MLHP_PURE const AbsMesh<D>& mesh( ) const override;
    MLHP_EXPORT MLHP_PURE size_t memoryUsage( ) const override;
    MLHP_EXPORT MeshConstSharedPtr<D> meshPtr( ) const override;
    MLHP_EXPORT std::array<size_t, D> maxdegrees( CellIndex ielement ) const override; 
    MLHP_EXPORT CellIndex nelements( ) const override;
    MLHP_EXPORT MLHP_PURE DofIndex ndof( ) const override;
    MLHP_EXPORT DofIndex ndofelement( CellIndex ielement ) const override;
    MLHP_EXPORT DofIndex ndofelement( CellIndex ielement, size_t fieldIndex ) const override;
    MLHP_EXPORT size_t nfields( ) const override;
    MLHP_EXPORT void locationMap( CellIndex ielement, LocationMap& target ) const override;

    MLHP_EXPORT DofIndex faceDofs( CellIndex ielement,
                                   size_t iface, 
                                   size_t ifield,
                                   std::vector<size_t>& localDofs ) const override;

    MLHP_EXPORT BasisEvaluationCache<D> createEvaluationCache( ) const override;

    MLHP_EXPORT std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                                         size_t maxDiffOrder,
                                                         BasisFunctionEvaluation<D>& shapes,
                                                         BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                            BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT void evaluateGridPoint( std::array<size_t, D> ijk,
                                        BasisFunctionEvaluation<D>& shapes,
                                        BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT void evaluateSinglePoint( std::array<double, D> rst,
                                          BasisFunctionEvaluation<D>& shapes,
                                          BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT const MeshMapping<D>& mapping( BasisEvaluationCache<D>& anyCache ) const override;

private:
    memory::vptr<const AbsBasis<D>> basis_;

    size_t ifield_;
    DofIndex ndof_;

    std::vector<DofIndex> dofMap_;
    std::vector<bool> dofMask_;
};

// Offsets dof indices by a constant value
template<size_t D>
class DofOffsetBasis : public AbsBasis<D>
{
public:
    using BasisPtr = memory::vptr<const AbsBasis<D>>;

    DofOffsetBasis( BasisPtr basis, DofIndex offset, DofIndex ndof = NoDof );

    const AbsBasis<D>& basis( ) const;
    const AbsMesh<D>& mesh( ) const override;

    MeshConstSharedPtr<D> meshPtr( ) const override { return basis( ).meshPtr( ); };

    DofIndex offset( ) const;

    CellIndex nelements( ) const override;
    DofIndex ndof( ) const override;
    DofIndex ndofelement( CellIndex ielement ) const override;
    DofIndex ndofelement( CellIndex ielement, size_t ifield ) const override;
    
    size_t nfields( ) const override;

    std::array<size_t, D> maxdegrees( CellIndex ielement ) const override;
    
    void locationMap( CellIndex ielement,
                      LocationMap& locationMap ) const override;
    
    DofIndex faceDofs( CellIndex ielement,
                       size_t iface, 
                       size_t ifield,
                       std::vector<size_t>& localDofs ) const override;

    BasisEvaluationCache<D> createEvaluationCache( ) const override;
    
    std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                             size_t maxDiffOrder,
                                             BasisFunctionEvaluation<D>& shapes,
                                             BasisEvaluationCache<D>& anyCache ) const override;
    
    void evaluateSinglePoint( std::array<double, D> rst,
                              BasisFunctionEvaluation<D>& shapes,
                              BasisEvaluationCache<D>& anyCache ) const override;
    
    void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                BasisEvaluationCache<D>& anyCache ) const override;
    
    void evaluateGridPoint( std::array<size_t, D> ijk,
                            BasisFunctionEvaluation<D>& shapes,
                            BasisEvaluationCache<D>& anyCache ) const override;
    
    const MeshMapping<D>& mapping( BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT
    size_t memoryUsage( ) const override;

private:
    BasisPtr basis_;
    DofIndex offset_;
    DofIndex ndof_;
};

template<size_t D>
class UnstructuredBasis final : public AbsBasis<D>
{
public:
    using UnstructuredMeshSharedPtr = std::shared_ptr<UnstructuredMesh<D>>;
           
    MLHP_EXPORT
    UnstructuredBasis( const UnstructuredMeshSharedPtr& mesh, 
                       size_t nfields = 1 );

    MLHP_EXPORT MLHP_PURE
    const AbsMesh<D>& mesh( ) const override;
    
    MLHP_EXPORT
    MeshConstSharedPtr<D> meshPtr( ) const override;

    MLHP_EXPORT MLHP_PURE
    CellIndex nelements( ) const override;

    MLHP_EXPORT MLHP_PURE
    DofIndex ndof( ) const override;

    MLHP_EXPORT MLHP_PURE
    DofIndex ndofelement( CellIndex ielement ) const override;

    MLHP_EXPORT MLHP_PURE
    DofIndex ndofelement( CellIndex ielement, size_t ifield ) const override;

    MLHP_EXPORT MLHP_PURE
    size_t nfields( ) const override;

    MLHP_EXPORT
    std::array<size_t, D> maxdegrees( CellIndex ielement ) const override;

    MLHP_EXPORT
    void locationMap( CellIndex ielement,
                      LocationMap& locationMap ) const override;

    MLHP_EXPORT
    DofIndex faceDofs( CellIndex ielement,
                       size_t iface, 
                       size_t ifield,
                       std::vector<size_t>& localDofs ) const override;

    MLHP_EXPORT
    BasisEvaluationCache<D> createEvaluationCache( ) const override;

    MLHP_EXPORT
    std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                             size_t maxDiffOrder,
                                             BasisFunctionEvaluation<D>& shapes,
                                             BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT
    void evaluateSinglePoint( std::array<double, D> rst,
                              BasisFunctionEvaluation<D>& shapes,
                              BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT
    void prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT
    void evaluateGridPoint( std::array<size_t, D> ijk,
                            BasisFunctionEvaluation<D>& shapes,
                            BasisEvaluationCache<D>& cache ) const override;

    MLHP_EXPORT MLHP_PURE
    const MeshMapping<D>& mapping( BasisEvaluationCache<D>& cache ) const override;
    
    //! Dynamic memory usage. Excludes mesh and sizeof( *this )
    MLHP_EXPORT MLHP_PURE 
    size_t memoryUsage( ) const override;

private:
    UnstructuredMeshSharedPtr mesh_;
    size_t nfields_;
};

//! Empty basis without dofs
template<size_t D>
class DummyBasis final : public AbsBasis<D>
{
public:
    MLHP_EXPORT 
    DummyBasis( const AbsMesh<D>& mesh, size_t nfields = 1 );
    
    MLHP_EXPORT 
    DummyBasis( std::shared_ptr<const AbsMesh<D>> mesh, size_t nfields = 1 );

    MLHP_EXPORT
    BasisEvaluationCache<D> createEvaluationCache( ) const override;

    MLHP_EXPORT
    std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                             size_t maxDiffOrder,
                                             BasisFunctionEvaluation<D>& shapes,
                                             BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT
    void evaluateSinglePoint( std::array<double, D> rst,
                              BasisFunctionEvaluation<D>& shapes,
                              BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT
    void prepareGridEvaluation( const CoordinateGrid<D>& rstGrid,
                                BasisEvaluationCache<D>& anyCache ) const override;

    MLHP_EXPORT
    void evaluateGridPoint( std::array<size_t, D> ijk,
                            BasisFunctionEvaluation<D>& shapes,
                            BasisEvaluationCache<D>& anyCache ) const override;
    
    MLHP_EXPORT MLHP_PURE
    const MeshMapping<D>& mapping( BasisEvaluationCache<D>& cache ) const override;
    
    const AbsMesh<D>& mesh( ) const override { return *mesh_; }
    MeshConstSharedPtr<D> meshPtr( ) const override { return mesh_.shared( ); }
    CellIndex nelements( ) const override { return mesh_->ncells( ); }
    DofIndex ndof( ) const override { return 0; }
    DofIndex ndofelement( CellIndex ) const override { return 0; }
    DofIndex ndofelement( CellIndex, size_t ) const override { return 0; }
    size_t nfields( ) const override { return nfields_; };
    std::array<size_t, D> maxdegrees( CellIndex ) const override { return array::makeSizes<D>( 0 ); }
    void locationMap( CellIndex, LocationMap& ) const override { return; }
    DofIndex faceDofs( CellIndex, size_t, size_t, std::vector<size_t>& ) const override { return 0; }
    size_t memoryUsage( ) const override { return 0; }

private:
    struct Cache;
    size_t nfields_;
    memory::vptr<const AbsMesh<D>> mesh_;
};

template<size_t D> MLHP_EXPORT
void print( const UnstructuredBasis<D>& basis, std::ostream& os );

namespace basis
{

template<size_t D> MLHP_EXPORT
LocationMapVector locationMapVector( const AbsBasis<D>& basis );

template<size_t D> MLHP_EXPORT
LocationMapRange locationMapRange( const AbsBasis<D>& basis );

template<size_t D> MLHP_EXPORT
LocationMap locationMap( const AbsBasis<D>& basis, 
                         CellIndex ielement );

template<size_t D> MLHP_EXPORT
DofIndex fieldComponentOffset( const AbsBasis<D>& basis,
                               CellIndex ielement, 
                               size_t fieldIndex );

template<size_t D> MLHP_EXPORT
double averageNumberOfElementDofs( const AbsBasis<D>& basis );

template<size_t D> MLHP_EXPORT
AnsatzTemplateVector createAnsatzTemplates( const std::vector<std::array<size_t, D>>& degrees,
                                            size_t nfields = 1 );

//! Calls basis.faceDofs and subtracts offset from indices
template<size_t D> MLHP_EXPORT
DofIndex faceDofsWithoutOffset( const AbsBasis<D>& basis,
                                CellIndex ielement,
                                size_t iface,
                                size_t ifield,
                                std::vector<size_t>& target );

template<size_t D> MLHP_EXPORT
std::vector<std::array<size_t, D>> maxdegrees( const AbsBasis<D>& basis );

template<size_t D> MLHP_EXPORT
size_t maxdegree( const AbsBasis<D>& basis );

template<size_t D> MLHP_EXPORT
LinearizedVectors<CellIndex> findSupportElements( const AbsBasis<D>& basis,
                                                  const std::vector<DofIndex>& dofs );

//! Find all the dofs that are supported on the given elements. 
//! If exclusively is true then return dofs that are only supported on the given elements.
template<size_t D> MLHP_EXPORT
DofIndexVector findSupportedDofs( const AbsBasis<D>& basis,
                                  const std::vector<CellIndex>& cells,
                                  const std::vector<DofIndex>& dirichletIndices = { },
                                  bool exclusive = false,
                                  bool invert = false );

template<size_t D> MLHP_EXPORT
spatial::ScalarFunction<D> scalarEvaluator( memory::vptr<const AbsBasis<D>> basis,
                                            memory::vptr<const std::vector<double>> dofs,
                                            size_t ifield = 0,
                                            size_t difforder = 0,
                                            size_t icomponent = 0,
                                            double outside = 0.0 );

template<size_t D> MLHP_EXPORT
spatial::VectorFunction<D> vectorEvaluator( memory::vptr<const AbsBasis<D>> basis,
                                            memory::vptr<const std::vector<double>> dofs,
                                            size_t difforder = 0 );

template<size_t D>
struct EvaluatorComponent
{
    size_t ifield;
    double defaultValue;
    std::array<size_t, D> diffIndices;
};

template<size_t D> MLHP_EXPORT
spatial::VectorFunction<D> vectorEvaluator( memory::vptr<const AbsBasis<D>> basis,
                                            memory::vptr<const std::vector<double>> dofs,
                                            std::vector<EvaluatorComponent<D>> components );

} // namespace basis

struct TensorSpace
{
    template<size_t D> MLHP_EXPORT
    static InitialMaskProvider<D> initialMaskProvider( );
};

struct TrunkSpace
{
    template<size_t D> MLHP_EXPORT
    static InitialMaskProvider<D> initialMaskProvider( );
};

//! Helps converting between isotropic (scalar) and anisotopic (tuple) degrees
class PolynomialDegreeTuple
{
public:
    MLHP_EXPORT
    PolynomialDegreeTuple( size_t degree );

    MLHP_EXPORT 
    PolynomialDegreeTuple( const std::vector<size_t>& degrees );

    template<size_t D> MLHP_EXPORT
    PolynomialDegreeTuple( std::array<size_t, D> degrees );

    template<size_t D> MLHP_EXPORT
    std::array<size_t, D> get( );

private:
    std::vector<size_t> degrees_;
    size_t dimensionality_;
};

//! Same degrees everywhere
struct UniformGrading
{
    PolynomialDegreeTuple degrees;

    template<size_t D> MLHP_EXPORT
    AnsatzTemplateVector operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );
};

//! Set degrees on finest elements. Increment degrees by one per level coarser.
struct LinearGrading
{
    PolynomialDegreeTuple fineDegrees;

    template<size_t D> MLHP_EXPORT
    AnsatzTemplateVector operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );
};

//! Interpolate between degree set on root and leaf elements
struct InterpolatedGrading
{
    PolynomialDegreeTuple coarseDegrees;
    PolynomialDegreeTuple fineDegrees;

    template<size_t D> MLHP_EXPORT
    AnsatzTemplateVector operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );
};

//! Set degrees for each refinement level
struct PerLevelGrading
{
    using GradingFunction = std::function<PolynomialDegreeTuple( RefinementLevel level, 
                                                                 RefinementLevel maxLevel )>;

    MLHP_EXPORT PerLevelGrading( const GradingFunction& gradingFunction );
    MLHP_EXPORT PerLevelGrading( const PolynomialDegreeVector& degrees );
    MLHP_EXPORT PerLevelGrading( const std::vector<PolynomialDegreeTuple>& degrees );

    GradingFunction gradingFunction_;

    template<size_t D> MLHP_EXPORT
    AnsatzTemplateVector operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );
};

template<typename T>
concept GradingConcept = std::invocable<T, const AbsHierarchicalGrid<1>&, size_t>;

template<typename BasisType, size_t D>
MultilevelHpBasisSharedPtr<D> makeHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                           const PolynomialDegreeTuple& degrees, 
                                           size_t nfields = 1 );

template<typename BasisType, GradingConcept GradingType, size_t D>
MultilevelHpBasisSharedPtr<D> makeHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                           const GradingType& grading, 
                                           size_t nfields = 1 );

template<typename BasisType, size_t D>
MultilevelHpBasisSharedPtr<D> makeHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                           const PolynomialDegreeDistributor<D>& degrees,
                                           size_t nfields = 1 );

template<size_t D>
std::shared_ptr<BSplineBasis<D>> makeBSplineBasis( std::shared_ptr<const CartesianGrid<D>> grid,
                                                   std::array<size_t, D> degrees,
                                                   std::array<size_t, D> continuities,
                                                   size_t nfields = 1 );

template<size_t D>
std::shared_ptr<BSplineBasis<D>> makeBSplineBasis( std::shared_ptr<const CartesianGrid<D>> grid,
                                                   size_t degree, 
                                                   size_t continuity, 
                                                   size_t nfields = 1 );

//! Uniform grading
template<typename BasisType, size_t D>
MultilevelHpBasisFactory<D> makeHpBasisFactory( const PolynomialDegreeTuple& degrees );

//! Grading one of { UniformGrading, LinearGrading, InterpolatedGrading }
template<typename BasisType, size_t D, GradingConcept GradingType>
MultilevelHpBasisFactory<D> makeHpBasisFactory( const GradingType& grading );

//! Custom std::function for grading
template<typename BasisType, size_t D>
MultilevelHpBasisFactory<D> makeHpBasisFactory( const PolynomialDegreeDistributor<D>& degrees );

} // mlhp

#include "mlhp/core/basis_impl.hpp"

#endif // MLHP_CORE_BASIS_HPP
