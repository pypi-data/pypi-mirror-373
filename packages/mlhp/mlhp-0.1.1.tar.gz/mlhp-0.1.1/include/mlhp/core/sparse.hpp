// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_SPARSE_HPP
#define MLHP_CORE_SPARSE_HPP
    
#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/memory.hpp"

#include <vector>
#include <tuple>
#include <cstddef>
#include <functional>
#include <algorithm>
#include <numeric>
#include <cmath>

namespace mlhp::linalg
{

using IndexSetRange = utilities::IndexRangeFunction<void( size_t, std::vector<SparseIndex>& )>;
using SparseDataStructure = std::tuple<SparseIndex*, SparsePtr*, double*>;

class MLHP_EXPORT AbsSparseMatrix : utilities::DefaultVirtualDestructor
{
public:
    using IndexType = SparseIndex;

    explicit AbsSparseMatrix( );
    virtual ~AbsSparseMatrix( );

    MLHP_PURE SparseIndex size1( ) const;
    MLHP_PURE SparseIndex size2( ) const;
    MLHP_PURE SparsePtr nnz( ) const;

    MLHP_PURE virtual double operator()( size_t i, size_t j ) const;
    MLHP_PURE virtual double* find( size_t i, size_t j );
    MLHP_PURE const double* find( size_t i, size_t j ) const;
    MLHP_PURE virtual bool symmetricHalf( ) const = 0;   
    virtual void multiply( const double* vector, double* target ) const = 0;
 
    std::vector<double> operator*( const std::vector<double>& vector ) const;
    
    SparseDataStructure release( );

    void claim( SparseDataStructure data, 
                SparseIndex size1, 
                SparseIndex size2 );

    auto indices( ) { return indices_; }
    auto indptr( ) { return indptr_; }
    auto data( ) { return data_; }
    auto indices( ) const { return indices_; }
    auto indptr( ) const { return indptr_; }
    auto data( ) const { return data_; }

    MLHP_PURE size_t memoryUsage( ) const;

protected:
    void cleanup( );

    void copyAssign( const AbsSparseMatrix& other );
    void moveAssign( AbsSparseMatrix&& other );

private:

    SparseIndex* indices_;
    SparsePtr* indptr_;

    double* data_;

    SparseIndex size1_, size2_;
};

class MLHP_EXPORT UnsymmetricSparseMatrix final : public AbsSparseMatrix
{
public:
    using IndexType = typename AbsSparseMatrix::IndexType;
    using AbsSparseMatrix::AbsSparseMatrix;

    UnsymmetricSparseMatrix( const UnsymmetricSparseMatrix& other );
    UnsymmetricSparseMatrix& operator=( const UnsymmetricSparseMatrix& other );

    UnsymmetricSparseMatrix( UnsymmetricSparseMatrix&& other );
    UnsymmetricSparseMatrix& operator=( UnsymmetricSparseMatrix&& other );

    MLHP_PURE bool symmetricHalf( ) const override { return false; }   

    void multiply( const double* vector, double* target ) const override;
};

//! Compressed sparse row format with upper storage
class MLHP_EXPORT SymmetricSparseMatrix final : public AbsSparseMatrix
{
public:
    using IndexType = typename AbsSparseMatrix::IndexType;
    using AbsSparseMatrix::AbsSparseMatrix;

    SymmetricSparseMatrix( const SymmetricSparseMatrix& other );
    SymmetricSparseMatrix& operator=( const SymmetricSparseMatrix& other );

    SymmetricSparseMatrix( SymmetricSparseMatrix&& other );
    SymmetricSparseMatrix& operator=( SymmetricSparseMatrix&& other );

    MLHP_PURE double operator()( size_t i, size_t j ) const override;
    MLHP_PURE double* find( size_t i, size_t j ) override;
    MLHP_PURE bool symmetricHalf( ) const override { return true; }   
    void multiply( const double* vector, double* target ) const override;
};

MLHP_EXPORT void print( const AbsSparseMatrix& matrix, std::ostream& os );
MLHP_EXPORT void print( const UnsymmetricSparseMatrix& matrix, std::ostream& os );
MLHP_EXPORT void print( const SymmetricSparseMatrix& matrix, std::ostream& os );

//using SparseBlockIterator = std::function<void( size_t index, std::vector<SparseIndexType>& target )>;
//
//template<typename MatrixType, typename ElementIndexType, typename DofIndexType>
//MatrixType allocateSparseMatrix( const SparseBlockIterator<ElementIndexType, DofIndexType>& blocks )

struct IterativeSolverInfo
{
    std::vector<double> residualNorms_;

