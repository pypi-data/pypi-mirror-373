#!/usr/bin/env bash

set -o nounset
set -o errexit

if [ -n "$(echo 'false' | bash -l)" ]; then
    echo "ERROR, Your bash setup spits out extra text when it's run"
    exit -1
fi

# Make sure this script has all the environment setup
export PATH="$(dirname $(echo 'which python' | bash -l)):$PATH"

path=$(dirname $0)
cd $path

SRC_DIR="$path"
OUT_DIR="$path/doc_dist"
LINK_DIR="$path/doc_link"

rm -rf ${OUT_DIR}

# This function gets the path of any python packages we're watching
function modPath() {
    python <<EOPY
import os.path as p
import $1
dir = p.dirname($1.__file__)
# Convert it to bash if required
if dir[1] == ':':
    dir = '/' + dir[0] + dir[2:].replace('\\\\', '/')
print(dir)
EOPY
}

ARGS=""

# Run the command
ARGS="$ARGS --host 0.0.0.0"
ARGS="$ARGS --port 8041"
ARGS="$ARGS --watch ${LINK_DIR}"

# Add in any API docs
for x in $(cat $path/doc_link/plugin_api_list.txt); do
    ARGS="$ARGS --watch $(modPath $x)"
done

# Add the source and dest paths
ARGS="$ARGS ${SRC_DIR} ${OUT_DIR}"

echo "Running sphinx-autobuild with args :"
echo "$ARGS"

sphinx-autobuild $ARGS
