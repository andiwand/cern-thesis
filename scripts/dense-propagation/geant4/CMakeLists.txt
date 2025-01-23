cmake_minimum_required(VERSION 3.16...3.21)
project(dense_g4 VERSION 0.0.1 LANGUAGES C CXX)

option(WITH_GEANT4_UIVIS "Build example with Geant4 UI and Vis drivers" ON)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED ui_all vis_all)
else()
  find_package(Geant4 REQUIRED)
endif()

include(${Geant4_USE_FILE})
include_directories(${PROJECT_SOURCE_DIR}/src)

file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cpp)
file(GLOB headers ${PROJECT_SOURCE_DIR}/src/*.hpp)

add_executable(run_chart_eloss run_chart_eloss.cpp ${sources} ${headers})
target_link_libraries(run_chart_eloss ${Geant4_LIBRARIES})

add_executable(run_chart_msc_eloss run_chart_msc_eloss.cpp ${sources} ${headers})
target_link_libraries(run_chart_msc_eloss ${Geant4_LIBRARIES})

add_executable(run_print_material run_print_material.cpp ${sources} ${headers})
target_link_libraries(run_print_material ${Geant4_LIBRARIES})

add_executable(run_print_physics_list run_print_physics_list.cpp ${sources} ${headers})
target_link_libraries(run_print_physics_list ${Geant4_LIBRARIES})

add_executable(run_visualisation run_visualisation.cpp ${sources} ${headers})
target_link_libraries(run_visualisation ${Geant4_LIBRARIES})
