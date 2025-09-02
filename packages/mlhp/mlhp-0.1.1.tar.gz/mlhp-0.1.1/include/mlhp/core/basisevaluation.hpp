// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_BASISEVALUATION_HPP
#define MLHP_CORE_BASISEVALUATION_HPP

#include "mlhp/core/memory.hpp"
#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"

#include <vector>
#include <array>

namespace mlhp
{

//! Matrix of basis function evaluations with additional info
//! The data layout is described in the comment below the class definition.
template<size_t D>
class BasisFunctionEvaluation
{
public:

    // ------------------ Sizes ---------------------

    size_t nfields( ) const;
    size_t maxdifforder( ) const;

    size_t ndof( ) const;
    size_t ndof( size_t ifield ) const;

    // Number of simd vector blocks
    size_t nblocks( ) const;
    size_t nblocks( size_t ifield ) const;

    // Padded number of total and field dofs
    size_t ndofpadded( ) const;
    size_t ndofpadded( size_t ifield ) const;

    // [ndof, nblocks, ndofpadded]
    auto sizes( ) const;
    auto sizes( size_t ifield ) const;

    // Amount of dynamic memory allocated (in bytes)
    size_t memoryUsage( ) const;

    static constexpr size_t blocksize( );
    static constexpr size_t ncomponents( size_t difforder );

    // ------------- Evaluation data ----------------

    std::array<double, D> rst( ) const;
    std::array<double, D> xyz( ) const;

    CellIndex elementIndex( ) const;

    // Pointer to shape functions
    auto get( size_t ifield, size_t difforder );
    auto get( size_t ifield, size_t difforder ) const;

    // Pointer to shape functions assuming no aliasing
    auto noalias( size_t ifield, size_t difforder );
    auto noalias( size_t ifield, size_t difforder ) const;

    // Same as above but as array for multiple diff orders
    template<size_t MaxDiff>
    auto noalias( size_t ifield = 0 );

    template<size_t MaxDiff>
    auto noalias( size_t ifield = 0 ) const;
      
    // ------------------ Setup ---------------------

    // 1. Allocate header. Must be called before adding dofs.
    void initialize( CellIndex ielement, size_t nfields, size_t maxdifforder );

    // 2. Can be called multiple times and out of order
    void addDofs( size_t ifield, size_t ndof );

    // 3. Allocate memory according to 1. and 2.
    void allocate( );

    // Set mapping data
    void setRst( std::array<double, D> rst );
    void setXyz( std::array<double, D> rst );

    void setElementIndex( CellIndex ielement );

private:
    size_t nfields_, maxdifforder_, ndof_, nblocks_;
    
    CellIndex ielement_;
    std::array<double, D> rst_, xyz_;

    // Offsets and sizes (documentation below)
    std::vector<size_t> info_;

    // Basis function values (documentation below)
    memory::AlignedVector<double> data_;

    size_t offset( size_t ifield, size_t difforder ) const;
};

/* 
 * The shape function evaluation is stored in data_ in a contiguous
 * fashion. For 2 field components with maxdifforder = 1 we get:
 * 
 * get( 0, 0 )  -->  [[            N1            |  ],
 * get( 0, 1 )  -->   [           dN1/dx         |  ],
 *                    [           dN1/dy         |  ],
 * get( 1, 0 )  -->   [            N2            |  ],
 * get( 1, 1 )  -->   [           dN2/dx         |  ],
 *                    [           dN2/dy         |  ]]
 *                                                /
 *                                               /
 *                       padding, such that new rows are 
 *                       aligned to mlhp::simd_alignment 
 * 
 * The sizes and offsets stored in info_:
 *     [0, nfields)          --> number of dofs for each field
 *     [nfields, 2*nfields)  --> number of SIMD blocks per field
 *     [2*nfields, end)      --> the offset in data_ for each 
 *                               field and each diff order
 * 
 * The number of offsets is: nfields * (maxdifforder + 1) + 1
 */

// ------------------ Evaluate solution ------------------

//! Evaluate solution as sum over basis functions times coefficients.
template<size_t D>
auto evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       size_t ifield = 0 );

//! Evaluate multiple fields into an std::array<double, nfields>
template<size_t nfields, size_t D>
auto evaluateSolutions( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs );


// -------------- Evaluate first derivative --------------

//! Evaluate solution gradient as sum over basis function gradient times coefficients.
template<size_t D>
auto evaluateGradient( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       size_t ifield = 0 );

//! Evaluate solution gradient of multiple fields. The result is an array of arrays 
//! indexed as du[ifield][icomponent] 
template<size_t nfields, size_t D>
auto evaluateGradients( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs );


// ----- Generic solution evaluation into std::array -----

//! Evaluate given field at diff order
template<size_t diffOrder, size_t D>
auto evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       size_t ifield = 0 );

//! Evaluate given field at diff order
template<size_t nfields, size_t difforder, size_t D>
auto evaluateSolutions( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs );


// ----- Generic solution evaluation into std::span ------

//! Evaluate solution for the given diff order and field index into target memory (all diff components).
template<size_t D> MLHP_EXPORT
void evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       std::span<double> target,
                       size_t difforder = 0,
                       size_t ifield = 0 );

//! Evaluate solution for the given diff order, diff component, and field index into target memory 
//! (e.g. diff order 1 and diff index 1 is first derivative in direction 1).
template<size_t D>
void evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       std::span<double> target,
                       size_t difforder,
                       size_t icomponent,
                       size_t ifield );

//! Evaluate solution for multiple fields and the given diff order into target memory 
//! indexed as target[ifield * ncomponents + icomponent]. It must therefore hold at least 
//! nfields * ncomponents entries.
template<size_t D> MLHP_EXPORT
void evaluateSolutions( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs,
                        std::span<double> target,
                        size_t difforder = 0 );

// --------------- Other helper functions ----------------

//! Take shapes.rst( ) to set xyz and map derivatives
template<size_t D> MLHP_EXPORT
double mapBasisEvaluation( BasisFunctionEvaluation<D>& shapes,
                           const AbsMapping<D>& mapping );

//! Array with number of dofs per field component
template<size_t nfields, size_t D>
auto fieldSizes( const BasisFunctionEvaluation<D>& shapes );

//! Array with first local dof index per field component: [0, nx, nx + ny, ...]
//! Entry at index nfields is the total (unpadded) number of dofs
template<size_t nfields, size_t D>
auto fieldOffsets( const BasisFunctionEvaluation<D>& shapes );

template<size_t D> MLHP_EXPORT MLHP_PURE
size_t fieldOffset( const BasisFunctionEvaluation<D>& shapes, 
                    size_t ifield );

} // mlhp

#include "mlhp/core/basisevaluation_impl.hpp"

#endif // MLHP_CORE_BASISEVALUATION_HPP
