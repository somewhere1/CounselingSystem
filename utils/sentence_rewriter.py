"""
Sentence rewriter utility for the counseling system.
Rewrites formal sentences to natural, conversational language.
"""

import logging
from typing import Optional, List, Dict, Any
from ..llm_client import get_llm_client
from ..config import config

logger = logging.getLogger(__name__)


class SentenceRewriter:
    """使用大语言模型改写句子的工具类"""
    
    def __init__(self, model_name: str = None):
        """
        初始化改写器
        
        Args:
            model_name: 使用的模型名称，默认使用系统配置的对话模型
        """
        self.llm_client = get_llm_client()
        self.model_name = model_name or config.model.CONVERSATION_MODEL
        
        # 改写句子的提示词模板
        self.rewrite_prompt = """
你是一位语言专家，专门将正式、生硬的表达改写成自然、符合人类说话习惯的句子。

## 改写原则：
1. **口语化**：使用日常对话中的表达方式
2. **自然流畅**：符合中文的语言习惯
3. **温暖亲切**：保持友好、支持的语调
4. **简洁明了**：避免冗长复杂的句式
5. **保持原意**：不改变句子的核心含义

## 具体要求：
- 避免过于正式的连接词
- 保持疑问语气的自然性
- 适合心理咨询师与来访者对话的语境

## 改写示例：
原句：今天我们可以先聊聊你现在的感受，看看是什么让你最近觉得迷茫。
改写：我们先来聊聊你最近的感受吧，有什么特别的事情让你觉得困扰吗？

原句：请您描述一下您的情绪状态。
改写：你能跟我说说你现在的心情怎么样吗？

## 任务：
上下文：{context}
需要改写的句子：{sentence}

请根据上下文，将句子改写得更自然、更符合人类说话习惯。

要求：
- 保持专业但亲切的语调
- 使用自然的中文表达
- 让来访者感到舒适和被理解
- 只返回改写后的句子，不要其他解释
"""
    
    def rewrite_sentence(self, sentence: str, temperature: float = 0.7) -> str:
        """
        改写单个句子（无上下文）
        
        Args:
            sentence: 要改写的句子
            temperature: 生成的随机性
            
        Returns:
            改写后的句子
        """
        return self.rewrite_with_context(sentence, "心理咨询对话场景", temperature)
    
    def rewrite_with_context(self, sentence: str, context: str, temperature: float = 0.7) -> str:
        """
        带上下文的句子改写
        
        Args:
            sentence: 要改写的句子
            context: 上下文信息
            temperature: 生成的随机性
            
        Returns:
            改写后的句子
        """
        try:
            # 构建完整的提示词
            prompt = self.rewrite_prompt.format(context=context, sentence=sentence)
            
            messages = [
                {"role": "system", "content": "你是一位专业的语言专家，擅长改写句子。"},
                {"role": "user", "content": prompt}
            ]
            
            # 使用统一的LLM客户端
            rewritten = self.llm_client.generate_conversation_response(
                messages, 
                temperature=temperature
            )
            
            logger.debug(f"句子改写成功: {sentence[:30]}... -> {rewritten[:30]}...")
            return rewritten.strip()
            
        except Exception as e:
            logger.error(f"带上下文改写失败: {str(e)}")
            return sentence

    def rewrite_multiple_sentences(self, sentences: List[str], temperature: float = 0.7) -> List[Dict[str, str]]:
        """
        批量改写多个句子（无上下文）
        
        Args:
            sentences: 要改写的句子列表
            temperature: 生成的随机性
            
        Returns:
            改写后的句子列表，格式: [{"original": "原句", "rewritten": "改写后"}, ...]
        """
        sentences_with_context = [
            {"sentence": sentence, "context": "心理咨询对话场景"} 
            for sentence in sentences
        ]
        
        return self.rewrite_multiple_with_context(sentences_with_context, temperature)

    def rewrite_multiple_with_context(self, sentences_with_context: List[Dict[str, str]], temperature: float = 0.7) -> List[Dict[str, str]]:
        """
        批量改写多个带上下文的句子
        
        Args:
            sentences_with_context: 包含句子和上下文的列表，格式: [{"sentence": "句子", "context": "上下文"}, ...]
            temperature: 生成的随机性
            
        Returns:
            改写后的句子列表
        """
        rewritten_sentences = []
        
        for i, item in enumerate(sentences_with_context):
            logger.info(f"正在改写第 {i+1}/{len(sentences_with_context)} 句...")
            
            sentence = item.get('sentence', '')
            context = item.get('context', '')
            
            rewritten = self.rewrite_with_context(sentence, context, temperature)
            rewritten_sentences.append({
                'original': sentence,
                'context': context,
                'rewritten': rewritten
            })
        
        return rewritten_sentences
    
    def rewrite_cbt_stage_sentences(self, sentences: List[str], stage: str, temperature: float = 0.7) -> List[Dict[str, str]]:
        """
        根据CBT阶段改写句子
        
        Args:
            sentences: 要改写的句子列表
            stage: CBT阶段名称
            temperature: 生成的随机性
            
        Returns:
            改写后的句子列表
        """
        # CBT阶段对应的上下文
        stage_contexts = {
            "设置议程": "CBT咨询的议程设置阶段，需要与来访者建立融洽关系并确定会话重点",
            "情绪检查": "CBT咨询的情绪检查阶段，需要温和地了解来访者的情绪状态",
            "获取信息": "CBT咨询的信息收集阶段，需要关心地询问来访者的情况",
            "讨论诊断": "CBT咨询的诊断讨论阶段，需要用通俗语言解释，避免标签化",
            "问题识别": "CBT咨询的问题识别阶段，需要引导来访者思考和探索",
            "认知模型": "CBT咨询的认知模型教育阶段，需要通俗易懂地解释认知与情绪的关系",
            "行为激活": "CBT咨询的行为激活阶段，需要鼓励和支持来访者采取行动",
            "总结作业": "CBT咨询的总结布置作业阶段，需要鼓励和支持的语调"
        }
        
        context = stage_contexts.get(stage, "CBT心理咨询对话场景")
        
        sentences_with_context = [
            {"sentence": sentence, "context": context} 
            for sentence in sentences
        ]
        
        return self.rewrite_multiple_with_context(sentences_with_context, temperature)
    
    def enhance_counselor_response(self, response: str, stage: str = "对话") -> str:
        """
        增强咨询师回复的自然度
        
        Args:
            response: 咨询师的原始回复
            stage: 当前CBT阶段
            
        Returns:
            增强后的回复
        """
        context = f"CBT心理咨询的{stage}阶段，咨询师需要用自然、温暖的语言与来访者交流"
        
        return self.rewrite_with_context(response, context)


