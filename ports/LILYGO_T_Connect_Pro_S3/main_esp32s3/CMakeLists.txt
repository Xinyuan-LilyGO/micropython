# Set location of base MicroPython directory.
if(NOT MICROPY_DIR)
    get_filename_component(MICROPY_DIR ${CMAKE_CURRENT_LIST_DIR}/../../.. ABSOLUTE)
endif()

# Set location of the ESP32 port directory.
if(NOT MICROPY_PORT_DIR)
    get_filename_component(MICROPY_PORT_DIR ${MICROPY_DIR}/ports/LILYGO_T_Connect_Pro_S3 ABSOLUTE)
endif()

set(MICROPY_PY_TINYUSB ON)

include(${MICROPY_PORT_DIR}/esp32_common.cmake)
