#!/usr/bin/env bash
# Quick script to check status of all mask generation workers
# Launch all 6 domain workers in parallel
# ./run_masks_parallel.sh

# # Check the status of all workers
# ./check_mask_workers.sh

# # Follow logs for a specific domain
# tail -f logs/mask_generation/mask_blocksworld.log
# tail -f logs/mask_generation/mask_logistics.log
# tail -f logs/mask_generation/mask_satellite.log
# tail -f logs/mask_generation/mask_zenotravel.log
# tail -f logs/mask_generation/mask_driverlog.log
# tail -f logs/mask_generation/mask_depots.log

# # Stop a specific worker
# kill $(cat logs/pids/mask_blocksworld.pid)

# # Stop all workers
# for domain in blocksworld logistics satellite zenotravel driverlog depots; do
#     kill $(cat logs/pids/mask_${domain}.pid) 2>/dev/null
# done


PIDS_DIR=./logs/pids
DOMAINS=(blocksworld logistics satellite zenotravel driverlog depots)

echo "Mask Generation Workers Status"
echo "==============================="
echo ""

running_count=0
stopped_count=0

for domain in "${DOMAINS[@]}"; do
    PID_FILE="$PIDS_DIR/mask_${domain}.pid"
    
    if [ ! -f "$PID_FILE" ]; then
        echo "[$domain] No PID file (never started)"
        ((stopped_count++))
        continue
    fi
    
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo "[$domain] ✓ RUNNING (pid=$pid)"
        ((running_count++))
    else
        echo "[$domain] ✗ STOPPED (pid=$pid)"
        ((stopped_count++))
    fi
done

echo ""
echo "Summary: $running_count running, $stopped_count stopped"
echo ""

if [ $running_count -gt 0 ]; then
    echo "To follow logs:"
    for domain in "${DOMAINS[@]}"; do
        PID_FILE="$PIDS_DIR/mask_${domain}.pid"
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                echo "  tail -f ./logs/mask_generation/mask_${domain}.log"
            fi
        fi
    done
fi
