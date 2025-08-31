#!/usr/bin/env python3
"""
PPTX 文件自定义属性读取工具
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import shutil


def read_pptx_properties(filepath: str) -> Dict[str, Any]:
    """
    读取 PPTX 文件的自定义属性
    
    Args:
        filepath: PPTX 文件路径
        
    Returns:
        包含文件属性的字典
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    if not filepath.lower().endswith('.pptx'):
        raise ValueError(f"文件不是 PPTX 格式: {filepath}")
    
    properties = {
        'core_properties': {},
        'app_properties': {},
        'custom_properties': {}
    }
    
    try:
        with zipfile.ZipFile(filepath, 'r') as pptx_zip:
            # 读取核心属性 (core.xml)
            if 'docProps/core.xml' in pptx_zip.namelist():
                core_xml = pptx_zip.read('docProps/core.xml')
                properties['core_properties'] = parse_core_properties(core_xml)
            
            # 读取应用属性 (app.xml)
            if 'docProps/app.xml' in pptx_zip.namelist():
                app_xml = pptx_zip.read('docProps/app.xml')
                properties['app_properties'] = parse_app_properties(app_xml)
            
            # 读取自定义属性 (custom.xml)
            if 'docProps/custom.xml' in pptx_zip.namelist():
                custom_xml = pptx_zip.read('docProps/custom.xml')
                properties['custom_properties'] = parse_custom_properties(custom_xml)
    
    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的 PPTX 格式: {filepath}")
    except Exception as e:
        raise RuntimeError(f"读取文件时发生错误: {e}")
    
    return properties


