#!/bin/bash
for f in "topol.h" "elements.h" "strFuncts.h" \
         "debug.h" "scene.h" "palettes.h" "pybind/src/nvenn2.cpp"
do echo $f
g=$(basename $f)
if [[ -e ../../../gh/$f ]]
then
    if [[ -e $g ]]
    then
        echo "Target exists. Deleting existing link."
        rm $g
    fi
fi
echo "Creating new link."
ln ../../../gh/$f $g

done

