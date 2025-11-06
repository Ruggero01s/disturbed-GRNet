#!/usr/bin/env bash
# Launch mask generation workers in parallel (one process per attack percentage).
# Each worker will run the adversarial generator for all configured domains/hole percentages,
# but using a single attack percentage. Logs and PIDs are saved under ./logs.

set -eu

# Configurable
PYTHON=${PYTHON:-.venv/bin/python3}
ATTACK_LEVELS=(10 20 30)
LOG_DIR=./logs/mask_generation
PIDS_DIR=./logs/pids
WORKER_SCRIPT=adversarial_gen/code/run_masks_worker.py

mkdir -p "$LOG_DIR"
mkdir -p "$PIDS_DIR"

echo "Starting mask workers: ${ATTACK_LEVELS[*]}"

for a in "${ATTACK_LEVELS[@]}"; do
    LOG_FILE="$LOG_DIR/mask_${a}.log"
    PID_FILE="$PIDS_DIR/mask_${a}.pid"

    if [ -f "$PID_FILE" ]; then
        oldpid=$(cat "$PID_FILE")
        if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
            echo "Worker for attack $a already running (pid=$oldpid). Skipping start."
            continue
        else
            echo "Removing stale PID file $PID_FILE"
            rm -f "$PID_FILE"
        fi
    fi

    echo "Launching worker for attack $a (logs: $LOG_FILE)"
    nohup "$PYTHON" "$WORKER_SCRIPT" --attack "$a" > "$LOG_FILE" 2>&1 &
    pid=$!
    echo "$pid" > "$PID_FILE"
    echo "  started pid=$pid"
done

echo "All workers launched. To follow logs:"
for a in "${ATTACK_LEVELS[@]}"; do
    echo "  tail -f $LOG_DIR/mask_${a}.log  # (or open in your editor)"
done

echo "To stop a worker: kill $(cat $PIDS_DIR/mask_<level>.pid)"

exit 0
