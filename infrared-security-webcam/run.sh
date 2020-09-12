#!/bin/bash
#sudo echo 'SUBSYSTEM=="vchiq",MODE="0666"' | sudo tee --append /etc/udev/rules.d/99-camera.rules <---- Only use once!
docker run --network host --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/video0:/dev/video0 --device /dev/gpiomem --device /dev/vchiq -v /opt/vc:/opt/vc --restart unless-stopped -v -it security-webcam:latest /bin/bash
