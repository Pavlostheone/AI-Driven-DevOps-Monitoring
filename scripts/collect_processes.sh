#!/bin/bash

ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head
