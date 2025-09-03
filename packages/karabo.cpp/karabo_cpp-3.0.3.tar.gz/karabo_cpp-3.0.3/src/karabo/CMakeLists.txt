# This file is part of Karabo.
#
# http://www.karabo.eu
#
# Copyright (C) European XFEL GmbH Schenefeld. All rights reserved.
#
# Karabo is free software: you can redistribute it and/or modify it under
# the terms of the MPL-2 Mozilla Public License.
#
# You should have received a copy of the MPL-2 Public License along with
# Karabo. If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.
#
# Karabo is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# The project that builds the Karabo Framework Library (libkarabo.so)
#
# Variables that influence the configuration/generation behavior of this project:
#
# KARABO_LIB_TARGET_NAME: this is the name of the target that is the Karabo
#                         Framework C++ shared library. If set by a parent
#                         project, that value is kept.
#
# CMAKE_PREFIX_PATH: this variable is expected to have the root directory of
#                    the external build (and run) time dependencies of the
#                    karabo shared library (the main target of this project).
#                    A warning is emited at configuration time if the variable
#                    does not pass a minimal sanity test of being defined and
#                    point to an existing directory.

cmake_minimum_required(VERSION 3.15)

project(karabo-core)

# Returns a list with all the paths in the input list modified so
# the current value of CMAKE_PREFIX_PATH in the input path is replaced
# with the string "${CMAKE_PREFIX_PATH}".
function(make_relative_to_cmake_prefix_path INPUT_LIST OUTPUT_LIST)
    set(${AUX_LIST} "")
    foreach (INPUT_PATH ${INPUT_LIST})
        string(REPLACE
            ${CMAKE_PREFIX_PATH}
            "\${CMAKE_PREFIX_PATH}"
            OUTPUT_PATH
            ${INPUT_PATH}
        )
        list(APPEND AUX_LIST ${OUTPUT_PATH})
    endforeach()
    set(${OUTPUT_LIST} "${AUX_LIST}" PARENT_SCOPE)
endfunction()


include("../cmake/cxx-options.cmake")
include("../cmake/karabo-lib-target-name.cmake")

# Checks that the target system is UNIX - true for Linux, macOS and Cygwin
# This is needed because some parts of the Framework - e.g. src/karabo/net/TcpChannel.cc -
# are not compatible with non UNIX systems.
if(NOT UNIX)
    message(
        FATAL_ERROR
        "The Karabo Framework requires a UNIX compatible target system"
    )
endif()

# Extracts KARABO_VERSION from the appropriate Git tag, writes to
# a file to be used by the Karabo Framework at build time.
message(STATUS "Resolving Karabo Version from Git repository")
set(KARABO_VERSION "3.0.3")
set(KARABO_VERSION_MAJOR "3")
set(KARABO_VERSION_MINOR "0")
set(KARABO_VERSION_PATCH "3")
message(STATUS "Karabo Version: ${KARABO_VERSION}")
message(STATUS "Karabo Version Major: ${KARABO_VERSION_MAJOR}")
message(STATUS "Karabo Version Minor: ${KARABO_VERSION_MINOR}")
message(STATUS "Karabo Version Patch: ${KARABO_VERSION_PATCH}")
# Create header with version macros from its template.
# Yes, we place the generated header into the source code directory...
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/util/VersionMacros.in
               ${CMAKE_CURRENT_SOURCE_DIR}/util/VersionMacros.hh
               @ONLY
)

project(
    "KaraboLib"
    VERSION ${KARABO_VERSION_MAJOR}.${KARABO_VERSION_MINOR}.${KARABO_VERSION_PATCH}
    LANGUAGES C CXX
)

configure_file(
    "${CMAKE_CURRENT_LIST_DIR}/cmake/karaboPackageDependencies-GNU-Linux-x86.pc.in"
    "${CMAKE_BINARY_DIR}/karaboDependencies.pc"
    @ONLY
)

# Define the libkarabo target
set(EXCLUDE_DIR "/tests/")

# collect the source files excluding the ones in the `tests` folder
file(GLOB_RECURSE SOURCE_FILES CONFIGURE_DEPENDS "*.cc")
foreach (TMP_PATH ${SOURCE_FILES})
    string (FIND ${TMP_PATH} ${EXCLUDE_DIR} EXCLUDE_DIR_FOUND)
    if (NOT ${EXCLUDE_DIR_FOUND} EQUAL -1)
        list (REMOVE_ITEM SOURCE_FILES ${TMP_PATH})
    endif ()
endforeach()

# collect the header files excluding the ones in the `tests` folder
file(GLOB_RECURSE HDR_FILES CONFIGURE_DEPENDS "*.hh")
foreach (TMP_PATH ${HDR_FILES})
    string (FIND ${TMP_PATH} ${EXCLUDE_DIR} EXCLUDE_DIR_FOUND)
    if (NOT ${EXCLUDE_DIR_FOUND} EQUAL -1)
        list (REMOVE_ITEM HDR_FILES ${TMP_PATH})
    endif ()
endforeach()

add_library(
        ${KARABO_LIB_TARGET_NAME} SHARED
        ${SOURCE_FILES}
)

