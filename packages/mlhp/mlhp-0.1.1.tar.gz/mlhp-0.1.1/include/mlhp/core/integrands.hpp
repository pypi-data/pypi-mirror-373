// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_INTEGRANDS_HPP
#define MLHP_CORE_INTEGRANDS_HPP

#include "mlhp/core/integrandtypes.hpp"
#include "mlhp/core/spatial.hpp"

#include <span>

namespace mlhp
{

// Standard linear system domain integrands

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& mass,
                                          const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( std::optional<spatial::ScalarFunction<D>> mass,
                                          std::optional<spatial::ScalarFunction<D>> rhs,
                                          memory::vptr<const std::vector<double>> dofs,
                                          size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::VectorFunction<D>& rhs );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( std::optional<spatial::VectorFunction<D>> mass,
                                          std::optional<spatial::VectorFunction<D>> rhs,
                                          memory::vptr<const std::vector<double>> dofs = nullptr );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makePoissonIntegrand( const spatial::ScalarFunction<D>& conductivity,
                                         const spatial::ScalarFunction<D>& source );

template<size_t D>  MLHP_EXPORT
DomainIntegrand<D> makeAdvectionDiffusionIntegrand( const spatial::VectorFunction<D, D>& velocity,
                                                    const spatial::ScalarFunction<D>& diffusivity,
                                                    const spatial::ScalarFunction<D>& source );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeFunctionIntegrand( const spatial::ScalarFunction<D>& function );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeFunctionIntegrand( const spatial::VectorFunction<D>& function );

//! Defines strain and strain operator (B-matrix)
template<size_t D>
struct KinematicEquation final
{
    using AnyCache = utilities::Cache<KinematicEquation<D>>;
    using Create = AnyCache( const AbsBasis<D>& basis );

    using Prepare = void( AnyCache& anyCache,
                          const MeshMapping<D>& mapping,
                          const LocationMap& locationMap );

    using Evaluate = void( AnyCache& anyCache,
                           const BasisFunctionEvaluation<D>& shapes,
                           std::span<const double> solutionGradient,
                           std::span<double> strain,
                           std::span<double> strainOperator );

    std::function<Create> create = utilities::returnEmpty<AnyCache>( );
    std::function<Prepare> prepare = utilities::doNothing( );
    std::function<Evaluate> evaluate;

    size_t nfields = 0;       // Number of solution field components
    size_t ncomponents = 0;   // Number of strain components
    bool largestrain = false; // Tells integrand to assemble geometric tangent: grad(N) * sigma * grad(N)
    std::string name = "";    // to find out what kind of kinematics this is
};

// Defines stress and material tangent matrix (C-matrix)
template<size_t D>
struct ConstitutiveEquation final
{
    using AnyCache = utilities::Cache<ConstitutiveEquation<D>>;
    using Create = AnyCache( const AbsBasis<D>& basis,
                             const KinematicEquation<D>& kinematics );

    using Prepare = void( AnyCache& anyCache,
                          const MeshMapping<D>& mapping,
                          const LocationMap& locationMap );

    using Evaluate = void( AnyCache& anyCache,
                           const BasisFunctionEvaluation<D>& shapes,
                           std::span<const double> strain,
                           std::span<double> stress,
                           std::span<double> tangent );

    std::function<Create> create = utilities::returnEmpty<AnyCache>( );
    std::function<Prepare> prepare = utilities::doNothing( );
    std::function<Evaluate> evaluate;

    size_t ncomponents = 0;   // number of stress components (size of material matrix)
    bool symmetric = false;   // symmetry of material matrix
    bool incremental = false; // total strain or strain increment formulation
    std::string name = "";    // to find out what kind of material this is
};

template<size_t D> MLHP_EXPORT
KinematicEquation<D> makeSmallStrainKinematics( );

MLHP_EXPORT
ConstitutiveEquation<3> makeIsotropicElasticMaterial( const spatial::ScalarFunction<3>& youngsModulus,
                                                      const spatial::ScalarFunction<3>& poissonRatio );

MLHP_EXPORT
ConstitutiveEquation<2> makePlaneStrainMaterial( const spatial::ScalarFunction<2>& youngsModulus,
                                                 const spatial::ScalarFunction<2>& poissonRatio );

MLHP_EXPORT
ConstitutiveEquation<2> makePlaneStressMaterial( const spatial::ScalarFunction<2>& youngsModulus,
                                                 const spatial::ScalarFunction<2>& poissonRatio );

//! Computes B^T * C * B and N^T * force, where B is the strain operator and C is the material matrix. 
//! This version passes an empty deformation gradient to kinematics and an empty strain to constitutive.
template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                              const spatial::VectorFunction<D, D>& force );

