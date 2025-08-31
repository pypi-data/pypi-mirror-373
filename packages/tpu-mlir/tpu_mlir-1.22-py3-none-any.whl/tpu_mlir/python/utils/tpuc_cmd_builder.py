import json
try:
    from loguru import logger
except ImportError:
    from logging import root as logger

import os
import sys
import argparse
from typing import List, Dict, Any, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, Field, validator, ValidationError
import textwrap


class PassOption(BaseModel):
    """Model for Pass options"""

    name: str
    argument: str
    type: str
    description: str
    default_value: str = ""

    class Config:
        arbitrary_types_allowed = True


class Pass(BaseModel):
    """Model for Pass"""

    name: str
    argument: str
    summary: str
    description: str = ""
    options: List[PassOption] = []

    class Config:
        arbitrary_types_allowed = True



# Predefined Pass constants
PASSES_DATA = {
    
    "add-postprocess": Pass(
        name="AddPostprocess",
        argument="add-postprocess",
        summary="post handle in mlir by tpuc-opt",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_16",
                argument="type",
                type="std::string",
                description="type of add-postprocess.",
                default_value="",
            ),
            
        ],
    ),
    
    "address-assign": Pass(
        name="AddressAssign",
        argument="address-assign",
        summary="assign address in tpu by tpuc-opt",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_11",
                argument="reuse_addr",
                type="bool",
                description="reuse tensor memory.",
                default_value="true",
            ),
            
            PassOption(
                name="aa57_anonymous_12",
                argument="merge_weight",
                type="bool",
                description="merge weight memory.",
                default_value="false",
            ),
            
            PassOption(
                name="aa57_anonymous_13",
                argument="compress_weight",
                type="bool",
                description="compress weight memory.",
                default_value="true",
            ),
            
            PassOption(
                name="aa57_anonymous_14",
                argument="weight_map_file",
                type="std::string",
                description="record weight offset with its name into a csv map file.",
                default_value="_weight_map.csv",
            ),
            
        ],
    ),
    
    "codegen": Pass(
        name="Codegen",
        argument="codegen",
        summary="codegen in tpu by tpuc-opt",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_16",
                argument="model_file",
                type="std::string",
                description="save to model file",
                default_value="",
            ),
            
            PassOption(
                name="aa57_anonymous_17",
                argument="embed_debug_info",
                type="bool",
                description="embed debug and profiling data to model file.",
                default_value="false",
            ),
            
            PassOption(
                name="aa57_anonymous_18",
                argument="model_version",
                type="std::string",
                description="model version.",
                default_value="lastest",
            ),
            
            PassOption(
                name="aa57_anonymous_19",
                argument="bmodel_only",
                type="bool",
                description="dump bmodel only.",
                default_value="false",
            ),
            
            PassOption(
                name="aa57_anonymous_20",
                argument="gdma_check",
                type="bool",
                description="gdma address check.",
                default_value="true",
            ),
            
        ],
    ),
    
    "convert-qdq-to-calibrated-dialect": Pass(
        name="QDQConvert",
        argument="convert-qdq-to-calibrated-dialect",
        summary="Convert from qdq model to regular quantized model",
        description="",
        options=[
            
        ],
    ),
    
    "convert-top-to-linalg": Pass(
        name="ConvertTopToLinalg",
        argument="convert-top-to-linalg",
        summary="Convert top-level Top Ops to Linalg Ops",
        description="",
        options=[
            
            PassOption(
                name="b578_anonymous_9",
                argument="includeWeight",
                type="bool",
                description="true for including weight datas in linalg.mlir, or false for not",
                default_value="false",
            ),
            
        ],
    ),
    
    "convert-top-to-tosa": Pass(
        name="ConvertTopToTosa",
        argument="convert-top-to-tosa",
        summary="Convert top-level Top Ops to Tosa Ops",
        description="",
        options=[
            
            PassOption(
                name="b578_anonymous_8",
                argument="includeWeight",
                type="bool",
                description="true for including weight datas in tosa.mlir, or false for not",
                default_value="false",
            ),
            
        ],
    ),
    
    "convert-top-to-tpu": Pass(
        name="ConvertTopToTpu",
        argument="convert-top-to-tpu",
        summary="Convert top-level Top Ops to Tpu Ops",
        description="",
        options=[
            
            PassOption(
                name="b578_anonymous_0",
                argument="qtable",
                type="std::string",
                description="a table of Ops that quantized to specific mode",
                default_value="",
            ),
            
            PassOption(
                name="b578_anonymous_1",
                argument="asymmetric",
                type="bool",
                description="true for asymmetric quantization, or false for symmetric",
                default_value="false",
            ),
            
            PassOption(
                name="b578_anonymous_2",
                argument="doWinograd",
                type="bool",
                description="true for trying winograd ,or false for not",
                default_value="false",
            ),
            
            PassOption(
                name="b578_anonymous_3",
                argument="weightFileName",
                type="std::string",
                description="weight file name to save",
                default_value="",
            ),
            
            PassOption(
                name="b578_anonymous_4",
                argument="q_group_size",
                type="int",
                description="group size for per-group W4A16/W8A16 quant",
                default_value="0",
            ),
            
            PassOption(
                name="b578_anonymous_5",
                argument="q_symmetric",
                type="bool",
                description="true for symmetrci w4a16/w8a16 quant, false for asymmetric",
                default_value="false",
            ),
            
            PassOption(
                name="b578_anonymous_6",
                argument="matmul_perchannel",
                type="bool",
                description="true if matmul uses perchannel quant, or false for pertensor quant",
                default_value="false",
            ),
            
            PassOption(
                name="b578_anonymous_7",
                argument="gelu_mode",
                type="std::string",
                description="supported values: normal, tanh, sigm",
                default_value="normal",
            ),
            
        ],
    ),
    
    "core-parallel": Pass(
        name="CoreParallel",
        argument="core-parallel",
        summary="split the operation to fine-grained and run it in parallel on TPU",
        description="",
        options=[
            
        ],
    ),
    
    "ddr-interleave": Pass(
        name="DDRInterleave",
        argument="ddr-interleave",
        summary="DDR interleave mode",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_10",
                argument="interleave-region",
                type="int64_t",
                description="interleave_region:1 The DDRC is configured to balance performance across most use cases.",
                default_value="1",
            ),
            
        ],
    ),
    
    "deinit": Pass(
        name="Deinit",
        argument="deinit",
        summary="deinit module",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_3",
                argument="no_save_weight",
                type="bool",
                description="whether to save weight.",
                default_value="false",
            ),
            
        ],
    ),
    
    "dev-parallel": Pass(
        name="DevParallel",
        argument="dev-parallel",
        summary="distribute module to multi modules to run in multi devices",
        description="",
        options=[
            
        ],
    ),
    
    "extra-optimize": Pass(
        name="ExtraOptimize",
        argument="extra-optimize",
        summary="after top optimize in mlir by tpuc-opt",
        description="",
        options=[
            
        ],
    ),
    
    "fuse-preprocess": Pass(
        name="FusePreprocess",
        argument="fuse-preprocess",
        summary="Fuse preprocess in cvimodels",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_13",
                argument="mode",
                type="std::string",
                description="default quantization mode: INT8/BF16",
                default_value="",
            ),
            
            PassOption(
                name="6a85_anonymous_14",
                argument="customization_format",
                type="std::string",
                description="set input pixel_format",
                default_value="",
            ),
            
            PassOption(
                name="6a85_anonymous_15",
                argument="align",
                type="bool",
                description="whether input align, only for cv18xx",
                default_value="false",
            ),
            
        ],
    ),
    
    "future-update": Pass(
        name="FutureUpdate",
        argument="future-update",
        summary="add some op for updating in future",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_0",
                argument="rank",
                type="int64_t",
                description="lora rank",
                default_value="0",
            ),
            
            PassOption(
                name="aa57_anonymous_1",
                argument="weight_list",
                type="std::string",
                description="which weight to update",
                default_value="none",
            ),
            
        ],
    ),
    
    "import-calibration-table": Pass(
        name="ImportCalibrationTable",
        argument="import-calibration-table",
        summary="Import calibration table by tpuc-opt",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_10",
                argument="file",
                type="std::string",
                description="calibration table file path",
                default_value="",
            ),
            
            PassOption(
                name="6a85_anonymous_11",
                argument="asymmetric",
                type="bool",
                description="true for asymmetric quantization, or false for symmetric",
                default_value="true",
            ),
            
        ],
    ),
    
    "init": Pass(
        name="Init",
        argument="init",
        summary="init module",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_0",
                argument="freq",
                type="uint64_t",
                description="chip frequance",
                default_value="",
            ),
            
            PassOption(
                name="6a85_anonymous_1",
                argument="weight_in_mem",
                type="bool",
                description="whether to save weight in memory instead of hard disk.",
                default_value="false",
            ),
            
            PassOption(
                name="6a85_anonymous_2",
                argument="level",
                type="uint64_t",
                description="log level",
                default_value="",
            ),
            
        ],
    ),
    
    "layer-group": Pass(
        name="LayerGroup",
        argument="layer-group",
        summary="convert to layer group in tpu by tpuc-opt",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_3",
                argument="opt",
                type="int64_t",
                description="opt=1: group layers as many as possible. opt=2: dynamic programming layer group",
                default_value="2",
            ),
            
            PassOption(
                name="aa57_anonymous_4",
                argument="group_by_cores",
                type="std::string",
                description="whether force group by cores",
                default_value="auto",
            ),
            
            PassOption(
                name="aa57_anonymous_5",
                argument="compress_mode",
                type="std::string",
                description="compress mode",
                default_value="none",
            ),
            
            PassOption(
                name="aa57_anonymous_6",
                argument="lgcache",
                type="std::string",
                description="whether to dump cut_results",
                default_value="true",
            ),
            
            PassOption(
                name="aa57_anonymous_7",
                argument="debugger",
                type="int64_t",
                description="0: do nothing; 1: do LayerGroup and create debugger file; 2: only create debugger file; 3: do LayerGroup with debugger file; 4: do partial LayerGroup with debugger file.",
                default_value="0",
            ),
            
            PassOption(
                name="aa57_anonymous_8",
                argument="debugger_filename",
                type="std::string",
                description="debugger file name",
                default_value="",
            ),
            
            PassOption(
                name="aa57_anonymous_9",
                argument="disable_group_overlap",
                type="bool",
                description="disable group overlap",
                default_value="false",
            ),
            
        ],
    ),
    
    "net_statistic": Pass(
        name="NetStatistic",
        argument="net_statistic",
        summary="net statistic",
        description="",
        options=[
            
        ],
    ),
    
    "op-divide": Pass(
        name="OpDivide",
        argument="op-divide",
        summary="divide large global op to save global memory",
        description="",
        options=[
            
        ],
    ),
    
    "op-reorder": Pass(
        name="OpReorder",
        argument="op-reorder",
        summary="op reorder in tpu by tpuc-opt",
        description="",
        options=[
            
        ],
    ),
    
    "opt-post-processor": Pass(
        name="OptPostProcessor",
        argument="opt-post-processor",
        summary="Graph Optimization after LayerGroup but before AddressAssign",
        description="",
        options=[
            
        ],
    ),
    
    "processor-assign": Pass(
        name="ProcessorAssign",
        argument="processor-assign",
        summary="Assign chip type",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_4",
                argument="chip",
                type="std::string",
                description="chip: cv183x/cv182x/cv186x/bm1684/bm1684x/bm1688/bm1690/cv184x/sgtpuv8/sg2262",
                default_value="",
            ),
            
            PassOption(
                name="6a85_anonymous_5",
                argument="mode",
                type="std::string",
                description="default quantization mode: INT8/BF16/F16/F32/F8/F8E4M3/F8E5M2",
                default_value="",
            ),
            
            PassOption(
                name="6a85_anonymous_6",
                argument="num_device",
                type="int64_t",
                description="num of devices to distributed.",
                default_value="1",
            ),
            
            PassOption(
                name="6a85_anonymous_7",
                argument="num_core",
                type="int64_t",
                description="core_num=1: Set how many cores will be used to run model in parallel.",
                default_value="1",
            ),
            
            PassOption(
                name="6a85_anonymous_8",
                argument="addr_mode",
                type="std::string",
                description="addr assign mode",
                default_value="auto",
            ),
            
            PassOption(
                name="6a85_anonymous_9",
                argument="high_precision",
                type="bool",
                description="force some ops goto fp32",
                default_value="false",
            ),
            
        ],
    ),
    
    "processor-top-optimize": Pass(
        name="ProcessorOptimize",
        argument="processor-top-optimize",
        summary="Before lowering, do some extra Op conversions for different chips",
        description="",
        options=[
            
        ],
    ),
    
    "processor-tpu-optimize": Pass(
        name="ProcessorOptimize",
        argument="processor-tpu-optimize",
        summary="aplly passes in tpu by tpuc-opt",
        description="",
        options=[
            
        ],
    ),
    
    "pruning": Pass(
        name="Pruning",
        argument="pruning",
        summary="do pruning for matmul op",
        description="",
        options=[
            
            PassOption(
                name="6a85_anonymous_12",
                argument="config",
                type="std::string",
                description="path of config_file.",
                default_value="",
            ),
            
        ],
    ),
    
    "shape-infer": Pass(
        name="ShapeInfer",
        argument="shape-infer",
        summary="do shape inference for each op",
        description="",
        options=[
            
        ],
    ),
    
    "shape-optimize": Pass(
        name="ShapeOptimize",
        argument="shape-optimize",
        summary="optimize bad shape in tpu by tpuc-opt",
        description="",
        options=[
            
        ],
    ),
    
    "show-address": Pass(
        name="ShowAddress",
        argument="show-address",
        summary="print final mlir address by tpuc-opt",
        description="",
        options=[
            
        ],
    ),
    
    "strip-io-quant": Pass(
        name="StripIOQuant",
        argument="strip-io-quant",
        summary="remove input & output fp32<->int8 converiton in int8model",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_21",
                argument="quant_input",
                type="bool",
                description="strip input quant.",
                default_value="false",
            ),
            
            PassOption(
                name="aa57_anonymous_22",
                argument="quant_output",
                type="bool",
                description="strip output quant.",
                default_value="false",
            ),
            
            PassOption(
                name="aa57_anonymous_23",
                argument="quant_input_list",
                type="std::string",
                description="choose index to strip input quant.",
                default_value="",
            ),
            
            PassOption(
                name="aa57_anonymous_24",
                argument="quant_output_list",
                type="std::string",
                description="choose index to strip output quant.",
                default_value="",
            ),
            
            PassOption(
                name="aa57_anonymous_25",
                argument="quant_output_bf16",
                type="bool",
                description="force output to be bf16 type",
                default_value="false",
            ),
            
        ],
    ),
    
    "subnet-divide": Pass(
        name="SubnetDivide",
        argument="subnet-divide",
        summary="subnet divide in tpu by tpuc-opt",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_2",
                argument="dynamic",
                type="bool",
                description="dynamic compiler or not.",
                default_value="false",
            ),
            
        ],
    ),
    
    "time-fixed-subnet": Pass(
        name="TimeFixedSubnet",
        argument="time-fixed-subnet",
        summary="Split the model by fixed duration intervals",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_15",
                argument="json_file",
                type="std::string",
                description=".subnets.json",
                default_value="",
            ),
            
        ],
    ),
    
    "trunc-io": Pass(
        name="TruncIO",
        argument="trunc-io",
        summary="truncate final mlir according to inputs/outputs, keeping the structure as far as possible.",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_26",
                argument="inputs",
                type="std::string",
                description="new input names",
                default_value="",
            ),
            
            PassOption(
                name="aa57_anonymous_27",
                argument="outputs",
                type="std::string",
                description="new output names",
                default_value="",
            ),
            
            PassOption(
                name="aa57_anonymous_28",
                argument="weight_shared",
                type="bool",
                description="whether to share weight",
                default_value="false",
            ),
            
            PassOption(
                name="aa57_anonymous_29",
                argument="trunc_mode",
                type="int",
                description="determine how many END_OPs under consideration, optional values is: 0, 1.0 -> only one END_OP (default)1 -> one or more END_OPs",
                default_value="0",
            ),
            
        ],
    ),
    
    "trunc-layer": Pass(
        name="TruncLayer",
        argument="trunc-layer",
        summary="Cut any mlir as sub mlir",
        description="",
        options=[
            
            PassOption(
                name="aa57_anonymous_30",
                argument="cutLocs",
                type="std::string",
                description="cut loc names, split by comma, like 0,1,2",
                default_value="",
            ),
            
        ],
    ),
    
    "weight-fold": Pass(
        name="WeightFold",
        argument="weight-fold",
        summary="fold weight if all input of an operation is weight",
        description="",
        options=[
            
        ],
    ),
    
    "weight-reorder": Pass(
        name="WeightReorder",
        argument="weight-reorder",
        summary="weight reorder in tpu by tpuc-opt",
        description="",
        options=[
            
        ],
    ),
    
}


