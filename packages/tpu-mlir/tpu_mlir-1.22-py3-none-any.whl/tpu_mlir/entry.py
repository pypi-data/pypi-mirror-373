import tpu_mlir,os
from tpu_mlir import run_subprocess_c, run_subprocess_py

# f"{package_path}/bin/
def model_tool():
	file_name = f"{os.getenv('TPUC_ROOT')}/bin/model_tool"
	run_subprocess_c(file_name)

def tpuc_tool():
	file_name = f"{os.getenv('TPUC_ROOT')}/bin/tpuc-tool"
	run_subprocess_c(file_name)

def tpuc_opt():
	file_name = f"{os.getenv('TPUC_ROOT')}/bin/tpuc-opt"
	run_subprocess_c(file_name)

def cvimodel_debug():
	file_name = f"{os.getenv('TPUC_ROOT')}/bin/cvimodel_debug"
	run_subprocess_c(file_name)

### total 4 entry generated for f"{package_path}/bin/

# f"{package_path}/python/tools/
def compare_visualizer():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/compare_visualizer.py"
	run_subprocess_py(file_name)

def mlir2graph():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/mlir2graph.py"
	run_subprocess_py(file_name)

def tdb():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/tdb.py"
	run_subprocess_py(file_name)

def tpu_profile():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/tpu_profile.py"
	run_subprocess_py(file_name)

def gen_rand_input():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/gen_rand_input.py"
	run_subprocess_py(file_name)

def bmodel_combine():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/bmodel_combine.py"
	run_subprocess_py(file_name)

def bmodel_dis():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/bmodel_dis.py"
	run_subprocess_py(file_name)

def logdebug_tool():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/logdebug_tool.py"
	run_subprocess_py(file_name)

def run_calibration():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/run_calibration.py"
	run_subprocess_py(file_name)

def run_sensitive_layer():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/run_sensitive_layer.py"
	run_subprocess_py(file_name)

def tool_maskrcnn():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/tool_maskrcnn.py"
	run_subprocess_py(file_name)

def bmrt_test_soc():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/bmrt_test_soc.py"
	run_subprocess_py(file_name)

def bmodel_truncater():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/bmodel_truncater.py"
	run_subprocess_py(file_name)

def code_stripper():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/code_stripper.py"
	run_subprocess_py(file_name)

def mlir_cut():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/mlir_cut.py"
	run_subprocess_py(file_name)

def debugit():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/debugit.py"
	run_subprocess_py(file_name)

def profile_analysis():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/profile_analysis.ipynb"
	run_subprocess_c(file_name)

def bmodel_checker():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/bmodel_checker.py"
	run_subprocess_py(file_name)

def remote_test():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/remote_test.py"
	run_subprocess_py(file_name)

def riscv_code_opt():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/riscv_code_opt.py"
	run_subprocess_py(file_name)

def model_inference_cpu():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_inference_cpu.py"
	run_subprocess_py(file_name)

def op_locator():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/op_locator.py"
	run_subprocess_py(file_name)

def model_eval_imagenet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_eval_imagenet.py"
	run_subprocess_py(file_name)

def gen_rewriter_config():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/gen_rewriter_config.py"
	run_subprocess_py(file_name)

def model_convert():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_convert.py"
	run_subprocess_py(file_name)

def assign_output():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/assign_output.py"
	run_subprocess_py(file_name)

def gen_shell():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/gen_shell.py"
	run_subprocess_py(file_name)

def mlir2onnx():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/mlir2onnx.py"
	run_subprocess_py(file_name)

def model_eval():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_eval.py"
	run_subprocess_py(file_name)

def model_transform():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_transform.py"
	run_subprocess_py(file_name)

def run_qtable():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/run_qtable.py"
	run_subprocess_py(file_name)

def llm_convert():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/llm_convert.py"
	run_subprocess_py(file_name)

def pmu_dump():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/pmu_dump.py"
	run_subprocess_py(file_name)

def layergroup_lmem_assign_visualizer():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/layergroup_lmem_assign_visualizer.ipynb"
	run_subprocess_c(file_name)

def npz_tool():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/npz_tool.py"
	run_subprocess_py(file_name)

def llm_analyse():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/llm_analyse.py"
	run_subprocess_py(file_name)

