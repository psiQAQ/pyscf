#!/usr/bin/env bash
set -e

#XXX default clang compiler does not support openmp, shall we use gcc?
cd ./pyscf/lib
#curl -L https://github.com/fishjojo/pyscf-deps/raw/master/pyscf-1.7.5-deps-macos-10.14.tar.gz | tar xzf -
mkdir build; cd build
#cmake -DBUILD_LIBXC=OFF -DBUILD_XCFUN=OFF ..
revision="${LIBXC_REVISION:-f4439479220beff707fc071e14345a205c885521}"
if [[ ! "$revision" =~ ^[0-9a-f]{40}$ ]]; then
  echo "LIBXC_REVISION must be a 40-character lowercase commit hash" >&2
  exit 1
fi
cmake -DLIBXC_URL=https://gitlab.com/libxc/libxc/-/archive/$revision/libxc-$revision.tar.gz ..
make -j4
cd ..
rm -Rf build
cd ../..
