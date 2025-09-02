// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/kdtree.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/algorithm.hpp"

#include <execution>
#include <filesystem>

namespace mlhp
{
namespace kdtree
{
namespace
{

template<size_t D>
void appendEvents( const spatial::BoundingBox<D>& bounds,
                   std::vector<Event>& events,
                   size_t itriangle )
{
    for( std::uint8_t axis = 0; axis < D; ++axis )
    {
        MLHP_CHECK( bounds[1][axis] >= bounds[0][axis], "Invalid bounding box.");

        // Not planar
        if( bounds[1][axis] > bounds[0][axis] )
        {
            events.push_back( { itriangle, bounds[0][axis], axis, Event::Type::Starts } );
            events.push_back( { itriangle, bounds[1][axis], axis, Event::Type::Ends } );
        }
        // Planar
        else
        {
            auto x = std::midpoint( bounds[0][axis], bounds[1][axis] );

            events.push_back( { itriangle, x, axis, Event::Type::Planar } );
        }
    }
}

auto makeEventComparator( )
{
    return [=]( const Event& left, const Event& right )
    {
        if( left.position != right.position )
        {
            return left.position < right.position;
        }
        
        auto leftType = static_cast<size_t>( left.type );
        auto rightType = static_cast<size_t>( right.type );

        if( leftType != rightType )
        {
            return leftType < rightType;
        }

        if( left.axis != right.axis )
        {
            return left.axis < right.axis;
        }

        return left.itriangle < right.itriangle;
    };
}

} // namespace

template<size_t D>
std::vector<Event> createSortedEventList( const kdtree::ObjectProvider<D>& provider,
                                          const spatial::BoundingBox<D>& bounds )
{
    auto chunkData = utilities::divideIntoChunks<size_t>( provider.size( ), 128, 1024 );
    auto globalEvents = std::vector<Event> { };

    #pragma omp parallel
    {
        auto events = std::vector<Event> { };

        #pragma omp for schedule( dynamic )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( chunkData[0] ); ++ii )
        {
            auto ichunk = static_cast<size_t>( ii );

            auto [chunkBegin, chunkEnd] = utilities::chunkRange( ichunk, chunkData );

            utilities::resize0( events );

            for( auto itriangle = chunkBegin; itriangle < chunkEnd; ++itriangle )
            {
                auto clippedBounds = provider( itriangle, bounds );

                if( spatial::boundingBoxIsValid( clippedBounds ) )
                {
                    appendEvents( clippedBounds, events, itriangle );
                }
            }

            #pragma omp critical
            {
                globalEvents.insert( globalEvents.end( ), events.begin( ), events.end( ) );
            }
        } // for ichunk
    } // omp parallel 

    //std::sort( std::execution::parallel_unsequenced_policy { }, globalEvents.begin( ), 
    //    globalEvents.end( ), makeEventComparator( parameters ) );

    std::sort( globalEvents.begin( ), globalEvents.end( ), makeEventComparator( ) );

    return globalEvents;
}

template<size_t D>
auto makeSurfaceAreaRatioCalculator( spatial::BoundingBox<D> V )
{
    auto SA = []( const spatial::BoundingBox<D>& box )
    {
        auto diff = box[1] - box[0];
        auto area = 0.0;

        for( size_t axis0 = 0; axis0 < D; ++axis0 )
        {
            area += 2.0 * array::product( array::setEntry( diff, axis0, 1.0 ) );
        }

        return area;
    };

    auto area = SA( V );

    return [=]( size_t normal, double position )
    {
        auto [A0, A1] = splitBoundingBox( V, static_cast<std::uint8_t>( normal ), position );
        
        MLHP_CHECK( position >= V[0][normal], "Position below bounds." );
        MLHP_CHECK( position <= V[1][normal], "Position above bounds." );

        double t = 0.5;

        if( area < std::sqrt( std::numeric_limits<double>::min( ) ) )
        {
            return std::array { 1e20, 1e20, 0.5 };
        }

        if( auto diff = V[1][normal] - V[0][normal]; diff > 1e-10 )
        {
            t = ( position - V[0][normal] ) / diff;
        }

        return std::array { SA( A0 ) / area, SA( A1 ) / area, t };
    };
}

template<size_t D>
auto makeSurfaceAreaHeuristic( spatial::BoundingBox<D> bounds, 
                               const Parameters& parameters )
{
    auto SA = makeSurfaceAreaRatioCalculator( bounds );

    return [=](std::uint8_t axis, double x, size_t NL, size_t NR, size_t NP)
    {
        auto [PL, PR, t] = SA(axis, x);

        auto bias = ( NL == 0 || NR == 0 ) && PL != 1 && PR != 1 && t > 1e-8 && t < 1.0 - 1e-8;
        auto lambda = bias ? parameters.emptyCellBias : 1.0;

        auto cpL = lambda * ( parameters.KT + parameters.KL * ( PL * ( NL + NP ) + PR * NR ) );
        auto cpR = lambda * ( parameters.KT + parameters.KL * ( PL * NL + PR * ( NR + NP ) ) );

        MLHP_CHECK( cpL >= 0.0, "Invalid cost estimate" );
        MLHP_CHECK( cpR >= 0.0, "Invalid cost estimate" );

        return cpL < cpR ? std::pair { cpL, 0 } : std::pair { cpR, 1 };
    };
}

template<size_t D>
std::array<double, 3> computeSurfaceAreaRatios( spatial::BoundingBox<D> bounds,
                                                size_t normal, double position )
{
    return makeSurfaceAreaRatioCalculator<D>( bounds )( normal, position );
}

template<size_t D>
Plane findPlane( size_t N, const spatial::BoundingBox<D>& V, std::span<const Event> E, const Parameters& parameters )
{
    auto NLk = array::makeSizes<D>( 0 );
    auto NPk = array::makeSizes<D>( 0 );
    auto NRk = array::makeSizes<D>( N );

    auto minP = Plane { 0.0, 0, 0, std::numeric_limits<double>::max( ) };
    auto nevents = E.size( );

    auto SAH = makeSurfaceAreaHeuristic( V, parameters );

    for( size_t i = 0; i < E.size( ); )
    {
        auto k = E[i].axis;
        auto x = E[i].position;

        MLHP_CHECK( x >= V[0][k] - 1e-10, "Invalid event." );
        MLHP_CHECK( x <= V[1][k] + 1e-10, "Invalid event." );

        size_t pPlus = 0, pMinus = 0, pPlane = 0;

        while( i < nevents && E[i].axis == k && E[i].position == x && E[i].type == Event::Type::Ends )
        {
            pMinus += 1;
            i += 1;
        }

        while( i < nevents && E[i].axis == k && E[i].position == x && E[i].type == Event::Type::Planar )
        {
            pPlane += 1;
            i += 1;
        }

        while( i < nevents && E[i].axis == k && E[i].position == x && E[i].type == Event::Type::Starts )
        {
            pPlus += 1;
            i += 1;
        }

        NPk[k]  = pPlane;
        NRk[k] -= pPlane;
        NRk[k] -= pMinus;

        auto [C, pSide] = SAH( k, x, NLk[k], NRk[k], NPk[k] );

        if( C < std::get<3>( minP ) )
        {
            minP = { x, k, pSide, C };
        }

        NLk[k] += pPlus;
        NLk[k] += pPlane;
        NPk[k] = 0;
    }

    return minP;
}

void classifyTriangles( std::span<const size_t> indices,
                        std::span<const Event> events,
                        std::vector<size_t>& sides,
                        Plane plane )
{
    sides.resize( indices.size( ) );
    
    std::fill( sides.begin( ), sides.end( ), 1 );

    auto [position, axis, side, C] = plane;

    for( auto E : events )
    {
        if( E.axis == axis )
        {
            if( E.type == Event::Type::Ends && E.position <= position )
            {
                sides[E.itriangle] = 0;
            }
            else if( E.type == Event::Type::Starts && E.position >= position )
            {
                sides[E.itriangle] = 2;
            }
            else if( E.type == Event::Type::Planar )
            {
                if( E.position < position || ( E.position <= position && side == 0 ) )
                {
                    sides[E.itriangle] = 0;
                }
                else if( E.position > position || ( E.position >= position && side == 1 ) )
                {
                    sides[E.itriangle] = 2;
                }
            }
        } // if same axis
    } // for each event
} // classifyTriangles

std::vector<size_t> classifyTriangles( std::span<const size_t> indices,
                                       std::span<const Event> events,
                                       Plane plane )
{
    auto sides = std::vector<size_t> { };

    classifyTriangles( indices, events, sides, plane );

    return sides;
}

template<size_t D>
std::array<spatial::BoundingBox<D>, 2> splitBoundingBox( spatial::BoundingBox<D> bounds, std::uint8_t axis, double position )
{
    spatial::BoundingBox<D> bounds0 = bounds, bounds1 = bounds;

    bounds0[1][axis] = position;
    bounds1[0][axis] = position;

    return std::array { bounds0, bounds1 };
}

struct SAH
{
    using Data = Event;

