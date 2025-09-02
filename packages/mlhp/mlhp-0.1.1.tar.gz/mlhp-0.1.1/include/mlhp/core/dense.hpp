// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_DENSE_HPP
#define MLHP_CORE_DENSE_HPP

#include "mlhp/core/memory.hpp"
#include "mlhp/core/coreexport.hpp"

#include <cstddef>
#include <span>
#include <optional>

namespace mlhp::linalg
{

//! Solve linear equation system M * x = b. 
//! M : n x n input/target matrix that will be overwritten by its LU decomposition
//! p : target vector of size n to store the permutation 
//! b : input vector of size n holding the right hand side
//! u : target vector of size n to store the solution
MLHP_EXPORT void solve( std::span<double> M,
                        std::span<size_t> p,
                        std::span<const double> b,
                        std::span<double> u );

//! Inverts row major dense matrix. Replicates scipy.linalg.lu_factor, but with a permuation 
//! instead of the raw pivot vector, see the example they show in the documentation)
//! source : n x n input matrix (will be overwritten by its LU decomposition for larger problem sizes)
//! p      : target vector of size n to hold the permutation matrix if an LU decomposition is used
//! target : n x n output matrix to hold the iverse
MLHP_EXPORT void invert( std::span<double> source,
                         std::span<size_t> p,
                         std::span<double> target );

//! Compute determinant of a row-major dense matrix. 
//! M   : n x x input matrix (will be overwritten by its LU decomposition for larger problem sizes)
//! p   : target vector of size n to hold the permutation matrix if an LU decomposition is used
//! eps : Matrix is considered singular when lu encounters a column whose values are all below eps
MLHP_EXPORT double det( std::span<double> M,
                        std::span<size_t> p,
                        std::optional<double> eps = std::nullopt );

//! In-place row-major LU decomposition with partial pivoting
//! M   : n x n input/target matrix that will hold the LU decomposition
//! p   : target vector of size n to store the permutation 
//! eps : Matrix is considered singular when lu encounters a column whose values are all below eps
//! Returns the number of row swaps or -1 if the matrix is singular
MLHP_EXPORT int luFactor( std::span<double> M, 
                          std::span<size_t> p,
                          std::optional<double> eps = std::nullopt );

//! Forward and backward substitution using lu decomposition
//! LU : n x n input matrix holding an LU-decomposition
//! p  : input vector of size n holding the permutation of the LU-decomposition
//! b  : input vector of size n holding the right hand side
//! u  : target vector of size n to store the solution
MLHP_EXPORT void luSubstitute( std::span<const double> LU,
                               std::span<const size_t> p,
                               std::span<const double> b,
                               std::span<double> u );

//! Compute determinant based on LU decomposition (product of diagonal entries)
//! LU : n x n input matrix holding an LU-decomposition
//! p  : input vector of size n holding the permutation of the LU-decomposition
MLHP_EXPORT MLHP_PURE double luDeterminant( std::span<const double> LU,
                                            std::span<const size_t> p,
                                            int luResult );

//! Matrix inversion using lu decomposition
//! LU : n x n input matrix holding an LU-decomposition
//! p  : input vector of size n holding the permutation of the LU-decomposition
MLHP_EXPORT void luInvert( std::span<const double> LU,
                           std::span<const size_t> p,
                           std::span<double> I );

//! QR decomposition of an m x n matrix (with m >= n).
//! M      : m x n input matrix that will not be modified
//! Q      : m x m target matrix whose columns are orthogonal. If reduce == true, the output will be m x n row-major
//! R      : m x n target matrix to hold triangular (full storage) part (effectively n x n, since rows > n are zero).
//! sizes  : number of rows and number of columns in M
//! reduce : Rearrange Q to be m x n row-major. This retains M = Q * R, since the values in R below n are zero
MLHP_EXPORT void qr( std::span<const double> M, 
                     std::span<double> Q, 
                     std::span<double> R, 
                     std::array<size_t, 2> sizes,
                     bool reduce = true );

//! In-place reduces the n x n matrix A with row-major storage to its Hessenberg form H 
//! (means making it "almost triangular"). The Hessenberg decomposition of a matrix full-
//! fills A = Q * H * Q^T. The matrix H only has one sub-diagonal directly below the main 
//! diagonal. This forms the first step of the QR-algorithm for eigendecomposition.
//! See also scipy.linalg.hessenberg.
//! A   : n x n input/target matrix will be modified in place 
//! tmp : target vector of size n required for temporary storage during the algorithm
//! Q   : n x n target matrix (optional) to hold the transformation matrix Q
MLHP_EXPORT void hessenberg( std::span<double> A, 
                             std::span<double> tmp, 
                             std::span<double> V = { } );

//! Computes eigenvalues and eigenvectors of a symmetric matrix
//! A      : n x n source/target matrix (row-major, full storage) that will hold eigenvectors as rows
//! lambda : target vector of size n to hold the eigenvalues 
//! tmp    : target vector of size n required for temporary storage during the algorithm
MLHP_EXPORT void eigh( std::span<double> A, 
                       std::span<double> lambda, 
                       std::span<double> tmp );

//! Computes the non-symmetric eigenvalue problem of the n x n matrix A.
//! A    : n x n input/target matrix that will be reduced in-place to triangular form 
//! real : target vector of size n for holding the real part of the eigenvalues
//! imag : target vector of size n for holding the imaginary part of the eigenvalues
//! Q    : n x n target matrix (optional) for holding eigenvectors as contiguous rows
MLHP_EXPORT void eig( std::span<double> A,
                      std::span<double> real,
                      std::span<double> imag,
                      std::span<double> V = { } );

//! Generalized eigenvalue problem A * v = lambda * B * v (calls eig with B^-1 * A).
//! A    : n x n matrix that will be overwritten with B^-1 * A 
//! B    : n x n matrix that will be overwritten with its LU-decomposition
//! real : target vector of size n for real part of eigenvalues
//! imag : target vector of size n for imaginary part of eigenvalues
//! perm : target vector of size n for the permutation of the LU-decomposition
//! V    : n x n target matrix (optional) for eigenvectors as contiguous rows
MLHP_EXPORT void eig( std::span<double> A,
                      std::span<double> B,
                      std::span<double> real,
                      std::span<double> imag,
                      std::span<size_t> perm,
                      std::span<double> V = { } );

//! Sort eigendecomposition using a custom bubble sort (eigenvectors can be left empty)
MLHP_EXPORT void sorteig( std::span<double> lambda,
                          std::span<double> eigenvectors,
                          bool abs = false,
                          bool ascending = true );

MLHP_EXPORT void sorteig( std::span<double> lambda, 
                          bool abs = false,
                          bool ascending = true );

//! Matrix-matrix product for square row-major matrices
//! left   : n x n input matrix (left operand)
//! right  : n x n input matrix (right operand)
//! target : n x n target matrix to hold the result
//! size   : matrix size n
template<bool fillZero = true>
void mmproduct( const double* left, 
                const double* right, 
                double* target, 
                size_t size );

//! General matrix-matrix product for row-major matrices:
//! [leftM x leftN] * [leftN x rightN] -> [leftM x rightN]
//! left   : leftM x leftN input matrix (left operand)
//! right  : leftN x rightN input matrix (right operand)
//! target : leftM x rightN target matrix to hold the result
//! leftM  : number of rows of the left operand and the result
//! leftN  : number of column of left and number of rows of 
//!          right operand (this dimension will be eliminated)
//! rightN : number of columns of right operand and result
template<bool fillZero = true>
void mmproduct( const double* left, 
                const double* right, 
                double* target, 
                size_t leftM, 
                size_t leftN, 
                size_t rightN );

//! Matrix vector product result = A * x
template<size_t M, size_t N, bool fillZero = true>
void mvproduct( std::span<const double> A,
                std::span<const double, N> x,
                std::span<double, M> result );

//! Matrix vector product A * x with fixed dimensions
template<size_t M, size_t N = M>
std::array<double, M> mvproduct( std::span<const double> A, 
                                 std::span<const double, N> x );

MLHP_EXPORT MLHP_PURE
double norm( std::span<const double> data );

MLHP_EXPORT
bool issymmetric( std::span<const double> M, size_t size, double tolerance = 1e-10 );

MLHP_EXPORT 
void identity( std::span<double> M, size_t size );

// Assumptions: Aligned, padded, no aliasing
struct SymmetricDenseMatrix { };
struct UnsymmetricDenseMatrix { };

template<bool Symmetric>
struct DenseMatrixTypeHelper { using type = SymmetricDenseMatrix; };

template<>
struct DenseMatrixTypeHelper<false> { using type = UnsymmetricDenseMatrix; };

template<bool Symmetric>
using DenseMatrixType = typename DenseMatrixTypeHelper<Symmetric>::type;

template<typename MatrixType>
inline constexpr bool isSymmetricDense = std::is_same_v<MatrixType, SymmetricDenseMatrix>;

template<typename MatrixType>
inline constexpr bool isUnsymmetricDense = std::is_same_v<MatrixType, UnsymmetricDenseMatrix>;

template<typename DenseMatrixType>
constexpr size_t denseRowIncrement( size_t iRow, size_t paddedLength );

template<typename T = double>
auto symmetricNumberOfBlocks( size_t iRow );

template<typename T = double>
auto symmetricDenseOffset( size_t rowI, size_t columnJ );

template<typename MatrixType, typename T>
auto indexDenseMatrix( T* matrix, size_t i, size_t j, size_t paddedSize );

template<typename MatrixType, typename T = double>
auto denseMatrixStorageSize( size_t size );

template<typename TargetMatrixType, typename MatrixExpr>
void elementLhs( double* target, size_t size, size_t nblocks, MatrixExpr&& expression );

// Write block into dense matrix (symmetric version only writes lower trianglular part)
template<typename TargetMatrixType, typename MatrixExpr> inline
void elementLhs( double* target, size_t allsize1, 
                 size_t offset0, size_t size0, 
                 size_t offset1, size_t size1, 
                 MatrixExpr&& expression );

template<typename MatrixExpr>
void unsymmetricElementLhs( double* target, size_t size, size_t nblocks, MatrixExpr&& function );

// Same as above but assuming upper storage
template<typename MatrixExpr>
void symmetricElementLhs( double* target, size_t size, size_t nblocks, MatrixExpr&& function );

// In-place addition of a vector with a given expression, assuming no aliasing.
template<typename VectorExpr = void>
void elementRhs( double* target, size_t size, size_t nblocks, VectorExpr&& function );

template<typename T>
auto adapter( T&& span, size_t size1 );

// Helper functions

//! Determines [c, s, r], such that [[c, -s], [s, c]] @ [a, b] = [X, 0], and r = ||[a, b]||
MLHP_EXPORT std::array<double, 3> givensr( double a, double b );

//! givensr, but without giving back the length
MLHP_EXPORT std::array<double, 2> givens( double a, double b );

//! Computes the householder reflection (v, beta), such that: x - beta * v * dot(v, x) = || x || * e1
//! We can use u = v * sqrt(beta / 2) that fullfill x - 2 * u * dot(u, x) = || x || * e1
//! Returns: beta, || x ||
MLHP_EXPORT std::tuple<double, double> householderVector( std::span<const double> x, std::span<double> v );

//! Computes the reflector matrix P, such that P * x = || x || * e1
MLHP_EXPORT std::tuple<double, double> householderMatrix( std::span<const double> x, std::span<double> P );

//! Small size eigendecompositions
MLHP_EXPORT MLHP_PURE std::array<double, 2> eigh2D( std::array<double, 2 * 2> A );
MLHP_EXPORT MLHP_PURE std::array<std::array<double, 2>, 2> eigh2Dv( std::array<double, 2 * 2> A, std::array<double, 2> lambdas );

} // namespace mlhp::linalg

#include "mlhp/core/dense_impl.hpp"

#endif // MLHP_CORE_DENSE_HPP
