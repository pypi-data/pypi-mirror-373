// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/alias.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/sparse.hpp"
#include "mlhp/core/memory.hpp"
#include "mlhp/core/basis.hpp"

namespace mlhp
{

/*
 *  ------------ Test quad connectivity -------------
 *
 *     33----34-----35----36-----37-----------39
 *     |            |            |            |
 *     |            26  28   30  32           |
 *     23    24     |            |            |
 *     |            25  27   29  31           |
 *     |            |            |            |
 *     17----18-----19--20---21--22-----------38
 *     |            |            |
 *     7   9   11   13    15     |
 *     |            |            16
 *     6   8   10   12    14     |
 *     |            |            |
 *     0---1----2---3------4-----5
 *
 *
 * location maps (with randomly chosen local numbering):
 *   [[ 0, 1, 2, 3, 6, 8, 10, 12, 7, 9, 11, 13, 17, 18, 19 ]
 *    [ 3, 12, 13, 19, 4, 14, 15, 21, 5, 16, 22, 20 ]
 *    [ 17, 23, 33, 34, 35, 26, 25, 19, 18, 24 ]
 *    [ 38, 22, 39, 37, 31, 32 ]
 *    [ 27, 29, 28, 30, 37, 36, 35, 26, 32, 31, 25, 22, 19, 21, 20 ]]
 */

TEST_CASE( "allocateSparseMatrix_test" )
{
    LocationMapVector locationMaps
    {
        { 0, 1, 2, 3, 6, 8, 10, 12, 7, 9, 11, 13, 17, 18, 19 },
        { 3, 12, 13, 19, 4, 14, 15, 21, 5, 16, 22, 20 },
        { 17, 23, 33, 34, 35, 26, 25, 19, 18, 24 },
        { 38, 22, 39, 37, 31, 32 },
        { 27, 29, 28, 30, 37, 36, 35, 26, 32, 31, 25, 22, 19, 21, 20 }
    };

    linalg::UnsymmetricSparseMatrix sparseMatrix;

    REQUIRE_NOTHROW( sparseMatrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( locationMaps ) );

    REQUIRE( sparseMatrix.size1( ) == 40 );
    REQUIRE( sparseMatrix.size2( ) == 40 );

    auto [indices, indptr, data] = sparseMatrix.release( );

    for( auto& locationMap : locationMaps )
    {
        std::sort( locationMap.begin( ), locationMap.end( ) );
    }

    std::vector<std::vector<size_t>> dofElementMapping =
    {
        { 0 }   , { 0 }   , { 0 }      , { 0, 1 }, { 1 },          // dofs  0 -  4
        { 1 }   , { 0 }   , { 0 }      , { 0 }   , { 0 },          // dofs  5 -  9
        { 0 }   , { 0 }   , { 0, 1 }   , { 0, 1 }, { 1 },          // dofs 10 - 14
        { 1 }   , { 1 }   , { 0, 2 }   , { 0, 2 }, { 0, 1, 2, 4 }, // dofs 15 - 19
        { 1, 4 }, { 1, 4 }, { 1, 3, 4 }, { 2 }   , { 2 },          // dofs 20 - 24
        { 2, 4 }, { 2, 4 }, { 4 }      , { 4 }   , { 4 },          // dofs 25 - 29
        { 4 }   , { 3, 4 }, { 3, 4 }   , { 2 }   , { 2 },          // dofs 30 - 34
        { 2, 4 }, { 4 }   , { 3, 4 }   , { 3 }   , { 3 }           // dofs 35 - 39
    };

    std::vector<size_t> connectingDofSizes;
    std::vector<size_t> expectedIndices;

    for( const std::vector<size_t>& elementIndices : dofElementMapping )
    {
        std::vector<size_t> concatenated;

        for( const auto& elementIndex : elementIndices )
        {
            const auto& locationMap = locationMaps[elementIndex];

            concatenated.insert( concatenated.end( ), locationMap.begin( ), locationMap.end( ) );
        }

        std::sort( concatenated.begin( ), concatenated.end( ) );
        concatenated.erase( std::unique( concatenated.begin( ), concatenated.end( ) ), concatenated.end( ) );

        connectingDofSizes.push_back( concatenated.size( ) );
        expectedIndices.insert( expectedIndices.end( ), concatenated.begin( ), concatenated.end( ) );
    };

    size_t nnz = expectedIndices.size( );
    
    REQUIRE( indptr[40] == nnz );

    for( size_t iEntry = 0; iEntry < nnz; ++iEntry )
    {
        CHECK( indices[iEntry] == expectedIndices[iEntry] );
        CHECK( data[iEntry] == 0.0 );
    }

    size_t rowPtr = 0;

    for( size_t iDof = 0; iDof < 40; ++iDof )
    {
        CHECK( indptr[iDof] == rowPtr );

        rowPtr += connectingDofSizes[iDof];
    }

    CHECK( indptr[40] == rowPtr );

    delete[] indptr;
    delete[] indices;
    delete[] data;

} // allocateSparseMatrix_test


namespace assemblytesthelper
{

auto paddedMatrix( std::initializer_list<std::initializer_list<double>> lists )
{
    AlignedDoubleVector data;

    for( const auto& row : lists )
    {
        auto oldSize = data.size( );

        data.resize( oldSize + memory::paddedLength<double>( row.size( ) ), 0.0 );

        std::copy( row.begin( ), row.end( ), data.begin( ) + static_cast<std::ptrdiff_t>( oldSize ) );
    }

    return data;
}

auto paddedVector( std::initializer_list<double> list )
{
    return paddedMatrix( { list } );
}

} // namespace assemblytesthelper

TEST_CASE( "AssemblyKernel_test" )
{
    LocationMapVector locationMaps
    {
        { 0, 1, 5 },
        { 1, 3, 2 },
        { 5, 6 },
        { 0, 4, 5, 6 }
    };

    auto rhs3 = assemblytesthelper::paddedVector( { 2.0, 1.0, 3.0 } );
    auto rhs2 = assemblytesthelper::paddedVector( { -2.0, -1.0 } );
    auto rhs4 = assemblytesthelper::paddedVector( { 3.0, -4.0, 2.0, -3.0 } );
    
    DofIndicesValuesPair boundaryDofs { { 0, 2 }, { -3.3, 2.2 } };

    SECTION( "UnsymmetricElement" )
    {
        auto matrix1 = allocateMatrix<linalg::UnsymmetricSparseMatrix>( locationMaps, boundaryDofs.first );
        auto matrix2 = allocateMatrix<linalg::UnsymmetricSparseMatrix>( locationMaps, boundaryDofs.first );

        auto F1 = std::vector<double>( 5, 0.0 );
        auto F2 = std::vector<double>( 5, 0.0 );

        auto type1 = AssemblyType::UnsymmetricMatrix;
        auto type2 = AssemblyType::Vector;

        auto assembleSystem = makeAssemblyKernel( { matrix1, F1 }, { type1, type2 }, boundaryDofs, 7 );
        auto assembleLhs = makeAssemblyKernel( { matrix2 }, { type1 }, boundaryDofs, 7 );
        auto assembleRhs = makeAssemblyKernel( { F2 }, { type2 }, boundaryDofs, 7 );

        CHECK( matrix1.nnz( ) == 15 );

        std::fill( matrix1.data( ), matrix1.data( ) + matrix1.nnz( ), 0.0 );

        auto matrix33 = assemblytesthelper::paddedMatrix( { {  1.0,  2.0,  1.0 },
                                                            { -2.0,  1.0,  3.0 },
                                                            {  1.0, -3.0,  2.0 } } );

        auto matrix22 = assemblytesthelper::paddedMatrix( { {  2.0, -1.0 },
                                                            { -1.0,  3.0 } } );

        auto matrix44 = assemblytesthelper::paddedMatrix ( { {  2.0,  1.0,  2.0, -3.0 },
                                                             { -1.0, -1.0,  2.0, -2.0 },
                                                             { -3.0,  1.0, -1.0,  3.0 },
                                                             {  1.0,  0.0, -1.0,  1.0 } } );

        std::vector<size_t> tmp;

        // Scatter system
        assembleSystem( { matrix33, rhs3 }, locationMaps[0], tmp );
        assembleSystem( { matrix33, rhs3 }, locationMaps[1], tmp );
        assembleSystem( { matrix22, rhs2 }, locationMaps[2], tmp );
        assembleSystem( { matrix44, rhs4 }, locationMaps[3], tmp );

        // Scatter matrix
        assembleLhs( { matrix33 }, locationMaps[0], tmp );
        assembleLhs( { matrix33 }, locationMaps[1], tmp );
        assembleLhs( { matrix22 }, locationMaps[2], tmp );
        assembleLhs( { matrix44 }, locationMaps[3], tmp );

        // Scatter vector
        assembleRhs( { rhs3 }, locationMaps[0], tmp );
        assembleRhs( { rhs3 }, locationMaps[1], tmp );
        assembleRhs( { rhs2 }, locationMaps[2], tmp );
        assembleRhs( { rhs4 }, locationMaps[3], tmp );

        std::vector<double> expectedData {  2.0, 2.0, 3.0, -2.0, 1.0, -1.0, 2.0, -2.0,
                                           -3.0, 1.0, 3.0,  2.0, 0.0, -2.0, 4.0 };

        std::vector<double> expectedRhs1 { -5.8, -5.6, -7.3, -3.6, -0.7 };
        std::vector<double> expectedRhs2 { 3.0, 1.0, -4.0, 3, -4 };

        CHECK( utilities::floatingPointEqual( expectedData.begin( ), expectedData.end( ), matrix1.data( ), 1e-12 ) );
        CHECK( utilities::floatingPointEqual( expectedData.begin( ), expectedData.end( ), matrix2.data( ), 1e-12 ) );

        CHECK( utilities::floatingPointEqual( expectedRhs1.begin( ), expectedRhs1.end( ), F1.begin( ), 1e-12 ) );
        CHECK( utilities::floatingPointEqual( expectedRhs2.begin( ), expectedRhs2.end( ), F2.begin( ), 1e-12 ) );
    }

    SECTION( "SymmetricElement" )
    {
        auto matrix1 = allocateMatrix<linalg::SymmetricSparseMatrix>( locationMaps, boundaryDofs.first );
        auto matrix2 = allocateMatrix<linalg::UnsymmetricSparseMatrix>( locationMaps, boundaryDofs.first );
        auto matrix3 = allocateMatrix<linalg::SymmetricSparseMatrix>( locationMaps, boundaryDofs.first );
        auto matrix4 = allocateMatrix<linalg::UnsymmetricSparseMatrix>( locationMaps, boundaryDofs.first );

        CHECK( matrix1.nnz( ) == 10 );
        CHECK( matrix2.nnz( ) == 15 );

        std::fill( matrix1.data( ), matrix1.data( ) + matrix1.nnz( ), 0.0 );
        std::fill( matrix2.data( ), matrix2.data( ) + matrix2.nnz( ), 0.0 );
        std::fill( matrix3.data( ), matrix3.data( ) + matrix3.nnz( ), 0.0 );
        std::fill( matrix4.data( ), matrix4.data( ) + matrix4.nnz( ), 0.0 );

        std::vector<double> F1( 5, 0.0 );
        std::vector<double> F2( 5, 0.0 );

        auto type1 = AssemblyType::SymmetricMatrix;
        auto type2 = AssemblyType::Vector;

        auto assembleSystem1 = makeAssemblyKernel( { matrix1, F1 }, { type1, type2 }, boundaryDofs, 7 );
        auto assembleSystem2 = makeAssemblyKernel( { matrix2, F2 }, { type1, type2 }, boundaryDofs, 7 );
        auto assembleLhs1 = makeAssemblyKernel( { matrix3 }, { type1 }, boundaryDofs, 7 );
        auto assembleLhs2 = makeAssemblyKernel( { matrix4 }, { type1 }, boundaryDofs, 7 );

        auto matrix33 = assemblytesthelper::paddedMatrix( { {  1.0 },
                                                            { -2.0,  1.0 },
                                                            {  1.0, -3.0,  2.0 } } );

        auto matrix22 = assemblytesthelper::paddedMatrix( { {  2.0 },
                                                            { -1.0,  3.0 } } );

        auto matrix44 = assemblytesthelper::paddedMatrix ( { {  2.0 },
                                                             { -1.0, -1.0 },
                                                             { -3.0,  1.0, -1.0 },
                                                             {  1.0,  0.0, -1.0,  1.0 } } );

        std::vector<size_t> tmp;

        // Scatter system
        assembleSystem1( { matrix33, rhs3 }, locationMaps[0], tmp );
        assembleSystem1( { matrix33, rhs3 }, locationMaps[1], tmp );
        assembleSystem1( { matrix22, rhs2 }, locationMaps[2], tmp );
        assembleSystem1( { matrix44, rhs4 }, locationMaps[3], tmp );

        assembleSystem2( { matrix33, rhs3 }, locationMaps[0], tmp );
        assembleSystem2( { matrix33, rhs3 }, locationMaps[1], tmp );
        assembleSystem2( { matrix22, rhs2 }, locationMaps[2], tmp );
        assembleSystem2( { matrix44, rhs4 }, locationMaps[3], tmp );

        // Scatter matrix
        assembleLhs1( { matrix33 }, locationMaps[0], tmp );
        assembleLhs1( { matrix33 }, locationMaps[1], tmp );
        assembleLhs1( { matrix22 }, locationMaps[2], tmp );
        assembleLhs1( { matrix44 }, locationMaps[3], tmp );

        assembleLhs2( { matrix33 }, locationMaps[0], tmp );
        assembleLhs2( { matrix33 }, locationMaps[1], tmp );
        assembleLhs2( { matrix22 }, locationMaps[2], tmp );
        assembleLhs2( { matrix44 }, locationMaps[3], tmp );

        std::vector<double> expectedDataSymmetric
        {
            2.0, -2.0,       -3.0,
                  1.0,
                       -1.0,  1.0,  0.0,
                              3.0, -2.0,
                                    4.0
        };

        std::vector<double> expectedDataUnsymmetric
        {
             2.0, -2.0,       -3.0,
            -2.0,  1.0,
                        -1.0,  1.0,  0.0,
            -3.0,        1.0,  3.0, -2.0,
                         0.0, -2.0,  4.0
        };

        std::vector<double> expectedRhs { -5.8, 7.6, -7.3, -3.6, -0.7 };

        CHECK( utilities::floatingPointEqual( expectedDataSymmetric.begin( ),
                                              expectedDataSymmetric.end( ),
                                              matrix1.data( ), 1e-12 ) );

        CHECK( utilities::floatingPointEqual( expectedDataSymmetric.begin( ),
                                              expectedDataSymmetric.end( ),
                                              matrix3.data( ), 1e-12 ) );

        CHECK( utilities::floatingPointEqual( expectedDataUnsymmetric.begin( ),
                                              expectedDataUnsymmetric.end( ),
                                              matrix2.data( ), 1e-12 ) );

        CHECK( utilities::floatingPointEqual( expectedDataUnsymmetric.begin( ),
                                              expectedDataUnsymmetric.end( ),
                                              matrix4.data( ), 1e-12 ) );

        CHECK( utilities::floatingPointEqual( expectedRhs.begin( ), expectedRhs.end( ), F1.begin( ), 1e-12 ) );
        CHECK( utilities::floatingPointEqual( expectedRhs.begin( ), expectedRhs.end( ), F2.begin( ), 1e-12 ) );
    }
}

} // namespace mlhp
