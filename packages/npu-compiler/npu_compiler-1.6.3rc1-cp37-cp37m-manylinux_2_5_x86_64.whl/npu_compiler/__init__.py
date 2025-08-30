#coding: utf-8

import os
os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # 0: 所有消息 (默认) 1: 屏蔽 INFO 2: 屏蔽 INFO + WARNING 3: 屏蔽 INFO + WARNING + ERROR

import sys
from collections import OrderedDict
from prettytable import PrettyTable

# 编译器版本
VERSION = "1.6.3rc1"

class NpuVersionManagerHelper(object):
    core_supports = OrderedDict([
        ("LEO"   , {
            "frameworks" : ("TF",),
            "fw_versions" : {
                "TF" : ((1,10), (1,11), (1,12), (1,13), (1,14), (1,15)),
                },
            "alias": "V100",
            "has_quant": False,
            "config_module": "npu_compiler.v100.config",
            "compiler_module": "npu_compiler.v100.compiler",
            "factories_module": {
                "TF":"npu_compiler.v100.ops",
                },
            }
        ),
        ("GRUS"  , {
            "frameworks" : ("TF", "PT"),
            "fw_versions" : {
                "TF" : ((1,10), (1,11), (1,12), (1,13), (1,14), (1,15)),
                "PT" : ((1,10), (1,11), (1,12), (1,13))
                },
            "alias": "V150",
            "has_quant": False,
            "config_module": "npu_compiler.v150.config",
            "compiler_module": "npu_compiler.v150.compiler",
            "factories_module": {
                "TF":"npu_compiler.v150.tf_ops",
                "PT":"npu_compiler.v150.pt_ops",
                },
            }
        ),
        ("APUS"  , {
            "frameworks" : ("TF", "PT"),
            "fw_versions" : {
                "TF" : ((1,10), (1,11), (1,12), (1,13), (1,14), (1,15)),
                "PT" : ((1,12), (1,13))
                },
            "alias": "V120",
            "has_quant": True,
            "config_module": "npu_compiler.v120.config",
            "compiler_module": "npu_compiler.v120.compiler",
            "factories_module": {
                "TF":"npu_compiler.v120.tf_ops",
                "PT":"npu_compiler.v120.pt_ops",
                },
            }
        ),
        ("FORNAX", {
            "frameworks" : ("TF", "PT"),
            "fw_versions" : {
                "TF" : ((1,10), (1,11), (1,12), (1,13), (1,14), (1,15)),
                "PT" : ((1,12), (1,13))
                },
            "alias": "V122",
            "has_quant": True,
            "config_module": "npu_compiler.v122.config",
            "compiler_module": "npu_compiler.v122.compiler",
            "factories_module": {
                "TF":"npu_compiler.v122.tf_ops",
                "PT":"npu_compiler.v122.pt_ops",
                },
            }
        ),
        ("AQUILA", {
            "frameworks" : ("TF",),
            "fw_versions" : {
                "TF" : ((1,10), (1,11), (1,12), (1,13), (1,14), (1,15)),
                },
            "alias": "V180",
            "has_quant": True,
            "config_module": "npu_compiler.v180.config",
            "compiler_module": "npu_compiler.v180.compiler",
            "factories_module": {
                "TF":"npu_compiler.v180.ops",
                },
            }
        ),
    ])

    py_supports = OrderedDict([
        ((3, 6), ("TF",)),
        ((3, 7), ("TF", "PT")),
        ((3, 8), ("PT",)),
    ])

    @classmethod
    def get_pt_support_cores_pt_versions(cls):
        # 获取每个core支持哪几个pytorch版本
        cores = OrderedDict([])
        for core, core_info in cls.core_supports.items():
            if "PT" in core_info["frameworks"]:
                cores[core] = core_info["fw_versions"]["PT"]
        return cores

    @classmethod
    def get_pt_support_py_version(cls):
        # 支持pytorch的python版本
        py_versions = []
        for py_version, fws in cls.py_supports.items():
            if "PT" in fws:
                py_versions.append(py_version)
        return py_versions

    @classmethod
    def get_core_funcs(cls):
        # 获取每个core的加载、编译、量化函数
        core_funcs = OrderedDict([])
        for core, core_info in cls.core_supports.items():
            config_module_name = core_info["config_module"]
            config_module = __import__(config_module_name, fromlist=["Config"])
            config_class = getattr(config_module, "Config")

            compiler_module_name = core_info["compiler_module"]
            if core_info["has_quant"]:
                compiler_func_list = ["run", "quant"]
            else:
                compiler_func_list = ["run"]
            compiler_module = __import__(compiler_module_name, fromlist=compiler_func_list)

            core_funcs[core] = {
                    "load": config_class.load_config,
                    "run": getattr(compiler_module, "run"),
                    }
            if core_info["has_quant"]:
                core_funcs[core]["quant"] = getattr(compiler_module, "quant")
            if core_info["alias"]:
                core_funcs[core_info["alias"]] = core_funcs[core]
        return core_funcs

    @classmethod
    def get_supported_frameworks(cls):
        # 获取支持的机器学习框架
        supported_frameworks = set()
        for frameworks in cls.py_supports.values():
            supported_frameworks.update(set(frameworks))
        return list(supported_frameworks)

    @classmethod
    def get_supported_cores(cls, with_alias):
        # 获取支持的core名称
        supported_cores = []
        for core, core_info in cls.core_supports.items():
            supported_cores.append(core)
            if with_alias and core_info["alias"]:
                supported_cores.append(core_info["alias"])
        return supported_cores

    @classmethod
    def get_supported_core_frameworks(cls):
        # 获取每个core支持哪几个机器学习框架
        supported_core_frameworks = OrderedDict([])
        for core, core_info in cls.core_supports.items():
            supported_core_frameworks[core] = core_info["frameworks"]
        return supported_core_frameworks

    @classmethod
    def get_supported_factories(cls, py_version):
        # 获取每个core的机器学习框架的ops工厂类
        py_supported_frameworks = cls.py_supports[py_version]
        supported_factories = {}
        for core, core_info in cls.core_supports.items():
            supported_factories[core] = {}
            for framework, factory_module_name in core_info["factories_module"].items():
                if framework in py_supported_frameworks:
                    factory_module = __import__(factory_module_name, fromlist=["OpsFactory"])
                    factory_class = getattr(factory_module, "OpsFactory")
                    supported_factories[core][framework] = factory_class
        return supported_factories

    @classmethod
    def get_core_with_quant(cls):
        # 获取需要跑量化推理的core名
        core_with_quant = []
        for core, core_info in cls.core_supports.items():
            if core_info["has_quant"]:
                core_with_quant.append(core)
        return core_with_quant

    @classmethod
    def get_supported_py_versions(cls):
        return cls.py_supports.keys()

    @classmethod
    def get_supported_py_frameworks(cls):
        return cls.py_supports


