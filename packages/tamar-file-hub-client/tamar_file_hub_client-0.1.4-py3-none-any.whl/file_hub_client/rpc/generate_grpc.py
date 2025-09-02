"""
生成gRPC Python代码的脚本
"""
import os
import subprocess
from pathlib import Path


def generate_grpc_code():
    """生成gRPC Python代码"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    proto_dir = current_dir / "protos"
    gen_dir = current_dir / "gen"
    
    # 创建生成目录
    gen_dir.mkdir(exist_ok=True)
    
    # 创建__init__.py文件
    (gen_dir / "__init__.py").touch()
    
    # 获取所有proto文件
    proto_files = list(proto_dir.glob("*.proto"))
    
    for proto_file in proto_files:
        print(f"生成 {proto_file.name} 的Python代码...")
        
        # 生成gRPC代码
        cmd = [
            "python3", "-m", "grpc_tools.protoc",
            f"-I{proto_dir}",
            f"--python_out={gen_dir}",
            f"--grpc_python_out={gen_dir}",
            str(proto_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            raise RuntimeError(f"生成gRPC代码失败: {result.stderr}")
        else:
            print(f"成功生成 {proto_file.name}")
    
    # 修复导入路径
    fix_imports(gen_dir)
    
    print("所有gRPC代码生成完成！")


def fix_imports(gen_dir):
    """修复生成的Python文件中的导入路径"""
    for py_file in gen_dir.glob("*_pb2*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 修复导入路径 - 现在有多个proto文件
        for proto_name in ["file_service", "folder_service", "taple_service"]:
            content = content.replace(f"import {proto_name}_pb2", f"from . import {proto_name}_pb2")
        
        with open(py_file, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    """命令行入口点"""
    try:
        generate_grpc_code()
    except Exception as e:
        print(f"生成失败: {e}")
        return 1
    return 0


if __name__ == "__main__":
    generate_grpc_code() 