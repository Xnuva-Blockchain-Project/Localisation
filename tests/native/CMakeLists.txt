cmake_minimum_required(VERSION 3.22)

project(LocalisationQualification LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core)

add_executable(
    localisation-qualification main.cpp
)

target_link_libraries(
    localisation-qualification PRIVATE Qt6::Core
)
