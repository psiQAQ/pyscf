#!/usr/bin/env bash
set -euo pipefail
root="$PWD"
mkdir -p "$root/tmp/cms-evidence" "$root/tmp/cms-scratch"
export TMPDIR="$root/tmp/cms-scratch"
exec > >(tee "$root/tmp/cms-evidence/prepare.log") 2>&1
echo "prepare PID=$$"
uname -a
cat /etc/os-release
lscpu
git rev-parse HEAD
python --version
python -m pip install 'pip==26.3'
python -m pip install 'numpy==2.4.6' 'scipy==1.17.1' 'h5py==3.16.0' \
  'pytest==9.2.0' 'pytest-xdist==3.8.0' 'pytest-timeout==2.4.0' \
  'pytest-cov==7.1.0' 'coverage==7.17.2' 'execnet==2.1.2' \
  'iniconfig==2.3.1' 'packaging==26.3' 'pluggy==1.7.0' 'pygments==2.21.0' \
  'pyberny==0.7.0' 'molsym==1.3.1' 'geometric==1.1.1' \
  'networkx==3.6.1' 'six==1.17.0' 'trexio==2.6.1' threadpoolctl
python -m pip install --no-deps 'pyscf-dispersion==1.7.0'
python -m pip freeze > "$root/tmp/cms-evidence/packages.txt"
cd "$root/tmp/cms-source"
git rev-parse HEAD
bash .github/workflows/ci_linux/deps_apt.sh
gcc --version
cmake --version
bash .github/workflows/ci_linux/build_pyscf.sh
tar czf "$root/tmp/cms-native.tar.gz" --exclude='*.c' --exclude='*.h' --exclude='*.f' \
  --exclude='*.py' --exclude='*.pyc' pyscf/lib
