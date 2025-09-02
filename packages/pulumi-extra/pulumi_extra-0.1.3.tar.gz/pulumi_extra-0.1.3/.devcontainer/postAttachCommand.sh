#!/usr/bin/env bash

sudo chown --recursive "$(id --user):$(id --group)" ~

make install
