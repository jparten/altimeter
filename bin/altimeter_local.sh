#!/usr/bin/env bash

set -ef -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ALTI_DIR=$(dirname "$SCRIPT_DIR")
export PYTHONPATH="$PYTHONPATH:$ALTI_DIR"

pushd $ALTI_DIR >/dev/null
trap 'popd >/dev/null' EXIT

# trick to use fd5 and tee to output the full output to console while
# also saving the last line (which is the json filepaths used by the next
# process) in a var.
exec 5>&1
json_path=$("bin/aws2json.py" $@ | tee /dev/fd/5 | tail -n1)
echo "Created JSON $json_path"
rdf_path=$(dirname "$json_path")/graph.rdf
bin/json2rdf.py "$json_path" "$rdf_path"
echo "Created RDF $rdf_path"