    Parameters parameters;

    template<size_t D>
    std::vector<Event> initializeData( const kdtree::ObjectProvider<D>& provider,
                                       const spatial::BoundingBox<D>& bounds )
    {
        return kdtree::createSortedEventList( provider, bounds );
    }

    template<size_t D>
    std::optional<Plane> split( std::span<const size_t> items,
                                std::span<const Event> data,
                                const spatial::BoundingBox<D>& bounds )
    {
        auto plane = findPlane( items.size( ), bounds, data, parameters );
        auto subdivide = std::get<3>( plane ) <= parameters.KL * items.size( );

        return subdivide ? std::optional { plane } : std::nullopt;
    }

    std::vector<size_t> map0 = { }, map1 = { }, sides = { };

    template<size_t D>
    auto associate( const kdtree::ObjectProvider<D>& provider,
                    std::span<const size_t> triangles,
                    std::span<const Event> events,
                    const spatial::BoundingBox<D>& bounds,
                    Plane plane,
                    std::vector<size_t>& triangles0,
                    std::vector<size_t>& triangles1,
                    std::vector<Event>& events0,
                    std::vector<Event>& events1 )
    {

        classifyTriangles( triangles, events, sides, plane );

        map0.resize( triangles.size( ), NoValue<size_t> );
        map1.resize( triangles.size( ), NoValue<size_t> );
    
        auto [split0, split1] = splitBoundingBox( bounds, std::get<1>( plane ), std::get<0>( plane ) );
        
        // Split triangles while clipping those in the intersection plane
        for( size_t i = 0; i < sides.size( ); ++i )
        {
            if( sides[i] == 0 )
            {
                map0[i] = triangles0.size( );

                triangles0.push_back( triangles[i] );
            }
            else if( sides[i] == 2 )
            {
                map1[i] = triangles1.size( );

                triangles1.push_back( triangles[i] );
            }
            else
            {
                auto bounds0 = provider( triangles[i], split0 );
                auto bounds1 = provider( triangles[i], split1 );

                auto valid0 = spatial::boundingBoxIsValid( bounds0 );
                auto valid1 = spatial::boundingBoxIsValid( bounds1 );

                if( valid0 )
                {
                    map0[i] = triangles0.size( );

                    triangles0.push_back( triangles[i] );

                    appendEvents( bounds0, events0, map0[i] );
                }

                if( valid1 )
                {
                    map1[i] = triangles1.size( );

                    triangles1.push_back( triangles[i] );

                    appendEvents( bounds1, events1, map1[i] );
                }
            }
        }
        
        auto size0 = events0.size( );
        auto size1 = events1.size( );

        // Create new event lists with left only and right only
        for( auto& event : events )
        {
            if( sides[event.itriangle] == 0 )
            {
                events0.push_back( event );

                events0.back( ).itriangle = map0[events0.back( ).itriangle];
            }
            if( sides[event.itriangle] == 2 )
            {
                events1.push_back( event );

                events1.back( ).itriangle = map1[events1.back( ).itriangle];
            }
        }
    
        // Merge lists
        auto cmp = makeEventComparator( );

        std::sort( events0.begin( ), events0.begin( ) + utilities::ptrdiff( size0 ), cmp );
        std::sort( events1.begin( ), events1.begin( ) + utilities::ptrdiff( size1 ), cmp );

        std::inplace_merge( events0.begin( ), events0.begin( ) + utilities::ptrdiff( size0 ), events0.end( ), cmp );
        std::inplace_merge( events1.begin( ), events1.begin( ) + utilities::ptrdiff( size1 ), events1.end( ), cmp );

        MLHP_CHECK_DBG( std::is_sorted( events0.begin( ), events0.end( ), cmp ), "Unsorted." );
        MLHP_CHECK_DBG( std::is_sorted( events1.begin( ), events1.end( ), cmp ), "Unsorted." );
    }
};

} // namespace kdtree

// Following I. Wald, V. Havran. On building fast kd-Trees for Ray Tracing, and on doing 
// that in O(N log N): https://dcgi.felk.cvut.cz/home/havran/ARTICLES/ingo06rtKdtree.pdf
// See also https://github.com/arvearve/Raytracer/blob/master/BasicRayTracer/kdTree.cpp
template<size_t D, typename Strategy>
KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,
                       const spatial::BoundingBox<D>& treeBounds,
                       Strategy& strategy )
{
    auto nodes = std::vector{ typename KdTree<D>::Node { } };
    auto leafItems = std::vector<size_t>{ };

    auto recurse = [&]( auto& self, size_t level, size_t index,
                        std::vector<size_t>&& indices,
                        std::vector<kdtree::Event>&& events,
                        spatial::BoundingBox<D> nodeBounds ) -> void
    {
        if( level < strategy.parameters.maxdepth )
        {
            auto optionalPlane = strategy.split( indices, events, nodeBounds );
        
            if( optionalPlane )
            {
                auto plane = *optionalPlane;
                auto size = nodes.size( );

                nodes[index].axis = std::get<1>( plane );
                nodes[index].data.position = std::get<0>( plane );
                nodes[index].leafOrChild = static_cast<CellIndex>( size );

                nodes.push_back( typename KdTree<D>::Node { } );
	            nodes.push_back( typename KdTree<D>::Node { } );

                std::vector<size_t> indices0, indices1;
                std::vector<kdtree::Event> events0, events1;

                strategy.associate( provider, indices, events, nodeBounds, plane, indices0, indices1, events0, events1 );

                auto [bounds0, bounds1] = kdtree::splitBoundingBox( nodeBounds, std::get<1>( plane ), std::get<0>( plane ) );
        
                self( self, level + 1, size + 0, std::move( indices0 ), std::move( events0 ), bounds0 );
                self( self, level + 1, size + 1, std::move( indices1 ), std::move( events1 ), bounds1 );
        
                return;
            }
        }

        MLHP_CHECK( indices.size( ) <= NoValue<std::uint8_t>, "Error in KdTree construction: item count (n = " + 
            std::to_string( indices.size( ) ) + ") at cell index " + std::to_string( index ) + " exceeds 255." );

        nodes[index].data.offset = leafItems.size( );
        nodes[index].nitems = static_cast<std::uint8_t>( indices.size( ) );

        if( indices.size( ) >= NoValue<std::uint8_t> )
        {
            nodes[index].nitems = NoValue<std::uint8_t>;
            leafItems.push_back( indices.size( ) );
        }

        std::sort( indices.begin( ), indices.end( ) );

        leafItems.insert( leafItems.end( ), indices.begin( ), indices.end( ) );
    };
 
    auto data = strategy.initializeData( provider, treeBounds );
    auto indices = std::vector<size_t>( provider.size( ) );
    
    std::iota( indices.begin( ), indices.end( ), size_t { 0  } );
   
    recurse( recurse, 0, 0, std::move( indices ), std::move( data ), treeBounds );

    return KdTree<D>( treeBounds, std::move( nodes ), std::move( leafItems ) );
}

