#!/usr/bin/env bash
cd "$(dirname "$0")"
hatch clean; 
gitnextver .; 
hatch build; 
