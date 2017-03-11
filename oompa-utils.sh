#
# oompa-utils.sh
#



function cd-to-first-src {
  # TODO: need to use $(tracker find ...)
  # jump to the first folder returned by find-in-src
  cd $(find-in-src $* | head -1 | awk '{ print $9 }')
}


OOMPA_ROOT=$HOME/oompa

#
# utils for summaries of tracker logs (find stupid git problems,
# summaries the updates, find untagged or poorly tagged projects)
#

OOMPA_TRACKER_LOGS=$OOMPA_ROOT/tracker-logs

function get-oompa-tracker-logs {

    local DATES=$*
    local DATE
    if [ -z "$DATES" ]; then
	DATES=$(date +%Y%m%d)
    fi

    for DATE in $DATES; do
	echo $OOMPA_TRACKER_LOGS/$DATE.tracker.log
    done
}


function tracker-find-git-problems {

    echo "tracker-find-git-problems"
    echo
    
    # note: in general, it should be possible to automatically address these
    for OOMPA_LOG_PATH in $(get-oompa-tracker-logs $*); do
	echo "$OOMPA_LOG_PATH"
	echo
	cat $OOMPA_LOG_PATH | grep --context=5 "result: 1"
	echo
    done
}




# report project, tag, and description from tracker logs
#   (esp, skip the detailed file updates)

# cat /Users/jeff/oompa/tracker-logs/20160915.tracker.log | grep 

function tracker-summarize-updates {
    for OOMPA_LOG_PATH in $(get-oompa-tracker-logs $*); do
	echo "$OOMPA_LOG_PATH"
	echo
	cat $OOMPA_LOG_PATH | grep --context=2 UPD
	echo
    done
}



#
# find pfojects that are still not tagged in project-tags.tsv
#
function tracker-find-no-tags {

    echo "tracker-find-no-tags"
    echo

    for OOMPA_LOG_PATH in $(get-oompa-tracker-logs $*); do
	echo "$OOMPA_LOG_PATH"
	echo
	cat $OOMPA_LOG_PATH | grep --context=1 "no tag"
	echo
    done
}

