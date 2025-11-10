#!/usr/bin/env bash
# Launch mask generation workers in parallel (one process per domain).
# Each worker will run the adversarial generator for all hole percentages and attack percentages,
# but for a single domain. Logs and PIDs are saved under ./logs.

set -eu

# Configurable
PYTHON=${PYTHON:-.venv/bin/python3}
DOMAINS=(blocksworld logistics satellite zenotravel driverlog depots)
ATTACK_LEVELS=(5 10 15 20 30)
LOG_DIR=./logs/mask_generation
PIDS_DIR=./logs/pids
WORKER_SCRIPT=adversarial_gen/code/run_masks_worker.py
TMP_BASE_DIR=./tmp

mkdir -p "$LOG_DIR"
mkdir -p "$PIDS_DIR"

echo "Starting mask workers (one per domain): ${DOMAINS[*]}"
echo "Attack levels to generate: ${ATTACK_LEVELS[*]}"

worker_idx=1
for domain in "${DOMAINS[@]}"; do
    LOG_FILE="$LOG_DIR/mask_${domain}.log"
    PID_FILE="$PIDS_DIR/mask_${domain}.pid"
    TMP_DIR="${TMP_BASE_DIR}${worker_idx}"

    if [ -f "$PID_FILE" ]; then
        oldpid=$(cat "$PID_FILE")
        if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
            echo "Worker for domain $domain already running (pid=$oldpid). Skipping start."
            ((worker_idx++))
            continue
        else
            echo "Removing stale PID file $PID_FILE"
            rm -f "$PID_FILE"
        fi
    fi

    # Create unique temp directory for this worker
    mkdir -p "$TMP_DIR"

    echo "Launching worker for domain $domain (tmp: $TMP_DIR, logs: $LOG_FILE)"
    # Convert ATTACK_LEVELS array to space-separated string for arguments
    attack_args="${ATTACK_LEVELS[*]}"
    nohup "$PYTHON" "$WORKER_SCRIPT" --domains "$domain" --attacks $attack_args --tmp-dir "$TMP_DIR" < /dev/null > "$LOG_FILE" 2>&1 &
    pid=$!
    echo "$pid" > "$PID_FILE"
    disown "$pid" 2>/dev/null || true
    echo "  started pid=$pid (detached, using $TMP_DIR)"
    
    ((worker_idx++))
done

echo ""
echo "All workers launched. Each worker uses its own temp directory:"
worker_idx=1
for domain in "${DOMAINS[@]}"; do
    echo "  Worker $domain: ${TMP_BASE_DIR}${worker_idx}"
    ((worker_idx++))
done

echo ""
echo "To follow logs:"
for domain in "${DOMAINS[@]}"; do
    echo "  tail -f $LOG_DIR/mask_${domain}.log"
done

echo ""
echo "To stop a worker: kill \$(cat $PIDS_DIR/mask_<domain>.pid)"
echo "Example: kill \$(cat $PIDS_DIR/mask_blocksworld.pid)"

exit 0
