#!/bin/bash
#----------------------------------------------------
#
# SLURM SCRIPT, for runs at TACC (e.g. frontera)
#
# notes:
#   -- this script is for launching a NEW run!
#      CAUTION: this script will erase the corresponding $RUN_DIR in $SCRATCH,
#          which is the directory where the code will be run.
#      
#   -- this script must be located in the same directory as the eppic.i file,
#      and must have the same name as that file, but with a .slurm extension.
#      e.g. eppic_runname.slurm --> will run eppic_runname.i
#
#   -- Launch this script by executing "sbatch filename.slurm"
#      on a Frontera login node, from ANY directory.
#
#   -- this script will run the code in an appropriately-named directory in $SCRATCH.
#      e.g. script at $HOME/eppic/input_decks/someruns/run00/eppic_dev_v0.slurm, -->
#         RUN_DIR=$SCRATCH/eppic/runs/someruns/run00
#         mkdirm -p $RUN_DIR # if necessary.
#      
#      note the assumption that this script is somewhere inside $HOME/eppic/input_decks
#      also note that all files in the directory with this script will be copied.
#      this script works best if you keep each run in its own folder.
#
#   -- note from TACC: Max recommended MPI ranks per CLX node: 56
#      (start small, increase gradually).
#
#----------------------------------------------------

#SBATCH -J eppic_dev           # Job name
#SBATCH -o %x_%j.o       # Name of stdout output file = {jobname}_{jobid}.o
#SBATCH -p development         # Queue (partition) name
#SBATCH -N 4               # Total # of nodes
#SBATCH --tasks-per-node=56  # Tasks per node. (specify this, OR -n, but not both)
#SBATCH -t 0:03:00        # Run time (hh:mm:ss)
#SBATCH -A ATM23011       # Project/Allocation name (req'd if you have more than 1)
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH --mail-user=sevans7@bu.edu
# Any other commands must appear after all #SBATCH directives.

# # CONSTANTS # #
VERBOSE=true   # use "true" or "false"

EPPIC=${HOME}/eppic   # path to the eppic folder
EPPIC_X=${EPPIC}/bin/eppic.x  # path to the eppic.x file
SCR_EPPIC=${SCRATCH}/eppic   # path to the eppic folder in scratch
SCR_RUNS=${SCR_EPPIC}/runs   # path to the runs folder in scratch

# # FILE PATHS # #
JOBFILE_NAME_NOEXT=${SLURM_JOB_NAME}_${SLURM_JOB_ID}   # e.g. "eppic_runname_6010577"
JOBFILE_NAME=${JOBFILE_NAME_NOEXT}.o   # must match SBATCH -o formatting from above.

if [[ -n "${SLURM_JOB_ID:-}" ]] ; then   # --> the script is being run through slurm.
    # get script name from job ID.
    lines=$(scontrol show job "$SLURM_JOB_ID")  # has line "Command=stuff", where SCRIPT_FILE=stuff.
    while IFS= read -r line; do   # this loop will extract SCRIPT_FILE from lines.
        line="${line#"${line%%[![:space:]]*}"}"  # Remove leading whitespace
        if [[ "$line" == Command=* ]]; then
            value="${line#*=}" # Extract the part after "Command="
            value="${value##*( )}"  # Trim whitespace from stuff
            value="${value%%*( )}"  # Trim whitespace from stuff
            SCRIPT_FILE="$value"   # Store the value in a new variable
            break
        fi
    done <<< "$lines"
else  # --> the script is being run directly
    SCRIPT_FILE=$(realpath $0)
fi

SCRIPT_NAME=$(basename $SCRIPT_FILE .slurm)  # e.g. "eppic_runname"  # without .slurm extension
EPPIC_I=${SCRIPT_NAME}.i                     # e.g. "eppic_runname.i"

SCRIPT_DIR=$(dirname $SCRIPT_FILE)           # e.g. $EPPIC/input_decks/someruns/run00
REL_DIR=$(realpath -m --relative-to=$EPPIC/input_decks $SCRIPT_DIR) # e.g. someruns/run00
RUN_DIR=${SCR_RUNS}/${REL_DIR}               # e.g. $SCR_RUNS/someruns/run00
RUN_LOGS=${RUN_DIR}/logs_${SLURM_JOB_ID}     # e.g. $SCR_RUNS/someruns/run00/logs_6010577
TAR_EPPIC=${RUN_LOGS}/eppic.tgz  # full path to file which will store tarball of eppic code.

JOB_FILE=${SLURM_SUBMIT_DIR}/${JOBFILE_NAME}    # full path to job file (the .o file)

if [[ "$VERBOSE" = true ]] ; then
    echo "paths (some are based on script location & name):"
    echo "  SCRIPT_NAME: $SCRIPT_NAME"
    echo "  EPPIC_I: $EPPIC_I"
    echo "  EPPIC_X: $EPPIC_X"
    echo "  SCRIPT_FILE: $SCRIPT_FILE"
    echo "  SCRIPT_DIR: $SCRIPT_DIR"
    echo "  SCR_RUNS: $SCR_RUNS"
    echo "  REL_DIR: $REL_DIR"
    echo "  RUN_DIR: $RUN_DIR"
    echo "  RUN_LOGS: $RUN_LOGS"
    echo "  TAR_EPPIC: $TAR_EPPIC"
    echo "  JOB_FILE: $JOB_FILE"