template<size_t D>
KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,
                       const spatial::BoundingBox<D>& bounds,
                       const kdtree::Parameters& parameters )
{    
    auto strategy = kdtree::SAH { parameters };

    return buildKdTree( provider, bounds, strategy );
}

template<size_t D>
KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,
                       const kdtree::Parameters& parameters )
{
    auto global = spatial::makeEmptyBoundingBox<D>( );
    auto size = static_cast<std::int64_t>( provider.size( ) );

    #pragma omp parallel
    {
        auto local = spatial::makeEmptyBoundingBox<D>( );
        auto full = spatial::makeFullBoundingBox<D>( );

        #pragma omp for
        for( std::int64_t ii = 0; ii < size; ++ii )
        {
            auto bounds = provider( static_cast<size_t>( ii ), full );

            local = spatial::boundingBoxOr( local, bounds );
        }

        #pragma omp critical
        {
            global = spatial::boundingBoxOr( global, local );
        }
    }

    return buildKdTree( provider, global, parameters );
}

template<size_t D>
KdTree<D>::KdTree( spatial::BoundingBox<D> bounds,
                   std::vector<Node>&& nodes,
                   std::vector<size_t>&& data ) :
        bounds_ ( bounds ), nodes_( std::move( nodes ) ), data_( std::move( data ) )
{ 
    auto count = []( auto&& node ) { return node.axis == NoValue<std::uint8_t>; };
    auto leafcount = std::count_if( nodes_.begin( ), nodes_.end( ), count );

    fullIndices_.resize( static_cast<size_t>( leafcount ) );
    parents_.resize( nfull( ) );
    parents_[0] = NoCell;

    auto ileaf = CellIndex { 0 };

    for( auto ifull = CellIndex { 0 }; ifull < nodes_.size( ); ++ifull )
    {
        if( isLeaf( ifull ) )
        {
            nodes_[ifull].leafOrChild = ileaf;
            fullIndices_[ileaf++] = ifull;
        }
        else
        {
            parents_[nodes_[ifull].leafOrChild + 0] = ifull;
            parents_[nodes_[ifull].leafOrChild + 1] = ifull;
        }
    }
}

