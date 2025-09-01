#! /usr/bin/env bash

function test_bluer_ugv_swallow_dataset_combine() {
    local options=$1

    local object_name=test_bluer_ugv_swallow_dataset_combine-$(bluer_ai_string_timestamp_short)

    bluer_ugv_swallow_dataset_combine \
        $options,count=2,~recent \
        $object_name
}
