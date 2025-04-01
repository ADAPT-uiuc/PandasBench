#! /bin/bash

nb_root=$1

if [ "$nb_root" == "" ]; then
    echo "Usage: $0 <notebook root>"
    exit
fi

if [ "${nb_root: -1}" == "/" ]; then
    nb_root="${nb_root:0:$((${#nb_root}-1))}"
fi

dirs=($(ls))
for dir in "${dirs[@]}"; do
    if [ "${dir}" == "copier.sh" ]; then
        continue
    fi
    subdir=$(ls $dir/)
    target_src=${dir}/${subdir}/input
    target_dest=${nb_root}/${target_src}
    cp -r $target_src $target_dest
    echo Copied ${target_src} to ${target_dest}
done