template<size_t D>
MeshUniquePtr<D> KdTree<D>::clone( ) const
{
    return std::make_unique<KdTree<D>>( *this );
}

template<size_t D>
CellIndex KdTree<D>::nfull( ) const
{
    return static_cast<CellIndex>( nodes_.size( ) );
}

template<size_t D>
CellIndex KdTree<D>::nleaves( ) const
{
    return static_cast<CellIndex>( fullIndices_.size( ) );
}

template<size_t D>
CellIndex KdTree<D>::ncells( ) const
{
    return nleaves( );
}

template<size_t D>
size_t KdTree<D>::maxdepth( ) const
{
    auto traverse = [&]( auto& self, CellIndex index ) MLHP_PURE -> size_t
    {
        return isLeaf( index ) ? size_t { 0 } : std::max( 
            self( self, child( index, 0 ) ), self( self, child( index, 1 ) ) ) + 1;
    };

    return traverse( traverse, 0 );
}

template<size_t D>
size_t KdTree<D>::memoryUsage( ) const
{
    auto size = utilities::vectorInternalMemory( data_, fullIndices_, parents_ );

    return size + sizeof( nodes_[0] ) * nodes_.capacity( );
}

template<size_t D>
spatial::BoundingBox<D> KdTree<D>::boundingBox( ) const
{
    return bounds_;
}

