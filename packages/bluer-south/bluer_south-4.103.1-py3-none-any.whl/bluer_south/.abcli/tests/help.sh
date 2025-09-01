#! /usr/bin/env bash

function test_bluer_south_help() {
    local options=$1

    local module
    for module in \
        "@south" \
        \
        "@south pypi" \
        "@south pypi browse" \
        "@south pypi build" \
        "@south pypi install" \
        \
        "@south pytest" \
        \
        "@south test" \
        "@south test list" \
        \
        "bluer_south"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
