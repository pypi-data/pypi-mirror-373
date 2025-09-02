// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_TOPOLOGYCORE_HPP
#define MLHP_CORE_TOPOLOGYCORE_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/utilities.hpp"

namespace mlhp::topology
{

MLHP_EXPORT
RefinementLevelVector refinementLevels( const CellIndexVector& parents );

MLHP_EXPORT
RefinementLevel maxRefinementLevel( const CellIndexVector& parents );

MLHP_EXPORT
std::vector<bool> leafMask( const CellIndexVector& parents );

MLHP_EXPORT
CellIndexVector leafIndexOrChild( const CellIndexVector& parents,
                                  const std::vector<bool>& leafMask );

template<size_t D> MLHP_EXPORT
void checkConsistency( CoordinateConstSpan<D> vertices, 
                       std::span<const size_t> connectivity,
                       std::span<const size_t> offsets,
                       std::span<const CellType> types );

//! Filter vertices that do not belong to any cell and return vertex index map
template<size_t D> MLHP_EXPORT
std::vector<size_t> filterVertices( CoordinateList<D>& vertices,
                                    std::span<size_t> connectivity );

//! Reorder connectivity to ensure positive Jacobian
template<size_t D> MLHP_EXPORT
void reorderVertices( CoordinateConstSpan<D> vertices,
                      std::span<size_t> connectivity,
                      std::span<const size_t> offsets,
                      std::span<const CellType> types );

//! Compute cell - cell connectivity
template<size_t D> MLHP_EXPORT 
NeighboursVector neighbours( std::span<const size_t> connectivity,
                             std::span<const size_t> offsets,
                             std::span<const CellType> types );

//! Local vertex indices for given cell type and face id
template<size_t D> MLHP_EXPORT 
void faceVertices( CellType type, size_t iface, std::vector<size_t>& target );

MLHP_EXPORT
std::string cellTypeString( CellType type, size_t D, bool plural, bool upper = false );

} // mlhp::topology

namespace mlhp
{

//! Split face index into normal and side. For example, face 3 of a cube in 3D 
//! is normal to axis 1 (y) and is the second face along that axis (index 1).
constexpr std::pair<size_t, size_t> normalAxisAndSide( size_t iface )
{
    auto axis = iface / 2;

    return { axis, iface - 2 * axis };
}

constexpr size_t ncubeFaceIndex( size_t normal, size_t axis )
{
    return 2 * normal + axis;
}

}

#endif // MLHP_CORE_TOPOLOGYCORE_HPP
