#! /usr/bin/env bash

function test_bluer_ugv_swallow_dataset_combine_explicit() {
    local options=$1

    local object_name=test_bluer_ugv_swallow_dataset_combine-$(bluer_ai_string_timestamp_short)

    bluer_ugv_swallow_dataset_combine \
        $options, \
        $object_name \
        --datasets 2025-07-09-10-59-15-x9eemj,2025-07-09-11-02-42-m4b3is
}
