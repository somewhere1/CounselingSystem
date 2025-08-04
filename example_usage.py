"""
Example usage of the refactored counseling system.
Demonstrates different ways to use the system components.
"""

import os
import sys
from typing import Dict, Any

# Add parent directory to path for proper module resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from refactored_counseling_system import (
    CounselingSystemApp, 
    ConversationSession, 
    ConversationMode,
    config
)
from refactored_counseling_system.file_utils import SessionDataManager

def _save_example_session_results(filename: str, session_results: Dict[str, Any]):
    """Save session results to files for example runs."""
    try:
        print(f"\n=== Saving session results as '{filename}' ===")
        
        # Initialize session data manager
        session_data_manager = SessionDataManager()
        
        # Extract data from session results
        dialogue_history = session_results.get("dialogue_history", [])  # 经过R1推理修改的最终对话
        original_history = session_results.get("session_data", {}).get("original_dialogue_history", [])  # 未经R1修改的原始对话
        reasoning_history = session_results.get("session_data", {}).get("reasoning_history", [])
        reasoning_history_by_round = session_results.get("session_data", {}).get("reasoning_history_by_round", [])
        summary_history = session_results.get("session_data", {}).get("summary_history", [])
        modification_history = session_results.get("session_data", {}).get("modification_history", [])
        
        # Fallback: if no original history is available, use dialogue history as backup
        if not original_history:
            original_history = dialogue_history.copy()
            print("⚠️  Warning: No original dialogue history found, using final dialogue as fallback")
        
        # Save all session data
        success = session_data_manager.save_session_results(
            filename=filename,
            dialogue_history=dialogue_history,
            reasoning_history=reasoning_history,
            summary_history=summary_history,
            modification_history=modification_history,
            original_history=original_history,
            reasoning_history_by_round=reasoning_history_by_round
        )
        
        if success:
            print("✓ Session files saved successfully!")
            print("Files saved:")
            print(f"  - {filename}_summary_对话_first.json (经过R1推理修改的最终对话)")
            print(f"  - {filename}_summary_R1推理_first.json (按轮次分组的推理过程)")
            print(f"  - {filename}_summary_摘要_first.json (会话摘要)")
            print(f"  - {filename}_summary_点评_first.json (修改历史)")
            print(f"  - {filename}_summary_noR1_first.json (咨询师首次未经R1修改的原始回复)")
            
            # Print info about reasoning rounds and response comparisons
            if reasoning_history_by_round:
                print(f"  ✨ R1推理文件包含 {len(reasoning_history_by_round)} 轮咨询师回复的推理过程:")
                for round_data in reasoning_history_by_round:
                    round_num = round_data.get("round", "?")
                    reasoning_count = len(round_data.get("reasoning_history", []))
                    original_resp = round_data.get("original_counselor_response", "")
                    final_resp = round_data.get("final_counselor_response", "")
                    
                    print(f"    - 轮次{round_num}: {reasoning_count}次推理评估")
                    
                    # Show if there was a modification
                    if original_resp and final_resp and original_resp != final_resp:
                        print(f"      📝 回复已修改: 原始 → 最终版本")
                    elif original_resp and final_resp and original_resp == final_resp:
                        print(f"      ✅ 回复未修改: 首次生成即被接受")
            
            # Compare dialogue histories
            print(f"\n📊 对话统计:")
            print(f"  - 最终对话轮数: {len(dialogue_history)}")
            print(f"  - 原始对话轮数: {len(original_history)}")
            
            if len(dialogue_history) == len(original_history):
                print(f"  ✅ 对话轮数一致")
            else:
                print(f"  ⚠️  对话轮数不一致，可能存在数据问题")
        else:
            print("✗ Failed to save session files")
            
    except Exception as e:
        print(f"✗ Error saving session results: {e}")
        import traceback
        traceback.print_exc()