def mlir_truncio():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/mlir_truncio.py"
	run_subprocess_py(file_name)

def deploy_qat():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/deploy_qat.py"
	run_subprocess_py(file_name)

def fp_forward():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/fp_forward.py"
	run_subprocess_py(file_name)

def run_bmprofile():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/run_bmprofile.py"
	run_subprocess_py(file_name)

def model_runner():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_runner.py"
	run_subprocess_py(file_name)

def visual():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/visual.py"
	run_subprocess_py(file_name)

def bmodel_dumper():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/bmodel_dumper.py"
	run_subprocess_py(file_name)

def compare_visualizer_demo():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/compare_visualizer_demo.ipynb"
	run_subprocess_c(file_name)

def model_deploy():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/model_deploy.py"
	run_subprocess_py(file_name)

def duration_BW_usage_statistics():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/tools/duration_BW_usage_statistics.py"
	run_subprocess_py(file_name)

### total 46 entry generated for f"{package_path}/python/tools/

# f"{package_path}/python/samples/
def classify_resnext50():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_resnext50.py"
	run_subprocess_py(file_name)

def detect_ssd_12():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_ssd-12.py"
	run_subprocess_py(file_name)

def detect_retinaface():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_retinaface.py"
	run_subprocess_py(file_name)

def seg_humanseg():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/seg_humanseg.py"
	run_subprocess_py(file_name)

def detect_ultraface():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_ultraface.py"
	run_subprocess_py(file_name)

def detect_yolov3():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_yolov3.py"
	run_subprocess_py(file_name)

def classify_xception():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_xception.py"
	run_subprocess_py(file_name)

def classify_inception_v3():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_inception_v3.py"
	run_subprocess_py(file_name)

def classify_efficientnet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_efficientnet.py"
	run_subprocess_py(file_name)

def detect_pp_yoloe():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_pp_yoloe.py"
	run_subprocess_py(file_name)

def classify_mobilenet_v2():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_mobilenet_v2.py"
	run_subprocess_py(file_name)

def detect_pp_yolox():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_pp_yolox.py"
	run_subprocess_py(file_name)

def classify_shufflenet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_shufflenet.py"
	run_subprocess_py(file_name)

def segment_yolo():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/segment_yolo.py"
	run_subprocess_py(file_name)

def detect_pp_picodet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_pp_picodet.py"
	run_subprocess_py(file_name)

def classify_squeezenet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_squeezenet.py"
	run_subprocess_py(file_name)

def classify_DenseNet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_DenseNet.py"
	run_subprocess_py(file_name)

def classify_resnet18():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_resnet18.py"
	run_subprocess_py(file_name)

def detect_yolov5():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/detect_yolov5.py"
	run_subprocess_py(file_name)

def classify_resnet50():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_resnet50.py"
	run_subprocess_py(file_name)

def classify_LeNet():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_LeNet.py"
	run_subprocess_py(file_name)

def classify_vgg16():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/samples/classify_vgg16.py"
	run_subprocess_py(file_name)

### total 22 entry generated for f"{package_path}/python/samples/

# f"{package_path}/python/test/
def test_MaskRCNN():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/test/test_MaskRCNN.py"
	run_subprocess_py(file_name)

def test_onnx():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/test/test_onnx.py"
	run_subprocess_py(file_name)

def README():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/test/README.txt"
	run_subprocess_c(file_name)

def test_tpulang():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/test/test_tpulang.py"
	run_subprocess_py(file_name)

def test_torch():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/test/test_torch.py"
	run_subprocess_py(file_name)

def test_tflite():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/test/test_tflite.py"
	run_subprocess_py(file_name)

### total 6 entry generated for f"{package_path}/python/test/

# f"{package_path}/python/PerfAI/
def PerfAI():
	file_name = f"{os.getenv('TPUC_ROOT')}/python/PerfAI/PerfAI.sh"
	run_subprocess_c(file_name)

### total 1 entry generated for f"{package_path}/python/PerfAI/

# f"{package_path}/customlayer/test/test_custom_tpulang.py
def test_custom_tpulang():
	file_name = f"{os.getenv('TPUC_ROOT')}/customlayer/test/test_custom_tpulang.py"
	run_subprocess_py(file_name)

### total 1 entry generated for f"{package_path}/customlayer/test/test_custom_tpulang.py

