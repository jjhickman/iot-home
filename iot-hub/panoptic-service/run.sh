#!/bin/bash
#sudo echo 'SUBSYSTEM=="vchiq",MODE="0666"' | sudo tee --append /etc/udev/rules.d/99-camera.rules # <----- Only run once!
docker run --network host --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/video0:/dev/video0 --device /dev/vchiq -v /opt/vc:/opt/vc --restart unless-stopped -v /dev/bus/usb:/dev/bus/usb -it panoptic-ubuntu-arm64v8:latest /bin/bash
