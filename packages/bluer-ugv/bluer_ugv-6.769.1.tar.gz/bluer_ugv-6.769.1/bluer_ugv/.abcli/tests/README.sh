#! /usr/bin/env bash

function test_bluer_ugv_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_ugv build_README
}
