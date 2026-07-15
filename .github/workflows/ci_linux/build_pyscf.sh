#!/usr/bin/env bash

set -e

cd ./pyscf/lib
revision="${LIBXC_REVISION:-}"
wpbeh_revision="${LIBXC_WPBEH_REVISION:-}"
if [ -n "$revision" ]; then
  case "$revision" in
    *[!0-9a-f]*) echo "LIBXC_REVISION must be a 40-character lowercase commit SHA" >&2; exit 2 ;;
  esac
  [ "${#revision}" -eq 40 ] || { echo "LIBXC_REVISION must be a 40-character lowercase commit SHA" >&2; exit 2; }
fi
case "$wpbeh_revision" in
  *[!0-9a-f]*) echo "LIBXC_WPBEH_REVISION must be a 40-character lowercase commit SHA" >&2; exit 2 ;;
esac
[ -z "$wpbeh_revision" ] || [ "${#wpbeh_revision}" -eq 40 ] || {
  echo "LIBXC_WPBEH_REVISION must be a 40-character lowercase commit SHA" >&2; exit 2;
}
[ -z "$wpbeh_revision" ] || [ -n "$revision" ] || {
  echo "LIBXC_WPBEH_REVISION requires LIBXC_REVISION" >&2; exit 2;
}
archive=$(mktemp)
patch_dir=""
trap 'rm -f "$archive"; [ -z "$patch_dir" ] || rm -rf "$patch_dir"' EXIT
curl --fail --location --retry 5 --retry-delay 2 --retry-all-errors --output "$archive" \
  "https://github.com/pyscf/pyscf-build-deps/blob/master/pyscf-2.8a-deps.tar.gz?raw=true"
tar xzf "$archive"
mkdir build; cd build
if [ -n "$revision" ]; then
  libxc_url="https://gitlab.com/libxc/libxc/-/archive/$revision/libxc-$revision.tar.gz"
  if [ -n "$wpbeh_revision" ]; then
    patch_dir=$(mktemp -d)
    mkdir "$patch_dir/source"
    curl --fail --location --retry 5 --retry-delay 2 --retry-all-errors \
      --output "$patch_dir/libxc.tar.gz" "$libxc_url"
    tar xzf "$patch_dir/libxc.tar.gz" -C "$patch_dir/source" --strip-components=1
    curl --fail --location --retry 5 --retry-delay 2 --retry-all-errors \
      --output "$patch_dir/source/src/maple2c/gga_exc/gga_x_wpbeh.c" \
      "https://gitlab.com/libxc/libxc/-/raw/$wpbeh_revision/src/maple2c/gga_exc/gga_x_wpbeh.c"
    patched_archive="$patch_dir/libxc-wpbeh.tar.gz"
    tar czf "$patched_archive" -C "$patch_dir/source" .
    libxc_url="file://$patched_archive"
  fi
  cmake -DBUILD_LIBXC=ON -DBUILD_XCFUN=ON -DBUILD_LIBCINT=OFF -DXCFUN_MAX_ORDER=4 \
    -DLIBXC_URL="$libxc_url" ..
else
  cmake -DBUILD_LIBXC=OFF -DBUILD_XCFUN=ON -DBUILD_LIBCINT=OFF -DXCFUN_MAX_ORDER=4 ..
fi
make -j4
cd ..
rm -Rf build
cd ../..
