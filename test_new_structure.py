#!/usr/bin/env python3
"""
简单测试脚本来验证新的推理历史保存结构
"""

import os
import sys

# Add parent directory to path for proper module resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from refactored_counseling_system import ConversationSession, ConversationMode
from refactored_counseling_system.file_utils import SessionDataManager

def test_new_structure():
    """测试新的推理历史保存结构"""
    print("=== 测试新的推理历史保存结构 ===")
    
    # Sample patient information
    patient_info = """
    患者信息：
    姓名：测试患者
    年龄：25岁
    主要问题：测试新的保存结构功能
    """
    
    # Create a session
    session = ConversationSession(
        patient_info=patient_info,
        is_first_session=True,
        conversation_mode=ConversationMode.PATIENT_FIRST
    )
    
    print("🚀 开始会话...")
    
    # Run the session
    results = session.run_full_session()
    
    print(f"\n📊 会话完成:")
    print(f"  - 总轮数: {results['statistics']['total_turns']}")
    print(f"  - 推理评估次数: {results['statistics'].get('reasoning_evaluations', 0)}")
    
    # 检查数据结构
    session_data = results.get("session_data", {})
    
    print(f"\n🔍 检查数据结构:")
    print(f"  - 最终对话历史: {len(results.get('dialogue_history', []))} 轮")
    print(f"  - 原始对话历史: {len(session_data.get('original_dialogue_history', []))} 轮")
    print(f"  - 按轮次分组的推理: {len(session_data.get('reasoning_history_by_round', []))} 轮")
    
    # 显示推理详情
    reasoning_by_round = session_data.get('reasoning_history_by_round', [])
    if reasoning_by_round:
        print(f"\n🧠 推理详情:")
        for round_data in reasoning_by_round:
            round_num = round_data.get("round", "?")
            original_resp = round_data.get("original_counselor_response", "")
            final_resp = round_data.get("final_counselor_response", "")
            reasoning_count = len(round_data.get("reasoning_history", []))
            
            print(f"  轮次 {round_num}:")
            print(f"    - 推理次数: {reasoning_count}")
            
            if original_resp and final_resp:
                if original_resp == final_resp:
                    print(f"    - ✅ 首次生成即被接受")
                else:
                    print(f"    - 📝 回复经过修改")
                    print(f"      原始: {original_resp[:50]}{'...' if len(original_resp) > 50 else ''}")
                    print(f"      最终: {final_resp[:50]}{'...' if len(final_resp) > 50 else ''}")
    
    # Save session results
    print(f"\n💾 保存会话结果...")
    session_data_manager = SessionDataManager()
    
    # Extract data
    dialogue_history = results.get("dialogue_history", [])
    original_history = session_data.get("original_dialogue_history", [])
    reasoning_history = session_data.get("reasoning_history", [])
    reasoning_history_by_round = session_data.get("reasoning_history_by_round", [])
    summary_history = session_data.get("summary_history", [])
    modification_history = session_data.get("modification_history", [])
    
    success = session_data_manager.save_session_results(
        filename="test_new_structure",
        dialogue_history=dialogue_history,
        reasoning_history=reasoning_history,
        summary_history=summary_history,
        modification_history=modification_history,
        original_history=original_history,
        reasoning_history_by_round=reasoning_history_by_round
    )
    
    if success:
        print("✅ 保存成功!")
        print("生成的文件:")
        print("  - test_new_structure_summary_对话_first.json")
        print("  - test_new_structure_summary_R1推理_first.json")
        print("  - test_new_structure_summary_noR1_first.json")
        print("  - test_new_structure_summary_摘要_first.json")
        print("  - test_new_structure_summary_点评_first.json")
    else:
        print("❌ 保存失败!")

if __name__ == "__main__":
    test_new_structure()