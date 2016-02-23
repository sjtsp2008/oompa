#
# oompa-utils.sh
#



function cd-to-first-src {
  # TODO: need to use $(tracker find ...)
  # jump to the first folder returned by find-in-src
  cd $(find-in-src $* | head -1 | awk '{ print $9 }')
}
