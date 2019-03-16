#!/usr/bin/env bash
set -eu
export AFL_SKIP_CPUFREQ=1

PYBIN=$(which python3)

TEST=$1

py-afl-fuzz \
	-i ${TEST}_input/ \
	-o ./fuzzout \
	-m 2000 \
	-- \
	$PYBIN ${TEST}.py
