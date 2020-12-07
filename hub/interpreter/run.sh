#!/bin/bash
docker run --privileged --restart unless-stopped -v /dev/bus/usb:/dev/bus/usb -it jjhickman/tpu-interpreter bash