template<size_t D>
void KdTree<D>::intersect( const spatial::BoundingBox<D>& bounds,
                           const BBIntersectCallback& callback ) const
{
    if( spatial::boundingBoxIntersectsOther( bounds, bounds_ ) )
    {
        auto traverse = [&]( auto&& self, CellIndex index ) -> void
        {    
            if( !isLeaf( index ) )
            {
                auto [axis, position] = split( index );

                auto eps = 1e-12 * ( bounds[1][axis] - bounds[0][axis] );

                if( bounds[0][axis] - eps <= position ) self( self, child( index, 0 ) );
                if( bounds[1][axis] + eps >= position ) self( self, child( index, 1 ) );
            }
            else
            {
                callback( index );
            }
        };

        traverse( traverse, 0 );
    }
}

namespace
{

template<size_t D>
auto internalIntersectRay( const KdTree<D>& tree,
                           const std::array<double, D>& rayOrigin,
                           const std::array<double, D>& invDirection,
                           auto&& callback )
{
    auto treebounds = tree.boundingBox( );
    auto tminmax = spatial::OptionalTBounds { };
    
    auto raysIntersectsBounds = [&]( const auto& bounds )
    { 
        tminmax = spatial::boundingBoxIntersectsInvRay( bounds, rayOrigin, invDirection );

        return tminmax != std::nullopt && ( *tminmax )[1] >= 0.0;
    };

    auto traverse = [&]( auto&& self, spatial::BoundingBox<D> bounds, CellIndex index ) -> bool
    {
        if( !tree.isLeaf( index ) )
        {
            auto [axis, position] = tree.split( index );
            auto bounds0 = std::array { bounds[0][axis], position };
            auto bounds1 = std::array { position, bounds[1][axis] };
            
            auto first = LocalPosition { 0 };
            auto second = LocalPosition { 1 };
            auto keepGoing = true;

            if( invDirection[axis] < 0.0 )
            {
                std::swap( bounds0, bounds1 );
                std::swap( first, second );
            }

            bounds[0][axis] = bounds0[0]; 
            bounds[1][axis] = bounds0[1];

            // Further traverse tree
            if( raysIntersectsBounds( bounds ) )
            {
                keepGoing = self( self, bounds, tree.childUnchecked( index, first ) );
            }

            if( keepGoing )
            {
                bounds[0][axis] = bounds1[0]; 
                bounds[1][axis] = bounds1[1];

                if( raysIntersectsBounds( bounds ) )
                {
                    keepGoing = self( self, bounds, tree.childUnchecked( index, second ) );
                }
            }

            return keepGoing;
        }
        else
        {
            return callback( index, *tminmax );
        }
    };

    if( raysIntersectsBounds( treebounds ) )
    {
        traverse( traverse, treebounds, 0 );
    }
}

} // namespace

template<size_t D> 
void KdTree<D>::intersectInv( const std::array<double, D>& rayOrigin,
                              const std::array<double, D>& invDirection,
                              const RayIntersectCallback& callback ) const
{
    internalIntersectRay<D>( *this, rayOrigin, invDirection, callback );
}

template<size_t D>
CellIndex KdTree<D>::fullIndexAt( std::array<double, D> xyz ) const
{
    auto ifull = NoCell;

    if( spatial::insideBoundingBox( bounds_, xyz ) )
    {
        auto traverse = [&]( auto&& self, CellIndex index ) MLHP_PURE -> CellIndex
        {
            if( isLeaf( index ) )
            {
                return index;
            }
            
            auto [axis, position] = split( index );

            return xyz[axis] < position  ? 
                self( self, childUnchecked( index, 0 ) ) : 
                self( self, childUnchecked( index, 1 ) );
        };

        ifull = traverse( traverse, 0 );
    }

    return ifull;
}

template<size_t D>
CellType KdTree<D>::cellType( CellIndex ) const
{
    return CellType::NCube;
}

