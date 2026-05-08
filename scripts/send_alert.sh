#!/bin/bash

SUBJECT="$1"
MESSAGE="$2"
MAIL_TO="$3"

echo "$MESSAGE" | mailx -s "$SUBJECT" "$MAIL_TO"
