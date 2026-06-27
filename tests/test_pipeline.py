"""
Unit tests for the AI Guardian Pipeline
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from workflow_pipeline import (
    WorkflowPipeline,
    DataQualityAnalyzer,
    FairnessAuditor,
    PrivacyScanner,
    ExplainabilityAnalyzer,
    RiskAssessor,
    ComplianceChecker,
    AITrustScoreCalculator,
    DeploymentDecisionEngine,
    StageStatus,
    WorkflowStage
)

class TestDataQualityAnalyzer(unittest.TestCase):
    """Test data quality analysis"""
    
    def setUp(self):
        """Create test data"""
        self.clean_df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': ['A', 'B', 'C', 'D', 'E']
        })
        
        self.messy_df = pd.DataFrame({
            'feature1': [1, 2, np.nan, 4, 5],
            'feature2': ['A', 'B', 'A', 'B', 'A']
        })
    
    def test_clean_data_quality(self):
        """Test analysis on clean data"""
        result = DataQualityAnalyzer.analyze(self.clean_df)
        self.assertGreater(result.score, 85)
        self.assertIn(result.status, [StageStatus.PASSED, StageStatus.WARNING])
    
    def test_messy_data_quality(self):
        """Test analysis on data with missing values"""
        result = DataQualityAnalyzer.analyze(self.messy_df)
        self.assertLess(result.score, 85)
        self.assertEqual(result.details['missing_percentage'], 10.0)
    
    def test_quality_result_structure(self):
        """Test result structure"""
        result = DataQualityAnalyzer.analyze(self.clean_df)
        self.assertEqual(result.stage, WorkflowStage.DATA_QUALITY)
        self.assertIsNotNone(result.score)
        self.assertIsNotNone(result.details)
        self.assertGreater(result.duration_seconds, 0)

class TestFairnessAuditor(unittest.TestCase):
    """Test fairness audit"""
    
    def setUp(self):
        """Create test data"""
        self.balanced_df = pd.DataFrame({
            'age': [20, 30, 40, 50, 20, 30, 40, 50],
            'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
            'feature': [1, 2, 3, 4, 5, 6, 7, 8]
        })
        
        self.imbalanced_df = pd.DataFrame({
            'age': [20, 20, 20, 20, 50, 50, 50, 50],
            'gender': ['M'] * 6 + ['F'] * 2,
            'feature': range(8)
        })
    
    def test_balanced_fairness(self):
        """Test on balanced data"""
        result = FairnessAuditor.audit(self.balanced_df)
        self.assertGreater(result.score, 60)
    
    def test_imbalanced_fairness(self):
        """Test on imbalanced data"""
        result = FairnessAuditor.audit(self.imbalanced_df)
        self.assertLess(result.score, 85)

class TestPrivacyScanner(unittest.TestCase):
    """Test privacy scanning"""
    
    def setUp(self):
        """Create test data"""
        self.safe_df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': ['A', 'B', 'C', 'D', 'E']
        })
        
        self.risky_df = pd.DataFrame({
            'email': ['a@example.com', 'b@example.com', 'c@example.com'],
            'phone': ['123-456-7890', '098-765-4321', '555-555-5555'],
            'ssn': ['123-45-6789', '098-76-5432', '555-55-5555']
        })
    
    def test_safe_data_privacy(self):
        """Test on safe data"""
        result = PrivacyScanner.scan(self.safe_df)
        self.assertGreater(result.score, 80)
    
    def test_risky_data_privacy(self):
        """Test on data with PII"""
        result = PrivacyScanner.scan(self.risky_df)
        self.assertLess(result.score, 80)
        self.assertGreater(len(result.details['pii_columns']), 0)

class TestExplainabilityAnalyzer(unittest.TestCase):
    """Test explainability analysis"""
    
    def setUp(self):
        """Create test data"""
        self.interpretable_df = pd.DataFrame({
            'age': range(100),
            'income': range(100, 200),
            'category': ['A', 'B'] * 50
        })
        
        self.complex_df = pd.DataFrame(
            np.random.randn(100, 60),
            columns=[f'var_{i}' for i in range(60)]
        )
    
    def test_interpretable_explainability(self):
        """Test on interpretable data"""
        result = ExplainabilityAnalyzer.analyze(self.interpretable_df)
        self.assertGreater(result.score, 75)
    
    def test_complex_explainability(self):
        """Test on complex data"""
        result = ExplainabilityAnalyzer.analyze(self.complex_df)
        self.assertLess(result.score, 85)

class TestWorkflowPipeline(unittest.TestCase):
    """Test complete pipeline"""
    
    def setUp(self):
        """Create test data"""
        self.test_df = pd.DataFrame({
            'feature1': np.random.randn(1000),
            'feature2': np.random.choice(['A', 'B', 'C'], 1000),
            'target': np.random.choice([0, 1], 1000)
        })
    
    def test_pipeline_execution(self):
        """Test full pipeline execution"""
        pipeline = WorkflowPipeline()
        report = pipeline.execute(self.test_df)
        
        # Verify report structure
        self.assertIsNotNone(report.total_score)
        self.assertGreaterEqual(report.total_score, 0)
        self.assertLessEqual(report.total_score, 100)
        self.assertIsNotNone(report.can_deploy)
        self.assertEqual(len(report.stages), 8)
    
    def test_all_stages_executed(self):
        """Test all stages are executed"""
        pipeline = WorkflowPipeline()
        report = pipeline.execute(self.test_df)
        
        stage_types = [s.stage for s in report.stages]
        self.assertIn(WorkflowStage.DATA_QUALITY, stage_types)
        self.assertIn(WorkflowStage.FAIRNESS, stage_types)
        self.assertIn(WorkflowStage.PRIVACY, stage_types)
        self.assertIn(WorkflowStage.EXPLAINABILITY, stage_types)
        self.assertIn(WorkflowStage.RISK, stage_types)
        self.assertIn(WorkflowStage.COMPLIANCE, stage_types)
        self.assertIn(WorkflowStage.TRUST_SCORE, stage_types)
        self.assertIn(WorkflowStage.DEPLOYMENT, stage_types)

if __name__ == '__main__':
    unittest.main()
