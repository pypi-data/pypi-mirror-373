#! /usr/bin/env bash

function bluer_ugv_swallow_select_target() {
    bluer_ai_eval dryrun=$do_dryrun \
        python3 -m bluer_ugv.swallow \
        select_target \
        "$@"
}
