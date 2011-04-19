#!/bin/bash
# $Id$
# ------------------------------------------------------------------------------
#
# Compilation script for CLUBB. It generates:
#  - libraries: libclubb_bugsrad.a, libclubb_param.a, libclubb_coamps.a
#  - executables: clubb_standalone clubb_tuner jacobian int2txt
#
# Sub-makefiles for each target are automatically generated using the 
# 'mkmf' utility. Dependencies among source files are sorted out by 'mkmf'. 
# A master makefile is generated that invokes all sub-makefiles.
#
# Machine specific settings are included through a configuration
# file located under config/
#
# This script also depends on external files containing a list of source 
# files to be included in each target, which we need to maintain manually:
# - file_list/bugsrad_files : files needed for libclubb_bugsrad.a
# - file_list/param_files : files needed for libclubb_param.a
# - file_list/model_files : files needed for clubb_standalone, clubb_tuner, 
#                           and jacobian
# - file_list/clubb_standalone_files : files needed for clubb_standalone
# - file_list/clubb_tuner_files : files needed for clubb_tuner
# - file_list/jacobian_files : files needed for jacobian
# - file_list/int2txt_files : files needed for int2txt
# - file_ilst/clubb_gfdl_activation_files : files needed for libclubb_gfdlact.a
#
# The following files are automatically generated by the script based on 
# the directories in src:
# - file_list/coamps_files : files needed for libclubb_coamps.a
# - file_list/numerical_recipes_files : Numerical Recipes files for clubb_tuner
# - file_list/clubb_optional_files: Code in the UNRELEASED_CODE blocks of clubb
# These three file lists can be empty if Numerical Recipes or COAMPS 
# microphysics is not available due to licensing restrictions.
# ------------------------------------------------------------------------------

# Flag to allow for promotion of reals to double precision at compile time
# This will exclude numerical recipes files which will preculde use of the tuner
l_double_precision=false

# Figure out the directory where the script is located
scriptPath=`dirname $0`

# Store the current directory location so it can be restored
restoreDir=`pwd`

# Change directories to the one the script is located in
cd $scriptPath

if [ -z $1 ]; then
	# Set using the default config flags

	CONFIG=./config/linux_x86_64_g95_optimize.bash # Linux (Redhat Enterprise 5)
#	CONFIG=./config/macosx_x86_64_gfortran.bash # MacOS X
#	CONFIG=./config/aix_powerpc_xlf90_bluefire.bash # IBM AIX on Bluefire
#	CONFIG=./config/solaris_generic_oracle.bash # Oracle Solaris

else
	# Set config based on the first argument given to compile.bash

	CONFIG=$1
fi

# Load desired configuration file

source $CONFIG

# ------------------------------------------------------------------------------
# Append preprocessor flags and libraries as needed

if [ -e $srcdir/COAMPS_micro ]; then
	CPPDEFS="${CPPDEFS} -DCOAMPS_MICRO"
	LDFLAGS="${LDFLAGS} -lclubb_coamps"
	COAMPS_LIB="libclubb_coamps.a"
fi
if [ -e $srcdir/Numerical_recipes ]; then
	CPPDEFS="${CPPDEFS} -DTUNER"
fi
if [ -e $srcdir/Benchmark_cases/Unreleased_cases ]; then
	CPPDEFS="${CPPDEFS} -DUNRELEASED_CODE"
fi

if [ -e $srcdir/SCM_Activation ]; then
	#CPPDEFS="${CPPDEFS} -DAERSOL_ACT"
	LDFLAGS="${LDFLAGS} -lclubb_gfdlact"
	GFDLACT_LIB="libclubb_gfdlact.a"
fi

# ------------------------------------------------------------------------------
# Required libraries + platform specific libraries from LDFLAGS
LDFLAGS="-L$libdir -lclubb_param -lclubb_bugsrad -lclubb_morrison -lclubb_mg $LDFLAGS"

# ------------------------------------------------------------------------------
# Special addition for XLF, which uses the xlf for fixed format and xlf90 for 
# free format Fortran files.  For other compilers we can just assume FC is 
# good enough for fixed and free format.
if [ -z "${F77}" ] || [ -z "${F90}" ]; then
	if [ -z ${FC} ]; then
		echo "Either FC, or F90 and F77 must be defined"
		exit -1
	else
		F90="${FC}"
		F77="${FC}"
	fi
