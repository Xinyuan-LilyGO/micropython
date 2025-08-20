/*
 * Copyright [2021] Mauro Riva <info@lemariva.com>
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MICROPY_INCLUDED_ESP32_MODCAMERA_H
#define MICROPY_INCLUDED_ESP32_MODCAMERA_H

enum { OV2640, OV7725};

#define TAG "camera"

//WROVER-KIT PIN Map
#define CAM_PIN_PWDN     -1  // power down is not used
#define CAM_PIN_RESET    -1  // software reset will be performed
#define CAM_PIN_XCLK     21  // Changed from 0 to 21
#define CAM_PIN_SIOD     1   // SDA, using free GPIO
#define CAM_PIN_SIOC     41   // SCL, using free GPIO

// Note: D0 to D7 should not conflict with other uses. 
// Adjust if needed to respect the other GPIO mappings 
#define CAM_PIN_D7      40  // Assuming Y7
#define CAM_PIN_D6      39  // Assuming Y8
#define CAM_PIN_D5      38  // Assuming Y6
#define CAM_PIN_D4      36  // Assuming PCLK
#define CAM_PIN_D3      16  // Assuming Y5
#define CAM_PIN_D2      47  // Assuming Y4
#define CAM_PIN_D1      15  // Assuming D1
#define CAM_PIN_D0      35  // Assuming D0, free GPIO

#define CAM_PIN_VSYNC   9  // Free GPIO, assuming no conflict
#define CAM_PIN_HREF    14  // Free GPIO, assuming no conflict
#define CAM_PIN_PCLK    37  // Free GPIO, assuming no conflict
#define XCLK_FREQ_10MHz    10000000
#define XCLK_FREQ_20MHz    20000000

//White Balance
#define WB_NONE     0
#define WB_SUNNY    1
#define WB_CLOUDY   2
#define WB_OFFICE   3
#define WB_HOME     4

//Special Effect  
#define EFFECT_NONE    0
#define EFFECT_NEG     1
#define EFFECT_BW      2
#define EFFECT_RED     3
#define EFFECT_GREEN   4
#define EFFECT_BLUE    5
#define EFFECT_RETRO   6                       


#endif