template<size_t D>
CellIndex KdTree<D>::fullIndex( CellIndex ileaf ) const
{
    //MLHP_EXPECTS_DBG( ileaf < nleaves( ) );

    return fullIndices_[ileaf];
}

template<size_t D>
CellIndex KdTree<D>::leafIndex( CellIndex ifull ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) && isLeaf( ifull ) );

    return nodes_[ifull].leafOrChild;
}

template<size_t D>
spatial::BoundingBox<D> KdTree<D>::boundingBox( CellIndex ileaf ) const
{
    auto traverse = [this]( auto& self, CellIndex index ) MLHP_PURE -> spatial::BoundingBox<D>
    {
        if( index > 0)
        {
            auto bounds = self( self, parents_[index] );
            auto axis = nodes_[parents_[index]].axis;
            auto position = nodes_[parents_[index]].data.position;

            bounds[1 - localPosition( index )][axis] = position;

            return bounds;
        }
        else
        {
            return bounds_;
        }
    };

    return traverse( traverse, fullIndex( ileaf ) );
}

template<size_t D>
void KdTree<D>::neighbours( [[maybe_unused]] CellIndex icell, 
                            [[maybe_unused]] size_t iface, 
                            [[maybe_unused]] std::vector<MeshCellFace>& target ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
MeshMapping<D> KdTree<D>::createMapping( ) const
{
    auto mapping = MeshMapping<D> { };

    mapping.mapping = std::make_shared<CartesianMapping<D>>( );
    mapping.mesh = this;

    return mapping;
}

template<size_t D>
void KdTree<D>::prepareMapping( CellIndex icell, MeshMapping<D>& mapping ) const
{
    auto& cartesianMapping = dynamic_cast<CartesianMapping<D>&>( *mapping.mapping.get( ) );

    cartesianMapping.resetBounds( boundingBox( icell ) );

    mapping.icell = icell;
}

template<size_t D>
BackwardMappingFactory<D> KdTree<D>::createBackwardMappingFactory( ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
std::unique_ptr<AbsMapping<D, D - 1>> KdTree<D>::createInterfaceMapping( ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
void KdTree<D>::prepareInterfaceMappings( [[maybe_unused]] MeshCellFace face0,
                                          [[maybe_unused]] MeshCellFace face1,
                                          [[maybe_unused]] AbsMapping<D, D - 1>& mapping0,
                                          [[maybe_unused]] AbsMapping<D, D - 1>& mapping1 ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
CellIndex KdTree<D>::isLeaf( CellIndex ifull ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) );

    return nodes_[ifull].axis == NoValue<std::uint8_t>;
}

template<size_t D>
CellIndex KdTree<D>::child( CellIndex ifull, LocalPosition position ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) );

    return isLeaf( ifull ) ? NoCell : childUnchecked( ifull, position );
}

template<size_t D>
CellIndex KdTree<D>::childUnchecked( CellIndex ifull, LocalPosition position ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) );

    return nodes_[ifull].leafOrChild + position;
}

template<size_t D>
CellIndex KdTree<D>::parent( CellIndex ifull ) const
{
    return parents_[ifull];
}

template<size_t D>
LocalPosition KdTree<D>::localPosition( CellIndex ifull ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) );

    return ifull != 0 ? static_cast<LocalPosition>( ifull - 
        nodes_[parents_[ifull]].leafOrChild ) : NoLocalPosition;
}

template<size_t D>
std::pair<std::uint8_t, double> KdTree<D>::split( CellIndex ifull ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) && !isLeaf( ifull ) );

    return { nodes_[ifull].axis, nodes_[ifull].data.position };
}

template<size_t D>
std::span<const size_t> KdTree<D>::itemsFull( CellIndex ifull ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) && isLeaf( ifull ) );

    if( auto nitems = nodes_[ifull].nitems; nitems < NoValue<std::uint8_t> )
    {
        return std::span { utilities::begin( data_, nodes_[ifull].data.offset ), nitems };
    }
    else
    {
        auto begin = utilities::begin( data_, nodes_[ifull].data.offset + 1 );

        return std::span { begin, data_[nodes_[ifull].data.offset] };
    }
}

template<size_t D>
void KdTree<D>::stateFull( CellIndex ifull, std::int16_t state )
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) && isLeaf( ifull ) );

    nodes_[ifull].state = state;
}

template<size_t D>
std::int16_t KdTree<D>::stateFull( CellIndex ifull ) const
{
    //MLHP_EXPECTS_DBG( ifull < nfull( ) && isLeaf( ifull ) );

    return nodes_[ifull].state;
}

template<size_t D>
std::span<const size_t> KdTree<D>::itemsLeaf( CellIndex ileaf ) const
{
    //MLHP_EXPECTS_DBG( ileaf < nleaves( ) );

    return itemsFull( fullIndex( ileaf ) );
}