fi


# ------------------------------------------------------------------------------
# Generate template for makefile generating tool 'mkmf'


cd $bindir
cat > mkmf_template << EOF
# mkmf_template needed my 'mkmf' and generated by 'compile.bash'
# Edit 'compile.bash' to customize.

F77 = ${F77}
F90 = ${F90}
LD = ${LD}
CPPFLAGS = ${CPPFLAGS}
FFLAGS = ${FFLAGS}
LDFLAGS = ${LDFLAGS}
EOF
cd $dir

# ------------------------------------------------------------------------------
# Generate file lists
# It would be nice to generate file lists for clubb_standalone / clubb_tuner 
# dynamically, but this not possible without some major re-factoring of 
# the CLUBB source directories.

# ------------------------------------------------------------------------------
#  Determine which restricted files are in the source directory and make a list
ls $srcdir/Benchmark_cases/Unreleased_cases/*.F90 > $dir/file_list/clubb_optional_files
ls $srcdir/CLUBB_core/*.F90 > $dir/file_list/clubb_param_files
ls $srcdir/Latin_hypercube/*.* >> $dir/file_list/clubb_optional_files
ls $srcdir/COAMPS_micro/*.F > $dir/file_list/clubb_coamps_files
ls $srcdir/SCM_Activation/aer_ccn_act_k.F90 > $dir/file_list/clubb_gfdl_activation_files

if [ "$l_double_precision" == "false" ]	# Excludes numerical recipes if using double precision
then
	ls $srcdir/Numerical_recipes/*.f90 > $dir/file_list/numerical_recipes_files
fi

# ------------------------------------------------------------------------------
# Generate makefiles using 'mkmf'
# Note: I have done a maleficium thing and put ${WARNINGS} as a preprocessor
# flag when in reality it has nothing to do with preprocessing.  This is because
# 3rd party code from ACM TOMS and Numerical recipes has a .f90 extension and we
# don't want use the warning flags on code we didn't write.  The consequence of
# this is that if we add a new file that has a .f90 extension 
# the warning flags will not be used on that file.  -dschanen 29 Jan 2009

cd $objdir
$mkmf -t $bindir/mkmf_template -p $libdir/libclubb_param.a -m Make.clubb_param -c "${CPPDEFS}" \
  -o "${WARNINGS}" $clubb_param_mods $dir/file_list/clubb_param_files

$mkmf -t $bindir/mkmf_template \
  -p $libdir/libclubb_bugsrad.a -m Make.clubb_bugsrad -c "${CPPDEFS}" $dir/file_list/clubb_bugsrad_files

$mkmf -t $bindir/mkmf_template \
  -p $libdir/libclubb_coamps.a -m Make.clubb_coamps -c "${CPPDEFS}" $dir/file_list/clubb_coamps_files

$mkmf -t $bindir/mkmf_template \
  -p $libdir/libclubb_morrison.a -m Make.clubb_morrison -c "${CPPDEFS} -DCLUBB" $dir/file_list/clubb_morrison_files
  
$mkmf -t $bindir/mkmf_template \
  -p $libdir/libclubb_mg.a -m Make.clubb_mg -c "${CPPDEFS} -DCLUBB" $dir/file_list/clubb_mg_files

$mkmf -t $bindir/mkmf_template \
  -p $libdir/libclubb_gfdlact.a -m Make.clubb_gfdlact -c "${CPPDEFS} -DCLUBB" $dir/file_list/clubb_gfdl_activation_files

$mkmf -t $bindir/mkmf_template -p $bindir/clubb_standalone \
  -m Make.clubb_standalone -c "${CPPDEFS} ${WARNINGS}" $clubb_standalone_mods \
  $dir/file_list/clubb_standalone_files $dir/file_list/clubb_optional_files \
  $dir/file_list/clubb_model_files

if [ "$l_double_precision" == "false" ] # Excludes the tuner if using double precision
then
	$mkmf -t $bindir/mkmf_template -p $bindir/clubb_tuner \
  	  -m Make.clubb_tuner -c "${CPPDEFS} ${WARNINGS}" $dir/file_list/clubb_tuner_files \
  	  $dir/file_list/clubb_optional_files $dir/file_list/clubb_model_files \
  	  $dir/file_list/numerical_recipes_files
fi

$mkmf -t $bindir/mkmf_template -p $bindir/jacobian \
  -m Make.jacobian -c "${CPPDEFS} ${WARNINGS}" $dir/file_list/jacobian_files \
  $dir/file_list/clubb_optional_files $dir/file_list/clubb_model_files

$mkmf -t $bindir/mkmf_template -p $bindir/int2txt -m Make.int2txt \
  -o "${WARNINGS}" $dir/file_list/int2txt_files

cd $dir

#-------------------------------------------------------------------------------
# Determine if additional folders need to be checked against the standard
if [ -e $srcdir/Benchmark_cases/Unreleased_cases ]; then
	CLUBBStandardsCheck_unreleased_cases="-perl ../utilities/CLUBBStandardsCheck.pl ../src/Benchmark_cases/Unreleased_cases/*.F90"
fi

if [ -e $srcdir/Latin_hypercube ]; then
	CLUBBStandardsCheck_latin_hypercube="-perl ../utilities/CLUBBStandardsCheck.pl ../src/Latin_hypercube/*.F90"
fi

# ------------------------------------------------------------------------------
# Generate master makefile
# CLUBB generates libraries.  The dependencies between such libraries must
# be handled manually.

cd $bindir
cat > Makefile << EOF
# Master makefile for CLUBB generated by 'compile.bash'
# Edit 'compile.bash' to customize.

all:	libclubb_param.a libclubb_bugsrad.a clubb_standalone clubb_tuner \
	jacobian int2txt
	perl ../utilities/CLUBBStandardsCheck.pl ../src/*.F90
	perl ../utilities/CLUBBStandardsCheck.pl ../src/CLUBB_core/*.F90
	perl ../utilities/CLUBBStandardsCheck.pl ../src/Benchmark_cases/*.F90
	$CLUBBStandardsCheck_unreleased_cases
	perl ../utilities/CLUBBStandardsCheck.pl ../src/KK_micro/*.F90
	$CLUBBStandardsCheck_latin_hypercube

libclubb_param.a:
	cd $objdir; $gmake -f Make.clubb_param

libclubb_bugsrad.a: libclubb_param.a
	cd $objdir; $gmake -f Make.clubb_bugsrad

libclubb_coamps.a:
	cd $objdir; $gmake -f Make.clubb_coamps

libclubb_morrison.a: libclubb_param.a
	cd $objdir; $gmake -f Make.clubb_morrison
	
libclubb_mg.a: libclubb_param.a
	cd $objdir; $gmake -f Make.clubb_mg

libclubb_gfdlact.a: 
	cd $objdir; $gmake -f Make.clubb_gfdlact

clubb_standalone: libclubb_bugsrad.a libclubb_param.a $COAMPS_LIB libclubb_morrison.a libclubb_mg.a $GFDLACT_LIB
	-rm -f $bindir/clubb_standalone
	cd $objdir; $gmake -f Make.clubb_standalone

clubb_tuner: libclubb_bugsrad.a libclubb_param.a $COAMPS_LIB libclubb_morrison.a libclubb_mg.a $GFDLACT_LIB
	-rm -f $bindir/clubb_tuner
	cd $objdir; $gmake -f Make.clubb_tuner		# Comment out if using double precision


jacobian: libclubb_bugsrad.a libclubb_param.a $COAMPS_LIB libclubb_morrison.a libclubb_mg.a $GFDLACT_LIB
	-rm -f $bindir/jacobian
	cd $objdir; $gmake -f Make.jacobian

int2txt: libclubb_bugsrad.a libclubb_param.a $COAMPS_LIB libclubb_morrison.a libclubb_mg.a
	-rm -rf $bindir/int2txt
	cd $objdir; $gmake -f Make.int2txt

clean:
	-rm -f $objdir/*.o \
	$objdir/*.mod
	
distclean:
	-rm -f $objdir/*.* \
	$objdir/.cppdefs \
	$libdir/lib* \
	$bindir/clubb_standalone \
	$bindir/clubb_tuner \
	$bindir/int2txt \
	$bindir/jacobian \
	$bindir/mkmf_template \
	$bindir/Makefile \

EOF
cd $dir

# ------------------------------------------------------------------------------
# Invoke master makefile

cd $bindir
$gmake
# Get the exit status of the gmake command
exit_status=${?}
cd $restoreDir

# Exit returing the result of the make
exit $exit_status
