START_TIME=$(date -u +%s)
echo

echo "Input files:"
ls -a

echo
echo "Preparing..."
echo

mkdir venv
tar -xzf $VENV_TAR -C venv
source venv/bin/activate
conda-unpack

export NUMEXPR_NUM_THREADS=$THREAD_COUNT
export NUMEXPR_MAX_THREADS=$THREAD_COUNT
export OMP_NUM_THREADS=$THREAD_COUNT
export MKL_NUM_THREADS=$THREAD_COUNT
export OPENBLAS_NUM_THREADS=$THREAD_COUNT
export VECLIB_MAXIMUM_THREADS=$THREAD_COUNT

tar -xf out/$TAR_NAME
cd $CURRENT_DIR

export PYTHONPATH="$WORKING_DIR:$PYTHONPATH"

echo "Running..."
echo

python3 $EXECUTABLE_PATH/act_run.py --run_name $RUN_NAME

if [ $? != 0 ]; then
    exit 1
fi

echo
echo "Done running!"
echo

cd ..

mv $CURRENT_DIR/out/* .

echo "Output files:"
ls -a

echo
END_TIME=$(date -u +%s)
ELAPSED=$(($END_TIME - $START_TIME))
echo "Total execution time: $ELAPSED seconds."
echo
echo "Finished!"
