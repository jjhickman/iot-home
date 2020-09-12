#!/bin/bash
docker run --privileged --network host --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/gpiomem --device /dev/vchiq -v /opt/vc:/opt/vc -it raspbian/stretch:latest /bin/bash
