#!/bin/sh

watchmedo auto-restart \
  --pattern *.py \
  --directory /io/superduper \
  --directory /io/slidge \
  --recursive \
  python -- -m slidge -c /etc/slidge/slidge.ini
