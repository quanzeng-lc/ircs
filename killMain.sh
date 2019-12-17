#! /bin/bash
echo `ps -ef | grep 'python main.py'`
`ps -ef | grep 'python main.py' | grep -v 'ii' | awk '{print $2}' | xargs kill -9`
