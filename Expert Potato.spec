# -*- mode: python ; coding: utf-8 -*-

# Expert Potato 优化构建配置
# 目标：通过运行时下载模型策略，将打包体积从3GB减少到50-200MB

# 需要排除的模块 - 大幅扩展排除列表
excluded_modules = [
    # HuggingFace相关（大型模块）
    'transformers',
    'datasets',
    'tokenizers',
    'accelerate',
    'diffusers',
    'huggingface_hub.inference',
    'huggingface_hub.repository',
    
    # PyTorch大型模块 - 更激进的排除
    'torch.distributed',
    'torch.optim',
    'torch.jit',
    'torch.onnx',
    'torch.quantization',
    'torch.fx',
    'torch.ao',
    'torch.profiler',
    'torch.autograd.profiler',
    'torch.utils.tensorboard',
    'torch.utils.benchmark',
    'torch.utils.bottleneck',
    'torch.utils.checkpoint',
    'torch.utils.cpp_extension',
    'torch.utils.data.datapipes',
    'torch.testing',
    'torch.hub',
    'torch.backends.mkldnn',
    'torch.backends.mkl',
    'torch.backends.openmp',
    'torch.backends.quantized',
    'torch.nn.modules.activation',
    'torch.nn.modules.batchnorm',
    'torch.nn.modules.container',
    'torch.nn.modules.conv',
    'torch.nn.modules.dropout',
    'torch.nn.modules.linear',
    'torch.nn.modules.loss',
    'torch.nn.modules.normalization',
    'torch.nn.modules.padding',
    'torch.nn.modules.pooling',
    'torch.nn.modules.rnn',
    'torch.nn.modules.sparse',
    'torch.nn.modules.transformer',
    'torch.nn.modules.upsampling',
    'torch.nn.modules.utils',
    'torch.nn.parallel',
    'torch.nn.utils',
    'torch.optim.lr_scheduler',
    'torch.optim.optimizer',
    'torch.optim.sgd',
    'torch.optim.adam',
    'torch.optim.adamw',
    'torch.optim.rmsprop',
    
    # TorchAudio大型模块
    'torchaudio.datasets',
    'torchaudio.models',
    'torchaudio.pipelines',
    'torchaudio.prototype',
    'torchaudio.compliance',
    'torchaudio.kaldi_io',
    'torchaudio.sox_effects',
    
    # 其他大型依赖
    'scipy',
    'sklearn',
    'pandas',
    'matplotlib',
    'seaborn',
    'plotly',
    'jupyter',
    'notebook',
    'ipython',
    'sympy',
    'networkx',
    'PIL.ImageTk',
    'tkinter',
]

block_cipher = None

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/config', 'config'), ('src/ui', 'ui'), ('src/pages', 'pages'), ('src/core', 'core')],
    hiddenimports=['PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui', 'qfluentwidgets', 'faster_whisper', 'torch', 'torchaudio', 'requests', 'hupper'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

# 过滤掉模型文件和缓存
def filter_binaries_and_datas(items):
    """过滤掉模型文件、缓存文件和大型二进制文件"""
    filtered = []
    excluded_count = 0
    total_excluded_size = 0
    
    for item in items:
        if len(item) >= 2:
            name, path = item[0], item[1]
            should_exclude = False
            
            # 排除模型文件
            if any(pattern in name.lower() for pattern in [
                'whisper', 'model', '.bin', '.pt', '.pth', '.onnx', '.safetensors',
                'pytorch_model', 'tf_model', 'flax_model'
            ]):
                should_exclude = True
                
            # 排除缓存目录
            if any(pattern in path.lower() for pattern in [
                'cache', 'huggingface', 'transformers_cache', '.cache',
                'models--', 'snapshots'
            ]):
                should_exclude = True
                
            # 排除大型CUDA库（更激进的过滤）
            if any(pattern in name.lower() for pattern in [
                'cublas', 'cufft', 'curand', 'cusparse', 'cusolver',
                'cudnn', 'nccl', 'nvtx', 'cublaslt', 'cusparse',
                'cusolverdn', 'cufftw', 'nvjpeg', 'nvrtc'
            ]) and name.lower().endswith(('.dll', '.so', '.dylib')):
                should_exclude = True
                
            # 排除大型PyTorch二进制文件
            if any(pattern in name.lower() for pattern in [
                'torch_cpu.dll', 'torch_cuda.dll', 'c10_cuda.dll',
                'torch_python.dll', 'caffe2_nvrtc.dll'
            ]):
                should_exclude = True
                
            # 排除大型TorchAudio文件
            if any(pattern in name.lower() for pattern in [
                'torchaudio.dll', '_torchaudio.pyd'
            ]):
                should_exclude = True
                
            # 排除大型numpy/scipy相关文件
            if any(pattern in name.lower() for pattern in [
                'mkl_', 'libopenblas', 'libblas', 'liblapack'
            ]) and name.lower().endswith(('.dll', '.so', '.dylib')):
                should_exclude = True
                
            if should_exclude:
                excluded_count += 1
                try:
                    import os
                    if os.path.exists(path):
                        total_excluded_size += os.path.getsize(path)
                except:
                    pass
                continue
                
        filtered.append(item)
    
    print(f"🗑️  已排除 {excluded_count} 个大型文件，节省约 {total_excluded_size / (1024*1024):.1f} MB")
    return filtered

# 应用过滤器
a.binaries = filter_binaries_and_datas(a.binaries)
a.datas = filter_binaries_and_datas(a.datas)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 文件夹版本（推荐用于开发和测试）
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Expert Potato',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Expert Potato',
)

# 单文件版本（可选，体积会更大）
# exe_onefile = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.datas,
#     [],
#     name='Expert Potato',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=False,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
# )
