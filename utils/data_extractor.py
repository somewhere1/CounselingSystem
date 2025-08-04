"""
Data extraction utilities for the counseling system.
Extracts stages and suggestions from counseling dialogue JSON files.
"""

import os
import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class StageExtractor:
    """用于从JSON文件中提取对话的"所处阶段"信息的工具类"""
    
    def __init__(self):
        # 定义一个极其宽松的正则表达式，仅用于定位"所处阶段"并捕获其后的所有内容
        self.stage_finder = re.compile(r'所处阶段(.*)')
        
    def extract_stages_from_directory(self, directory_path: str) -> Tuple[Optional[Dict[str, List[Optional[str]]]], Optional[List[str]]]:
        """
        从指定目录下的所有JSON文件中提取"所处阶段"信息。
        
        Args:
            directory_path (str): 要扫描的目录路径
            
        Returns:
            tuple: 包含两个元素的元组
                - 第一个元素 (dict): 文件名到阶段列表的映射
                - 第二个元素 (list): 处理过程中出错的文件名列表
        """
        all_stages_data = {}
        error_files = []
        
        if not os.path.isdir(directory_path):
            logger.error(f"目录 '{directory_path}' 不存在")
            return None, None
        
        files_to_process = sorted([f for f in os.listdir(directory_path) if f.endswith('.json')])
        logger.info(f"在 '{directory_path}' 目录中找到 {len(files_to_process)} 个JSON文件")
        
        for filename in files_to_process:
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    logger.warning(f"文件 '{filename}' 的顶层内容不是列表，已跳过")
                    error_files.append(filename)
                    continue
                
                file_stages = []
                # 遍历文件中的每一个内部列表（代表一个对话回合）
                for i, turn_list in enumerate(data):
                    stage = None  # 默认值为None，确保即使提取失败也占位
                    
                    if isinstance(turn_list, list) and turn_list:
                        last_item_str = turn_list[0]
                        
                        if isinstance(last_item_str, str):
                            match = self.stage_finder.search(last_item_str)
                            if match:
                                # 第一步：获取"所处阶段"之后的所有原始文本
                                raw_content = match.group(1)
                                
                                # 第二步：清洗前后多余的符号，提取核心内容
                                # 清除开头的非字母数字字符（如 '":"' 或 '\\":\\"'）
                                cleaned_content = re.sub(r'^[":\s\\]+', '', raw_content)
                                # 清除结尾的非字母数字字符（如 '"}' 或 '\\"}'）
                                cleaned_content = re.sub(r'["\\}\s]*$', '', cleaned_content)
                                
                                stage = cleaned_content.strip()
                            else:
                                logger.warning(f"文件 '{filename}', 回合 {i+1}, 未找到 '所处阶段'")
                        else:
                            logger.warning(f"文件 '{filename}', 回合 {i+1}, 末尾项不是字符串")
                    else:
                        logger.warning(f"文件 '{filename}', 回合 {i+1}, 内容为空或格式不正确")
                    
                    file_stages.append(stage)
                
                # 双重验证：确保提取的列表长度与原始数据长度一致
                if len(file_stages) != len(data):
                    logger.error(f"文件 '{filename}' 处理后长度不匹配({len(file_stages)} vs {len(data)})，已跳过")
                    error_files.append(filename)
                    continue
                
                all_stages_data[filename] = file_stages
                
            except json.JSONDecodeError:
                logger.error(f"文件 '{filename}' 包含无效的JSON格式，已跳过")
                error_files.append(filename)
            except Exception as e:
                logger.error(f"处理文件 '{filename}' 时发生未知错误: {e}")
                error_files.append(filename)
        
        return all_stages_data, error_files
    
    def save_extracted_stages(self, extracted_data: Dict[str, List[Optional[str]]], 
                             output_json_file: str, output_txt_file: str) -> None:
        """
        保存提取的阶段数据到JSON和文本文件
        
        Args:
            extracted_data: 提取的阶段数据
            output_json_file: 输出JSON文件路径
            output_txt_file: 输出文本文件路径
        """
        # 保存到JSON文件
        logger.info(f"正在将结果保存到 '{output_json_file}'...")
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        
        # 保存到纯文本文件以便查看
        logger.info(f"正在将纯文本结果保存到 '{output_txt_file}'...")
        with open(output_txt_file, 'w', encoding='utf-8') as f:
            for filename, stages in extracted_data.items():
                f.write(f"--- {filename} ---\n")
                if stages:
                    # 将None转换为特定标记以便打印
                    printable_stages = [s if s is not None else "[阶段未找到]" for s in stages]
                    f.write("\n".join(printable_stages))
                else:
                    f.write("未提取到任何阶段。")
                f.write("\n\n")


