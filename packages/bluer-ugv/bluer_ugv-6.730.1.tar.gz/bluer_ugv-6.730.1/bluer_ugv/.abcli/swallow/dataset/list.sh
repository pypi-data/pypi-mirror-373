#! /usr/bin/env bash

function bluer_ugv_swallow_dataset_list() {
    local options=$1
    local do_download=$(bluer_ai_option_int "$options" download 1)

    if [[ "$do_download" == 1 ]]; then
        bluer_ugv_swallow_dataset_download
        [[ $? -ne 0 ]] && return 1
    fi

    bluer_objects_metadata_get \
        key=dataset-list,object \
        $BLUER_UGV_SWALLOW_DATASET_LIST
}
