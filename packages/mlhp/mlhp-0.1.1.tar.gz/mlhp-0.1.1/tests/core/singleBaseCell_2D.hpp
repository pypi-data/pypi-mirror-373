// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_FEKERNEL_TEST_SINGLEBASECELL2D_HPP
#define MLHP_FEKERNEL_TEST_SINGLEBASECELL2D_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/ndarray.hpp"

#include <array>
#include <vector>
#include <optional>

namespace mlhp::singlebasecell2d
{

extern size_t numberOfElements;
extern size_t numberOfLeafElements;

extern std::vector<RefinementLevel> levels;
extern std::vector<CellIndex> parents;
extern std::vector<bool> isLeaf;
extern std::vector<PositionInParent<2>> positionsInParent;
extern std::vector<std::array<CellIndex, 4>> children;
extern std::vector<std::array<CellIndex, 4>> neighboursData;
extern std::vector<std::array<size_t, 2>> inhomogeneousDegrees;
extern LinearizedTensorProductIndices<2> homogeneousTensorProductIndices34;
extern LinearizedTensorProductIndices<2> inhomogeneousTensorProductIndices;

NCubeNeighboursVector<2> neighbours( );

std::vector<std::pair<CellIndex, size_t>> boundaries( );

std::vector<std::vector<std::vector<size_t>>> elementFaceDofs( );

} // mlhp::singlebasecell2d

/*
 * Quad tree of depth 3 on [0, 1] x [0 x 1] towards boundary 
 * of circle with origin (0,0) and radius 0.8 (using 6 seed
 * points in each direction). Below is the numbering of the 
 * resulting tree.
 *
 * level 0:
 *  ---------------------------------------
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                  0                    |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 * |                                       |
 *  ---------------------------------------
 *
 * level 1:
 *  ---------------------------------------
 * |                   |                   |
 * |                   |                   |
 * |                   |                   |
 * |         2         |         4         |
 * |                   |                   |
 * |                   |                   |
 * |                   |                   |
 * |-------------------|-------------------|
 * |                   |                   |
 * |                   |                   |
 * |                   |                   |
 * |         1         |         3         |
 * |                   |                   |
 * |                   |                   |
 * |                   |                   |
 *  ---------------------------------------
 *
 * level 2:
 *  ---------------------------------------
 * |         |         |         |         |
 * |    6    |    8    |    14   |    16   |
 * |         |         |         |         |
 * |---------|---------|---------|---------|
 * |         |         |         |         |
 * |    5    |    7    |    13   |    15   |
 * |         |         |         |         |
 * |-------------------|-------------------|
 * |                   |         |         |
 * |                   |    10   |    12   |
 * |                   |         |         |
 * |                   |---------|---------|
 * |                   |         |         |
 * |                   |    9    |    11   |
 * |                   |         |         |
 *  ---------------------------------------
 *
 * level 3:
 *  ---------------------------------------
 * | 18 | 20 | 26 | 28 |         |         |
 * |----|----|----|----|         |         |
 * | 17 | 19 | 25 | 27 |         |         |
 * |---------|---------|---------|---------|
 * |         | 22 | 24 | 42 | 44 |         |
 * |         |----|----|----|----|         |
 * |         | 21 | 23 | 41 | 43 |         |
 * |-------------------|---------|---------|
 * |                   | 30 | 32 | 38 | 40 |
 * |                   |----|----|----|----|
 * |                   | 29 | 31 | 37 | 39 |
 * |                   |---------|---------|
 * |                   |         | 34 | 36 |
 * |                   |         |----|----|
 * |                   |         | 33 | 35 |
 *  ---------------------------------------
 */

/* Inhomogeneous anisotropic degrees:
 *
 *  -------------------------------------------------------
 * | 2, 3 | 3, 2 | 1, 1 | 2, 4 |             |             |
 * |------|------|------|------|    1, 1     |     2, 4    |
 * | 4, 2 | 1, 3 | 4, 3 | 3, 3 |             |             |
 * |-------------|------|------|-------------|-------------|
 * |             | 3, 2 | 4, 1 | 3, 3 | 2, 3 |             |
 * |     4, 4    |------|------|------|------|     1, 3    |
 * |             | 2, 3 | 2, 2 | 2, 3 | 4, 1 |             |
 * |---------------------------|------|------|-------------|
 * |                           | 3, 2 | 3, 3 | 4, 1 | 3, 2 |
 * |                           |------|------|------|------|
 * |                           | 1, 1 | 1, 2 | 2, 3 | 4, 1 |
 * |           2, 3            |-------------|------|------|
 * |                           |             | 3, 4 | 2, 2 |
 * |                           |    3, 4     |------|------|
 * |                           |             | 1, 1 | 4, 3 |
 *  -------------------------------------------------------
 */

#endif // MLHP_FEKERNEL_TEST_SINGLEBASECELL2D_HPP