//! Computes J = B^T * C * B and R = N^T * force - B^T * C * u, where B is the strain operator and C
//! is the tangent material matrix. The dofs are used to evaluate the deformation gradient, so if the
//! formulation uses strain increments, then dofs must be the dof increment.
template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                              memory::vptr<const std::vector<double>> dofs,
                                              const spatial::VectorFunction<D, D>& force,
                                              bool integrateTangent = true );

// https://en.wikipedia.org/wiki/Elastic_modulus
struct ElasticConverter
{
    double lambda_, mu_;

    ElasticConverter( double E, double nu )
    {
        auto tmp1 = ( 1.0 - 2.0 * nu );
        auto tmp2 = E / ( ( 1.0 + nu ) * tmp1 );

        lambda_ = nu * tmp2;
        mu_ = 0.5 * tmp1 * tmp2;
    }

    auto lambda( ) const { return lambda_; } 
    auto mu( ) const { return mu_; }         
    auto lameParameters( ) const { return std::array { lambda( ), mu( ) }; }

    auto shearModulus( ) const { return mu_; }
    auto bulkModulus( ) const { return lambda_ + 2.0 / 3.0 * mu_; }
    auto bulkAndShearModuli( ) const { return std::array { bulkModulus( ), shearModulus( ) }; }
};

// Defines Voigt notation (consistent with Paraview)
// 
// In 2D:
// S00  S01
//      S11       ->  [S00, S11, S01]
// 
// In 3D: 
// S00  S01  S02
//      S11  S12  ->  [S00, S11, S22, S01, S12, S02]
//           S22
//
template<size_t D>
struct VoigtIndices
{
    //! Go from (i, j) to Voigt index
    //! 1D: [[0]]
    //! 2D: [[0, 2], 
    //!      [2, 1]]
    //! 3D: [[0, 3, 5], 
    //!      [3, 1, 4], 
    //!      [5, 4, 2]]
    static constexpr auto vector = []( )
    {
        auto ij = std::array<std::array<size_t, D>, D> { };
        auto index = size_t { 0 };

        for( size_t k = 0; k < D; ++k )
        {
            for( size_t l = 0; l < D - k; ++l )
            {
                ij[l][l + k] = index++;
                ij[l + k][l] = ij[l][l + k];
            }
        }

        return ij; 
    }( );

    //! Go from Voigt index to upper matrix index (i, j)
    //! 1D: [(0, 0)]
    //! 2D: [(0, 0), (1, 1), (0, 1)]
    //! 3D: [(0, 0), (1, 1), (2, 2), (0, 1), (1, 2), (0, 2)]
    static constexpr auto matrix = []( )
    {
        auto indices = std::array<std::array<size_t, 2>, ( D * ( D + 1 ) ) / 2> { };
        auto index = size_t { 0 };

        for( size_t k = 0; k < D; ++k )
        {
            for( size_t l = 0; l < D - k; ++l )
            {
                indices[index++] = { l, l + k };
            }
        }

        return indices; 
    }( );

    static constexpr auto size = matrix.size( );
};

//! Expand tensor in reduced, i.e. Voigt notation, (with 6 components in 3D) to the
//! full tensor (9 components in 3D). If reduced is already the full tensor, then 
//! simply copy the values from reduced to full.
template<size_t D> MLHP_EXPORT
void expandVoigtNotation( std::span<const double> reduced,
                          std::span<double> fullTensor );

//! Check for possible ways kinematics and constitutive could be incompatible (e.g. number of stress/strain components)
template<size_t D> MLHP_EXPORT
void checkConsistency( const memory::vptr<const KinematicEquation<D>>& kinematics,
                       const memory::vptr<const ConstitutiveEquation<D>>& constitutive );

//! Check for possible ways kinematics could be incompatible with basis (e.g. number of solution field components)
template<size_t D> MLHP_EXPORT
void checkConsistency( const AbsBasis<D>& basis,
                       const memory::vptr<const KinematicEquation<D>>& kinematics );

// Standard scalar domain integrands

struct ErrorIntegrals
{
    double analyticalSquared = 0, numericalSquared = 0, differenceSquared = 0;

    double numerical( ) { return std::sqrt( numericalSquared ); }
    double analytical( ) { return std::sqrt( analyticalSquared ); }
    double difference( ) { return std::sqrt( differenceSquared ); }
    double relativeDifference( ) { return std::sqrt( differenceSquared / analyticalSquared ); }

    operator AssemblyTargetVector( ) { return { analyticalSquared, numericalSquared, differenceSquared }; }
};

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2ErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                         const spatial::ScalarFunction<D>& solutionFunction );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeEnergyErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                             const spatial::VectorFunction<D, D>& analyticalDerivatives );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeInternalEnergyIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                                memory::vptr<const KinematicEquation<D>> kinematics,
                                                memory::vptr<const ConstitutiveEquation<D>> constitutive );

