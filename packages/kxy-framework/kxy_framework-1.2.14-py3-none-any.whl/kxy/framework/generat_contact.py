import os
import re

def generate_interface_files_recursive(sevices_folder='services', source_dir: str = None):
    """
    递归遍历指定目录下的所有Python文件，为services目录下的文件生成对应的接口文件
    接口文件统一生成到 app/contract/+parent_folder 目录下
    
    Args:
        source_dir (str): 源代码目录路径，默认为当前目录
    """
    
    if source_dir is None:
        source_dir = os.path.dirname(__file__)
    
    # 遍历所有目录，寻找名为services的文件夹
    for root, dirs, files in os.walk(source_dir):
        # 检查当前目录是否为services目录
        if os.path.basename(root) == sevices_folder:
            # 获取上级目录作为parent_folder
            parent_folder = os.path.basename(os.path.dirname(root))
            
            # 构建接口文件输出目录路径: app/contract/+parent_folder
            contract_base_dir = os.path.join(source_dir, 'app', 'contract')
            contract_output_dir = os.path.join(contract_base_dir, parent_folder)
            
            # 创建输出目录（如果不存在）
            os.makedirs(contract_output_dir, exist_ok=True)
            
            print(f"处理目录: {root}")
            print(f"接口文件将生成到: {contract_output_dir}")
            
            # 获取services目录下所有.py文件（排除__init__.py和已有的接口文件）
            py_files = [
                f for f in files 
                if f.endswith(".py") 
                and f != "__init__.py" 
                and not f.startswith("I")
            ]
            
            for file in py_files:
                file_path = os.path.join(root, file)
                interface_file_name = "I" + file
                interface_file_path = os.path.join(contract_output_dir, interface_file_name)
          
                # 提取文件中的类
                file_content = extract_file_content(file_path)
                
                if file_content['classes']:
                    # 生成接口文件内容
                    interface_content = generate_interface_content(file, file_content)
                    
                    # 写入接口文件
                    with open(interface_file_path, 'w', encoding='utf-8') as f:
                        f.write(interface_content)
                    
                    print(f"成功生成接口文件: {interface_file_name}")

