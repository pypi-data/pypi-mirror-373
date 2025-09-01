#! /usr/bin/env bash

function test_bluer_south_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_south build_README
}
