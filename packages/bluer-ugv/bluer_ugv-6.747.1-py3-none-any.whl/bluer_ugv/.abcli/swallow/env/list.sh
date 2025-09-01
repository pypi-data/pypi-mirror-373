#! /usr/bin/env bash

function bluer_ugv_swallow_env_list() {
    pushd $abcli_path_assets/env/ >/dev/null
    bluer_objects_ls swallow-raspbian-*.env
    popd >/dev/null
}
