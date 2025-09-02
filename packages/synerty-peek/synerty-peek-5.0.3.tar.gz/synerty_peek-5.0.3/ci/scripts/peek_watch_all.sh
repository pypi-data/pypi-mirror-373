#!/bin/bash


CMD='tail -n7 SED_PEEK_LOG_HOME/peek*/*.log;'
CMD="${CMD}"'echo;'
CMD="${CMD}"'echo;'

if which peek_cat_queues.sh > /dev/null
then
    CMD="${CMD}$(which peek_cat_queues.sh);"
fi

watch -n 5 "${CMD}"