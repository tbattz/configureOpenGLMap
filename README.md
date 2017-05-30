# configureOpenGLMap
A python GUI to configure OpenGLMap (see https://github.com/tbattz/openGLMap).

![configureOpenGLMap Window](https://raw.github.com/tbattz/configureOpenGLMap/master/preview.png)

# Configurations
## Display
The display section allows the user to set which screen openGLMap will launch on, the screen size and whether the program launches in full screen mode. Node that if fullscreen is not selected, then openGLMap will default to screen 1.

## Aircraft
The aircraft section determines what models are loaded for each aircraft, and the corresponding IP and port number for the mavlink stream with the information determining the aircrafts position and attitude.
The first column is the aircraft name, while the second opens a file select dialog to select a .obj file for the aircraft model. If a .mtl file with the same name as the .obj file exists in the same directory, then this will be used to load the textures for the model.
The third column is the IP address for the mavlink stream. If the mavlink stream originates from the same computer that the program is running on, say using ArduPilot's SITL (Software in the loop), then you can enter any IP that represets loopback, as long as the port number matches that of the output mavlink stream. If the mavlink stream originates from another network location, then the IP will need to be that of the other network location.
The "plus" and "minus" buttons allow multiple aircraft to be added.

## Origin
The origin of the world is set here, in terms of the lattitude (degrees), longitude (degrees), altitude (m).

## Volume
Define volumes in 3D space to draw. These can be used to define no-fly areas, buildings or obstacles. Each volume has an associated RGB (0-255) colour, an alpha transparency (0 is fully transparent). The points can be moved by left clicking and dragging them. New points can be added by toggling the radio button to the desired polygon, and left clicking in the desired location on the map. To remove a point, right click on it. A volume must have at least 3 points. Finer control of the location of the points is given with the Edit Points button, which opens another dialog to manually adjust the lattitude and longitude of each of the points, as well as setting the bottom (low altitude) and top (high altitude) of the polygon at each of the points.

The map can moved around with the arrow keys, and zoomed in and out with the +,- keys and scroll wheel. Moving the map around will start downloading some of the map tiles. The downloading of tiles is more efficient in the main program, than it is in the configuration tool, so it is suggested you use that to download most of your maps.

## Generate
Once each of the options have been filled in correctly, a configuration file can be generated using the "Generate Configuration" button. If the options are in correct, you will get a warning popup. If they are required options, then no config file will be generated, while if they are optional, a config file will be generated with these incorrect selections missing.

The generated file is currentConfig.txt located in ../../Configs (in the Configs folder of openGLMap).
