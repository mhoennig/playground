#!/bin/sh

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

while true; do
    .venv/bin/python interview.py
    exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        echo "App crashed (exit code $exit_code), restarting ..."
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