class SuggestionExtractor:
    """用于从JSON文件中提取"改进意见"的工具类"""
    
    def __init__(self):
        # 用于找到"改进意见"键值的正则表达式
        self.suggestion_pattern = re.compile(r'"改进意见":"((?:[^"\\]|\\.)*)"')
    
    def extract_suggestions_structured(self, source_folder: str, output_folder: str) -> List[str]:
        """
        从源文件夹中的所有JSON文件提取"改进意见"，保持原始列表结构
        
        Args:
            source_folder: 源文件夹路径
            output_folder: 输出文件夹路径
            
        Returns:
            List[str]: 验证失败的文件名列表
        """
        if not os.path.isdir(source_folder):
            logger.error(f"源文件夹 '{source_folder}' 未找到")
            return []
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            logger.info(f"已创建输出文件夹: '{output_folder}'")
        
        failed_validation_files = []
        
        logger.info(f"正在扫描 '{source_folder}' 中的文件...")
        for filename in os.listdir(source_folder):
            if not filename.endswith('.json'):
                continue
            
            source_file_path = os.path.join(source_folder, filename)
            output_file_path = os.path.join(output_folder, filename)
            
            logger.info(f"正在处理文件: {filename}")
            
            try:
                with open(source_file_path, 'r', encoding='utf-8') as f:
                    original_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"文件 {filename} 不是有效的JSON。跳过。错误: {e}")
                continue
            except Exception as e:
                logger.warning(f"无法读取或处理文件 {filename}。跳过。错误: {e}")
                continue
            
            original_outer_len = len(original_data)
            original_inner_lens = [len(sublist) for sublist in original_data]
            
            suggestions_data = []
            
            for original_inner_list in original_data:
                new_inner_list = []
                for item_string in original_inner_list:
                    # 在当前项字符串中查找所有建议
                    matches = self.suggestion_pattern.findall(item_string)
                    
                    if matches:
                        # 如果字符串格式不正确，可能有多个匹配
                        # 我们将它们连接以保留所有信息
                        new_inner_list.append(" | ".join(matches))
                    else:
                        # 如果没有找到建议，添加占位符以保持长度一致
                        new_inner_list.append("未找到改进意见")
                
                suggestions_data.append(new_inner_list)
            
            # 验证步骤
            new_outer_len = len(suggestions_data)
            new_inner_lens = [len(sublist) for sublist in suggestions_data]
            
            logger.debug(f"- 原始结构: 外层列表长度 = {original_outer_len}, 内层列表长度 = {original_inner_lens}")
            logger.debug(f"- 提取后结构: 外层列表长度 = {new_outer_len}, 内层列表长度 = {new_inner_lens}")
            
            if original_outer_len == new_outer_len and original_inner_lens == new_inner_lens:
                logger.info("- 验证成功: 内外层列表的长度与原文件一致")
            else:
                logger.warning("- 验证失败: 提取后的结构与原文件不匹配。仍会保存文件")
                failed_validation_files.append(filename)
            
            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(suggestions_data, f, ensure_ascii=False, indent=4)
                logger.info(f"- 结果已保存至: {output_file_path}")
            except Exception as e:
                logger.error(f"- 错误: 无法写入文件 {output_file_path}。错误: {e}")
        
        if failed_validation_files:
            logger.warning(f"以下 {len(failed_validation_files)} 个文件未能通过结构验证:")
            for f_name in failed_validation_files:
                logger.warning(f"  - {f_name}")
        else:
            logger.info("所有文件均已成功处理并通过验证")
        
        return failed_validation_files