class NpuVersionManager(object):
    # 编译器支持的芯片版本名称
    SUPPORT_CORE_VERSION = NpuVersionManagerHelper.get_supported_cores(True)
    # 编译器目前支持的前端深度学习框架
    SUPPORT_FRAMEWORKS   = NpuVersionManagerHelper.get_supported_frameworks()

    @classmethod
    def get_npu_funcs_dict(cls):
        return NpuVersionManagerHelper.get_core_funcs()

    @classmethod
    def get_core_with_quant(cls):
        core_with_quant = NpuVersionManagerHelper.get_core_with_quant()
        return ",".join(core_with_quant)

    @classmethod
    def get_ops_table_dict(cls):
        """
        ops_table_dict:
        {
            "LEO":    {"TF":  [OpsFactory_1_0_tf],
                       "ALL": [OpsFactory_1_0_tf]},
            "APUS":   {"TF":  [OpsFactory_1_2_tf],
                       "PT":  [OpsFactory_1_2_pt],
                       "ALL": [OpsFactory_1_2_tf, OpsFactory_1_2_pt]},
            "ALL":    {"TF":  [OpsFactory_1_0_tf, OpsFactory_1_2_tf],
                       "PT":  [OpsFactory_1_2_pt],
                       "ALL": [OpsFactory_1_0_tf, OpsFactory_1_2_tf, OpsFactory_1_2_pt]},
        }
        """
        supportied_factories = NpuVersionManagerHelper.get_supported_factories(EnvironmentChecker.get_python_version())
        ops_table_dict = {}
        ops_table_dict["ALL"] = {}
        ops_table_dict["ALL"]["ALL"] = []
        for core, core_info in supportied_factories.items():
            ops_table_dict[core] = {}
            ops_table_dict[core]["ALL"] = []
            for framework, factory in core_info.items():
                ops_table_dict[core][framework] = [factory]
                ops_table_dict[core]["ALL"].append(factory)
                if framework not in ops_table_dict["ALL"]:
                    ops_table_dict["ALL"][framework] = []
                ops_table_dict["ALL"][framework].append(factory)
                ops_table_dict["ALL"]["ALL"].append(factory)
        return ops_table_dict

    @classmethod
    def get_env_compatibility_info(cls):
        supported_core_frameworks = NpuVersionManagerHelper.get_supported_core_frameworks()

        first_row_value   = ["PYTHON VERSION(COL) \ CORE_VERSION(ROW)"]
        first_row_value.extend(NpuVersionManagerHelper.get_supported_cores(False))
        table = PrettyTable(first_row_value)
        for python_version, python_frameworks in NpuVersionManagerHelper.get_supported_py_frameworks().items():
            row_value = [python_version]
            for core_frameworks in supported_core_frameworks.values():
                supported_frameworks = set(python_frameworks) & set(core_frameworks)
                row_value.append(list(supported_frameworks))
            table.add_row(row_value)

        for value in first_row_value:
            table.align[value] = "c"
        return table


