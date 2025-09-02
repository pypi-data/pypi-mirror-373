function( CreateExampleCppDriver name description )

    string( TOUPPER ${name} nameUpperCase )
    
    set( exampleOption MLHP_EXAMPLE_CPP_${nameUpperCase} )
    
    if( ${MLHP_EXAMPLES} )
    
        option( ${exampleOption} ${description} OFF )
        
        if( "${${exampleOption}}" )
        
            add_executable( ${name} examples/${name}.cpp  )
            
            target_link_libraries( ${name} PRIVATE mlhpcore )
                        
            set_target_properties( ${name} PROPERTIES ${MLHP_OUTPUT_DIRS} )
            
        endif( "${${exampleOption}}" )
           
    else( ${MLHP_EXAMPLES} )
  
        unset( ${exampleOption} CACHE )
        
    endif( ${MLHP_EXAMPLES} )
    
endfunction()

function( CreateExamplePythonDriver name description )

    if( ${MLHP_EXAMPLES} AND ${MLHP_PYTHON} )
    
        configure_file( examples/${name}.py ${MLHP_BUILD_BINARY_DIR}/${name}.py COPYONLY )
    
    endif( ${MLHP_EXAMPLES} AND ${MLHP_PYTHON} )

endfunction()
