#! /usr/bin/env bash

function bluer_ugv_swallow() {
    local task=$1

    local function_name=bluer_ugv_swallow_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 - bluer_ugv.swallow "$@"
}

bluer_ai_source_caller_suffix_path /swallow