class CounselorResponseEnhancer:
    """咨询师回复增强器"""
    
    def __init__(self):
        self.rewriter = SentenceRewriter()
    
    def enhance_response(self, response: str, dialogue_context: Dict[str, Any]) -> str:
        """
        根据对话上下文增强咨询师回复
        
        Args:
            response: 原始回复
            dialogue_context: 对话上下文信息
            
        Returns:
            增强后的回复
        """
        # 提取上下文信息
        current_stage = dialogue_context.get('current_stage', '对话')
        patient_emotion = dialogue_context.get('patient_emotion', '平静')
        session_type = dialogue_context.get('session_type', '首次会话')
        
        # 构建详细上下文
        detailed_context = f"CBT心理咨询的{current_stage}阶段，{session_type}，来访者情绪状态：{patient_emotion}"
        
        return self.rewriter.rewrite_with_context(response, detailed_context)
    
    def enhance_multiple_responses(self, responses: List[str], dialogue_context: Dict[str, Any]) -> List[str]:
        """
        批量增强多个咨询师回复
        
        Args:
            responses: 原始回复列表
            dialogue_context: 对话上下文信息
            
        Returns:
            增强后的回复列表
        """
        enhanced_responses = []
        
        for response in responses:
            enhanced = self.enhance_response(response, dialogue_context)
            enhanced_responses.append(enhanced)
        
        return enhanced_responses


# 便捷函数
def quick_rewrite(sentence: str, context: str = "心理咨询对话场景") -> str:
    """快速改写单个句子的便捷函数"""
    try:
        rewriter = SentenceRewriter()
        return rewriter.rewrite_with_context(sentence, context)
    except Exception as e:
        logger.error(f"快速改写失败: {e}")
        return sentence


def quick_enhance_counselor_response(response: str, stage: str = "对话") -> str:
    """快速增强咨询师回复的便捷函数"""
    try:
        enhancer = CounselorResponseEnhancer()
        return enhancer.enhance_response(response, {"current_stage": stage})
    except Exception as e:
        logger.error(f"快速增强失败: {e}")
        return response


# 集成到对话系统的工具函数
def integrate_with_counselor_agent(original_response: str, 
                                 current_stage: str,
                                 patient_emotion: str = "平静",
                                 session_type: str = "首次会话") -> str:
    """
    与咨询师代理集成的句子增强函数
    
    Args:
        original_response: 原始回复
        current_stage: 当前CBT阶段
        patient_emotion: 患者情绪状态
        session_type: 会话类型
        
    Returns:
        增强后的回复
    """
    enhancer = CounselorResponseEnhancer()
    
    dialogue_context = {
        'current_stage': current_stage,
        'patient_emotion': patient_emotion,
        'session_type': session_type
    }
    
    return enhancer.enhance_response(original_response, dialogue_context) 