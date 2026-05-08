#!/bin/bash

PING_RESULT=$(ping -c 2 google.com | tail -1)

echo "$PING_RESULT"
