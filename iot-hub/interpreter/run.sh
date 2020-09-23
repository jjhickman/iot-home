#!/bin/bash
docker run --privileged --network host --restart unless-stopped -v /dev/bus/usb:/dev/bus/usb -it jjhickman/interpreter-arm64v8:latest /bin/bash
