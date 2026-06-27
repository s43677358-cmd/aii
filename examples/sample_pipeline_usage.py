"""
Example: Using the AI Guardian Pipeline Programmatically
"""

import pandas as pd
import json
from workflow_pipeline import WorkflowPipeline, FileUploadHandler
from datetime import datetime

# Example 1: Load and assess a CSV file
def example_csv_assessment():
    print("Example 1: CSV Dataset Assessment")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv('sample.csv')
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Execute pipeline
    pipeline = WorkflowPipeline()
    report = pipeline.execute(df)
    
    # Display results
    print(f"\nAI Trust Score: {report.total_score:.1f}/100")
    print(f"Can Deploy: {report.can_deploy}")
    print(f"Recommendation: {report.recommendation}")
    
    # Show stage results
    print("\nStage Results:")
    for stage_result in report.stages:
        status_emoji = "✅" if "Passed" in stage_result.status.value else "⚠️"
        print(f"  {status_emoji} {stage_result.stage.value}: {stage_result.score:.1f}")
    
    return report

# Example 2: Process multiple datasets
def example_batch_processing():
    print("\nExample 2: Batch Processing Multiple Datasets")
    print("=" * 50)
    
    files = ['dataset1.csv', 'dataset2.csv', 'dataset3.csv']
    results = {}
    
    pipeline = WorkflowPipeline()
    
    for file_path in files:
        try:
            df = pd.read_csv(file_path)
            report = pipeline.execute(df)
            results[file_path] = {
                'score': report.total_score,
                'can_deploy': report.can_deploy,
                'rows': len(df),
                'columns': len(df.columns)
            }
            print(f"✅ {file_path}: Score={report.total_score:.1f}, Deploy={report.can_deploy}")
        except Exception as e:
            print(f"❌ {file_path}: Error - {str(e)}")
            results[file_path] = {'error': str(e)}
    
    return results

# Example 3: Export detailed report
def example_export_report():
    print("\nExample 3: Export Detailed Report")
    print("=" * 50)
    
    # Load and process
    df = pd.read_csv('sample.csv')
    pipeline = WorkflowPipeline()
    report = pipeline.execute(df)
    
    # Create detailed report
    detailed_report = {
        "assessment_metadata": {
            "timestamp": datetime.now().isoformat(),
            "dataset_rows": len(df),
            "dataset_columns": len(df.columns),
            "dataset_size_mb": df.memory_usage(deep=True).sum() / 1024**2,
        },
        "overall_results": {
            "ai_trust_score": round(report.total_score, 2),
            "deployment_approved": report.can_deploy,
            "recommendation": report.recommendation,
        },
        "stage_results": []
    }
    
    # Add stage details
    for stage_result in report.stages:
        detailed_report["stage_results"].append({
            "stage_name": stage_result.stage.value,
            "status": stage_result.status.value,
            "score": round(stage_result.score, 2),
            "duration_seconds": round(stage_result.duration_seconds, 3),
            "details": stage_result.details
        })
    
    # Save report
    report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(detailed_report, f, indent=2)
    
    print(f"✅ Report saved to: {report_filename}")
    return detailed_report

# Example 4: Custom pipeline orchestration
def example_custom_orchestration():
    print("\nExample 4: Custom Pipeline Orchestration")
    print("=" * 50)
    
    from workflow_pipeline import (
        DataQualityAnalyzer, FairnessAuditor, PrivacyScanner,
        ExplainabilityAnalyzer, RiskAssessor
    )
    
    # Load data
    df = pd.read_csv('sample.csv')
    
    # Run individual stages
    print("Running individual assessments...\n")
    
    quality = DataQualityAnalyzer.analyze(df)
    print(f"Data Quality: {quality.score:.1f} - {quality.status.value}")
    
    fairness = FairnessAuditor.audit(df)
    print(f"Fairness: {fairness.score:.1f} - {fairness.status.value}")
    
    privacy = PrivacyScanner.scan(df)
    print(f"Privacy: {privacy.score:.1f} - {privacy.status.value}")
    
    explainability = ExplainabilityAnalyzer.analyze(df)
    print(f"Explainability: {explainability.score:.1f} - {explainability.status.value}")
    
    risk = RiskAssessor.assess([quality, fairness, privacy, explainability])
    print(f"Risk Assessment: {risk.score:.1f} - {risk.status.value}")

# Example 5: Error handling and validation
def example_error_handling():
    print("\nExample 5: Error Handling")
    print("=" * 50)
    
    # Test various error scenarios
    test_cases = [
        (None, "None input"),
        (pd.DataFrame(), "Empty dataframe"),
        (pd.DataFrame({'a': [1, 2, 3]}), "Minimal data"),
    ]
    
    pipeline = WorkflowPipeline()
    
    for df, description in test_cases:
        try:
            if df is None:
                raise ValueError("Dataset cannot be None")
            if df.empty:
                print(f"⚠️ {description}: Skipped (empty)")
                continue
            
            report = pipeline.execute(df)
            print(f"✅ {description}: Processed successfully")
        except Exception as e:
            print(f"❌ {description}: {str(e)}")

if __name__ == "__main__":
    print("\n")
    print("🛡️ AI Guardian OS - Pipeline Examples")
    print("=" * 50)
    
    # Run examples (comment out as needed)
    try:
        example_csv_assessment()
    except FileNotFoundError:
        print("⚠️ sample.csv not found. Skipping Example 1.")
    
    try:
        example_batch_processing()
    except FileNotFoundError:
        print("⚠️ Sample files not found. Skipping Example 2.")
    
    try:
        example_export_report()
    except FileNotFoundError:
        print("⚠️ sample.csv not found. Skipping Example 3.")
    
    example_custom_orchestration()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ All examples completed!")