def extract_file_content(file_path: str) -> dict:
    """
    从指定的Python文件中提取导入语句和类定义
    
    Args:
        file_path (str): Python文件路径
        
    Returns:
        dict: 包含导入语句和类信息的字典
    """
    result = {
        'imports': [],
        'classes': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取导入语句
        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            # 检查是否为导入语句
            if (line_stripped.startswith('import ') or line_stripped.startswith('from ')) and 'import' in line_stripped:
                result['imports'].append(line_stripped)
        
        # 使用正则表达式匹配类定义
        class_pattern = r'class\s+(\w+)(?:\s*\(([^)]*)\))?:\s*(.*?)(?=\n\S|\Z)'
        matches = re.finditer(class_pattern, content, re.DOTALL)
        
        for match in matches:
            class_name = match.group(1)
            parent_classes = match.group(2) if match.group(2) else ""
            class_body = match.group(3).strip()
            
            result['classes'].append({
                'name': class_name,
                'parents': parent_classes,
                'body': class_body
            })
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        
    return result

def generate_interface_content(original_file_name: str, file_content: dict) -> str:
    """
    生成接口文件的内容
    
    Args:
        original_file_name (str): 原始文件名
        file_content (dict): 文件内容，包括导入语句和类信息
        
    Returns:
        str: 接口文件内容
    """
    # 添加文件头注释
    content = f'# 接口文件 (基于 {original_file_name} 生成)\n\n'
    
    # 添加ABC导入语句（如果还没有）
    abc_import_needed = True
    abstractmethod_import_needed = True
    
    for imp in file_content['imports']:
        if 'from abc' in imp or 'import abc' in imp:
            abc_import_needed = False
            if 'abstractmethod' in imp:
                abstractmethod_import_needed = False
            break
    
    if abc_import_needed:
        content += 'from abc import ABC, abstractmethod\n'
    elif abstractmethod_import_needed:
        # 检查是否需要单独导入abstractmethod
        has_abstractmethod = any('from abc import' in imp and 'abstractmethod' in imp for imp in file_content['imports'])
        if not has_abstractmethod:
            content += 'from abc import abstractmethod\n'
    
    content += "\n"
    
    # 为每个类生成接口
    for cls in file_content['classes']:
        interface_name = f"I{cls['name']}"
        parents = "ABC"
        
        # 如果父类列表中没有ABC，添加它
        if "ABC" not in parents:
            if parents.strip():
                parents = f"{parents}, ABC"
            else:
                parents = "ABC"
        
        content += f"\nclass {interface_name}({parents}):\n"
        
        # 提取类体中的方法定义
        class_body = cls['body']
        methods = extract_methods_from_body(class_body)
        
        if methods:
            content += methods
        else:
            # 如果没有提取到方法，添加默认的抽象方法占位符
            content += "    @abstractmethod\n"
            content += "    def placeholder_method(self):\n"
            content += "        pass\n"
    
    return content

def extract_methods_from_body(class_body: str) -> str:
    """
    从类体中提取方法定义并转换为抽象方法，移除参数类型注解和返回类型注解
    
    Args:
        class_body (str): 类体内容
        
    Returns:
        str: 抽象方法定义
    """
    # 修改正则表达式，匹配函数定义（包括返回类型注解）
    method_pattern = r'def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*[^:]+)?\s*:'
    matches = re.finditer(method_pattern, class_body)
    
    methods_content = ""
    for match in matches:
        method_name = match.group(1)
        method_params = match.group(2)
        
        # 跳过特殊方法（如 __init__ 等）
        if method_name.startswith('__') and method_name.endswith('__'):
            continue
            
        # 移除参数中的类型注解
        cleaned_params = remove_type_annotations(method_params)
        
        methods_content += f"    @abstractmethod\n"
        methods_content += f"    async def {method_name}({cleaned_params}):\n"
        methods_content += f"        pass\n\n"
        
    return methods_content


def remove_type_annotations(params: str) -> str:
    """
    移除参数字符串中的类型注解，支持复杂类型如 Dict[str, object]
    
    Args:
        params (str): 参数字符串，如 "self, name: str, age: int = 18"
        
    Returns:
        str: 移除类型注解后的参数字符串，如 "self, name, age=18"
    """
    if not params:
        return params
    
    # 分割参数，但需要处理可能包含逗号的复杂类型注解
    param_parts = []
    current_part = ""
    bracket_count = 0
    in_brackets = False
    
    for char in params:
        if char == ',' and bracket_count == 0:
            param_parts.append(current_part.strip())
            current_part = ""
        else:
            if char in '[({':
                bracket_count += 1
                in_brackets = True
            elif char in '])}':
                bracket_count -= 1
                if bracket_count == 0:
                    in_brackets = False
            current_part += char
    
    if current_part:
        param_parts.append(current_part.strip())
    
    cleaned_params = []
    
    for param in param_parts:
        param = param.strip()
        
        # 处理 *args 和 **kwargs
        if param.startswith('*'):
            if ':' in param:
                # 分离参数名和类型注解
                parts = param.split(':', 1)
                param_name = parts[0].strip()
                annotation_part = parts[1].strip()
                
                # 检查是否有默认值
                if '=' in annotation_part:
                    annotation_and_default = annotation_part.split('=', 1)
                    type_annotation = annotation_and_default[0].strip()
                    default_value = annotation_and_default[1].strip()
                    param = f"{param_name}={default_value}"
                else:
                    param = param_name
        elif ':' in param:
            # 普通参数有类型注解
            parts = param.split(':', 1)
            param_name = parts[0].strip()
            annotation_part = parts[1].strip()
            
            # 检查是否有默认值
            if '=' in annotation_part:
                annotation_and_default = annotation_part.split('=', 1)
                type_annotation = annotation_and_default[0].strip()
                default_value = annotation_and_default[1].strip()
                param = f"{param_name}={default_value}"
            else:
                param = param_name
        # 否则保持原样（没有类型注解）
        
        cleaned_params.append(param)
    
    return ', '.join(cleaned_params)