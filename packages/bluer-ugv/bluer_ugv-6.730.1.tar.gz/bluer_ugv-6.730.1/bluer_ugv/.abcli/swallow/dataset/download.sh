#! /usr/bin/env bash

function bluer_ugv_swallow_dataset_download() {
    local options=$1
    local do_metadata=$(bluer_ai_option_int "$options" metadata 1)

    local download_options="-"
    [[ "$do_metadata" == 1 ]] &&
        download_options="filename=metadata.yaml"

    bluer_objects_download \
        $download_options \
        $BLUER_UGV_SWALLOW_DATASET_LIST
}
