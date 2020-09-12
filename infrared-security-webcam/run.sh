#!/bin/bash
sudo echo 'SUBSYSTEM=="vchiq",MODE="0666"' | sudo tee --append /etc/udev/rules.d/99-camera.rules
docker run --privileged --network host --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/video0:/dev/video0 --device /dev/vchiq -v /opt/vc:/opt/vc --restart unless-stopped -v /dev/bus/usb:/dev/bus/usb -it security-webcam:latest /bin/bash
