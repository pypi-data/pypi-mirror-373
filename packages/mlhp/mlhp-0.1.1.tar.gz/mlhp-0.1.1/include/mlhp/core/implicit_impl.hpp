// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_IMPLICIT_IMPL_HPP
#define MLHP_CORE_IMPLICIT_IMPL_HPP

namespace mlhp::implicit
{

template<size_t D, typename... ImplicitFunctions > inline
ImplicitFunction<D> add( const ImplicitFunction<D>& function1,
                         const ImplicitFunctions&... functions )
{
    return [=]( std::array<double, D> xyz ) -> bool
    {
        return function1( xyz ) || ( functions( xyz ) || ... || false );
    };
}

template<size_t D, typename... ImplicitFunctions > inline
ImplicitFunction<D> intersect( const ImplicitFunction<D>& function1,
                               const ImplicitFunctions&... functions )
{
    return [=]( std::array<double, D> xyz ) -> bool
    {
        return function1( xyz ) && ( functions( xyz ) && ... && true );
    };
}

template<size_t D, typename... ImplicitFunctions > inline
ImplicitFunction<D> subtract( const ImplicitFunction<D>& function1,
                              const ImplicitFunctions&... functions )
{
    return [=]( std::array<double, D> xyz ) -> bool
    {
        return function1( xyz ) && !( functions( xyz ) || ... || false );
    };
}

} // namespace mlhp::implicit

#endif // MLHP_CORE_IMPLICIT_IMPL_HPP
