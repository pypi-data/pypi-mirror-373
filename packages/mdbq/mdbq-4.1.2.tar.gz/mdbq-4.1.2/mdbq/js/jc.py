#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JS和CSS混淆工具
自动清除注释，默认不添加反调试

### 1. 检查工具
```bash
python3 jc.py --check
```

### 2. 安装依赖（仅首次使用）
```bash
python3 jc.py --install
```

### 3. 开始混淆
```bash
# 混淆整个项目
python3 jc.py -i ./

# 混淆指定目录
```bash
cd /Users/xigua/data2/sycm
python3 jc.py -i ./js -o /Users/xigua/Downloads/加密版本/sycm/js
python3 jc.py -i ./css -o /Users/xigua/Downloads/加密版本/sycm/css
```

## 注意事项
- 自动跳过 `.min.js` 和 `.min.css` 文件
- 保护重要的全局变量如 `window`、`document`、`navigator`

"""

import os
import subprocess
import shutil
import json
import argparse
from pathlib import Path

class EasyObfuscator:
    """极简版混淆器 - 使用全局安装的现成库"""
    
    def __init__(self, source_dir: str, output_dir: str = None):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else self.source_dir / "obfuscated"
        self.stats = {
            'js_files': 0,
            'css_files': 0,
            'other_files': 0,
            'errors': 0
        }
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def obfuscate_js_simple(self, input_file: Path, output_file: Path):
        """使用简单方法混淆JS文件"""
        try:
            # 首先尝试使用 javascript-obfuscator
            cmd = [
                'javascript-obfuscator', 
                str(input_file),
                '--output', str(output_file),
                '--compact', 'true',
                '--string-array', 'true',
                '--string-array-encoding', 'base64',
                '--string-array-threshold', '0.75',
                '--transform-object-keys', 'true',
                '--unicode-escape-sequence', 'false',
                '--debug-protection', 'false',
                '--self-defending', 'false',
                '--control-flow-flattening', 'false'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  ✅ JS混淆: {input_file.name}")
            self.stats['js_files'] += 1
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 备选方案：使用 terser
            try:
                cmd = [
                    'terser', str(input_file),
                    '--compress', 'drop_console=false,drop_debugger=true',
                    '--mangle', 'reserved=["window","document","navigator"]',
                    '--output', str(output_file),
                    '--comments', 'false'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"  ✅ JS压缩: {input_file.name}")
                self.stats['js_files'] += 1
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 最后备选：直接复制
                shutil.copy2(input_file, output_file)
                print(f"  ⚠️  JS复制: {input_file.name} (混淆工具不可用)")
                self.stats['other_files'] += 1
                return False
    
    def obfuscate_css_simple(self, input_file: Path, output_file: Path):
        """使用简单方法压缩CSS文件"""
        try:
            # 尝试使用 csso
            cmd = [
                'csso',
                '--input', str(input_file),
                '--output', str(output_file),
                '--restructure-off'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  ✅ CSS压缩: {input_file.name}")
            self.stats['css_files'] += 1
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 备选方案：使用 cleancss
            try:
                cmd = [
                    'cleancss',
                    '--output', str(output_file),
                    str(input_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"  ✅ CSS压缩: {input_file.name}")
                self.stats['css_files'] += 1
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 最后备选：手动简单压缩
                self.manual_css_compress(input_file, output_file)
                return False
    
    def manual_css_compress(self, input_file: Path, output_file: Path):
        """手动进行简单的CSS压缩"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # 简单的CSS压缩
            import re
            
            # 移除注释
            css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
            
            # 移除多余空白
            css_content = re.sub(r'\s+', ' ', css_content)
            css_content = re.sub(r';\s*}', ';}', css_content)
            css_content = re.sub(r'{\s*', '{', css_content)
            css_content = re.sub(r'}\s*', '}', css_content)
            css_content = re.sub(r';\s*', ';', css_content)
            
            css_content = css_content.strip()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            print(f"  ✅ CSS手动压缩: {input_file.name}")
            self.stats['css_files'] += 1
            
        except Exception as e:
            print(f"  ❌ CSS处理失败 {input_file.name}: {e}")
            shutil.copy2(input_file, output_file)
            self.stats['errors'] += 1
    
    def copy_other_files(self, input_file: Path, output_file: Path):
        """复制其他文件"""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(input_file, output_file)
            self.stats['other_files'] += 1
        except Exception as e:
            print(f"  ❌ 复制文件失败 {input_file.name}: {e}")
            self.stats['errors'] += 1
    
    def process_all_files(self):
        """处理所有文件"""
        print(f"🚀 开始处理目录: {self.source_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        
        # 确保输出目录存在
        self.ensure_output_dir()
        
        # 遍历所有文件
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file():
                # 跳过一些不需要处理的文件
                if (file_path.name.startswith('.') or 
                    'node_modules' in str(file_path) or
                    'obfuscated' in str(file_path) or
                    '__pycache__' in str(file_path)):
                    continue
                
                # 计算相对路径
                relative_path = file_path.relative_to(self.source_dir)
                output_path = self.output_dir / relative_path
                
                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 根据文件类型处理
                if file_path.suffix.lower() == '.js':
                    # 跳过已经压缩的文件
                    if not file_path.name.endswith('.min.js'):
                        self.obfuscate_js_simple(file_path, output_path)
                    else:
                        self.copy_other_files(file_path, output_path)
                        
                elif file_path.suffix.lower() == '.css':
                    # 跳过已经压缩的文件
                    if not file_path.name.endswith('.min.css'):
                        self.obfuscate_css_simple(file_path, output_path)
                    else:
                        self.copy_other_files(file_path, output_path)
                        
                else:
                    # 其他文件直接复制
                    self.copy_other_files(file_path, output_path)
        
        # 打印统计信息
        self.print_stats()
    
    def print_stats(self):
        """打印处理统计"""
        print("\n" + "="*50)
        print("📊 处理完成统计:")
        print(f"  JavaScript文件: {self.stats['js_files']}")
        print(f"  CSS文件: {self.stats['css_files']}")
        print(f"  其他文件: {self.stats['other_files']}")
        print(f"  错误: {self.stats['errors']}")
        print(f"  总计: {sum(self.stats.values())}")
        print(f"\n✅ 混淆文件已保存到: {self.output_dir}")
        print("="*50)
    
    def check_tools(self):
        """检查可用的工具"""
        print("🔍 检查可用工具...")
        
        tools = {
            'javascript-obfuscator': 'JavaScript混淆器',
            'terser': 'JavaScript压缩器',
            'csso': 'CSS优化器',
            'cleancss': 'CSS压缩器'
        }
        
        available_tools = []
        for tool, description in tools.items():
            try:
                subprocess.run([tool, '--version'], 
                             capture_output=True, check=True)
                print(f"  ✅ {tool}: {description}")
                available_tools.append(tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"  ❌ {tool}: 未安装")
        
        if not available_tools:
            print("\n⚠️  没有找到任何混淆工具！")
            print("请先安装：npm install -g javascript-obfuscator terser csso-cli clean-css-cli")
            return False
        
        print(f"\n✅ 找到 {len(available_tools)} 个可用工具")
        return True

def install_tools():
    """安装混淆工具"""
    print("📦 安装混淆工具...")
    
    try:
        cmd = ['npm', 'install', '-g', 
               'javascript-obfuscator', 
               'terser', 
               'csso-cli', 
               'clean-css-cli']
        
        result = subprocess.run(cmd, check=True)
        print("✅ 工具安装完成！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        print("\n请手动执行:")
        print("npm install -g javascript-obfuscator terser csso-cli clean-css-cli")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="极简版代码混淆工具 - 使用现成流行库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python jc.py -i ./js
  python jc.py -i ./ -o ./dist
  python jc.py -i ./src --install
        """
    )
    
    parser.add_argument('-i', '--input', 
                       help='输入目录路径')
    
    parser.add_argument('-o', '--output', 
                       help='输出目录路径 (默认: 输入目录/obfuscated)')
    
    parser.add_argument('--install', 
                       action='store_true', 
                       help='自动安装所需的 npm 工具')
    
    parser.add_argument('--check', 
                       action='store_true', 
                       help='检查可用工具')
    
    parser.add_argument('--version', 
                       action='version', 
                       version='%(prog)s 3.0.0')
    
    args = parser.parse_args()
    
    # 只检查工具
    if args.check:
        obfuscator = EasyObfuscator(".", ".")
        obfuscator.check_tools()
        return
    
    # 安装工具
    if args.install:
        if install_tools():
            print("现在可以开始混淆了！")
        return
    
    # 如果没有指定输入目录且不是检查/安装模式，则报错
    if not args.input:
        print("❌ 请指定输入目录: -i <目录路径>")
        print("或使用 --check 检查工具，--install 安装工具")
        return
    
    # 检查输入目录
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_path}")
        return
    
    if not input_path.is_dir():
        print(f"❌ 输入路径不是目录: {input_path}")
        return
    
    # 创建混淆器实例
    obfuscator = EasyObfuscator(
        source_dir=str(input_path),
        output_dir=args.output
    )
    
    try:
        # 检查工具可用性
        if not obfuscator.check_tools():
            print("\n💡 尝试运行: python jc.py --install")
            return
        
        # 开始处理
        obfuscator.process_all_files()
        print("\n🎉 混淆完成！文件已受到保护，可以安全部署。")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")

if __name__ == "__main__":
    main() 