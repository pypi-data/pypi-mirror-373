#!/bin/bash

# This script downloads the Testing version from KB web page
# builds with the standard options
# create tarball ready to be installed on CVMFS

usage="$(basename "$0") needs 1 argument:
Example:
$(basename "$0") 2022-07-05"

if [ $# -ne 1 ]
then
echo "$usage"
exit 1
fi

# Read the args
tag=$1

WORK_DIR=$PWD
wget --user=CTA --password="****" https://www.mpi-hd.mpg.de/hfm/CTA/MC/Software/Testing/corsika7.7_simtelarray.tar.gz
tar -zxvf corsika7.7_simtelarray.tar.gz
./build_all prod6-sc qgs2 gsl
# This is the most conservative variant (wrt to memory) without SCT
#./build_all prod6-alpha qgs2 gsl
cd sim_telarray/cfg/CTA/
# The sym links below are not necessary anymore after having added
# SIM_TELARRAY_CONFIG_PATH with the include paths in setupPackage.sh
#ln -s ../common/atm_trans_2147_1_10_2_0_2147.dat
#ln -s ../hess/hess_reflect.dat
#ln -s ../common/dummy_pulse.dat
#ln -s ../common/funnel_perfect.dat
#ln -s ../hess2/single_pixel_camera.dat
#ln -s ../hess/hess_funnels_r78.dat
#ln -s ../common/single_12m_mirror.dat
cd $WORK_DIR/sim_telarray
unlink read_hess
cd $WORK_DIR
tar zcvf corsika-$tag.tar.gz * --exclude='*tar.gz' --exclude="build.sh"