# finding dependencies
find_package(Boost REQUIRED)
find_package(amqpcpp REQUIRED)
find_package(spdlog REQUIRED)
find_package(fmt REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(pugixml REQUIRED)
find_package(date REQUIRED)

set_target_properties(
        ${KARABO_LIB_TARGET_NAME} PROPERTIES
        VERSION ${KARABO_VERSION_MAJOR}.${KARABO_VERSION_MINOR}.${KARABO_VERSION_PATCH}
        SOVERSION ${KARABO_VERSION_MAJOR}
        INSTALL_RPATH "$ORIGIN/../extern/lib"
)

target_link_options(
    ${KARABO_LIB_TARGET_NAME}
    PUBLIC
    "LINKER:--disable-new-dtags,-z,origin"
)

target_compile_definitions(
    ${KARABO_LIB_TARGET_NAME}
    PUBLIC __SO__
)

target_compile_options(
    ${KARABO_LIB_TARGET_NAME}
    PUBLIC -Wno-unused-local-typedefs -Wno-deprecated-declarations -Wall)

target_include_directories(
    ${KARABO_LIB_TARGET_NAME}
    PUBLIC $<BUILD_INTERFACE:${${PROJECT_NAME}_SOURCE_DIR}/..> $<INSTALL_INTERFACE:include/karabo>
)

target_include_directories(
    ${KARABO_LIB_TARGET_NAME}
    PUBLIC $<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>  $<INSTALL_INTERFACE:include>
)

# Adding dependecies to KARABO_LIB_TARGET_NAME
# These are linked against and provided to the public link interface
target_link_libraries(
    ${KARABO_LIB_TARGET_NAME}
    PUBLIC
    amqpcpp  # not a typo, this package does not define a namespace
    Boost::headers
    spdlog::spdlog
    fmt::fmt
    nlohmann_json::nlohmann_json
    pugixml::pugixml
    date::date
    curl
    openssl::openssl
)

# Adding interface libraries to KARABO_LIB_TARGET_NAME
# These are *NOT* linked against, only provided as part of the link interface
target_link_libraries(
    ${KARABO_LIB_TARGET_NAME}
    INTERFACE
    Boost::atomic
    Boost::chrono
    Boost::date_time
    Boost::filesystem
    Boost::regex
    Boost::system
    Boost::thread
)

# Headers to be installed
file(GLOB INCLUDE_FILES CONFIGURE_DEPENDS "*.hpp" "*/*.hpp")

# append all header files.
foreach (TMP_PATH ${HDR_FILES})
   list (APPEND INCLUDE_FILES ${TMP_PATH})
endforeach()

# Creating karabo folder in include and lib folders
install(DIRECTORY DESTINATION "lib")
install(DIRECTORY DESTINATION "include/karabo")

# Adding headers with the same tree directory of the project.
set(SRC_INCLUDE_PATH_PREFIX "/src/karabo/")
string(LENGTH ${SRC_INCLUDE_PATH_PREFIX} SRC_INCLUDE_PATH_PREFIX_LEN)
foreach (FILE_PATH ${INCLUDE_FILES})
    get_filename_component(DIR_PART ${FILE_PATH} DIRECTORY)
    get_filename_component(NAME_PART ${FILE_PATH} NAME)
    # the directory for the installed header should keep the relative path of the source tree
    # e.g ".../src/karabo/core/Device.hh" should go to "include/karabo/core/Device.hh".
    string(FIND ${DIR_PART} ${SRC_INCLUDE_PATH_PREFIX} COMMON_BASE_DIR_POS)
    if (${COMMON_BASE_DIR_POS} EQUAL -1)
        # No intermediary "karabo" directory in the path; no subdir to be added to install path.
        install(FILES ${FILE_PATH} DESTINATION "include/karabo")
    else ()
        math(EXPR INCLUDE_SUBDIR_POS "${COMMON_BASE_DIR_POS} + ${SRC_INCLUDE_PATH_PREFIX_LEN}")
        string(LENGTH ${DIR_PART} DIR_PART_LENGTH)
        string(SUBSTRING ${DIR_PART} ${INCLUDE_SUBDIR_POS} ${DIR_PART_LENGTH} INCLUDE_SUBDIR)
        install(FILES ${FILE_PATH} DESTINATION "include/karabo/${INCLUDE_SUBDIR}")
    endif()
endforeach()

install(TARGETS ${KARABO_LIB_TARGET_NAME}
        LIBRARY DESTINATION "lib"
        PUBLIC_HEADER DESTINATION "include/karabo"
        RUNTIME DESTINATION bin
)

install(FILES "../cmake/import_karabo_lib.cmake"
        DESTINATION "lib/cmake")


# Custom install for karaboDependencies.pc file.
install(FILES "${CMAKE_BINARY_DIR}/karaboDependencies.pc"
        DESTINATION "lib/pkgconfig")
# install here for backwards compatibility.
install(FILES "${CMAKE_BINARY_DIR}/karaboDependencies.pc"
        DESTINATION "lib")

file(WRITE "${CMAKE_BINARY_DIR}/VERSION" ${KARABO_VERSION})
install(FILES "${CMAKE_BINARY_DIR}/VERSION" DESTINATION .)

if((CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME) AND BUILD_UNIT_TESTING)
    # Code path hit when compiling this subproject independently.
    # Makes sure ctest is callable from CMAKE_BINARY_DIRECTORY in this case
    enable_testing()
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/tests ${CMAKE_BINARY_DIR}/karabo/tests)
endif()
