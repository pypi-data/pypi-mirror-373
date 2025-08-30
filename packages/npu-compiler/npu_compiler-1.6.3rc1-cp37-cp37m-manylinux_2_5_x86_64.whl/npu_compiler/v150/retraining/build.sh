#!/bin/bash
TF_CFLAGS=( $(python -c 'import tensorflow as tf; print(" ".join(tf.sysconfig.get_compile_flags()))') )
TF_LFLAGS=( $(python -c 'import tensorflow as tf; print(" ".join(tf.sysconfig.get_link_flags()))') )

echo "compile gxnpuop.cc to .so lib"
#g++ -std=c++11 -Wno-pointer-arith -fpermissive -O0 -g -shared gxnpuop.cc -o gxnpuop.so -fPIC ${TF_CFLAGS[@]} ${TF_LFLAGS[@]}
g++ -std=c++11 -Wno-pointer-arith -fpermissive -Wno-unused-result -O2 -shared gxnpuop.cc -o gxnpuop.so -fPIC ${TF_CFLAGS[@]} ${TF_LFLAGS[@]}