def example_single_session():
    """Example of running a single counseling session."""
    print("=== Single Session Example ===")
    
    # Sample patient information
    patient_info = """
    患者信息：
    姓名：张三
    年龄：28岁
    主要问题：工作压力大，经常感到焦虑
    症状：失眠、注意力不集中、情绪低落
    持续时间：3个月
    """
    
    # Create a session
    session = ConversationSession(
        patient_info=patient_info,
        is_first_session=True,
        conversation_mode=ConversationMode.PATIENT_FIRST
    )
    
    # Run the session
    results = session.run_full_session()
    
    print(f"Session completed with {results['statistics']['total_turns']} turns")
    print(f"Reasoning evaluations: {results['statistics'].get('reasoning_evaluations', 0)}")
    print(f"Ended with goodbye: {results['session_summary']['ended_with_goodbye']}")
    
    # Save session results
    _save_example_session_results("example_session", results)
    
    # Print first few exchanges
    print("\nFirst few exchanges:")
    for i, exchange in enumerate(results['dialogue_history'][:4]):
        for role, content in exchange.items():
            print(f"{role}: {content}")
        if i < 3:
            print()

def example_batch_processing():
    """Example of batch processing patient profiles."""
    print("\n=== Batch Processing Example ===")
    
    # Initialize the main application
    app = CounselingSystemApp()
    
    # Validate system first
    validation = app.validate_system()
    if not validation.get("overall_status", False):
        print("System validation failed!")
        print(f"Validation results: {validation}")
        return
    
    print("System validation passed!")
    
    # Example of processing a folder of patient profiles
    # Note: You would need to have actual patient profile files
    folder_path = "sample_patient_profiles"
    
    # Create sample directory and files for demo
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
        # Create sample patient files
        sample_patients = [
            {
                "filename": "patient_001.txt",
                "content": "患者A：25岁，焦虑症状，工作压力大"
            },
            {
                "filename": "patient_002.txt", 
                "content": "患者B：30岁，抑郁情绪，人际关系困扰"
            }
        ]
        
        for patient in sample_patients:
            with open(os.path.join(folder_path, patient["filename"]), 'w', encoding='utf-8') as f:
                f.write(patient["content"])
    
    # Process the folder
    results = app.process_patient_folder(
        folder_path=folder_path,
        is_first_session=True,
        conversation_mode=ConversationMode.PATIENT_FIRST
    )
    
    # Print processing summary
    print(f"\n=== Batch Processing Summary ===")
    print(f"Total files: {results.get('total_files', 0)}")
    print(f"Processed: {results.get('processed', 0)}")
    print(f"Skipped: {results.get('skipped', 0)}")
    print(f"Errors: {results.get('errors', 0)}")
    
    # Save session results for each processed patient
    session_results = results.get("session_results", {})
    if session_results:
        print(f"\n=== Saving Session Results ===")
        for patient_name, session_data in session_results.items():
            print(f"\nSaving results for patient: {patient_name}")
            _save_example_session_results(f"batch_{patient_name}", session_data)
        
        print(f"\n✓ Successfully saved {len(session_results)} session results")
    else:
        print("\n⚠️  No session results to save")
    
    print(f"\nProcessing results: {results}")