class EnvironmentChecker(object):
    @classmethod
    def get_python_version(cls):
        python_major = sys.version_info[0]
        python_minor = sys.version_info[1]
        return (python_major, python_minor)

    @classmethod
    def check_python_env(cls):
        py_versions = NpuVersionManagerHelper.get_supported_py_versions()
        if cls.get_python_version() not in py_versions:
            print("[ERROR] The Python requirement is %s !" % str(py_versions))
            sys.exit(1)

    @classmethod
    def __get_torch_version(cls):
        try:
            import torch
            torch_version = torch.__version__
        except ImportError:
            print("[ERROR] Unable to import PyTorch module! Please confirm if PyTorch module has already been installed in the NPU compiler runtime environment.")
            sys.exit(1)

        version = torch_version.split(".")
        torch_major = int(version[0])
        torch_minor = int(version[1])
        return (torch_major, torch_minor)

    @classmethod
    def __torch_version_check(cls, python_version, core_version):
        torch_version  = cls.__get_torch_version()

        core_pt_versions = NpuVersionManagerHelper.get_pt_support_cores_pt_versions()[core_version]
        if torch_version not in core_pt_versions:
            print("[ERROR] NPU %s Compiler in python %s environment only support PyTorch version %s"\
                    % (core_version, python_version, str(core_pt_versions)))
            print("        Now PyTorch version is %s!" % str(torch_version))
            sys.exit(1)

    @classmethod
    def check_torch_env(cls, core_version):
        # 各版本core在config中调用该接口检测
        python_version = cls.get_python_version()
        if python_version not in NpuVersionManagerHelper.get_pt_support_py_version():
            print("[ERROR] NPU %s Compiler in python %s environment don't support to process PyTorch framework models!"\
                    % (core_version, str(python_version)))
            sys.exit(1)
        else:
            cls.__torch_version_check(python_version, core_version)


EnvironmentChecker.check_python_env()

