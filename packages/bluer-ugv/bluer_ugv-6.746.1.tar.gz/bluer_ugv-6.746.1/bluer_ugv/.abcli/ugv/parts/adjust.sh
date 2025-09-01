#! /usr/bin/env bash

function bluer_ugv_parts_adjust() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    bluer_ai_eval - \
        python3 -m bluer_ugv.parts \
        adjust \
        --dryrun $do_dryrun \
        "${@:2}"
}
