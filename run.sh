#!/bin/bash
cd /opt/avito_parser
export GOOGLE_APPLICATION_CREDENTIALS='./stok-ru-5c00d31fe9b2.json'
python3 main.py -c $1