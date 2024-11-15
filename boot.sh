#!/bin/bash

tmux new -s aatb -d

sleep 60

tmux new-window -n clock -t aatb:
tmux send-keys -t aatb:clock 'cd flip-clock' Enter
tmux send-keys -t aatb:clock 'python3 clock_digital.py' Enter
