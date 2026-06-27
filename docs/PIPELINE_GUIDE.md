# 🛡️ AI Guardian OS - Unified Workflow Pipeline

## Overview

The AI Guardian OS Unified Workflow Pipeline is a comprehensive responsible AI assessment platform that evaluates datasets across 9 critical dimensions:

```
1. Upload Dataset (1GB max)
   ↓
2. Data Quality Analysis
   ↓
3. Fairness Audit
   ↓
4. Privacy Scan
   ↓
5. Explainability Analysis
   ↓
6. Risk Assessment
   ↓
7. Compliance Check
   ↓
8. AI Trust Score
   ↓
9. Deployment Decision
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
# http://localhost:8501

# View MLflow UI
# http://localhost:5000
```

### Option 2: Local Installation (Linux/Mac)

```bash
# Make script executable
chmod +x run_pipeline.sh

# Run the application
./run_pipeline.sh
```

### Option 3: Local Installation (Windows)

```bash
# Run the batch script
run_pipeline.bat
```

### Option 4: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements_pipeline.txt

# Run Streamlit app
streamlit run pipeline_app.py
```

## Pipeline Stages

### 1. Upload Dataset
- **Maximum Size:** 1GB
- **Supported Formats:** CSV, Parquet, Excel, JSON
- **Preview:** First 10 rows displayed
- **Metadata:** Rows, columns, memory usage

### 2. Data Quality Analysis
- **Completeness:** Percentage of non-null values
- **Uniqueness:** Duplicate row detection
- **Type Consistency:** Data type analysis
- **Score:** Weighted combination (40% completeness + 60% uniqueness)

### 3. Fairness Audit
- **Sensitive Attributes:** Detects age, gender, race, ethnicity, etc.
- **Class Imbalance:** Identifies over/under-represented groups
- **Demographic Parity:** Checks for potential bias
- **Score:** Based on presence and balance of sensitive attributes

### 4. Privacy Scan
- **PII Detection:** Identifies email, phone, SSN, addresses
- **Unique Identifiers:** Flags potentially de-anonymizing columns
- **High Cardinality:** Detects numeric ID columns
- **Score:** Based on privacy risks (0-100)

### 5. Explainability Analysis
- **Feature Count:** Evaluates dimensionality
- **Feature Types:** Mix of numeric and categorical
- **Column Names:** Informativeness of feature names
- **Score:** Based on interpretability factors

### 6. Risk Assessment
- **Weighted Analysis:** Combines scores from stages 2-5
- **Risk Levels:** LOW, MEDIUM, HIGH
- **Identified Risks:** Specific issues per stage
- **Aggregated Score:** Weighted combination

### 7. Compliance Check
- **GDPR:** Personal data handling evaluation
- **EU AI Act:** Fairness and high-risk assessment
- **Data Governance:** Quality standards verification
- **Score:** Framework-based scoring

### 8. AI Trust Score
- **Weighted Components:**
  - Data Quality: 15%
  - Fairness: 20%
  - Privacy: 25%
  - Explainability: 15%
  - Risk: 15%
  - Compliance: 10%
- **Trust Levels:**
  - 🟢 EXCELLENT (90-100)
  - 🟡 GOOD (80-89)
  - 🟠 FAIR (70-79)
  - 🔴 POOR (<70)

### 9. Deployment Decision
- **Threshold:** ≥75/100 required
- **Checklist:** All 6 criteria must pass
- **Recommendation:** APPROVED or NOT RECOMMENDED
- **Next Steps:** Actionable recommendations

## Input Requirements

### Supported File Formats

**CSV**
```
head -5 data.csv
feature1,feature2,target
1.5,A,0
2.3,B,1
...
```

**Parquet**
```python
import pandas as pd
df = pd.read_parquet('data.parquet')
```

**Excel**
- Single sheet supported
- File format: .xlsx

**JSON**
- Records or list format
- Nested objects supported

### Data Requirements

- **Minimum Rows:** At least 100 rows recommended
- **Column Types:** Numeric and categorical supported
- **Missing Values:** Handled automatically
- **Duplicates:** Detected and reported

## Output & Results

### Dashboard Display

1. **Overall Metrics**
   - AI Trust Score (0-100)
   - Deployment Status (✅/❌)
   - Stages Passed Count
   - Total Execution Time

2. **Stage Results**
   - Individual scores
   - Status indicators
   - Detailed findings
   - Duration per stage

3. **Recommendations**
   - Deployment decision
   - Next steps
   - Remediation guidance

### Downloadable Reports

**JSON Report**
```json
{
  "timestamp": "2026-06-27T10:30:00",
  "total_score": 85.5,
  "can_deploy": true,
  "recommendation": "🚀 APPROVED FOR DEPLOYMENT",
  "stages": [
    {
      "stage": "Data Quality Analysis",
      "status": "✅ Passed",
      "score": 88.5,
      "details": { ... },
      "duration_seconds": 0.45
    },
    ...
  ]
}
```

**CSV Export**
- Original dataset with analysis metadata
- Quality scores per row
- Risk flags

## Configuration

### Streamlit Configuration (.streamlit/config.toml)

```toml
[client]
maxUploadSize = 1024  # MB