fi

# if SCRIPT_FILE is not actually a file, we should crash; one or more paths are wrong.
# this might occur if the filename includes unusual characters, e.g. '='.
if [[ ! -f $SCRIPT_FILE ]] ; then
    echo ""
    echo "ERROR: failed to properly determine SCRIPT_FILE; it is not an existing file!"
    echo "Stopping before editing any files in SCRATCH. Aborting."
    kill $$
fi

# if RUN_DIR contains ../ we should crash; something unexpected happened when determining path.
# this might occur if the script file wasn't put somewhere inside the $EPPIC directory.
if [[ $RUN_DIR == *../* ]] ; then
    echo ""
    echo "ERROR: RUN_DIR contains '../'! Expected a simple path."
    echo "Stopping before editing any files in SCRATCH. Aborting."
    kill $$
fi

# if there is more than 1 eppic.i file anywhere inside RUN_DIR, we should crash;
# this might occur if the script file was put in a directory containing multiple runs.
INTERNAL_EPPIC_I_FILES=$(find $RUN_DIR -name '*eppic.i' -type f -print)
if (( $(echo "$INTERNAL_EPPIC_I_FILES" | wc -l) > 1 )) ; then
    echo ""
    echo "ERROR: found more than 1 eppic.i file inside RUN_DIR and any subdirectories!"
    echo "Expected at most 1 eppic.i file, to avoid overwriting more than 1 existing run."
    echo "These are the files found:"
    echo "$INTERNAL_EPPIC_I_FILES"
    echo "Stopping before editing any files in SCRATCH. Aborting."
    kill $$
fi

# # CREATING & CLEANING RUN_DIR # #
# first, setup directory; copy inputs from $SCRIPT_DIR into $RUN_DIR.
mkdir -p $RUN_DIR   # make run directory, if needed!
rm -rf ${RUN_DIR}/*   # delete contents of run directory, if needed.
cp -r ${SCRIPT_DIR}/* $RUN_DIR  # copy script dir contents into rundir

# delete any *.o files in $RUN_DIR; we will copy the job file later.
rm -f ${RUN_DIR}/*.o

# # LOGS # #
mkdir -p $RUN_LOGS
# copy this .slurm file into RUN_LOGS.
cp $SCRIPT_FILE $RUN_LOGS
# copy tarball of the eppic codebase into RUN_LOGS.
cd $EPPIC
tar chf - src/*.h* src/*.c* src/make* src/classes */*.com bin |gzip - > $TAR_EPPIC
# copy eppic/bin/logs/latest into RUN_LOGS, if possible.
LATEST_LOGS=${EPPIC}/bin/logs/latest
if [[ -d $LATEST_LOGS ]]; then
    cp -r ${LATEST_LOGS}/* $RUN_LOGS
fi

# print the command we will use to run the job
if [[ "$VERBOSE" = true ]] ; then
    echo "cd $RUN_DIR"
    echo "ibrun $EPPIC_X $EPPIC_I"
fi

# copy the jobfile into RUN_LOGS; renaming to append 't=0' to the name.
if [[ "$VERBOSE" = true ]] ; then
    echo ""
    echo "before run, copying the jobfile into RUN_LOGS:"
    echo "cp $JOB_FILE $RUN_LOGS"
    echo "mv ${RUN_LOGS}/${JOBFILE_NAME} ${RUN_LOGS}/${JOBFILE_NAME_NOEXT}_t=0.o"
    echo ""
fi
cp $JOB_FILE $RUN_LOGS
mv ${RUN_LOGS}/${JOBFILE_NAME} ${RUN_LOGS}/${JOBFILE_NAME_NOEXT}_t=0.o

# # RUNNING THE JOB # #
cd $RUN_DIR
{
    # # SETUP # #
    start_time=$(date +%s)  # get the start time of the job.

    # # RUNNING # #
    # << actually run the job. ibrun is like mpirun on TACC, but autofills -np
    ibrun $EPPIC_X $EPPIC_I

    # # FINALIZING # #
    # copy the .o file into the logs directory.
    # note, if the job ends due to timeout, this will not happen.
    echo ""
    echo "--- run completed naturally! ---"
    echo "job starting time: $start_time"
    echo "job ending time: $(date +%s)"
    echo "job total time: $(( $(date +%s) - $start_time )) seconds"
    echo ""
    echo "copying the .slurm and .o file into $RUN_LOGS"
    cp $JOB_FILE $RUN_LOGS  # anything after this line won't be copied!
} || {   # error occurred.
    # # FINALIZING # #
    # copy the .o file into the logs directory.
    # note, if the job ends due to timeout, this will not happen.
    echo ""
    echo "--- run completed, with error! ---"
    echo "job starting time: $start_time"
    echo "job ending time: $(date +%s)"
    echo "job total time: $(( $(date +%s) - $start_time )) seconds"
    echo ""
    echo "copying the .slurm and .o file into $RUN_LOGS"
    cp $JOB_FILE $RUN_LOGS  # anything after this line won't be copied!
}