class DataExtractor:
    """数据提取工具的主类，整合阶段和建议提取功能"""
    
    def __init__(self):
        self.stage_extractor = StageExtractor()
        self.suggestion_extractor = SuggestionExtractor()
    
    def extract_stages_from_directory(self, directory_path: str, 
                                    output_json_file: str = 'extracted_stages.json',
                                    output_txt_file: str = 'extracted_stages.txt') -> Tuple[Optional[Dict[str, List[Optional[str]]]], Optional[List[str]]]:
        """
        从目录中提取所有文件的阶段信息
        
        Args:
            directory_path: 要扫描的目录路径
            output_json_file: 输出JSON文件名
            output_txt_file: 输出文本文件名
            
        Returns:
            tuple: (提取的数据, 错误文件列表)
        """
        logger.info(f"开始从目录 '{directory_path}' 中提取'所处阶段'信息...")
        
        extracted_data, errors = self.stage_extractor.extract_stages_from_directory(directory_path)
        
        if extracted_data is not None:
            logger.info(f"提取完成。成功处理 {len(extracted_data)} 个文件")
            
            if errors:
                logger.warning(f"处理过程中有 {len(errors)} 个文件遇到问题")
            
            # 保存提取的数据
            self.stage_extractor.save_extracted_stages(extracted_data, output_json_file, output_txt_file)
            logger.info("所有操作已完成")
        
        return extracted_data, errors
    
    def extract_suggestions_from_directory(self, source_folder: str, 
                                         output_folder: str = 'suggestions_only') -> List[str]:
        """
        从目录中提取所有文件的建议信息
        
        Args:
            source_folder: 源文件夹路径
            output_folder: 输出文件夹路径
            
        Returns:
            List[str]: 验证失败的文件名列表
        """
        logger.info(f"开始从目录 '{source_folder}' 中提取'改进意见'信息...")
        
        failed_files = self.suggestion_extractor.extract_suggestions_structured(source_folder, output_folder)
        
        if failed_files:
            logger.warning(f"有 {len(failed_files)} 个文件验证失败")
        else:
            logger.info("所有文件均已成功处理")
        
        return failed_files
    
    def process_counseling_data(self, base_directory: str, 
                               stages_output_prefix: str = 'extracted_stages',
                               suggestions_output_folder: str = 'suggestions_only') -> Dict[str, Any]:
        """
        处理心理咨询数据，同时提取阶段和建议信息
        
        Args:
            base_directory: 基础数据目录
            stages_output_prefix: 阶段输出文件前缀
            suggestions_output_folder: 建议输出文件夹
            
        Returns:
            Dict: 处理结果统计
        """
        results = {
            'stages': {'success': 0, 'errors': []},
            'suggestions': {'success': 0, 'failed_validation': []}
        }
        
        # 提取阶段信息
        stages_data, stage_errors = self.extract_stages_from_directory(
            base_directory,
            f'{stages_output_prefix}.json',
            f'{stages_output_prefix}.txt'
        )
        
        if stages_data:
            results['stages']['success'] = len(stages_data)
            results['stages']['errors'] = stage_errors or []
        
        # 提取建议信息
        failed_validations = self.extract_suggestions_from_directory(
            base_directory,
            suggestions_output_folder
        )
        
        # 计算成功处理的文件数
        json_files = [f for f in os.listdir(base_directory) if f.endswith('.json')]
        results['suggestions']['success'] = len(json_files) - len(failed_validations)
        results['suggestions']['failed_validation'] = failed_validations
        
        return results


# 便捷函数
def extract_stages_from_folder(folder_path: str, output_prefix: str = 'extracted_stages') -> Tuple[Optional[Dict[str, List[Optional[str]]]], Optional[List[str]]]:
    """快速提取阶段信息的便捷函数"""
    extractor = DataExtractor()
    return extractor.extract_stages_from_directory(
        folder_path,
        f'{output_prefix}.json',
        f'{output_prefix}.txt'
    )


def extract_suggestions_from_folder(source_folder: str, output_folder: str = 'suggestions_only') -> List[str]:
    """快速提取建议信息的便捷函数"""
    extractor = DataExtractor()
    return extractor.extract_suggestions_from_directory(source_folder, output_folder)


def process_counseling_data_folder(base_directory: str) -> Dict[str, Any]:
    """处理心理咨询数据文件夹的便捷函数"""
    extractor = DataExtractor()
    return extractor.process_counseling_data(base_directory) 