def example_concurrent_batch_processing():
    """Example of concurrent batch processing patient profiles."""
    print("\n=== Concurrent Batch Processing Example ===")
    
    # Initialize the main application
    app = CounselingSystemApp()
    
    # Validate system first
    validation = app.validate_system()
    if not validation.get("overall_status", False):
        print("System validation failed!")
        print(f"Validation results: {validation}")
        return
    
    print("System validation passed!")
    
    # Example of processing a folder of patient profiles with concurrent processing
    folder_path = "sample_patient_profiles_concurrent"
    
    # Create sample directory and files for demo
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
        # Create more sample patient files to demonstrate concurrent processing
        sample_patients = [
            {
                "filename": "patient_001.txt",
                "content": "患者A：25岁，焦虑症状，工作压力大"
            },
            {
                "filename": "patient_002.txt", 
                "content": "患者B：30岁，抑郁情绪，人际关系困扰"
            },
            {
                "filename": "patient_003.txt",
                "content": "患者C：35岁，失眠问题，生活节奏紊乱"
            },
            {
                "filename": "patient_004.txt",
                "content": "患者D：28岁，社交恐惧，不敢与人交流"
            },
            {
                "filename": "patient_005.txt",
                "content": "患者E：32岁，职业倦怠，对工作失去兴趣"
            }
        ]
        
        for patient in sample_patients:
            with open(os.path.join(folder_path, patient["filename"]), 'w', encoding='utf-8') as f:
                f.write(patient["content"])
    
    # Process the folder with concurrent processing
    print(f"Starting concurrent processing with 3 workers...")
    results = app.process_patient_folder_concurrent(
        folder_path=folder_path,
        max_workers=3,  # 同时处理3个患者
        is_first_session=True,
        conversation_mode=ConversationMode.PATIENT_FIRST
    )
    
    # Print processing summary
    print(f"\n=== Concurrent Processing Summary ===")
    print(f"Total files: {results.get('total_files', 0)}")
    print(f"Processed: {results.get('processed', 0)}")
    print(f"Skipped: {results.get('skipped', 0)}")
    print(f"Errors: {results.get('errors', 0)}")
    print(f"Concurrent workers used: {results.get('concurrent_workers', 0)}")
    
    # Save session results for each processed patient
    session_results = results.get("session_results", {})
    if session_results:
        print(f"\n=== Saving Session Results ===")
        for patient_name, session_data in session_results.items():
            print(f"\nSaving results for patient: {patient_name}")
            _save_example_session_results(f"concurrent_{patient_name}", session_data)
        
        print(f"\n✓ Successfully saved {len(session_results)} session results")
    else:
        print("\n⚠️  No session results to save")
    
    print(f"\nConcurrent processing results: {results}")
    
    # Performance comparison
    print(f"\n=== Performance Benefits ===")
    print(f"• Processed {results.get('processed', 0)} files concurrently")
    print(f"• Used {results.get('concurrent_workers', 0)} workers simultaneously")
    print(f"• This is much faster than sequential processing for large datasets")

def example_cbt_model_generation():
    """Example of generating CBT models."""
    print("\n=== CBT Model Generation Example ===")
    
    app = CounselingSystemApp()
    
    # Create sample dialogue data
    dialogue_folder = "sample_dialogues"
    if not os.path.exists(dialogue_folder):
        os.makedirs(dialogue_folder)
        
        sample_dialogue = [
            {"求助者": "我最近感到很焦虑，工作压力很大。"},
            {"咨询师": "我理解你的感受。能具体谈谈是什么工作压力让你感到焦虑吗？"},
            {"求助者": "主要是项目截止日期很紧，我担心完不成任务。"},
            {"咨询师": "这种担心是可以理解的。让我们一起探讨一些应对策略。"}
        ]
        
        with open(os.path.join(dialogue_folder, "001.txt_summary_对话.json"), 'w', encoding='utf-8') as f:
            import json
            json.dump(sample_dialogue, f, ensure_ascii=False, indent=2)
    
    # Generate CBT models
    results = app.generate_cbt_models(
        dialogue_folder=dialogue_folder,
        with_suggestion_path="sample_with_suggestion",
        half_suggestion_path="sample_half_suggestion", 
        without_suggestion_path="sample_without_suggestion"
    )
    
    print(f"CBT generation results: {results}")

def example_system_status():
    """Example of checking system status."""
    print("\n=== System Status Example ===")
    
    app = CounselingSystemApp()
    status = app.get_system_status()
    
    print("System Status:")
    print(f"  Processed files: {status.get('processed_files_count', 0)}")
    print(f"  Active sessions: {status.get('active_sessions_count', 0)}")
    print(f"  System ready: {status.get('system_ready', False)}")
    
    if 'config' in status:
        print("  Configuration:")
        for key, value in status['config'].items():
            print(f"    {key}: {value}")

