#!/usr/bin/env bash

STORE_DIR="${1:-hypergraph_store}"

clear
date

echo "=== STORE ==="
if [ -d "$STORE_DIR" ]; then
  du -sh "$STORE_DIR"
  find "$STORE_DIR" -type f | wc -l | awk '{print "files:", $1}'
else
  echo "$STORE_DIR not found yet"
fi

echo
echo "=== DISK ==="
df -h .

echo
echo "=== PYTHON PROCESS ==="
ps -o pid,etime,%cpu,%mem,rss,vsz,cmd -C python

echo
echo "=== MEMORY ==="
free -h

echo
echo "=== SWAP DETAIL ==="
swapon --show

echo
echo "=== LOAD ==="
uptime
