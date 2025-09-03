cmake_minimum_required(VERSION 3.15)

project(test_project VERSION 0.1 LANGUAGES CXX)

include(CTest)

add_executable(test_project_cmd main.cpp)
install(TARGETS test_project_cmd)

if(BUILD_TESTING)
    add_test(NAME my_test COMMAND test_project_cmd)
endif()
