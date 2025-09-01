#! /usr/bin/env bash

function bluer_ugv_swallow_dataset_combine() {
    local options=$1
    local do_download=$(bluer_ai_option_int "$options" download 1)
    local do_upload=$(bluer_ai_option_int "$options" upload 0)
    local count=$(bluer_ai_option "$options" count -1)
    local recent=$(bluer_ai_option_int "$options" recent 1)
    local sequence=$(bluer_ai_option "$options" sequence -1)
    local split=$(bluer_ai_option_int "$options" split 1)

    local object_name=$(bluer_ai_clarify_object $2 swallow-dataset-$(bluer_ai_string_timestamp_short))

    bluer_ai_eval - \
        python3 -m bluer_ugv.swallow.dataset \
        combine \
        --count $count \
        --download $do_download \
        --object_name $object_name \
        --recent $recent \
        --sequence $sequence \
        --split $split \
        "${@:3}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $object_name

    return 0
}