[server]
memory = 2048  # MB
port = 8501
```

### Environment Variables

```bash
export STREAMLIT_SERVER_MAXUPLOADSIZE=1024
export STREAMLIT_LOGGER_LEVEL=info
export MAX_PIPELINE_TIMEOUT=300  # seconds
```

## Troubleshooting

### File Upload Issues

**Error:** "File too large"
- Check Streamlit config `maxUploadSize`
- Verify Docker volume mounts
- Ensure sufficient disk space

**Error:** "Unsupported format"
- Verify file extension (.csv, .parquet, .xlsx, .json)
- Check file is not corrupted

### Pipeline Execution Issues

**Error:** "Pipeline timed out"
- Reduce dataset size
- Check system resources
- Increase timeout in config

**Error:** "Memory exceeded"
- Process smaller chunks
- Check available RAM
- Optimize data types

## Performance Tips

1. **Optimize File Size**
   - Use Parquet format (more efficient)
   - Remove unnecessary columns
   - Target <500MB for fast processing

2. **Data Preparation**
   - Remove duplicates beforehand
   - Standardize column names
   - Document sensitive attributes

3. **System Resources**
   - Allocate 2GB+ RAM
   - Use SSD for storage
   - Run on dedicated server for production

## API Usage

```python
from workflow_pipeline import WorkflowPipeline
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Execute pipeline
pipeline = WorkflowPipeline()
report = pipeline.execute(df)

# Access results
print(f"Trust Score: {report.total_score}")
print(f"Can Deploy: {report.can_deploy}")
print(f"Recommendation: {report.recommendation}")

# Iterate through stages
for stage_result in report.stages:
    print(f"{stage_result.stage.value}: {stage_result.score}")
```

## Examples

### Example 1: High-Quality Dataset

```
Dataset: customer_transactions.csv
- Rows: 100,000
- Columns: 15 (numeric + categorical)
- Quality: 95%
- Result: ✅ APPROVED FOR DEPLOYMENT
- Score: 92/100 (EXCELLENT)
```

### Example 2: Dataset with Privacy Concerns

```
Dataset: user_data.csv
- Rows: 50,000
- Columns: 20 (includes email, phone, address)
- Privacy Score: 45%
- Result: 🛑 NOT RECOMMENDED
- Action: Anonymize PII before resubmission
```

### Example 3: Biased Dataset

```
Dataset: hiring_data.csv
- Rows: 25,000
- Fairness Issues: Significant gender imbalance
- Fairness Score: 62%
- Result: 🛑 NOT RECOMMENDED
- Action: Rebalance training data, implement fairness constraints
```

## Best Practices

1. **Regular Assessments**
   - Re-run pipeline on updated datasets
   - Track scores over time
   - Monitor deployment performance

2. **Data Governance**
   - Document data lineage
   - Maintain data dictionary
   - Version datasets

3. **Bias Mitigation**
   - Identify sensitive attributes
   - Monitor fairness metrics
   - Implement fairness constraints

4. **Privacy Protection**
   - Anonymize PII
   - Use differential privacy
   - Implement access controls

5. **Monitoring**
   - Set up alerting
   - Track drift over time
   - Log all assessments

## Support & Resources

- **Documentation:** See this guide
- **Issues:** https://github.com/s43677358-cmd/aii/issues
- **Discussions:** https://github.com/s43677358-cmd/aii/discussions
- **Examples:** See `examples/` directory

## License

MIT License - See LICENSE file for details