    MLHP_EXPORT MLHP_PURE
    size_t niterations( ) const;
};

using IterativeSolverWithWithInfo = std::tuple<SparseSolver, std::shared_ptr<IterativeSolverInfo>>;

template<typename MatrixType>
inline constexpr bool isSymmetricSparse = std::is_same_v<MatrixType, SymmetricSparseMatrix>;

template<typename MatrixType>
inline constexpr bool isUnsymmetricSparse = std::is_same_v<MatrixType, UnsymmetricSparseMatrix>;

MLHP_EXPORT 
std::vector<double> gmres( const LinearOperator& multiply,
                           const double* rhs,
                           double* solution,
                           size_t systemSize,
                           size_t maximumNumberOfIterations,
                           double threshold );

MLHP_EXPORT 
std::vector<double> cg( const LinearOperator& A,
                        const std::vector<double>& b,
                        std::vector<double>& x0,
                        double rtol,
                        double atol,
                        size_t maxiter,
                        const LinearOperator& M,
                        memory::vptr<std::vector<double>> tmp = nullptr );

MLHP_EXPORT
std::vector<double> bicgstab( const LinearOperator& A,
                              const std::vector<double>& b,
                              std::vector<double>& x0,
                              double rtol,
                              double atol,
                              size_t maxiter,
                              const LinearOperator& M,
                              memory::vptr<std::vector<double>> tmp = nullptr );

MLHP_EXPORT 
LinearOperator makeDefaultMultiply( const AbsSparseMatrix& matrix );

MLHP_EXPORT
LinearOperator makeDefaultMultiply( const std::shared_ptr<const AbsSparseMatrix>& matrix );

MLHP_EXPORT 
LinearOperator makeNoPreconditioner( );

//! diagonal is target memory that will be used to store the diagonal
MLHP_EXPORT 
LinearOperator makeDiagonalPreconditioner( const AbsSparseMatrix& matrix,
                                           memory::vptr<std::vector<double>> diagonal = nullptr );

MLHP_EXPORT
UnsymmetricSparseMatrix makeAdditiveSchwarzPreconditioner( const UnsymmetricSparseMatrix& matrix,
                                                           const IndexSetRange& groups,
                                                           const std::vector<SparseIndex>& exclude,
                                                           SparseIndex ndof );

MLHP_EXPORT
SparseSolver makeCGSolver( double rtol = 1e-10,
                           double atol = 0.0,
                           size_t maxiter = NoValue<size_t> );

MLHP_EXPORT
IterativeSolverWithWithInfo makeCGSolverWithInfo( double rtol = 1e-10,
                                                  double atol = 0.0,
                                                  size_t maxiter = NoValue<size_t> );

MLHP_EXPORT
SparseSolver makeBiCGStabSolver( double rtol = 1e-10,
                                 double atol = 0.0,
                                 size_t maxiter = NoValue<size_t> );

MLHP_EXPORT
IterativeSolverWithWithInfo makeBiCGStabSolverWithInfo( double rtol = 1e-10,
                                                        double atol = 0.0,
                                                        size_t maxiter = NoValue<size_t> );

std::vector<double> gmres( const UnsymmetricSparseMatrix& A,
                           const std::vector<double>& rhs,
                           std::vector<double>& solution,
                           size_t max_iterations,
                           double threshold = 1e-12 );

MLHP_EXPORT
SymmetricSparseMatrix convertToSymmetric( const UnsymmetricSparseMatrix& matrix );

MLHP_EXPORT
UnsymmetricSparseMatrix convertToUnsymmetric( const SymmetricSparseMatrix& matrix );

MLHP_EXPORT
UnsymmetricSparseMatrix filterZeros( const UnsymmetricSparseMatrix& matrix, double tolerance = 0.0 );

MLHP_EXPORT
UnsymmetricSparseMatrix transpose( const UnsymmetricSparseMatrix& matrix );

//! Convert sparse to dense matrix in row-major format without padding
MLHP_EXPORT
std::vector<double> todense( const AbsSparseMatrix& M );

//! Extract submatrix with product indices: result = matrix[rowIndices x columnIndices]
//! Repeated indices will result in repeated rows/columns
MLHP_EXPORT
UnsymmetricSparseMatrix extractBlock( const UnsymmetricSparseMatrix& matrix,
                                      std::span<const DofIndex> rowIndices,
                                      std::span<const DofIndex> columnIndices );

} // namespace mlhp::linalg

#endif // MLHP_CORE_SPARSE_HPP
