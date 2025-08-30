#coding: utf-8
import os

from npu_compiler.v150.config import Config
from npu_compiler.v150.compiler import run

def compile_model(config_file):
    Config.parse_config(config_file, {"QUIET":True})
    Config.check_config()
    run()

