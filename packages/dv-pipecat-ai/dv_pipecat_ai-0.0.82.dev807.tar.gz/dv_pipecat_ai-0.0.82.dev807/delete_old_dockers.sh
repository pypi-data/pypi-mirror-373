#!/bin/bash

# Set to true for dry run (just show what would be deleted)
DRY_RUN=false

if [ "$DRY_RUN" = true ]; then
    echo "The following containers would be deleted:"
    docker ps -a --format '{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Command}}' | \
        grep 'Exited' | \
        grep 'python server.py'
else
    echo "Deleting containers..."
    docker ps -a --format '{{.ID}} {{.Status}} {{.Command}}' | \
        awk '/Exited.*python server.py/ {print \$1}' | \
        xargs -r docker rm
    echo "Done!"
fi