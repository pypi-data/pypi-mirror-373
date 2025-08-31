#! /usr/bin/env bash

function bluer_ugv() {
    local task=${1:-version}

    bluer_ai_generic_task \
        plugin=bluer_ugv,task=$task \
        "${@:2}"
}

bluer_ai_log $(bluer_ugv version --show_icon 1)

bluer_ai_source_caller_suffix_path /ugv
