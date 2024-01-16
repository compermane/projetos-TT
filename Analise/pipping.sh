#!/bin/bash

venv_name=$1
requirements_file=$2

cd $venv_name
source ./bin/activate

pip install -r $requirements_file