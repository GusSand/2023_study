#!/usr/bin/env bats

setup() {
    make
}

setup

@test "1 - Evaluating linked list" {
    eval "run ./unittests.exp"
    echo $output

#    [[ "$status" -eq 0 ]]
#    [[ "$output" == "This worked" ]]
    
}