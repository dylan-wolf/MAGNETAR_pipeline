# The MAGNETAR* Pipeline;

*Magnetic-field Analysis and Generation of Noise-filtered Emission from Time-ordered Astronomical Records

An End-to-End Polarimetric Data Reduction Framework.



Core Ideas to implement for testing error:

Signal model per sample (per detector):

$$
d_t = g[I(\hat n)]+ \rho \{Q(\hat n_t)\cos2\gamma_t+U(\hat n_t)\sin 2\gamma_t\}]+n_t
$$
where:
* $ \gamma_t$: detector + HWP angle in sky frame
* $\rho$: polatization efficiency
* Noise $n_t$: white +1/f

Demod / solve per pixel:
For each pixel, solve a tiny linear regression from all samples hitting that pixel:

$$d=aI+bQ+cU,\;a=1, \;b=ρcos2\gamma,\; c=ρsin2_gamma$$
d=aI+bQ+cU,a=1,b=ρcos2γ,c=ρsin2γ

weighted by inverse noise variance → gives I,Q,U and their $3\times3$ covariance.

Debias (simple Wardle–Kronberg):
$$
p_{meas}=\sqrt{\frac{Q^2+U^2}{I}},\;\; p_{deb}=\sqrt{max(p^2_{meas}−\sigma_p^2,\;0)} $$



# On Installing TOAST / toast-cmb Installation (Conda, Linux)


A clean, reproducible recipe—no trial‑and‑error steps.

## Assumptions

* You’re on Linux with a working **conda** environment (e.g., `magnetar`).
* Using `pip` inside that env.
* CMake ≥ 3.18 (≥ 3.27 shown below) is available.

## 1) Verify environment

```bash
conda activate magnetar
cmake --version    # should print 3.18+ (e.g., 3.27.9)
```

## 2) Install required libraries from conda-forge

The build needs BLAS/LAPACK (OpenBLAS), FFTW, SuiteSparse, and pkg-config.

```bash
conda install -y -c conda-forge \
  openblas "blas-devel>=3.9" liblapacke \
  fftw suitesparse metis pkg-config
```

## 3) Prime CMake’s search paths

Make conda’s include/lib dirs discoverable and prefer them during the build.

```bash
export CMAKE_PREFIX_PATH="$CONDA_PREFIX"
export CMAKE_LIBRARY_PATH="$CONDA_PREFIX/lib"
export CMAKE_INCLUDE_PATH="$CONDA_PREFIX/include"
export PKG_CONFIG_PATH="$CONDA_PREFIX/lib/pkgconfig"
```

## 4) Set **CMAKE_ARGS** with all required hints

These flags ensure CMake finds OpenBLAS, FFTW, and SuiteSparse correctly and embeds the rpath to conda libs.

```bash
export CMAKE_ARGS="\
-DTOAST_USE_SUITESPARSE=ON \
-DBUILD_TESTING=OFF \
-DTOAST_BUILD_TESTS=OFF \
-DBLA_VENDOR=OpenBLAS \
-DBLAS_LIBRARIES=$CONDA_PREFIX/lib/libopenblas.so \
-DLAPACK_LIBRARIES=$CONDA_PREFIX/lib/libopenblas.so \
-DFFTW_INCLUDE_DIR=$CONDA_PREFIX/include \
-DFFTW_LIBRARY=$CONDA_PREFIX/lib/libfftw3.so \
-DFFTW_THREADS_LIBRARY=$CONDA_PREFIX/lib/libfftw3_threads.so \
-DFFTW_OMP_LIBRARY=$CONDA_PREFIX/lib/libfftw3_omp.so \
-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath,$CONDA_PREFIX/lib \
-DCMAKE_BUILD_TYPE=Release"
```

> If your system’s CMake insists on probing `sgemm_` and fails, append the usual aux libs:

```bash
export CMAKE_ARGS="$CMAKE_ARGS \
-DBLAS_LIBRARIES=$CONDA_PREFIX/lib/libopenblas.so;-lm;-ldl;-lpthread \
-DLAPACK_LIBRARIES=$CONDA_PREFIX/lib/libopenblas.so;-lm;-ldl;-lpthread"
```

## 5) Install

```bash
python -m pip install --no-build-isolation --use-pep517 toast-cmb
```

This will build `toast` (C++ core via CMake) and then install `toast-cmb`.

## Sanity checks

```bash
python -c "import toast, toast_cmb, numpy as np; print('OK:', toast.__version__)"
```

## (Optional) Fallback path

If you ever need to pin `toast` explicitly, install it first (still honors `CMAKE_ARGS`):

```bash
pip install --no-build-isolation --no-cache-dir \
  "git+https://github.com/hpc4cmb/toast.git@v2.3.14"
python -m pip install --no-build-isolation --use-pep517 toast-cmb
```

## Notes

* `CMAKE_ARGS` is the reliable way to pass flags to the project’s CMake configure step from pip.
* `CMAKE_PREFIX_PATH` and friends ensure the conda toolchain and libs are preferred over system ones.
* Disabling tests (`BUILD_TESTING`, `TOAST_BUILD_TESTS`) speeds up and simplifies the build.
