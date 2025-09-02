// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_POSTPROCESSING_IMPL_HPP
#define MLHP_CORE_POSTPROCESSING_IMPL_HPP

#include "mlhp/core/mesh.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/utilities.hpp"

#include "vtu11/vtu11.hpp"

#include <functional>
#include <vector>
#include <any>

namespace mlhp
{
namespace detail
{

template<size_t D> MLHP_EXPORT
void createPostprocessingGrid( CoordinateGrid<D>& rst,
                               std::array<size_t, D> numberOfCells );

template<size_t D> MLHP_EXPORT
void appendVtuPostprocessingGrid( std::array<size_t, D> resolution,
                                  PostprocessTopologies topologies,
                                  std::vector<vtu11::VtkIndexType>& connectivity,
                                  std::vector<vtu11::VtkIndexType>& offsets,
                                  std::vector<vtu11::VtkCellType>& types );

MLHP_EXPORT
std::function<void( )> offsetPoints( const std::vector<double>& pointData,
                                     std::vector<vtu11::VtkIndexType>& connectivity );

template<size_t D> MLHP_EXPORT
void appendPointData( std::vector<double>& points,
                      const CoordinateList<D>& xyz );

template<size_t D> constexpr auto vtuOrdering( );

template<> constexpr auto vtuOrdering<1>( ) { return std::array<size_t, 2>{ 0, 1 }; }
template<> constexpr auto vtuOrdering<2>( ) { return std::array<size_t, 4>{ 0, 3, 1, 2 }; }
template<> constexpr auto vtuOrdering<3>( ) { return std::array<size_t, 8>{ 0, 4, 3, 7, 1, 5, 2, 6 }; }

constexpr vtu11::VtkCellType cubicTypes[] = { 1, 3, 9, 12 };
constexpr vtu11::VtkCellType simplexTypes[] = { 1, 3, 5, 10 };

} // namespace detail
} // mlhp

#endif // MLHP_CORE_POSTPROCESSING_IMPL_HPP