def parse_core_properties(xml_content: bytes) -> Dict[str, str]:
    """解析核心属性 XML"""
    properties = {}
    
    # 定义命名空间
    namespaces = {
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'dcmitype': 'http://purl.org/dc/dcmitype/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # 提取常用属性
        property_mappings = {
            'title': './/dc:title',
            'subject': './/dc:subject',
            'creator': './/dc:creator',
            'keywords': './/cp:keywords',
            'description': './/dc:description',
            'language': './/dc:language',
            'category': './/cp:category',
            'version': './/cp:version',
            'revision': './/cp:revision',
            'lastModifiedBy': './/cp:lastModifiedBy',
            'created': './/dcterms:created',
            'modified': './/dcterms:modified'
        }
        
        for prop_name, xpath in property_mappings.items():
            element = root.find(xpath, namespaces)
            if element is not None and element.text:
                properties[prop_name] = element.text.strip()
    
    except ET.ParseError as e:
        print(f"解析核心属性 XML 时出错: {e}", file=sys.stderr)
    
    return properties


def parse_app_properties(xml_content: bytes) -> Dict[str, str]:
    """解析应用属性 XML"""
    properties = {}
    
    # 定义命名空间
    namespaces = {
        'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # 提取常用属性
        property_mappings = {
            'application': './/ep:Application',
            'docSecurity': './/ep:DocSecurity',
            'scaleCrop': './/ep:ScaleCrop',
            'linksUpToDate': './/ep:LinksUpToDate',
            'pages': './/ep:Pages',
            'words': './/ep:Words',
            'characters': './/ep:Characters',
            'presentationFormat': './/ep:PresentationFormat',
            'paragraphs': './/ep:Paragraphs',
            'slides': './/ep:Slides',
            'notes': './/ep:Notes',
            'totalTime': './/ep:TotalTime',
            'hiddenSlides': './/ep:HiddenSlides',
            'mmClips': './/ep:MMClips',
            'headingPairs': './/ep:HeadingPairs',
            'titlesOfParts': './/ep:TitlesOfParts',
            'manager': './/ep:Manager',
            'company': './/ep:Company',
            'lines': './/ep:Lines',
            'paragraphs': './/ep:Paragraphs',
            'slides': './/ep:Slides',
            'notes': './/ep:Notes',
            'totalTime': './/ep:TotalTime',
            'hiddenSlides': './/ep:HiddenSlides',
            'mmClips': './/ep:MMClips'
        }
        
        for prop_name, xpath in property_mappings.items():
            element = root.find(xpath, namespaces)
            if element is not None and element.text:
                properties[prop_name] = element.text.strip()
    
    except ET.ParseError as e:
        print(f"解析应用属性 XML 时出错: {e}", file=sys.stderr)
    
    return properties


def parse_custom_properties(xml_content: bytes) -> Dict[str, str]:
    """解析自定义属性 XML"""
    properties = {}
    
    # 定义命名空间
    namespaces = {
        'cp': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
        'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # 查找所有自定义属性 - 使用正确的命名空间
        for prop in root.findall('.//cp:property', namespaces):
            name = prop.get('name')
            if name:
                # 查找属性值
                value_elem = prop.find('.//vt:lpwstr', namespaces)
                if value_elem is not None and value_elem.text:
                    properties[name] = value_elem.text.strip()
                else:
                    # 尝试其他数据类型
                    for vt_type in ['vt:i4', 'vt:r8', 'vt:bool', 'vt:filetime']:
                        value_elem = prop.find(f'.//{vt_type}', namespaces)
                        if value_elem is not None and value_elem.text:
                            properties[name] = value_elem.text.strip()
                            break
    
    except ET.ParseError as e:
        print(f"解析自定义属性 XML 时出错: {e}", file=sys.stderr)
    
    return properties


def format_properties(properties: Dict[str, Any]) -> str:
    """格式化属性输出"""
    output = []
    
    # 核心属性
    if properties['core_properties']:
        output.append("=== 核心属性 ===")
        for key, value in properties['core_properties'].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    # 应用属性
    if properties['app_properties']:
        output.append("=== 应用属性 ===")
        for key, value in properties['app_properties'].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    # 自定义属性
    if properties['custom_properties']:
        output.append("=== 自定义属性 ===")
        for key, value in properties['custom_properties'].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    if not any(properties.values()):
        output.append("未找到任何属性信息")
    
    return "\n".join(output)


def clear_pptx_properties(filepath: str, properties_to_clear: list) -> None:
    """
    清除 PPTX 文件中的指定属性
    
    Args:
        filepath: PPTX 文件路径
        properties_to_clear: 要清除的属性列表，格式为 ['core:lastModifiedBy', 'custom:ICV']
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    if not filepath.lower().endswith('.pptx'):
        raise ValueError(f"文件不是 PPTX 格式: {filepath}")
    
    try:
        with zipfile.ZipFile(filepath, 'r') as pptx_zip:
            # 创建临时文件列表
            temp_files = {}
            
            # 处理核心属性
            if 'docProps/core.xml' in pptx_zip.namelist():
                core_xml = pptx_zip.read('docProps/core.xml')
                modified_core = clear_core_property(core_xml, properties_to_clear)
                if modified_core:
                    temp_files['docProps/core.xml'] = modified_core
            
            # 处理自定义属性
            if 'docProps/custom.xml' in pptx_zip.namelist():
                custom_xml = pptx_zip.read('docProps/custom.xml')
                modified_custom = clear_custom_property(custom_xml, properties_to_clear)
                if modified_custom:
                    temp_files['docProps/custom.xml'] = modified_custom
            
            # 如果有修改，创建新的 PPTX 文件
            if temp_files:
                # 创建临时文件
                temp_pptx = filepath + '.tmp'
                
                try:
                    # 创建全新的 ZIP 文件，而不是修改现有的
                    with zipfile.ZipFile(filepath, 'r') as original_zip:
                        with zipfile.ZipFile(temp_pptx, 'w') as new_zip:
                            # 复制所有原始文件
                            for item in original_zip.infolist():
                                if item.filename not in temp_files:
                                    # 复制未修改的文件
                                    new_zip.writestr(item.filename, original_zip.read(item.filename))
                                else:
                                    # 写入修改后的文件
                                    new_zip.writestr(item.filename, temp_files[item.filename])
                    
                    # 替换原文件
                    shutil.move(temp_pptx, filepath)
                    print(f"已成功清除属性并保存到文件: {filepath}")
                    
                except Exception as e:
                    # 清理临时文件
                    if os.path.exists(temp_pptx):
                        os.remove(temp_pptx)
                    raise e
            else:
                print("未找到需要清除的属性")
    
    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的 PPTX 格式: {filepath}")
    except Exception as e:
        raise RuntimeError(f"清除属性时发生错误: {e}")


def clear_core_property(xml_content: bytes, properties_to_clear: list) -> Optional[bytes]:
    """清除核心属性中的指定属性"""
    namespaces = {
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'dcmitype': 'http://purl.org/dc/dcmitype/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    try:
        root = ET.fromstring(xml_content)
        modified = False
        
        for prop in properties_to_clear:
            if prop.startswith('core:'):
                prop_name = prop.split(':', 1)[1]
                if prop_name == 'lastModifiedBy':
                    # 查找并移除 lastModifiedBy 元素
                    element = root.find('.//cp:lastModifiedBy', namespaces)
                    if element is not None:
                        parent = root.find('.//cp:lastModifiedBy/..', namespaces)
                        if parent is not None:
                            parent.remove(element)
                            modified = True
        
        if modified:
            return ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return None
    
    except ET.ParseError as e:
        print(f"解析核心属性 XML 时出错: {e}", file=sys.stderr)
        return None


def clear_custom_property(xml_content: bytes, properties_to_clear: list) -> Optional[bytes]:
    """清除自定义属性中的指定属性"""
    namespaces = {
        'cp': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
        'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
    }
    
    try:
        root = ET.fromstring(xml_content)
        modified = False
        
        for prop in properties_to_clear:
            if prop.startswith('custom:'):
                prop_name = prop.split(':', 1)[1]
                if prop_name == 'ICV':
                    # 查找并移除 ICV 属性
                    # 使用与 parse_custom_properties 相同的方法来查找属性
                    for prop_elem in root.findall('.//cp:property', namespaces):
                        name_attr = prop_elem.get('name')
                        if name_attr == 'ICV':
                            # 找到父元素并移除该属性
                            for parent in root.iter():
                                if prop_elem in list(parent):
                                    parent.remove(prop_elem)
                                    modified = True
                                    break
        
        if modified:
            return ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return None
    
    except ET.ParseError as e:
        print(f"解析自定义属性 XML 时出错: {e}", file=sys.stderr)
        return None


def command_pptattr(filepath: str, clear_properties: bool = False) -> None:
    """
    执行 pptattr 命令
    
    Args:
        filepath: PPTX 文件路径
        clear_properties: 是否清除指定属性
    """
    try:
        if clear_properties:
            # 清除指定的属性
            properties_to_clear = ['core:lastModifiedBy', 'custom:ICV']
            # 优先使用保持 XML 结构的方法
            clear_pptx_properties_preserve_xml(filepath, properties_to_clear)
            
            print(f"清除后属性如下：")            
            properties = read_pptx_properties(filepath)
            print(format_properties(properties))
        else:
            # 读取并显示属性
            properties = read_pptx_properties(filepath)
            print(f"文件: {filepath}")
            print(format_properties(properties))
    
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1) 


def clear_pptx_properties_with_docx(filepath: str, properties_to_clear: list) -> None:
    """
    使用 python-docx 库清除 PPTX 文件中的指定属性（保持原有 XML 结构）
    
    Args:
        filepath: PPTX 文件路径
        properties_to_clear: 要清除的属性列表，格式为 ['core:lastModifiedBy', 'custom:ICV']
    """
    try:
        from docx import Document
        from docx.opc.constants import CONTENT_TYPE as CT
        from docx.oxml import parse_xml
        from docx.oxml.ns import qn
    except ImportError:
        print("警告: 未安装 python-docx 库，将使用备用方法")
        print("建议安装: pip install python-docx")
        return clear_pptx_properties(filepath, properties_to_clear)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    if not filepath.lower().endswith('.pptx'):
        raise ValueError(f"文件不是 PPTX 格式: {filepath}")
    
    try:
        # 使用 python-docx 打开文档
        doc = Document(filepath)
        
        # 获取核心属性
        core_props = doc.core_properties
        custom_props = doc.custom_properties
        
        modified = False
        
        # 清除核心属性
        for prop in properties_to_clear:
            if prop.startswith('core:'):
                prop_name = prop.split(':', 1)[1]
                if prop_name == 'lastModifiedBy' and hasattr(core_props, 'last_modified_by'):
                    if core_props.last_modified_by:
                        core_props.last_modified_by = None
                        modified = True
        
        # 清除自定义属性
        for prop in properties_to_clear:
            if prop.startswith('custom:'):
                prop_name = prop.split(':', 1)[1]
                if prop_name == 'ICV' and prop_name in custom_props:
                    del custom_props[prop_name]
                    modified = True
        
        if modified:
            # 保存文档
            doc.save(filepath)
            print(f"已成功清除属性并保存到文件: {filepath}")
        else:
            print("未找到需要清除的属性")
    
    except Exception as e:
        print(f"使用 python-docx 清除属性时发生错误: {e}")
        print("将使用备用方法...")
        return clear_pptx_properties(filepath, properties_to_clear)


def clear_pptx_properties_preserve_xml(filepath: str, properties_to_clear: list) -> None:
    """
    清除 PPTX 文件中的指定属性，尽可能保持原有 XML 结构
    
    Args:
        filepath: PPTX 文件路径
        properties_to_clear: 要清除的属性列表，格式为 ['core:lastModifiedBy', 'custom:ICV']
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    if not filepath.lower().endswith('.pptx'):
        raise ValueError(f"文件不是 PPTX 格式: {filepath}")
    
    try:
        with zipfile.ZipFile(filepath, 'r') as pptx_zip:
            # 创建临时文件列表
            temp_files = {}
            
            # 处理核心属性
            if 'docProps/core.xml' in pptx_zip.namelist():
                core_xml = pptx_zip.read('docProps/core.xml')
                modified_core = clear_core_property_preserve_xml(core_xml, properties_to_clear)
                if modified_core:
                    temp_files['docProps/core.xml'] = modified_core
            
            # 处理自定义属性
            if 'docProps/custom.xml' in pptx_zip.namelist():
                custom_xml = pptx_zip.read('docProps/custom.xml')
                modified_custom = clear_custom_property_preserve_xml(custom_xml, properties_to_clear)
                if modified_custom:
                    temp_files['docProps/custom.xml'] = modified_custom
            
            # 如果有修改，创建新的 PPTX 文件
            if temp_files:
                # 创建临时文件
                temp_pptx = filepath + '.tmp'
                shutil.copy2(filepath, temp_pptx)
                
                try:
                    # 创建全新的 ZIP 文件，而不是修改现有的
                    with zipfile.ZipFile(filepath, 'r') as original_zip:
                        with zipfile.ZipFile(temp_pptx, 'w') as new_zip:
                            # 复制所有原始文件
                            for item in original_zip.infolist():
                                if item.filename not in temp_files:
                                    # 复制未修改的文件
                                    new_zip.writestr(item.filename, original_zip.read(item.filename))
                                else:
                                    # 写入修改后的文件
                                    new_zip.writestr(item.filename, temp_files[item.filename])
                    
                    # 替换原文件
                    shutil.move(temp_pptx, filepath)
                    print(f"已成功清除属性并保存到文件: {filepath}")
                    
                except Exception as e:
                    # 清理临时文件
                    if os.path.exists(temp_pptx):
                        os.remove(temp_pptx)
                    raise e
            else:
                print("未找到需要清除的属性")
    
    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的 PPTX 格式: {filepath}")
    except Exception as e:
        raise RuntimeError(f"清除属性时发生错误: {e}")


def clear_core_property_preserve_xml(xml_content: bytes, properties_to_clear: list) -> Optional[bytes]:
    """清除核心属性中的指定属性，保持原有 XML 结构"""
    try:
        # 使用字符串操作来保持原有的 XML 结构
        xml_str = xml_content.decode('utf-8')
        modified = False
        
        for prop in properties_to_clear:
            if prop.startswith('core:'):
                prop_name = prop.split(':', 1)[1]
                if prop_name == 'lastModifiedBy':
                    # 查找并移除 lastModifiedBy 标签及其内容
                    import re
                    pattern = r'<cp:lastModifiedBy>[^<]*</cp:lastModifiedBy>'
                    if re.search(pattern, xml_str):
                        xml_str = re.sub(pattern, '', xml_str)
                        modified = True
        
        if modified:
            return xml_str.encode('utf-8')
        return None
    
    except Exception as e:
        print(f"清除核心属性时出错: {e}", file=sys.stderr)
        return None


def clear_custom_property_preserve_xml(xml_content: bytes, properties_to_clear: list) -> Optional[bytes]:
    """清除自定义属性中的指定属性，保持原有 XML 结构"""
    try:
        # 使用字符串操作来保持原有的 XML 结构
        xml_str = xml_content.decode('utf-8')
        modified = False
        
        for prop in properties_to_clear:
            if prop.startswith('custom:'):
                prop_name = prop.split(':', 1)[1]
                if prop_name == 'ICV':
                    # 查找并移除 ICV 属性标签及其内容
                    import re
                    # 匹配完整的 property 标签，包括 name="ICV" 的属性
                    pattern = r'<property[^>]*name="ICV"[^>]*>.*?</property>'
                    if re.search(pattern, xml_str, re.DOTALL):
                        xml_str = re.sub(pattern, '', xml_str, flags=re.DOTALL)
                        modified = True
        
        if modified:
            return xml_str.encode('utf-8')
        return None
    
    except Exception as e:
        print(f"清除自定义属性时出错: {e}", file=sys.stderr)
        return None 