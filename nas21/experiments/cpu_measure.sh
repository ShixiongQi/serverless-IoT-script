#!/bin/bash

echo "========= Check whether mpstat is installed ========="
if command -v mpstat >/dev/null 2>&1; then
    echo 'mpstat installed'
else
    echo 'Please install mpstat: sudo apt install sysstat'
    exit 1
fi

echo "========= Check whether bc is installed ========="
if command -v bc >/dev/null 2>&1; then
    echo 'bc installed'
else
    echo 'Please install bc: sudo apt-get install -y bc'
    exit 1
fi

# Run mpstat to collect CPU percentage
echo 'Collect CPU usage for '${1}' seconds'
mpstat_result=$(mpstat ${1} 1 | tail -1)
# Setting space as spliter 
IFS=' '
# Reading mpstat_result as an array as tokens separated by IFS
read -ra cpu_usage <<<"$mpstat_result" 
# echo "${cpu_usage[-1]}"
cpu_upper_limit=100
cpu_idle=$(echo ${cpu_usage[-1]} | bc -l)
total_cpu=$(echo "$cpu_upper_limit - $cpu_idle" | bc)
echo "CPU usage: $total_cpu"