def example_configuration():
    """Example of working with configuration."""
    print("\n=== Configuration Example ===")
    
    print("Current Configuration:")
    print(f"  Max dialogue length: {config.system.MAX_DIALOGUE_LENGTH}")
    print(f"  Max modification attempts: {config.system.MAX_MODIFICATION_ATTEMPTS}")
    print(f"  Conversation model: {config.model.CONVERSATION_MODEL}")
    print(f"  Reasoning model: {config.model.REASONING_MODEL}")
    print(f"  Summary start size: {config.system.SUMMARY_START_SIZE}")
    
    # Example of getting model parameters
    default_params = config.get_model_params("default")
    reasoning_params = config.get_model_params("reasoning")
    
    print(f"  Default model params: {default_params}")
    print(f"  Reasoning model params: {reasoning_params}")

def example_organized_saving():
    """Example of saving session results in organized folders."""
    print("\n=== Organized Folder Saving Example ===")
    
    # Initialize the main application
    app = CounselingSystemApp()
    
    # Validate system first
    validation = app.validate_system()
    if not validation.get("overall_status", False):
        print("System validation failed!")
        print(f"Validation results: {validation}")
        return
    
    print("System validation passed!")
    
    # Sample patient information
    patient_info = """
    患者信息：
    姓名：李四
    年龄：26岁
    主要问题：人际关系困扰，社交焦虑
    症状：害怕与人交流，容易紧张
    持续时间：6个月
    """
    
    # Create a session
    session = ConversationSession(
        patient_info=patient_info,
        is_first_session=True,
        conversation_mode=ConversationMode.PATIENT_FIRST
    )
    
    # Run the session
    results = session.run_full_session()
    
    print(f"Session completed with {results['statistics']['total_turns']} turns")
    
    # Save session results (will be organized in different folders)
    _save_example_session_results("organized_example", results)
    
    print("\n=== Folder Organization ===")
    print("Files have been saved to organized folders:")
    print("📁 dialogue_files/ - 对话历史文件")
    print("📁 reasoning_files/ - 推理过程文件")
    print("📁 summary_files/ - 会话摘要文件")
    print("📁 modification_files/ - 修改历史文件")
    print("📁 original_files/ - 原始对话文件")
    
    # Check if folders were created
    import os
    folders = ["dialogue_files", "reasoning_files", "summary_files", "modification_files", "original_files"]
    for folder in folders:
        if os.path.exists(folder):
            files = os.listdir(folder)
            print(f"✅ {folder}/ - {len(files)} files")
        else:
            print(f"❌ {folder}/ - folder not found")

def cleanup_example_files():
    """Clean up example files created during demo."""
    print("\n=== Cleaning up example files ===")
    
    folders_to_clean = [
        "sample_patient_profiles",
        "sample_patient_profiles_concurrent", # Added for concurrent processing
        "sample_dialogues", 
        "sample_with_suggestion",
        "sample_half_suggestion", 
        "sample_without_suggestion",
        # New organized folders
        "dialogue_files",
        "reasoning_files", 
        "summary_files",
        "modification_files",
        "original_files"
    ]
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                import shutil
                shutil.rmtree(folder)
                print(f"✓ Cleaned up: {folder}")
            except Exception as e:
                print(f"✗ Error cleaning {folder}: {e}")
        else:
            print(f"- Skipped (not found): {folder}")
    
    # Clean up individual files
    files_to_clean = [
        "processed_file.log",
        "example_session_summary_对话_first.json",
        "example_session_summary_R1推理_first.json", 
        "example_session_summary_摘要_first.json",
        "example_session_summary_点评_first.json",
        "example_session_summary_noR1_first.json"
    ]
    
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Cleaned up: {file}")
            except Exception as e:
                print(f"✗ Error cleaning {file}: {e}")
        else:
            print(f"- Skipped (not found): {file}")
    
    print("Cleanup completed!")

def main():
    """Run all examples."""
    print("Refactored Counseling System - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        #example_configuration()
        #example_system_status()
        #example_single_session()
        example_batch_processing()
        # example_cbt_model_generation()
        example_concurrent_batch_processing() # Uncomment to run concurrent example
        example_organized_saving() # Uncomment to run organized saving example
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
        # Ask if user wants to clean up
        cleanup = input("\nDo you want to clean up example files? (y/n): ")
        if cleanup.lower() == 'y':
            cleanup_example_files()
            print("Cleanup completed.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 