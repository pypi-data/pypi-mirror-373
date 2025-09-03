#!/bin/bash

# This script builds the corsika-77410-OPT version

usage="$(basename "$0") needs 4 arguments:
Example:
$(basename "$0") 2020-04-15 gcc48/gcc83 avx512/avx2/avx/sse4 size(4/8)"

if [ $# -ne 4 ]
then
echo "$usage"
exit 1
fi

# Read the args
tag=$1
gcc=$2
inst=$3
size=$4
WORK_DIR=$PWD

if [ -d "opt" ]; then
rm -Rf opt
fi

mkdir opt
git clone git@gite.lirmm.fr:cta-optimization-group/cta-optimization-project.git opt/
echo "build corsika 77410 OPT version"
cd opt/packages/
git checkout v0.3
make configure-corsika-77410-OPT
make hessioxxx
make sim_telarray
cd ..

./experience.py --om test --gen v_ref_${gcc}_${inst}_size${size}_static
ln -s corsika_v_ref_${gcc}_${inst}_size${size}_static packages/corsika-77410/run/corsika

echo "archive corsika-77410-opt"
cd packages
tar zcvf $WORK_DIR/corsika-77410-$tag-$inst.tar.gz corsika-77410/
