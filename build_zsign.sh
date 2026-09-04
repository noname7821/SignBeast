#!/bin/bash
cd /opt/render/project/src

apt-get update
apt-get install -y build-essential libssl-dev pkg-config git

rm -rf zsign
git clone https://github.com/zhlynn/zsign.git
cd zsign/build/linux

make clean
make

cp ../../bin/zsign /opt/render/project/src/zsign
chmod 755 /opt/render/project/src/zsign

ls -la /opt/render/project/src/zsign
