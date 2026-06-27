"""
AI Guardian OS - Unified Workflow Pipeline
Orchestrates the entire responsible AI assessment workflow
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Pipeline Enums ====================
class WorkflowStage(Enum):
    """Pipeline stages"""
    UPLOAD = "Upload Dataset"
    DATA_QUALITY = "Data Quality Analysis"
    FAIRNESS = "Fairness Audit"
    PRIVACY = "Privacy Scan"
    EXPLAINABILITY = "Explainability"
    RISK = "Risk Assessment"
    COMPLIANCE = "Compliance Check"
    TRUST_SCORE = "AI Trust Score"
    DEPLOYMENT = "Deployment Decision"

class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "⏳ Pending"
    RUNNING = "🔄 Running"
    PASSED = "✅ Passed"
    FAILED = "❌ Failed"
    WARNING = "⚠️ Warning"

# ==================== Data Classes ====================
@dataclass
class StageResult:
    """Result from a pipeline stage"""
    stage: WorkflowStage
    status: StageStatus
    score: float
    details: Dict
    timestamp: datetime
    duration_seconds: float

@dataclass
class PipelineReport:
    """Complete pipeline execution report"""
    dataset_name: str
    total_score: float
    stages: List[StageResult]
    recommendation: str
    timestamp: datetime
    can_deploy: bool

# ==================== File Upload Handler ====================
class FileUploadHandler:
    """Handles large file uploads (up to 1GB)"""
    
    MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB in bytes
    ALLOWED_EXTENSIONS = {'.csv', '.parquet', '.xlsx', '.json'}
    UPLOAD_DIR = Path("uploads")
    
    def __init__(self):
        self.UPLOAD_DIR.mkdir(exist_ok=True)
    
    @staticmethod
    def validate_file(uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if uploaded_file is None:
            return False, "No file selected"
        
        # Check file size
        file_size = len(uploaded_file.getvalue())
        if file_size > FileUploadHandler.MAX_FILE_SIZE:
            return False, f"File too large. Max size: 1GB, Got: {file_size / (1024**3):.2f}GB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check file extension
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext not in FileUploadHandler.ALLOWED_EXTENSIONS:
            return False, f"Unsupported format. Allowed: {FileUploadHandler.ALLOWED_EXTENSIONS}"
        
        return True, "File valid"
    
    @staticmethod
    def save_file(uploaded_file) -> Path:
        """Save uploaded file"""
        is_valid, message = FileUploadHandler.validate_file(uploaded_file)
        if not is_valid:
            raise ValueError(message)
        
        file_path = FileUploadHandler.UPLOAD_DIR / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"File saved: {file_path}")
        return file_path
    
    @staticmethod
    def load_data(file_path: Path) -> pd.DataFrame:
        """Load data from file"""
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.csv':
                return pd.read_csv(file_path)
            elif ext == '.parquet':
                return pd.read_parquet(file_path)
            elif ext == '.xlsx':
                return pd.read_excel(file_path)
            elif ext == '.json':
                return pd.read_json(file_path)
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise
        
        return None

# ==================== Pipeline Stages ====================
class DataQualityAnalyzer:
    """Stage 1: Data Quality Analysis"""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> StageResult:
        """Analyze data quality metrics"""
        start_time = datetime.now()
        
        try:
            # Calculate quality metrics
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isna().sum().sum()
            missing_percentage = (missing_cells / total_cells) * 100
            
            # Completeness score
            completeness_score = max(0, 100 - missing_percentage)
            
            # Uniqueness check
            duplicate_rows = df.duplicated().sum()
            uniqueness_score = max(0, 100 - (duplicate_rows / len(df) * 100)) if len(df) > 0 else 100
            
            # Type consistency
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            # Overall quality score
            quality_score = (completeness_score * 0.4 + uniqueness_score * 0.6)
            
            details = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_percentage": round(missing_percentage, 2),
                "duplicate_rows": int(duplicate_rows),
                "numeric_columns": len(numeric_cols),
                "categorical_columns": len(categorical_cols),
                "completeness_score": round(completeness_score, 2),
                "uniqueness_score": round(uniqueness_score, 2),
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            
            status = StageStatus.PASSED if quality_score >= 70 else StageStatus.WARNING
            
            return StageResult(
                stage=WorkflowStage.DATA_QUALITY,
                status=status,
                score=quality_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Data quality analysis failed: {e}")
            return StageResult(
                stage=WorkflowStage.DATA_QUALITY,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class FairnessAuditor:
    """Stage 2: Fairness Audit"""
    
    @staticmethod
    def audit(df: pd.DataFrame) -> StageResult:
        """Audit dataset for fairness issues"""
        start_time = datetime.now()
        
        try:
            sensitive_keywords = ['age', 'gender', 'race', 'ethnicity', 'religion', 'nationality']
            sensitive_cols = [col for col in df.columns if any(kw in col.lower() for kw in sensitive_keywords)]
            
            fairness_issues = []
            fairness_score = 100
            
            for col in sensitive_cols:
                if df[col].dtype == 'object' or df[col].nunique() < 20:
                    value_counts = df[col].value_counts()
                    imbalance_ratio = value_counts.max() / value_counts.min() if value_counts.min() > 0 else float('inf')
                    
                    if imbalance_ratio > 3:
                        fairness_issues.append(f"Imbalance in {col}: {imbalance_ratio:.2f}x")
                        fairness_score -= 15
            
            if len(sensitive_cols) > 0:
                fairness_score = max(50, fairness_score)
            else:
                fairness_score = 95
            
            details = {
                "sensitive_columns_detected": sensitive_cols,
                "potential_fairness_issues": fairness_issues,
                "recommendation": "Review sensitive attributes for potential bias" if len(sensitive_cols) > 0 else "No obvious sensitive attributes detected"
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if fairness_score >= 70 else StageStatus.WARNING
            
            return StageResult(
                stage=WorkflowStage.FAIRNESS,
                status=status,
                score=fairness_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Fairness audit failed: {e}")
            return StageResult(
                stage=WorkflowStage.FAIRNESS,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class PrivacyScanner:
    """Stage 3: Privacy Scan"""
    
    @staticmethod
    def scan(df: pd.DataFrame) -> StageResult:
        """Scan dataset for privacy risks"""
        start_time = datetime.now()
        
        try:
            privacy_risks = []
            privacy_score = 100
            
            pii_keywords = ['email', 'phone', 'ssn', 'id', 'address', 'name', 'password', 'token']
            pii_cols = [col for col in df.columns if any(kw in col.lower() for kw in pii_keywords)]
            
            if len(pii_cols) > 0:
                privacy_risks.append(f"Potential PII detected in columns: {pii_cols}")
                privacy_score -= 30
            
            for col in df.columns:
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio > 0.95 and df[col].dtype == 'object':
                    privacy_risks.append(f"Column '{col}' appears to be unique identifier (anonymization needed)")
                    privacy_score -= 20
            
            privacy_score = max(50, privacy_score)
            
            details = {
                "pii_columns": pii_cols,
                "privacy_risks": privacy_risks,
                "recommendation": "Consider data anonymization and pseudonymization" if privacy_score < 80 else "Privacy profile acceptable"
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if privacy_score >= 80 else StageStatus.WARNING
            
            return StageResult(
                stage=WorkflowStage.PRIVACY,
                status=status,
                score=privacy_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Privacy scan failed: {e}")
            return StageResult(
                stage=WorkflowStage.PRIVACY,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class ExplainabilityAnalyzer:
    """Stage 4: Explainability Analysis"""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> StageResult:
        """Analyze dataset explainability"""
        start_time = datetime.now()
        
        try:
            explainability_score = 85
            details = {
                "feature_count": len(df.columns),
                "feature_types": {
                    "numeric": len(df.select_dtypes(include=[np.number]).columns),
                    "categorical": len(df.select_dtypes(include=['object']).columns),
                },
                "observations": []
            }
            
            if len(df.columns) > 50:
                details["observations"].append("High dimensionality (>50 features) - may reduce interpretability")
                explainability_score -= 10
            
            short_names = sum(1 for col in df.columns if len(col) < 3)
            if len(df.columns) > 0 and short_names / len(df.columns) > 0.3:
                details["observations"].append("Many columns have very short names - consider more descriptive naming")
                explainability_score -= 5
            
            if details["feature_types"]["numeric"] > 0 and details["feature_types"]["categorical"] > 0:
                details["observations"].append("Good mix of numeric and categorical features")
                explainability_score = min(100, explainability_score + 5)
            
            details["recommendation"] = "Dataset appears interpretable" if explainability_score >= 80 else "Consider feature engineering and documentation"
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if explainability_score >= 75 else StageStatus.WARNING
            
            return StageResult(
                stage=WorkflowStage.EXPLAINABILITY,
                status=status,
                score=explainability_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Explainability analysis failed: {e}")
            return StageResult(
                stage=WorkflowStage.EXPLAINABILITY,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class RiskAssessor:
    """Stage 5: Risk Assessment"""
    
    @staticmethod
    def assess(stage_results: List[StageResult]) -> StageResult:
        """Assess overall risk based on previous stages"""
        start_time = datetime.now()
        
        try:
            risks = []
            aggregated_score = 0
            weights = {}
            
            for result in stage_results:
                if result.stage == WorkflowStage.DATA_QUALITY:
                    weights[WorkflowStage.DATA_QUALITY] = 0.25
                    if result.score < 70:
                        risks.append("Data quality concerns - high missing values or duplicates")
                elif result.stage == WorkflowStage.FAIRNESS:
                    weights[WorkflowStage.FAIRNESS] = 0.25
                    if result.score < 70:
                        risks.append("Fairness risks detected - potential bias in data")
                elif result.stage == WorkflowStage.PRIVACY:
                    weights[WorkflowStage.PRIVACY] = 0.30
                    if result.score < 80:
                        risks.append("Privacy concerns - PII or identifiable information present")
                elif result.stage == WorkflowStage.EXPLAINABILITY:
                    weights[WorkflowStage.EXPLAINABILITY] = 0.20
                    if result.score < 75:
                        risks.append("Model explainability may be compromised")
                
                aggregated_score += result.score * weights.get(result.stage, 0.1)
            
            if aggregated_score >= 85:
                risk_level = "LOW"
            elif aggregated_score >= 70:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"
            
            details = {
                "risk_level": risk_level,
                "identified_risks": risks,
                "aggregated_score": round(aggregated_score, 2),
                "recommendation": "Safe to proceed with caution" if aggregated_score >= 70 else "Address identified risks before deployment"
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if risk_level == "LOW" else (StageStatus.WARNING if risk_level == "MEDIUM" else StageStatus.FAILED)
            
            return StageResult(
                stage=WorkflowStage.RISK,
                status=status,
                score=aggregated_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return StageResult(
                stage=WorkflowStage.RISK,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class ComplianceChecker:
    """Stage 6: Compliance Check"""
    
    @staticmethod
    def check(stage_results: List[StageResult], df: pd.DataFrame) -> StageResult:
        """Check compliance with regulations"""
        start_time = datetime.now()
        
        try:
            compliance_checks = []
            compliance_score = 100
            
            privacy_result = next((r for r in stage_results if r.stage == WorkflowStage.PRIVACY), None)
            if privacy_result and privacy_result.score < 80:
                compliance_checks.append({
                    "framework": "GDPR",
                    "status": "⚠️ Review",
                    "details": "Personal data handling requires attention"
                })
                compliance_score -= 15
            else:
                compliance_checks.append({
                    "framework": "GDPR",
                    "status": "✓ Likely Compliant",
                    "details": "No obvious PII detected"
                })
            
            fairness_result = next((r for r in stage_results if r.stage == WorkflowStage.FAIRNESS), None)
            if fairness_result and fairness_result.score < 70:
                compliance_checks.append({
                    "framework": "EU AI Act",
                    "status": "⚠️ Review",
                    "details": "Fairness assessment shows potential high-risk issues"
                })
                compliance_score -= 15
            else:
                compliance_checks.append({
                    "framework": "EU AI Act",
                    "status": "✓ Acceptable",
                    "details": "Data meets EU AI Act fairness requirements"
                })
            
            quality_result = next((r for r in stage_results if r.stage == WorkflowStage.DATA_QUALITY), None)
            if quality_result and quality_result.score >= 80:
                compliance_checks.append({
                    "framework": "Data Governance",
                    "status": "✓ Met",
                    "details": "Quality standards achieved"
                })
            else:
                compliance_checks.append({
                    "framework": "Data Governance",
                    "status": "⚠️ Review",
                    "details": "Data quality needs improvement"
                })
                compliance_score -= 10
            
            compliance_score = max(50, compliance_score)
            
            details = {
                "compliance_checks": compliance_checks,
                "overall_score": round(compliance_score, 2),
                "recommendation": "Ready for compliance audit" if compliance_score >= 80 else "Remediation required before deployment"
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if compliance_score >= 80 else StageStatus.WARNING
            
            return StageResult(
                stage=WorkflowStage.COMPLIANCE,
                status=status,
                score=compliance_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return StageResult(
                stage=WorkflowStage.COMPLIANCE,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class AITrustScoreCalculator:
    """Stage 7: AI Trust Score Calculation"""
    
    @staticmethod
    def calculate(stage_results: List[StageResult]) -> StageResult:
        """Calculate overall AI Trust Score"""
        start_time = datetime.now()
        
        try:
            weights = {
                WorkflowStage.DATA_QUALITY: 0.15,
                WorkflowStage.FAIRNESS: 0.20,
                WorkflowStage.PRIVACY: 0.25,
                WorkflowStage.EXPLAINABILITY: 0.15,
                WorkflowStage.RISK: 0.15,
                WorkflowStage.COMPLIANCE: 0.10,
            }
            
            total_score = 0
            for result in stage_results:
                if result.stage in weights:
                    total_score += result.score * weights[result.stage]
            
            if total_score >= 90:
                trust_level = "🟢 EXCELLENT"
                description = "Highly trustworthy AI system"
            elif total_score >= 80:
                trust_level = "🟡 GOOD"
                description = "Trustworthy AI system with minor concerns"
            elif total_score >= 70:
                trust_level = "🟠 FAIR"
                description = "Acceptable AI system with notable concerns"
            else:
                trust_level = "🔴 POOR"
                description = "High-risk AI system - not recommended"
            
            details = {
                "trust_level": trust_level,
                "description": description,
                "component_scores": {
                    "data_quality": next((r.score for r in stage_results if r.stage == WorkflowStage.DATA_QUALITY), 0),
                    "fairness": next((r.score for r in stage_results if r.stage == WorkflowStage.FAIRNESS), 0),
                    "privacy": next((r.score for r in stage_results if r.stage == WorkflowStage.PRIVACY), 0),
                    "explainability": next((r.score for r in stage_results if r.stage == WorkflowStage.EXPLAINABILITY), 0),
                    "risk": next((r.score for r in stage_results if r.stage == WorkflowStage.RISK), 0),
                    "compliance": next((r.score for r in stage_results if r.stage == WorkflowStage.COMPLIANCE), 0),
                }
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if total_score >= 70 else StageStatus.WARNING
            
            return StageResult(
                stage=WorkflowStage.TRUST_SCORE,
                status=status,
                score=total_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Trust score calculation failed: {e}")
            return StageResult(
                stage=WorkflowStage.TRUST_SCORE,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

class DeploymentDecisionEngine:
    """Stage 8: Deployment Decision"""
    
    @staticmethod
    def decide(pipeline_results: List[StageResult]) -> StageResult:
        """Make final deployment recommendation"""
        start_time = datetime.now()
        
        try:
            trust_score_result = next((r for r in pipeline_results if r.stage == WorkflowStage.TRUST_SCORE), None)
            trust_score = trust_score_result.score if trust_score_result else 0
            
            can_deploy = trust_score >= 75
            
            deployment_checklist = {
                "data_quality": "✅" if any(r.stage == WorkflowStage.DATA_QUALITY and r.score >= 70 for r in pipeline_results) else "❌",
                "fairness": "✅" if any(r.stage == WorkflowStage.FAIRNESS and r.score >= 70 for r in pipeline_results) else "❌",
                "privacy": "✅" if any(r.stage == WorkflowStage.PRIVACY and r.score >= 80 for r in pipeline_results) else "❌",
                "explainability": "✅" if any(r.stage == WorkflowStage.EXPLAINABILITY and r.score >= 75 for r in pipeline_results) else "❌",
                "risk": "✅" if any(r.stage == WorkflowStage.RISK and r.score >= 70 for r in pipeline_results) else "❌",
                "compliance": "✅" if any(r.stage == WorkflowStage.COMPLIANCE and r.score >= 80 for r in pipeline_results) else "❌",
            }
            
            recommendation = "🚀 APPROVED FOR DEPLOYMENT" if can_deploy else "🛑 NOT RECOMMENDED FOR DEPLOYMENT"
            
            details = {
                "final_decision": recommendation,
                "trust_score": round(trust_score, 2),
                "deployment_checklist": deployment_checklist,
                "next_steps": [
                    "Conduct final manual review",
                    "Set up monitoring dashboards",
                    "Establish feedback loops"
                ] if can_deploy else [
                    "Address failing compliance areas",
                    "Improve data quality",
                    "Mitigate identified risks"
                ]
            }
            
            duration = (datetime.now() - start_time).total_seconds()
            status = StageStatus.PASSED if can_deploy else StageStatus.FAILED
            
            return StageResult(
                stage=WorkflowStage.DEPLOYMENT,
                status=status,
                score=trust_score,
                details=details,
                timestamp=datetime.now(),
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Deployment decision failed: {e}")
            return StageResult(
                stage=WorkflowStage.DEPLOYMENT,
                status=StageStatus.FAILED,
                score=0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

# ==================== Pipeline Orchestrator ====================
class WorkflowPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.results: List[StageResult] = []
    
    def execute(self, df: pd.DataFrame) -> PipelineReport:
        """Execute complete workflow pipeline"""
        self.results = []
        
        # Stage 1: Data Quality
        quality_result = DataQualityAnalyzer.analyze(df)
        self.results.append(quality_result)
        
        # Stage 2: Fairness
        fairness_result = FairnessAuditor.audit(df)
        self.results.append(fairness_result)
        
        # Stage 3: Privacy
        privacy_result = PrivacyScanner.scan(df)
        self.results.append(privacy_result)
        
        # Stage 4: Explainability
        explainability_result = ExplainabilityAnalyzer.analyze(df)
        self.results.append(explainability_result)
        
        # Stage 5: Risk Assessment
        risk_result = RiskAssessor.assess(self.results)
        self.results.append(risk_result)
        
        # Stage 6: Compliance
        compliance_result = ComplianceChecker.check(self.results, df)
        self.results.append(compliance_result)
        
        # Stage 7: Trust Score
        trust_result = AITrustScoreCalculator.calculate(self.results)
        self.results.append(trust_result)
        
        # Stage 8: Deployment Decision
        deployment_result = DeploymentDecisionEngine.decide(self.results)
        self.results.append(deployment_result)
        
        # Create report
        total_score = trust_result.score
        can_deploy = deployment_result.details["final_decision"].startswith("🚀")
        
        return PipelineReport(
            dataset_name="Dataset",
            total_score=total_score,
            stages=self.results,
            recommendation=deployment_result.details["final_decision"],
            timestamp=datetime.now(),
            can_deploy=can_deploy
        )
    
    def get_results(self) -> List[StageResult]:
        """Get all stage results"""
        return self.results