// Basis projection linear system domain integrands

template<size_t D> MLHP_EXPORT
BasisProjectionIntegrand<D> makeL2BasisProjectionIntegrand( memory::vptr<const std::vector<double>> oldDofs );

template<size_t D> MLHP_EXPORT
BasisProjectionIntegrand<D> makeTransientPoissonIntegrand( const spatial::ScalarFunction<D + 1>& capacity,
                                                           const spatial::ScalarFunction<D + 1>& diffusivity,
                                                           const spatial::ScalarFunction<D + 1>& source,
                                                           memory::vptr<const std::vector<double>> dofs0,
                                                           std::array<double, 2> timeStep,
                                                           double theta );

// Surface integrands

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::ScalarFunction<D>& rhs, size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::VectorFunction<D>& rhs );

// Integrate the for given field index
// 1) M_ij = N_i(x) * mass(x) * N_j(x)
// 2) F_i  = N_i(x) * rhs(x)
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,
                                             const spatial::ScalarFunction<D>& rhs,
                                             size_t ifield = 0 );

// Integrate the for all solution fields (for each field component separately, so no interaction)
// 1) M_ij = N_i(x) * mass(x) * N_j(x)
// 2) F_i  = N_i(x) * rhs(x)
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,
                                             const spatial::VectorFunction<D>& rhs );

// Integrate the for given field index 
// 1) M_ij = N_i(x) * mass(x) * N_j(x) if computeTangent is true
// 2) F_i  = N_i(x) * ( rhs(x) - mass(x) * N_j(x) * dofs_j )
// If !computeTangent, 2) will be assembled into target index 0
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,
                                             const spatial::ScalarFunction<D>& rhs,
                                             memory::vptr<const std::vector<double>> dofs,
                                             size_t ifield = 0,
                                             bool computeTangent = true );

// Integrate the for all solution fields (for each field component separately, so no interaction)
// 1) M_ij = N_i(x) * mass(x) * N_j(x) if computeTangent is true
// 2) F_i  = N_i(x) * ( rhs(x) - mass(x) * N_j(x) * dofs_j )
// If !computeTangent, 2) will be assembled into target index 0
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,
                                             const spatial::VectorFunction<D>& rhs,
                                             memory::vptr<const std::vector<double>>,
                                             bool computeTangent = true );


template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNormalNeumannIntegrand( const spatial::ScalarFunction<D>& pressure );

//! Constrain m * <u, n> = r; for example in 3D: m * <(u0, u1, u2), n> = r
// The weak residual is <w, n> * (<u, n> - r); for example in 3D:
//     int m * N0_i * n0 * (u0 * n0 + u1 * n1 + u2 * n2 - r) dx
//     int m * N1_i * n1 * (u0 * n0 + u1 * n1 + u2 * n2 - r) dx
//     int m * N2_i * n2 * (u0 * n0 + u1 * n1 + u2 * n2 - r) dx
// Or even simpler: m * (D^T * D - D^T * r), with D = [u0 * n0 + u1 * n1 + u2 * n2]
// Assembles matrix if mass != std::nullopt into first slot
// Assembles vector if rhs != std::nullopt into second slot (or first if no matrix)
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& mass,
                                           const std::optional<spatial::ScalarFunction<D>>& rhs );

//! Nonlinear (tangent/residual) version of the integrand above
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& mass,
                                           const std::optional<spatial::ScalarFunction<D>>& rhs,
                                           memory::vptr<const std::vector<double>> dofs );

//! Nitsche boundary integral
// Weak residual: beta * <w, u - f> - <w, <n, sigma(u)>> - <<sigma(w), n>, u - f>
// Element system: beta * N^T * N - N^T * (n^T * C * B) - (B^T * C^T * n) * N = beta * N^T * f - (B^T * C^T * n) * f
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                          memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                          const spatial::VectorFunction<D>& function,
                                          double beta );

//! Nonlinear (tangent/residual) version of the integrand above
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                          memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                          memory::vptr<const std::vector<double>> dofs,
                                          const spatial::VectorFunction<D>& function,
                                          double beta );

// Integrate stress times surface normal direction
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeReactionForceIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                                memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                                memory::vptr<const std::vector<double>> dofs );

// integrate f dGamma
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeFunctionSurfaceIntegrand( const spatial::ScalarFunction<D>& function );

// integrate f dGamma
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeFunctionSurfaceIntegrand( const spatial::VectorFunction<D>& function );

// integrate dot(f, n) dGamma
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNormalDotProductIntegrand( const spatial::VectorFunction<D>& function );

} // mlhp

#endif // MLHP_CORE_INTEGRANDS_HPP
