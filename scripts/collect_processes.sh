#!/bin/bash


source "$(dirname "$0")/config.env"

ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head
