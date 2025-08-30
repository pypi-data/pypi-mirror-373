#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

cd $HOME

LOG_AWK_ARGS='/^[0-9]{2}-[A-Za-z]{3}-[0-9]{4}/'
LOG_AWK_ARGS="${LOG_AWK_ARGS}"' {if (NR!=1) print "";} {printf "%s#n#", $0;}'



JC_AWK_ARGS='/^Traceback \(most recent call last\):/{f=1; print; next}'
JC_AWK_ARGS="${JC_AWK_ARGS}"' f && /^Traceback \(most recent call last\):/'
JC_AWK_ARGS="${JC_AWK_ARGS}"'{f=0; print; next} f{printf "%s", $0;'
JC_AWK_ARGS="${JC_AWK_ARGS}"' if(getline) printf "#n#"} END{print ""}'

DATE=$(date "+%y%m%d_%H%M")
DIR="peek_exception_collection/${DATE}"
mkdir -p $DIR
cd $DIR
find . -type f -delete || true

for SERVICE in logic worker agent field office
do
    logs="$(ls -tr $HOME/peek-${SERVICE}-service.log* 2> /dev/null)"
    if [ -z "${logs}" ]
    then
        echo "No logs for peek-${SERVICE}-service"
        continue
    fi

    # Extract logs
    for x in $logs
    do
        awk "${LOG_AWK_ARGS}" $x |
           grep -F 'Traceback (most recent call last)' |
           cut -c22- |
           sort -u |
           sed 's/#n#/\n/g' \
           >> ${SERVICE}.log.exceptions \
           || true
    done

    sudo journalctl -u peek_${SERVICE}.service |
        grep 'run_peek' |
        grep -v -e 'key=celery' \
              -e '(algorithms' \
              -e 'CryptographyDeprecationWarning' \
              -e 'peek_platform.util.LogUtil' \
              -e ']:[[:space:]]*$' |
        cut -c59-  \
        > ${SERVICE}.journalctl.exceptions \
       || true

done