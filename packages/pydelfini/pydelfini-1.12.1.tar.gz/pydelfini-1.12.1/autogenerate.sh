#!/bin/bash

set -e
cd "$(dirname "$0")"

if [[ ! -e venv/bin/activate ]]; then
    python3 -m venv venv
    . venv/bin/activate
    pip install -e '.[dev]'
else
    . venv/bin/activate
fi

### Update the delfini_core low level client library

qpushd() {
    if [[ -n $1 ]]; then
        pushd $1 >/dev/null
    else
        popd > /dev/null
    fi
}

checksumdir() {
    MD5=$(which md5 md5sum || true)
    find $1 -type f -exec $MD5 '{}' \; | $MD5
}
CURRENT_SUM=$(checksumdir pydelfini/delfini_core)

qpushd pydelfini

# Preserve hand-edited files
DELFINI_CORE="$PWD/delfini_core"
TMPF=$(mktemp)
qpushd delfini_core; tar cf $TMPF .opcignore $(< .opcignore); qpushd
restore_ignored() {
    echo "Restoring .opcignore files..."
    qpushd $DELFINI_CORE
    tar xf $TMPF
    rm $TMPF
    qpushd

    NEW_SUM=$(checksumdir pydelfini/delfini_core)
    if [[ $CURRENT_SUM != $NEW_SUM ]]; then
        echo
        echo "Changed:"
        git status --porcelain pydelfini/delfini_core
        exit 1
    fi
}
trap restore_ignored EXIT

# dereference requestBody and parameters
# this is necessary because of:
# - https://github.com/openapi-generators/openapi-python-client/issues/605
# - https://github.com/openapi-generators/openapi-python-client/issues/595

PROCESSED_API=$(mktemp)
python - $PROCESSED_API <<"EOF"
import sys, yaml, copy

doc = yaml.safe_load(open('../../../delfini-api.yaml'))

def deref(top, path):
    assert path.startswith('#/')
    x = top
    for component in path.split('/')[1:]:
        x = x[component]
    return copy.deepcopy(x)

for path_key, path in doc['paths'].items():
    if 'parameters' in path:
        for i in range(len(path['parameters'])):
            if '$ref' not in path['parameters'][i]:
                continue
            ref = path['parameters'][i]['$ref']
            path['parameters'][i] = deref(doc, ref)

    for method_key, method in path.items():
        if method_key == 'parameters':
            continue
        if 'parameters' in method:
            for i in range(len(method['parameters'])):
                if '$ref' not in method['parameters'][i]:
                    continue
                ref = method['parameters'][i]['$ref']
                method['parameters'][i] = deref(doc, ref)

        if 'requestBody' in method and '$ref' in method['requestBody']:
            method['requestBody'] = deref(doc, method['requestBody']['$ref'])

        for k in method['responses']:
            if '$ref' in method['responses'][k]:
                method['responses'][k] = deref(doc, method['responses'][k]['$ref'])

with open(sys.argv[1], 'w') as fp:
    fp.write(yaml.dump(doc))

EOF

openapi-python-client update \
                      --path $PROCESSED_API \
                      --config ../.openapi-python-client/config.yaml \
                      --meta none \
                      --custom-template-path ../.openapi-python-client/templates

rm $PROCESSED_API

qpushd