template<size_t D> MLHP_EXPORT
void print( const KdTree<D>& tree, std::ostream& os )
{
    auto nfull = tree.nfull( );
    auto nleaves = tree.nleaves( );
    
    auto averagePerLeaf = size_t { 0 };
    auto maxlevel = size_t { 0 };
    auto volumeEmpty = 0.0;
    
    auto levelData = std::vector<std::tuple<size_t, double>> { };

    auto traverse = [&]( auto& self, CellIndex icell, size_t level ) -> void
    { 
        if( levelData.size( ) <= level ) 
        {
            levelData.push_back( { } );
        }

        if( !tree.isLeaf( icell ) )
        {
            self( self, tree.child( icell, 0 ), level + 1 );
            self( self, tree.child( icell, 1 ), level + 1 );
        }
        else
        {
            auto ileaf = tree.leafIndex( icell );
            auto items = tree.itemsFull( icell );
            auto volume = spatial::boundingBoxVolume( tree.boundingBox( ileaf ) );

            maxlevel = std::max( level, maxlevel );
            averagePerLeaf += items.size( );
            volumeEmpty += items.empty( ) ? volume : 0.0;
            std::get<0>( levelData[level] ) += 1;
            std::get<1>( levelData[level] ) += volume;
        }
    };

    traverse( traverse, 0, 0 );
    
    auto volume = spatial::boundingBoxVolume( tree.boundingBox( ) );
    volumeEmpty /= volume;

    os << "KdTree<" << D << "> (address: " << &tree << ")\n";
    os << "    number of nodes       : " << utilities::thousandSeparator( nfull ) << "\n";
    os << "    number of leaves      : " << utilities::thousandSeparator( nleaves ) << "\n";
    os << "    maximum depth         : " << maxlevel << "\n";
    os << "    items per leaf        : " << std::round( ( 100.0 * averagePerLeaf ) / nleaves ) / 100 << "\n";
    os << "    volume of empty cells : " << std::round( 1000.0 * volumeEmpty ) / 10 << " %\n";
    os << "    heap memory usage     : " << utilities::memoryUsageString( tree.memoryUsage( ) ) << "\n";
    os << "    bounding box          : ";

    auto bounds = tree.boundingBox( );
    for( size_t axis = 0; axis < D; ++axis )
    {
        os << "[" << bounds[0][axis] << ", " << bounds[1][axis] << "]" << ( axis + 1 < D ? " x " : "\n\n" );
    }

    auto chunks = utilities::divideIntoChunks( levelData.size( ), size_t { 5 }, size_t { 2 } );

    os << "    levels  | leaves | volume |\n";
    os << "    --------|--------|--------|\n";
    for( size_t i = 0; i < std::get<0>( chunks ); ++i )
    {
        auto [begin, end] = utilities::chunkRange( i, chunks );

        for( size_t j = begin + 1; j < end; ++j )
        {
            std::get<0>( levelData[begin] ) += std::get<0>( levelData[j] );
            std::get<1>( levelData[begin] ) += std::get<1>( levelData[j] );
        }

        auto percentLeaves = std::round( ( 1000.0 * std::get<0>( levelData[begin] ) ) / nleaves ) / 10;
        auto volumePerLevel = std::round( ( 1000.0 * std::get<1>( levelData[begin] ) ) / volume ) / 10;
        os << "    " << std::left << std::setw( 2 ) << begin << " - " << std::setw( 2 ) << end - 1 << " | " << std::right;
        os << std::setw( 4 ) << percentLeaves << " % | ";
        os << std::setw( 4 ) << volumePerLevel << " % | " << "\n";
    }

    os << std::flush;
}

template<size_t D> MLHP_EXPORT
void printFull( const KdTree<D>& tree, std::ostream& os )
{
    auto indent = size_t { 2 };
    auto alignChar = '|';
    auto offset = std::to_string( tree.nfull( ) ).size( );

    auto traverse = [&]( auto& self, CellIndex index, size_t depth ) -> void
    { 
        os << "cell " << std::setw( offset ) << index << ": ";

        for( size_t i = 0; i < depth; ++i )
        {
            os << alignChar << std::setw( indent ) << "";
        }

        if( !tree.isLeaf( index ) )
        {
            auto [axis, position] = tree.split( index );

            os << "split axis " << static_cast<int>( axis ) << " at " << position << "\n";

            self( self, tree.childUnchecked( index, 0 ), depth + 1 );
            self( self, tree.childUnchecked( index, 1 ), depth + 1 );
        }
        else
        {
            auto items = tree.itemsFull( index );

            os << "leaf with index = " << tree.leafIndex( index ) << ", state = " << 
                static_cast<int>( tree.stateFull( index ) ) << ", items = [";

            for( size_t i = 0; i < items.size( ); ++i )
            {
                os << items[i] << ( ( i + 1 != items.size( ) ) ? ", " : "" );
            }

            os << "]\n";
        }

    };

    traverse( traverse, 0, 0 );

    os << std::flush;
}

