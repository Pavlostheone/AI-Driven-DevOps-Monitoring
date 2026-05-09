#!/bin/bash
if docker info >/dev/null 2>&1; then
    echo "Docker is running"
else
    echo "Docker is DOWN"
fi
