#!/bin/bash
cd /opt/render/project/src

rm -rf zsign
git clone https://github.com/zhlynn/zsign.git
cd zsign/build/linux
make
cp ../../bin/zsign /opt/render/project/src/zsign

chmod 755 /opt/render/project/src/zsign
ls -la /opt/render/project/src/zsign
