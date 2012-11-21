# $Id$
# Makefile definitions customized for Linux x86_64 using the Intel Fortran 
# compiler and ACML.  This uses a 4 byte real for the purposes of linking WRF-CLUBB.


# Fortran 95 compiler and linker
FC=ifort
LD=ifort

# Define path to directories
dir=`pwd` # dir where this script resides
bindir="$dir/../bin"  # dir for Makefile and executable
objdir="$dir/../obj"  # dir for *.o and *.mod files
libdir="$dir/../lib"  # dir for *.a library files
srcdir="$dir/../src"  # dir where the source files reside

# == Debugging ==
# No Debug flags
DEBUG=""
#DEBUG="-g -traceback -check bounds -check uninit -fpe0 -fpz"

# == Warnings ==
WARNINGS="-warn -warn notruncated_source"

# == Machine specific options ==
ARCH="-msse2 -fp-model precise" # This should work on most modern AMD/Intel computers
# == Used to promote all real's to double precision ==
DOUBLE_PRECISION="-real-size 64"

# == Optimization ==
OPTIMIZE="-O3 -vec-report0"

# == NetCDF Location ==
NETCDF="/usr/local/netcdf-intel64"

# == LAPACK libraries ==
ACML="/opt/acml5.1.0/ifort64/lib"
LAPACK="-L$ACML -Wl,-rpath,$ACML -lacml"
# Generic library
#LAPACK="-llapack -lblas -lgfortran"

# == Linking Flags ==
# Use -s to strip (no debugging); 
# Use -L<library path> -l<lib> to link in an external library
LDFLAGS="-L$NETCDF/lib -lnetcdf $LAPACK"

FFLAGS="$ARCH $OPTIMIZE $DEBUG"

# Preprocessing Directives:
#   -DNETCDF enables netCDF output
#   -Dradoffline and -Dnooverlap (see bugsrad documentation)
#   -DMKL enables MKL solver (PARDISO/GMRES) support
# You will need to `make clean' if you change these
# Use -I<include path> to set a module or header file directory
# Define include directories. 
# Need location of include and *.mod files for the netcdf library

CPPDEFS="-DNETCDF -Dnooverlap -Dradoffline -DCLUBB_REAL_TYPE=4"
CPPFLAGS="-I$NETCDF/include"

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