class TpucCommandBuilder:
    """
    TPU-MLIR command builder, used to generate tpuc-opt commands.
    Based on built-in pass and option information, and uses pydantic for parameter validation.
    """

    def __init__(self):
        self.commands = []
        self.passes = PASSES_DATA
        self.last_pass = None
        self.input_file = None

    def add_input_file(self, input_file: str) -> "TpucCommandBuilder":
        """Add input file"""
        self.commands = ["tpuc-opt", input_file]
        self.input_file = input_file
        return self

    def _validate_option_type(self, option: PassOption, value: Any) -> Any:
        """Validate option value type and convert to appropriate representation"""
        if option.type == "bool":
            if isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, str):
                if value.lower() in ("true", "yes", "1"):
                    return "true"
                elif value.lower() in ("false", "no", "0"):
                    return "false"
                else:
                    raise ValueError(
                        f"Option {option.argument} requires a boolean value, but received '{value}'"
                    )
            else:
                raise ValueError(
                    f"Option {option.argument} requires a boolean value, but received {type(value).__name__}"
                )

        elif (
            option.type == "int"
            or option.type.startswith("int")
            or option.type.startswith("uint")
        ):
            if isinstance(value, (int, float)) or (
                isinstance(value, str) and value.isdigit()
            ):
                return str(int(value))
            else:
                raise ValueError(
                    f"Option {option.argument} requires an integer, but received {type(value).__name__}: {value}"
                )

        elif option.type == "std::string" or option.type == "string":
            if value is None:
                return ""
            return str(value)

        # For other types, return string representation directly
        return str(value)

    def add_pass(self, pass_name: str, **options) -> "TpucCommandBuilder":
        """Add pass and its options, and validate the validity of options"""
        if pass_name not in self.passes:
            raise ValueError(
                f"Unknown pass: {pass_name}, available passes: {', '.join(self.passes.keys())}"
            )
        if not self.input_file:
            raise ValueError("Input file not set")

        pass_info = self.passes[pass_name]
        argument = pass_info.argument
        self.last_pass = argument

        # Build pass option string
        pass_str = f"--{argument}"

        # Process options
        if options:
            option_strs = []

            # Get valid options for this pass
            valid_options = {opt.argument: opt for opt in pass_info.options}

            # Validate provided options
            for key, value in options.items():
                if key in valid_options:
                    # Validate and convert option value
                    try:
                        validated_value = self._validate_option_type(
                            valid_options[key], value
                        )
                        option_strs.append(f"{key}={validated_value}")
                    except ValueError as e:
                        raise ValueError(f"Failed to validate option {key} for pass {pass_name}: {e}")
                else:
                    # Warn about unknown options
                    print(
                        f"Warning: Pass {pass_name} has no defined option '{key}'. Valid options: {', '.join(valid_options.keys())}"
                    )
                    # Still add it, in case it's an option not defined in JSON
                    option_strs.append(f"{key}={value}")

            if option_strs:
                pass_str += f"=\"{' '.join(option_strs)}\""

        self.commands.append(pass_str)
        return self

    def add_output_file(self, output_file: str) -> "TpucCommandBuilder":
        """Add output file"""
        self.commands.extend(["-o", output_file])
        return self

    def infer_output_file(self, output_dir: str) -> "TpucCommandBuilder":
        """Infer output file"""
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        if self.last_pass:
            self.commands.extend(["-o", os.path.join(output_dir, f"{base_name}_{self.last_pass}.mlir")])
        else:
            raise ValueError("Cannot infer output file because no pass has been executed")
        return self

    def add_raw_option(self, option: str) -> "TpucCommandBuilder":
        """Add raw option string"""
        self.commands.append(option)
        return self

    def build(self) -> str:
        """Build complete command string"""
        return " ".join(self.commands)

    def execute(self, log_level: str = "normal") -> None:
        """Execute command"""
        try:
            from tpu_mlir.python.utils.mlir_shell import _os_system

            _os_system(self.commands, log_level=log_level)
        except ImportError:
            print("Warning: Unable to import utils.mlir_shell, will use os.system to execute command")
            import os

            cmd_str = " ".join(self.commands)
            print(f"Executing command: {cmd_str}")
            os.system(cmd_str)

    def list_passes(self, filter_str: str = None) -> None:
        """List all available passes and their descriptions"""
        print(f"Available passes ({len(self.passes)}):")
        print("=" * 80)

        for name, pass_info in sorted(self.passes.items()):
            if (
                filter_str
                and filter_str.lower() not in name.lower()
                and filter_str.lower() not in pass_info.argument.lower()
            ):
                continue

            print(f"{name} (--{pass_info.argument}):")
            print(f"  Summary: {pass_info.summary}")
            if pass_info.options:
                print("  Options:")
                for opt in pass_info.options:
                    default_str = (
                        f" [Default: {opt.default_value}]" if opt.default_value else ""
                    )
                    print(
                        f"    - {opt.argument} ({opt.type}){default_str}: {opt.description}"
                    )
            print()

    def get_pass_info(self, pass_name: str) -> str:
        """Get detailed information for a specific pass"""
        if pass_name not in self.passes:
            return f"Error: Unknown pass '{pass_name}'"

        pass_info = self.passes[pass_name]
        result = [
            f"Pass: {pass_name} (--{pass_info.argument})",
            f"Summary: {pass_info.summary}",
            f"Description: {pass_info.description or 'No description'}",
        ]

        if pass_info.options:
            result.append("Options:")
            for opt in pass_info.options:
                default_str = (
                    f" [Default: {opt.default_value}]" if opt.default_value else ""
                )
                result.append(
                    f"  - {opt.argument} ({opt.type}){default_str}: {opt.description}"
                )
        else:
            result.append("Options: None")

        return "\n".join(result)

    # Convenient methods for commonly used passes
    
    def add_postprocess(self, **options) -> "TpucCommandBuilder":
        """Add add-postprocess pass

        post handle in mlir by tpuc-opt
        
        

        Options:
        
        - type (std::string): type of add-postprocess.
        
        
        """
        return self.add_pass("add-postprocess", **options)

    
    def address_assign(self, **options) -> "TpucCommandBuilder":
        """Add address-assign pass

        assign address in tpu by tpuc-opt
        
        

        Options:
        
        - reuse_addr (bool) [Default: true]: reuse tensor memory.
        
        - merge_weight (bool) [Default: false]: merge weight memory.
        
        - compress_weight (bool) [Default: true]: compress weight memory.
        
        - weight_map_file (std::string) [Default: "_weight_map.csv"]: record weight offset with its name into a csv map file.
        
        
        """
        return self.add_pass("address-assign", **options)

    
    def codegen(self, **options) -> "TpucCommandBuilder":
        """Add codegen pass

        codegen in tpu by tpuc-opt
        
        

        Options:
        
        - model_file (std::string): save to model file
        
        - embed_debug_info (bool) [Default: false]: embed debug and profiling data to model file.
        
        - model_version (std::string) [Default: "lastest"]: model version.
        
        - bmodel_only (bool) [Default: false]: dump bmodel only.
        
        - gdma_check (bool) [Default: true]: gdma address check.
        
        
        """
        return self.add_pass("codegen", **options)

    
    def convert_qdq_to_calibrated_dialect(self) -> "TpucCommandBuilder":
        """Add convert-qdq-to-calibrated-dialect pass

        Convert from qdq model to regular quantized model
        
        
        """
        return self.add_pass("convert-qdq-to-calibrated-dialect")

    
    def convert_top_to_linalg(self, **options) -> "TpucCommandBuilder":
        """Add convert-top-to-linalg pass

        Convert top-level Top Ops to Linalg Ops
        
        

        Options:
        
        - includeWeight (bool) [Default: false]: true for including weight datas in linalg.mlir, or false for not
        
        
        """
        return self.add_pass("convert-top-to-linalg", **options)

    
    def convert_top_to_tosa(self, **options) -> "TpucCommandBuilder":
        """Add convert-top-to-tosa pass

        Convert top-level Top Ops to Tosa Ops
        
        

        Options:
        
        - includeWeight (bool) [Default: false]: true for including weight datas in tosa.mlir, or false for not
        
        
        """
        return self.add_pass("convert-top-to-tosa", **options)

    
    def convert_top_to_tpu(self, **options) -> "TpucCommandBuilder":
        """Add convert-top-to-tpu pass

        Convert top-level Top Ops to Tpu Ops
        
        

        Options:
        
        - qtable (std::string): a table of Ops that quantized to specific mode
        
        - asymmetric (bool) [Default: false]: true for asymmetric quantization, or false for symmetric
        
        - doWinograd (bool) [Default: false]: true for trying winograd ,or false for not
        
        - weightFileName (std::string): weight file name to save
        
        - q_group_size (int) [Default: 0]: group size for per-group W4A16/W8A16 quant
        
        - q_symmetric (bool) [Default: false]: true for symmetrci w4a16/w8a16 quant, false for asymmetric
        
        - matmul_perchannel (bool) [Default: false]: true if matmul uses perchannel quant, or false for pertensor quant
        
        - gelu_mode (std::string) [Default: "normal"]: supported values: normal, tanh, sigm
        
        
        """
        return self.add_pass("convert-top-to-tpu", **options)

    
    def core_parallel(self) -> "TpucCommandBuilder":
        """Add core-parallel pass

        split the operation to fine-grained and run it in parallel on TPU
        
        
        """
        return self.add_pass("core-parallel")

    
    def ddr_interleave(self, **options) -> "TpucCommandBuilder":
        """Add ddr-interleave pass

        DDR interleave mode
        
        

        Options:
        
        - interleave-region (int64_t) [Default: 1]: interleave_region:1 The DDRC is configured to balance performance across most use cases.
        
        
        """
        return self.add_pass("ddr-interleave", **options)

    
    def deinit(self, **options) -> "TpucCommandBuilder":
        """Add deinit pass

        deinit module
        
        

        Options:
        
        - no_save_weight (bool) [Default: false]: whether to save weight.
        
        
        """
        return self.add_pass("deinit", **options)

    
    def dev_parallel(self) -> "TpucCommandBuilder":
        """Add dev-parallel pass

        distribute module to multi modules to run in multi devices
        
        
        """
        return self.add_pass("dev-parallel")

    
    def extra_optimize(self) -> "TpucCommandBuilder":
        """Add extra-optimize pass

        after top optimize in mlir by tpuc-opt
        
        
        """
        return self.add_pass("extra-optimize")

    
    def fuse_preprocess(self, **options) -> "TpucCommandBuilder":
        """Add fuse-preprocess pass

        Fuse preprocess in cvimodels
        
        

        Options:
        
        - mode (std::string): default quantization mode: INT8/BF16
        
        - customization_format (std::string): set input pixel_format
        
        - align (bool) [Default: false]: whether input align, only for cv18xx
        
        
        """
        return self.add_pass("fuse-preprocess", **options)

    
    def future_update(self, **options) -> "TpucCommandBuilder":
        """Add future-update pass

        add some op for updating in future
        
        

        Options:
        
        - rank (int64_t) [Default: 0]: lora rank
        
        - weight_list (std::string) [Default: "none"]: which weight to update
        
        
        """
        return self.add_pass("future-update", **options)

    
    def import_calibration_table(self, **options) -> "TpucCommandBuilder":
        """Add import-calibration-table pass

        Import calibration table by tpuc-opt
        
        

        Options:
        
        - file (std::string): calibration table file path
        
        - asymmetric (bool) [Default: true]: true for asymmetric quantization, or false for symmetric
        
        
        """
        return self.add_pass("import-calibration-table", **options)

    
    def init(self, **options) -> "TpucCommandBuilder":
        """Add init pass

        init module
        
        

        Options:
        
        - freq (uint64_t): chip frequance
        
        - weight_in_mem (bool) [Default: false]: whether to save weight in memory instead of hard disk.
        
        - level (uint64_t): log level
        
        
        """
        return self.add_pass("init", **options)

    
    def layer_group(self, **options) -> "TpucCommandBuilder":
        """Add layer-group pass

        convert to layer group in tpu by tpuc-opt
        
        

        Options:
        
        - opt (int64_t) [Default: 2]: opt=1: group layers as many as possible. opt=2: dynamic programming layer group
        
        - group_by_cores (std::string) [Default: "auto"]: whether force group by cores
        
        - compress_mode (std::string) [Default: "none"]: compress mode
        
        - lgcache (std::string) [Default: "true"]: whether to dump cut_results
        
        - debugger (int64_t) [Default: 0]: 0: do nothing; 1: do LayerGroup and create debugger file; 2: only create debugger file; 3: do LayerGroup with debugger file; 4: do partial LayerGroup with debugger file.
        
        - debugger_filename (std::string) [Default: ""]: debugger file name
        
        - disable_group_overlap (bool) [Default: false]: disable group overlap
        
        
        """
        return self.add_pass("layer-group", **options)

    
    def net_statistic(self) -> "TpucCommandBuilder":
        """Add net_statistic pass

        net statistic
        
        
        """
        return self.add_pass("net_statistic")

    
    def op_divide(self) -> "TpucCommandBuilder":
        """Add op-divide pass

        divide large global op to save global memory
        
        
        """
        return self.add_pass("op-divide")

    
    def op_reorder(self) -> "TpucCommandBuilder":
        """Add op-reorder pass

        op reorder in tpu by tpuc-opt
        
        
        """
        return self.add_pass("op-reorder")

    
    def opt_post_processor(self) -> "TpucCommandBuilder":
        """Add opt-post-processor pass

        Graph Optimization after LayerGroup but before AddressAssign
        
        
        """
        return self.add_pass("opt-post-processor")

    
    def processor_assign(self, **options) -> "TpucCommandBuilder":
        """Add processor-assign pass

        Assign chip type
        
        

        Options:
        
        - chip (std::string): chip: cv183x/cv182x/cv186x/bm1684/bm1684x/bm1688/bm1690/cv184x/sgtpuv8/sg2262
        
        - mode (std::string): default quantization mode: INT8/BF16/F16/F32/F8/F8E4M3/F8E5M2
        
        - num_device (int64_t) [Default: 1]: num of devices to distributed.
        
        - num_core (int64_t) [Default: 1]: core_num=1: Set how many cores will be used to run model in parallel.
        
        - addr_mode (std::string) [Default: "auto"]: addr assign mode
        
        - high_precision (bool) [Default: false]: force some ops goto fp32
        
        
        """
        return self.add_pass("processor-assign", **options)

    
    def processor_top_optimize(self) -> "TpucCommandBuilder":
        """Add processor-top-optimize pass

        Before lowering, do some extra Op conversions for different chips
        
        
        """
        return self.add_pass("processor-top-optimize")

    
    def processor_tpu_optimize(self) -> "TpucCommandBuilder":
        """Add processor-tpu-optimize pass

        aplly passes in tpu by tpuc-opt
        
        
        """
        return self.add_pass("processor-tpu-optimize")

    
    def pruning(self, **options) -> "TpucCommandBuilder":
        """Add pruning pass

        do pruning for matmul op
        
        

        Options:
        
        - config (std::string): path of config_file.
        
        
        """
        return self.add_pass("pruning", **options)

    
    def shape_infer(self) -> "TpucCommandBuilder":
        """Add shape-infer pass

        do shape inference for each op
        
        
        """
        return self.add_pass("shape-infer")

    
    def shape_optimize(self) -> "TpucCommandBuilder":
        """Add shape-optimize pass

        optimize bad shape in tpu by tpuc-opt
        
        
        """
        return self.add_pass("shape-optimize")

    
    def show_address(self) -> "TpucCommandBuilder":
        """Add show-address pass

        print final mlir address by tpuc-opt
        
        
        """
        return self.add_pass("show-address")

    
    def strip_io_quant(self, **options) -> "TpucCommandBuilder":
        """Add strip-io-quant pass

        remove input & output fp32<->int8 converiton in int8model
        
        

        Options:
        
        - quant_input (bool) [Default: false]: strip input quant.
        
        - quant_output (bool) [Default: false]: strip output quant.
        
        - quant_input_list (std::string): choose index to strip input quant.
        
        - quant_output_list (std::string): choose index to strip output quant.
        
        - quant_output_bf16 (bool) [Default: false]: force output to be bf16 type
        
        
        """
        return self.add_pass("strip-io-quant", **options)

    
    def subnet_divide(self, **options) -> "TpucCommandBuilder":
        """Add subnet-divide pass

        subnet divide in tpu by tpuc-opt
        
        

        Options:
        
        - dynamic (bool) [Default: false]: dynamic compiler or not.
        
        
        """
        return self.add_pass("subnet-divide", **options)

    
    def time_fixed_subnet(self, **options) -> "TpucCommandBuilder":
        """Add time-fixed-subnet pass

        Split the model by fixed duration intervals
        
        

        Options:
        
        - json_file (std::string): .subnets.json
        
        
        """
        return self.add_pass("time-fixed-subnet", **options)

    
    def trunc_io(self, **options) -> "TpucCommandBuilder":
        """Add trunc-io pass

        truncate final mlir according to inputs/outputs, keeping the structure as far as possible.
        
        

        Options:
        
        - inputs (std::string): new input names
        
        - outputs (std::string): new output names
        
        - weight_shared (bool) [Default: false]: whether to share weight
        
        - trunc_mode (int) [Default: 0]: determine how many END_OPs under consideration, optional values is: 0, 1.0 -> only one END_OP (default)1 -> one or more END_OPs
        
        
        """
        return self.add_pass("trunc-io", **options)

    
    def trunc_layer(self, **options) -> "TpucCommandBuilder":
        """Add trunc-layer pass

        Cut any mlir as sub mlir
        
        

        Options:
        
        - cutLocs (std::string): cut loc names, split by comma, like 0,1,2
        
        
        """
        return self.add_pass("trunc-layer", **options)

    
    def weight_fold(self) -> "TpucCommandBuilder":
        """Add weight-fold pass

        fold weight if all input of an operation is weight
        
        
        """
        return self.add_pass("weight-fold")

    
    def weight_reorder(self) -> "TpucCommandBuilder":
        """Add weight-reorder pass

        weight reorder in tpu by tpuc-opt
        
        
        """
        return self.add_pass("weight-reorder")

    
    def canonicalize(self) -> "TpucCommandBuilder":
        """Add canonicalize pass"""
        return self.add_raw_option("--canonicalize")

    def __repr__(self):
        return self.build()


