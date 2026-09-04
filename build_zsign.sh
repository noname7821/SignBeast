#!/bin/bash
cd /opt/render/project/src

apt-get update > /dev/null 2>&1
apt-get install -y build-essential libssl-dev pkg-config git > /dev/null 2>&1

rm -rf zsign_src
git clone https://github.com/zhlynn/zsign.git zsign_src > /dev/null 2>&1
cd zsign_src/build/linux

make clean > /dev/null 2>&1
make > /dev/null 2>&1

cp ../../bin/zsign /opt/render/project/src/zsign
chmod 755 /opt/render/project/src/zsign

ls -la /opt/render/project/src/zsign
