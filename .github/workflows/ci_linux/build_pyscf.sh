#!/usr/bin/env bash

set -e

cd ./pyscf/lib
archive=$(mktemp)
trap 'rm -f "$archive"' EXIT
curl --fail --location --retry 5 --retry-delay 2 --retry-all-errors --output "$archive" \
  "https://github.com/pyscf/pyscf-build-deps/blob/master/pyscf-2.8a-deps.tar.gz?raw=true"
tar xzf "$archive"
mkdir build; cd build
cmake -DBUILD_LIBXC=ON -DBUILD_XCFUN=ON -DBUILD_LIBCINT=OFF -DXCFUN_MAX_ORDER=4 \
  -DLIBXC_URL=https://gitlab.com/libxc/libxc/-/archive/f4439479220beff707fc071e14345a205c885521/libxc-f4439479220beff707fc071e14345a205c885521.tar.gz ..
make -j4
cd ..
rm -Rf build
cd ../..
