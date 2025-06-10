#!/bin/sh
# A script which runs the app locally just for testing purposes.
# It will restart the app if it crashes, and it will exit if the user presses Ctrl-C.

# Function to cleanup on exit
cleanup() {
    if [ -n "$python_pid" ]; then
        echo "Cleaning up..."
        kill $python_pid 2>/dev/null || true
    fi
    exit 0
}

# Set up trap for Ctrl-C
trap cleanup INT

# substitute for read -n which does not exist in a simple sh
read_char() {
    prompt="$1"
    printf "%s" "$prompt"

    oldstty=$(stty -g)
    stty -icanon -echo min 1 time 0
    key=$(dd bs=1 count=1 2>/dev/null)
    stty "$oldstty"

    printf "%s" "$key"
}

# Track startup crashes
startup_crashes=0
startup_crash_limit=3

while true; do
    # Start the Python process in background and capture its PID
    .venv/bin/python -m src.main &
    python_pid=$!
    
    # Wait for 20 seconds to check for early crashes
    sleep_count=0
    while [ $sleep_count -lt 20 ]; do
        # Check if process is still running
        if ! kill -0 $python_pid 2>/dev/null; then
            echo "App crashed during startup (within 20 seconds)"
            startup_crashes=$((startup_crashes + 1))
            
            if [ $startup_crashes -ge $startup_crash_limit ]; then
                echo "App crashed $startup_crash_limit times during startup. Exiting."
                exit 1
            fi
            
            echo "Attempting restart ($startup_crashes of $startup_crash_limit)..."
            continue 2
        fi
        sleep 1
        sleep_count=$((sleep_count + 1))
    done
    
    # Wait for the Python process to finish
    wait $python_pid
    exit_code=$?

    # Reset startup crash counter if we got past the startup phase
    startup_crashes=0

    if [ "$exit_code" -ne 0 ]; then
        echo "App crashed (exit code $exit_code)"
        if [ "$exit_code" -eq 130 ]; then
            echo "Ctrl+C detected, exiting..."
            exit 0
        fi
        continue
    fi

    while true; do
        key=$(read_char "Press [r] to restart, [q] to quit:")
        case "$key" in
            r|R)
                echo "Manual restart..."
                break
                ;;
            q|Q)
                echo "Quitting."
                exit 0
                ;;
            *)
                echo "Invalid input. Press [r] to restart or [q] to quit."
                ;;
        esac
    done
done

