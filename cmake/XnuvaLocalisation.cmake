# Shared experimental localisation build interface.
# XNUVA Blockchain Project.

include_guard(GLOBAL)

function(xnuva_add_localisation target)

    cmake_parse_arguments(
        LOC
        ""
        "IDENTITY;SOURCE_INVENTORY;TEMPLATES"
        ""
        ${ARGN}
    )

    if(NOT TARGET ${target})
        message(FATAL_ERROR
            "Localisation target does not exist: ${target}")
    endif()

    if(LOC_UNPARSED_ARGUMENTS OR LOC_KEYWORDS_MISSING_VALUES)
        message(FATAL_ERROR "Invalid localisation arguments")
    endif()

    if(NOT LOC_IDENTITY OR NOT LOC_SOURCE_INVENTORY)
        message(FATAL_ERROR
            "IDENTITY and SOURCE_INVENTORY are required")
    endif()

    get_filename_component(
        module
        "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.."
        ABSOLUTE
    )

    if(NOT LOC_TEMPLATES)
        set(LOC_TEMPLATES
            "${module}/migration/common-templates-v2.json")
    endif()

    foreach(input IDENTITY SOURCE_INVENTORY TEMPLATES)

        get_filename_component(
            LOC_${input}
            "${LOC_${input}}"
            ABSOLUTE
            BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}"
        )

        if(NOT EXISTS "${LOC_${input}}")
            message(FATAL_ERROR
                "Missing localisation input: ${LOC_${input}}")
        endif()

    endforeach()

    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    find_package(Qt6 REQUIRED COMPONENTS Core LinguistTools)

    if(NOT TARGET Qt6::rcc OR NOT TARGET Qt6::lrelease)
        message(FATAL_ERROR
            "Required Qt translation tools unavailable")
    endif()

    file(GLOB tools CONFIGURE_DEPENDS
        "${module}/tools/*.py"
    )

    file(GLOB inherited CONFIGURE_DEPENDS
        "${module}/common/inherited/qt/*.ts"
    )

    set(output
        "${CMAKE_CURRENT_BINARY_DIR}/localisation/${target}/translations.cpp"
    )

    add_custom_command(
        OUTPUT "${output}"

        COMMAND "${Python3_EXECUTABLE}"
            "${module}/tools/build_qt_resource.py"
            --identity "${LOC_IDENTITY}"
            --source-inventory "${LOC_SOURCE_INVENTORY}"
            --templates "${LOC_TEMPLATES}"
            --lrelease "$<TARGET_FILE:Qt6::lrelease>"
            --rcc "$<TARGET_FILE:Qt6::rcc>"
            --output "${output}"

        DEPENDS
            ${tools}
            ${inherited}
            "${LOC_IDENTITY}"
            "${LOC_SOURCE_INVENTORY}"
            "${LOC_TEMPLATES}"
            "${module}/common/inherited/SHA256SUMS"
            "${CMAKE_CURRENT_FUNCTION_LIST_FILE}"
            Qt6::rcc
            Qt6::lrelease

        COMMENT "Generating shared XNUVA localisation resources"

        VERBATIM
    )

    set_source_files_properties(
        "${output}"
        PROPERTIES GENERATED TRUE
    )

    target_sources(${target} PRIVATE "${output}")

endfunction()
