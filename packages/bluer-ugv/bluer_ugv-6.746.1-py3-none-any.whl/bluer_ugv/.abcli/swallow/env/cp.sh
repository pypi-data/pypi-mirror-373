#! /usr/bin/env bash

function bluer_ugv_swallow_env_cp() {
    bluer_ai_env_dot_cp swallow-raspbian-${1:-driving}
    [[ $? -ne 0 ]] && return 1

    bluer_sbc init
}