namespace kdtree
{

template<size_t D>
void accumulateItems( const KdTree<D>& tree, 
                      const spatial::BoundingBox<D>& bounds,
                      std::vector<size_t>& target )
{
    auto size = target.size( );

    tree.intersect( bounds, [&]( CellIndex ifull )
    {
        auto items = tree.itemsFull( ifull );

        target.insert( target.end( ), items.begin( ), items.end( ) );
    } );

    auto begin = target.begin( ) + utilities::ptrdiff( size );

    std::sort( begin, target.end( ) );
    
    target.erase( std::unique( begin, target.end( ) ), target.end( ) );
}

template<size_t D>
std::vector<size_t> accumulateItems( const KdTree<D>& tree,
                                     const spatial::BoundingBox<D>& bounds )
{
    auto target = std::vector<size_t> { };

    accumulateItems( tree, bounds, target );

    return target;
}

template<size_t D>
RayAccumulationResult accumulateItemsInv( const KdTree<D>& tree,
                                          const std::array<double, D>& rayOrigin,
                                          const std::array<double, D>& invDirection,
                                          std::vector<size_t>& target )
{
    auto size = target.size( );
    auto result = RayAccumulationResult { };

    internalIntersectRay<D>( tree, rayOrigin, invDirection, [&]( CellIndex ifull, auto& tminmax )
    {
        result.cellState = tree.stateFull( ifull );
        result.cellCount += 1;
        result.tminmax = tminmax;

        if( result.cellState == 0 )
        {
            auto items = tree.itemsFull( ifull );

            target.insert( target.end( ), items.begin( ), items.end( ) );

            return true;
        }

        return false;
    } );

    if( target.size( ) != size )
    {
        auto begin = target.begin( ) + utilities::ptrdiff( size );

        std::sort( begin, target.end( ) );
    
        target.erase( std::unique( begin, target.end( ) ), target.end( ) );
    }

    return result;
}

template<size_t D>
ItemStatePair accumulateItemsInv( const KdTree<D>& tree,
                                  const std::array<double, D>& rayOrigin,
                                  const std::array<double, D>& invDirection )
{
    auto target = std::vector<size_t> { };

    auto state = accumulateItemsInv( tree, rayOrigin, invDirection, target ).cellState;

    return std::pair { std::move( target ), state };
}

} // kdtree

#define MLHP_INSTANTIATE_DIM( D )                                                              \
                                                                                               \
    template class KdTree<D>;                                                                  \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,                          \
                           const kdtree::Parameters& parameters );                             \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,                          \
                           const spatial::BoundingBox<D>& bounds,                              \
                           const kdtree::Parameters& parameters );                             \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    void print( const KdTree<D>& tree, std::ostream& os );                                     \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    void printFull( const KdTree<D>& tree, std::ostream& os );                                 \
                                                                                               \
    namespace kdtree                                                                           \
    {                                                                                          \
        template MLHP_EXPORT                                                                   \
        void accumulateItems( const KdTree<D>& tree,                                           \
                              const spatial::BoundingBox<D>& bounds,                           \
                              std::vector<size_t>& target );                                   \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        std::vector<size_t> accumulateItems( const KdTree<D>& tree,                            \
                                             const spatial::BoundingBox<D>& bounds );          \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        RayAccumulationResult accumulateItemsInv( const KdTree<D>& tree,                       \
                                                  const std::array<double, D>& rayOrigin,      \
                                                  const std::array<double, D>& invDirection,   \
                                                  std::vector<size_t>& target );               \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        ItemStatePair accumulateItemsInv( const KdTree<D>& tree,                               \
                                          const std::array<double, D>& rayOrigin,              \
                                          const std::array<double, D>& invDirection );         \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        std::vector<Event> createSortedEventList( const kdtree::ObjectProvider<D>& provider,   \
                                                  const spatial::BoundingBox<D>& bounds );     \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        std::array<double, 3> computeSurfaceAreaRatios( spatial::BoundingBox<D> bounds,        \
                                                        size_t normal, double position );      \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        Plane findPlane( size_t N,                                                             \
                         const spatial::BoundingBox<D>& V,                                     \
                         std::span<const Event> E,                                             \
                         const Parameters& parameters  );                                      \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        std::array<spatial::BoundingBox<D>, 2> splitBoundingBox(                               \
            spatial::BoundingBox<D> bounds, std::uint8_t axis, double position );              \
    }

MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
