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
TMP_BASE_DIR=./tmp

mkdir -p "$LOG_DIR"
mkdir -p "$PIDS_DIR"

echo "Starting mask workers: ${ATTACK_LEVELS[*]}"

worker_idx=1
for a in "${ATTACK_LEVELS[@]}"; do
    LOG_FILE="$LOG_DIR/mask_${a}.log"
    PID_FILE="$PIDS_DIR/mask_${a}.pid"
    TMP_DIR="${TMP_BASE_DIR}${worker_idx}"

    if [ -f "$PID_FILE" ]; then
        oldpid=$(cat "$PID_FILE")
        if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
            echo "Worker for attack $a already running (pid=$oldpid). Skipping start."
            ((worker_idx++))
            continue
        else
            echo "Removing stale PID file $PID_FILE"
            rm -f "$PID_FILE"
        fi
    fi

    # Create unique temp directory for this worker
    mkdir -p "$TMP_DIR"

    echo "Launching worker for attack $a (tmp: $TMP_DIR, logs: $LOG_FILE)"
    nohup "$PYTHON" "$WORKER_SCRIPT" --attack "$a" --tmp-dir "$TMP_DIR" < /dev/null > "$LOG_FILE" 2>&1 &
    pid=$!
    echo "$pid" > "$PID_FILE"
    disown "$pid" 2>/dev/null || true
    echo "  started pid=$pid (detached, using $TMP_DIR)"
    
    ((worker_idx++))
done

echo ""
echo "All workers launched. Each worker uses its own temp directory:"
worker_idx=1
for a in "${ATTACK_LEVELS[@]}"; do
    echo "  Worker $a%: ${TMP_BASE_DIR}${worker_idx}"
    ((worker_idx++))
done

echo ""
echo "To follow logs:"
for a in "${ATTACK_LEVELS[@]}"; do
    echo "  tail -f $LOG_DIR/mask_${a}.log"
done

echo ""
echo "To stop a worker: kill \$(cat $PIDS_DIR/mask_<level>.pid)"

exit 0
