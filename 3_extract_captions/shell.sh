#! /bin/sh

# src directory of pdf files
src_path="../vis_data/papers"
dst_path="./precomputed"
 
for file in ${src_path}/*
do  
    temp_file=`basename $file  .pdf`  
    ./pdffigures -j $dst_path/$temp_file $file
    echo $temp_file
done
