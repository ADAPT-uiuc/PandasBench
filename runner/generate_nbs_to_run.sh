#! /bin/bash

nb_root=$1

if [ "$nb_root" == "" ]; then
    echo "Usage: $0 <notebook root>"
    exit
fi

if [ "${nb_root: -1}" == "/" ]; then
    nb_root="${nb_root:0:$((${#nb_root}-1))}"
fi

output_file=nbs_to_run.py

dirs=($(ls $nb_root))
echo "notebooks = [" > ${output_file}
for dir in "${dirs[@]}"; do
    subdir=$(ls ${nb_root}/${dir})
    echo "  ('"${dir}/${subdir}"', 1.0)," >> ${output_file}
done

echo "]" >> ${output_file}
