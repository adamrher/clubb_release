# $Id$
# Configuration file for Mac computers in W434.  It may work on other Macs
# as well but is not tested.

# Fortran 95 compiler and linker
FC=gfortran
LD=gfortran

# Define path to directories
dir=`pwd` # dir where this script resides
bindir="$dir/../bin"  # dir for Makefile and executable
objdir="$dir/../obj"  # dir for *.o and *.mod files
libdir="$dir/../lib"  # dir for *.a library files
srcdir="$dir/../src"  # dir where the source files reside


# It is sometimes helpful to turn on floating-point trapping for the 
#  standalone program, but this will not work when using the tuner.
# These are the options for debugging symbols, bounds checking & IEEE-754 
# floating point arithmetic
DEBUG="-g -fbounds-check -mieee-fp"

# == Warnings ==
WARNINGS="-Wall -pedantic"

# == Machine specific flags ==
# Note: some of these are 64 bit architectures, so make sure NetCDF is
# compiled accordingly.
ARCH="-march=native -msse3 -mfpmath=sse -fopenmp"

# == Optimization ==
OPTIMIZE="-O2"

# == NetCDF Location ==
# No netCDF for the Macs in W343
#NETCDF="/Users/dschanen/netcdf-gfortran" # MacOS X

# == LAPACK libraries ==
LAPACK="-llapack -lblas" # The netlib reference LAPACK/BLAS
#LAPACK="-L/usr/lib64 -llapack -L/usr/local/atlas/lib -lf77blas -lcblas -latlas" # ATLAS BLAS (faster)

# == Linking Flags ==
# Use -s to strip (no debugging); 
# Use -L<library path> -l<lib> to link in an external library
# Use -Wl,-rpath <library path> to set a search path for shared libs
#LDFLAGS="$ARCH $LAPACK -L$NETCDF/lib -Wl,-rpath $NETCDF/lib -lnetcdf -lnetcdff"
LDFLAGS="$ARCH $LAPACK" # OSX

# == Compiler flags ==
# You will need to `make clean' if you change these
FFLAGS="$ARCH $OPTIMIZE $DEBUG"

# Preprocessing Directives:
#   -DNETCDF enables netCDF output
#   -Dradoffline and -Dnooverlap (see BUGSrad documentation)
# You will need to `make clean' if you change these
# Use -I<include path> to set a module or header file directory
#NETCDF_INCLUDE="$NETCDF/include/"
#CPPFLAGS="-I$NETCDF_INCLUDE"
#CPPDEFS="-DNETCDF -Dnooverlap -Dradoffline"
CPPDEFS="-Dradoffline -Dnooverlap" # MacOS X (no netCDF)

# == Static library processing ==
AR=ar
ARFLAGS=cru
RANLIB=ranlib

# == Shared library processing ==
SHARED=$FC
SHAREDFLAGS="-fPIC -shared"

# Location of 'mkmf' utility
mkmf=$dir/mkmf

# gmake command to use and options: '-j 2' enables parallel compilation
gmake="make"
