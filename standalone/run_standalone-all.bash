#!/bin/bash
#######################################################################
# $Id: run_standalone-all.bash,v 1.22 2007-02-10 16:00:15 griffinb Exp $
#
# Script to run the standalone hoc program for all models.
# Tested with bash v2.  Might work with Ksh.
#
#######################################################################
# Useful on multiprocessor machines with OpenMP capable Fortran
# OMP_NUM_THREADS=2
#######################################################################

EXIT_CODE=( [0]=0 [1]=0 [2]=0 [3]=0 [4]=0 [5]=0 [6]=0 [7]=0 [8]=0 [9]=0 \
 [10]=0 [11]=0 [12]=0 [13]=0 )

RUN_CASE=( \
	arm atex bomex dycoms2_rf01 dycoms2_rf02_do dycoms2_rf02_ds \
 	dycoms2_rf02_nd dycoms2_rf02_so fire jun25_altocu mpace
        nov11_altocu rico wangara )

# This will loop over all runs in sequence 
for (( x=0; x < "${#RUN_CASE[@]}"; x++ )); do
#######################################################################
# Check for necessary namelists.  If files exist, then
# copy them over to the general input files.

 STANDALONE_IN='standalone_'"${RUN_CASE[$x]}"'.in'
 MODEL_IN='../model/'"${RUN_CASE[$x]}"'_model.in'
 STATS_IN='../stats/'"${RUN_CASE[$x]}"'_stats.in'

 if [ ! -e "$STANDALONE_IN" ] ; then
	echo $STANDALONE_IN " does not exist"
	exit 1
 fi

 if [ -e 'standalone.in' ] ; then
	rm -f 'standalone.in'
 fi

 ln -s $STANDALONE_IN 'standalone.in'
 cat $MODEL_IN $STATS_IN > "${RUN_CASE[$x]}"'_hoc.in'

#######################################################################
#
# State which case is being run
 echo "Running ""${RUN_CASE[$x]}"
# Run HOC 
 RESULT=`../bin/hoc_standalone 2>&1 |grep 'normal'`
#echo $RESULT
 if [ -z "$RESULT" ]; then
	EXIT_CODE[$x]=-1
 fi

# remove the namelists
 rm -f 'standalone.in'
 rm -f "${RUN_CASE[$x]}"'_hoc.in'

done

# Print the results
for (( x=0; x < "${#RUN_CASE[@]}"; x++ )); do
  if [ "${EXIT_CODE[$x]}" != 0 ]; then
	echo "${RUN_CASE[$x]}"' failure'
  fi
done
