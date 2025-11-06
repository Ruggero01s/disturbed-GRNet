#!/usr/bin/env bash
# Stop all mask generation workers and clean up temp directories

set -eu

PIDS_DIR=./logs/pids
TMP_BASE_DIR=./tmp

echo "Stopping mask generation workers..."

if [ ! -d "$PIDS_DIR" ]; then
    echo "No PID directory found. No workers to stop."
    exit 0
fi

stopped=0
failed=0

for pidfile in "$PIDS_DIR"/mask_*.pid; do
    if [ ! -f "$pidfile" ]; then
        continue
    fi
    
    pid=$(cat "$pidfile")
    attack_level=$(basename "$pidfile" | sed 's/mask_\(.*\)\.pid/\1/')
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "Stopping worker for attack $attack_level (pid=$pid)..."
        if kill "$pid" 2>/dev/null; then
            ((stopped++))
            echo "  ✓ Stopped"
        else
            ((failed++))
            echo "  ✗ Failed to stop (try: kill -9 $pid)"
        fi
    else
        echo "Worker for attack $attack_level (pid=$pid) is not running"
    fi
    
    # Remove PID file
    rm -f "$pidfile"
done

echo ""
echo "Cleaning up temporary directories..."
for i in 1 2 3; do
    tmpdir="${TMP_BASE_DIR}${i}"
    if [ -d "$tmpdir" ]; then
        echo "  Removing $tmpdir..."
        rm -rf "$tmpdir"
    fi
done

echo ""
echo "Summary:"
echo "  Workers stopped: $stopped"
if [ $failed -gt 0 ]; then
    echo "  Failed to stop: $failed"
fi
echo ""
echo "Cleanup complete!"

exit 0
