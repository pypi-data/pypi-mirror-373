#! /usr/bin/env bash

function test_bluer_ugv_swallow_dataset_download_upload() {
    local options=$1

    bluer_ugv_swallow_dataset_download
    [[ $? -ne 0 ]] && return 1

    bluer_ugv_swallow_dataset_upload
}
