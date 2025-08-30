#coding: utf-8

from npu_compiler.v100.config import Config
from npu_compiler.v100.compiler import run

def compile_npu(pb_file, config_file):
    Config.parse_config(config_file, {"VERBOSE":False})
    Config.check_config()
    run()

