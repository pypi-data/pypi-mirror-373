// This file is part of the mlhp project. License: See LICENSE

#include "pybind11/pybind11.h"

namespace mlhp::bindings
{

void bindSpatial( pybind11::module& m );
void bindDiscretization( pybind11::module& m );
void bindAssembly( pybind11::module& m ); 

PYBIND11_MODULE( pymlhpcore, m ) 
{
    m.doc( ) = "Multi-level hp discretization kernel.";

    bindSpatial( m );
    bindDiscretization( m );
    bindAssembly( m );
}

} // mlhp::bindings

