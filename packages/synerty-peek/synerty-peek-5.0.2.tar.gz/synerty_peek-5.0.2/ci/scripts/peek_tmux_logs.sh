#!/bin/bash

# Peek Services Log Monitor - Tmux Setup Script
# Usage: ssh -t peek@hostname ./peek-tmux-logs.sh
# Creates a 2x2 tmux session monitoring different Peek service logs

SESSION_NAME="peek-logs"
LOG_DIR="SED_PEEK_LOG_HOME"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed"
    exit 1
fi

# Kill existing session if it exists (ignore errors)
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Create new session (this will start tmux server automatically)
tmux new-session -d -s "$SESSION_NAME"
tmux split-window -h -p 50

tmux split-window -v -f -p 50
tmux split-window -h -p 50

tmux split-window -v -f -p 50
tmux split-window -h -p 50

# This is the top and p_cat_queues
tmux split-window -v -f -l 15
tmux split-window -h -p 40
tmux split-window -h -p 50


# Start log tailing in the top 4 panes (full logs)
# Remove the datews and times, thess are tails. so they are now, and we need the space
tmux send-keys -t "$SESSION_NAME:0.0" "tail -F $LOG_DIR/peek-logic/peek-logic.log | cut -f3- -d' '" Enter
tmux send-keys -t "$SESSION_NAME:0.1" "tail -F $LOG_DIR/peek-agent/peek-agent.log | cut -f3- -d' '" Enter
tmux send-keys -t "$SESSION_NAME:0.2" "tail -F $LOG_DIR/peek-worker/peek-worker.log | cut -f3- -d' '" Enter
tmux send-keys -t "$SESSION_NAME:0.3" "tail -F $LOG_DIR/peek-office/peek-office.log | cut -f3- -d' '" Enter

# Start ERROR-only log tailing in the bottom parts of each log pane

ALL_LOGS=" $LOG_DIR/peek-logic/peek-logic.log"
ALL_LOGS="$ALL_LOGS $LOG_DIR/peek-agent/peek-agent.log"
ALL_LOGS="$ALL_LOGS $LOG_DIR/peek-worker/peek-worker.log"
ALL_LOGS="$ALL_LOGS $LOG_DIR/peek-office/peek-office.log"

tmux send-keys -t "$SESSION_NAME:0.4" "clear; tail -F -n 0 $ALL_LOGS | grep ERROR" Enter

# 0.5, empty terminal

# Start nmon in bottom left pane, fallback to top if nmon not available
tmux send-keys -t "$SESSION_NAME:0.6" "top -c -u peek" Enter

# Start watch command in bottom right pane
tmux send-keys -t "$SESSION_NAME:0.7" "watch -d -n10 'df -h | grep -v -e tmpfs -e efivar'" Enter

# Start watch command in bottom right pane
tmux send-keys -t "$SESSION_NAME:0.8" "watch -d -n10 peek_cat_queues.sh" Enter

# Rename window
tmux rename-window -t "$SESSION_NAME:0" "Peek-Logs"

# Setup the configuration
tmux set -g mouse on
tmux set -g escape-time 0
tmux set -g display-time 2000
tmux set -g status-interval 5

# Add hostname to status line
tmux set -g status-left "[#H] "
tmux set -g status-left-length 20

# Attach to session
tmux attach-session -t "$SESSION_NAME"

