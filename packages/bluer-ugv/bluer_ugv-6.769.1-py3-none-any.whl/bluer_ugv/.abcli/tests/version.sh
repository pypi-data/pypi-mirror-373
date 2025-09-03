#! /usr/bin/env bash

function test_bluer_ugv_version() {
    local options=$1

    bluer_ai_eval ,$options \
        "bluer_ugv version ${@:2}"
}