def build_cli():
    """Create command line interface"""
    parser = argparse.ArgumentParser(description="TPU-MLIR Command Builder CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # List all passes
    list_passes_parser = subparsers.add_parser(
        "list-passes", help="List all available passes"
    )
    list_passes_parser.add_argument("--filter", type=str, help="Filter string")

    # List all options
    list_options_parser = subparsers.add_parser(
        "list-options", help="List all available options"
    )
    list_options_parser.add_argument("--filter", type=str, help="Filter string")

    # Get information for a specific pass
    info_parser = subparsers.add_parser("info", help="Get detailed information for a specific pass")
    info_parser.add_argument("pass_name", type=str, help="Pass name")

    # Example command
    example_parser = subparsers.add_parser("example", help="Show example usage")

    args = parser.parse_args()

    builder = TpucCommandBuilder()

    if args.command == "list-passes":
        builder.list_passes(args.filter)
    elif args.command == "list-options":
        builder.list_options(args.filter)
    elif args.command == "info":
        print(builder.get_pass_info(args.pass_name))
    elif args.command == "example":
        example_usage()
    else:
        parser.print_help()


def example_usage():
    """Show example usage"""
    example = """
# Example Usage

## 1. Create command builder instance
```python
from tpuc_command_builder import TpucCommandBuilder
builder = TpucCommandBuilder()
```

## 2. Convert from top model to tpu model
```python
cmd = (builder
    .add_input_file("model.mlir")
    .shape_infer()
    .canonicalize()
    .processor_assign(chip="bm1684x", mode="INT8", num_device=1, num_core=1)
    .processor_optimize()
    .convert_top_to_tpu(asymmetric=False, doWinograd=False)
    .canonicalize()
    .weight_fold()
    .add_output_file("model_tpu.mlir")
    .build()
)
print(cmd)
```

## 3. Generate final model
```python
builder = TpucCommandBuilder()
cmd = (builder
    .add_input_file("model_tpu.mlir")
    .strip_i_o_quant(quant_input=False, quant_output=False)
    .processor_optimize()
    .layer_group(opt=2)
    .address_assign(merge_weight=False)
    .codegen(model_file="model.bmodel", embed_debug_info=False)
    .add_output_file("/dev/null")
    .build()
)
print(cmd)
```

## 4. Execute command
```python
builder = TpucCommandBuilder()
(builder
    .add_input_file("model.mlir")
    .shape_infer()
    .add_output_file("model_shape.mlir")
    .execute()
)
```

## 5. Get pass information
```python
builder = TpucCommandBuilder()
info = builder.get_pass_info("ShapeInfer")
print(info)
```
"""
    print(textwrap.dedent(example))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        build_cli()
    else:
        example_usage()