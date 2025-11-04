# ⚡ Eskom Tender Processing Lambda Service

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![Amazon SQS](https://img.shields.io/badge/AWS-SQS-yellow.svg)](https://aws.amazon.com/sqs/)
[![Eskom API](https://img.shields.io/badge/API-Eskom-red.svg)](https://tenderbulletin.eskom.co.za/)
[![Pydantic](https://img.shields.io/badge/Validation-Pydantic-red.svg)](https://pydantic.dev/)

**Powering South Africa's energy procurement intelligence!** ⚡ This AWS Lambda service is the electrical heart of our tender scraping fleet - one of five specialized crawlers that harvest opportunities from South Africa's largest utility company. From massive power station projects to infrastructure upgrades, we capture every kilowatt of opportunity! 🔌

## 📚 Table of Contents

- [🎯 Overview](#-overview)
- [⚡ Lambda Function (lambda_handler.py)](#-lambda-function-lambda_handlerpy)
- [📊 Data Model (models.py)](#-data-model-modelspy)
- [🏷️ AI Tagging Initialization](#️-ai-tagging-initialization)
- [📋 Example Tender Data](#-example-tender-data)
- [🚀 Getting Started](#-getting-started)
- [📦 Deployment](#-deployment)
- [🧰 Troubleshooting](#-troubleshooting)

## 🎯 Overview

Welcome to the powerhouse of procurement data! 🏭 This service is your direct pipeline into Eskom's massive tender ecosystem, capturing multi-billion rand infrastructure projects, power generation contracts, and critical maintenance opportunities that keep South Africa's lights on! 💡

**What makes it electrifying?** ⚡
- 🔋 **Energy Sector Focus**: Specialized in power generation, transmission, and distribution tenders
- 🏗️ **Mega Project Capture**: From power station retrofits to grid infrastructure upgrades
- 🛡️ **Industrial-Grade Reliability**: Built to handle Eskom's complex tender structures and massive data volumes
- 🤖 **AI-Ready Pipeline**: Every tender pre-configured for intelligent categorization and enrichment

## ⚡ Lambda Function (`lambda_handler.py`)

The electrical brain of our operation! 🧠 The `lambda_handler` orchestrates the entire data harvesting process with industrial precision:

### 🔄 The Power Extraction Journey:

1. **🌐 Fetch Data**: Connects to the Eskom Tender Bulletin API - the official source for all Eskom procurement opportunities across the country.

2. **🛡️ Bulletproof Error Handling**: Built like a power station! Handles network storms, API blackouts, and response anomalies with enterprise-grade resilience. No downtime, no data loss! 💪

3. **⚙️ Data Processing**: Each tender goes through our industrial-strength parsing engine. We clean dates, validate structures, and ensure every field meets our exacting standards.

4. **✅ Quality Assurance**: Our `EskomTender` model runs rigorous validation checks. Bad data gets flagged, logged, and filtered out - only premium-grade tenders make it through! 🏆

5. **📦 Smart Batching**: Valid tenders are intelligently grouped into batches of 10 messages - optimized for maximum SQS throughput and cost efficiency.

6. **🚀 Queue Dispatch**: Each batch powers up to the central `AIQueue.fifo` SQS queue with the unique `MessageGroupId` of `EskomTenderScrape`. This keeps our power sector tenders organized and maintains perfect processing order.

## 📊 Data Model (`models.py`)

Our data architecture is engineered for power and precision! 🏗️

### `TenderBase` **(The Foundation)** 🏛️
The robust foundation that powers all our tender models! This abstract class defines the core electrical grid that connects all tenders:

**🔧 Core Attributes:**
- `title`: The tender's power rating - what's being procured?
- `description`: Technical specifications and project requirements
- `source`: Always "Eskom" for this industrial-grade scraper
- `published_date`: When this opportunity went live on the grid
- `closing_date`: Submission deadline - when the power window closes! ⏰
- `supporting_docs`: Critical technical documents and specifications
- `tags`: Keywords for AI intelligence (starts empty, gets energized by our AI service)

### `EskomTender` **(The Power Specialist)** ⚡
This powerhouse inherits all the foundational strength from `TenderBase` and adds Eskom's unique high-voltage features:

**🏭 Eskom-Specific Attributes:**
- `tender_number`: Official Eskom reference code (e.g., "MWP2577PS")
- `audience`: Who can bid? (e.g., "All Suppliers", "Pre-qualified Contractors")
- `office_location`: Physical location for tender collection and briefings
- `email`: Direct line to Eskom's procurement powerhouse
- `address`: Full address for site visits and document collection
- `province`: Which province needs the power boost

## 🏷️ AI Tagging Initialization

We're all about intelligent power distribution! 🤖 Every tender that flows through our system is perfectly prepared for downstream AI enhancement:

```python
# From models.py - Preparing for AI electrification! ⚡
return cls(
    # ... other fields
    tags=[],  # Initialize tags as an empty list, ready for the AI service.
    # ... other fields
)
```

This ensures **seamless integration** with our AI pipeline - every tender object arrives with a clean, empty `tags` field just waiting to be charged with intelligent categorizations! 🧠⚡

## 📋 Example Tender Data

Here's what a real Eskom mega-project looks like after our scraper works its magic! 🎩✨

```json
{
  "title": "The Medupi Power Station Flue Gas Desulphurization (Fgd) Retrofit Engineer, Procure, Construct (Epc) Project For An Estimated Contract Period Of Eight (8) Years.",
  "description": "The Medupi Power Station Flue Gas Desulphurization (Fgd) Retrofit Engineer, Procure, Construct (Epc) Project For An Estimated Contract Period Of Eight (8) Years.",
  "source": "Eskom",
  "publishedDate": "2024-09-09T12:40:55.587000",
  "closingDate": "2026-02-02T10:00:00",
  "supporting_docs": [
    {
      "name": "Eskom Tender Bulletin",
      "url": "https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID=90032"
    }
  ],
  "tags": [],
  "tenderNumber": "MWP2577PS",
  "audience": "All Suppliers",
  "officeLocation": "Eskom Megawatt Park, 1 Maxwell Drive Sunninghill.",
  "email": "cyril.ntshonga@eskom.co.za",
  "address": "Eskom Megawatt Park Tender Office Northside (Retail Centre) 1 Maxwell Drive Sunninghill Sandton",
  "province": "National"
}
```

**🔥 What this shows:**
- 💰 **Mega Project**: Multi-billion rand power station retrofit over 8 years
- 🏭 **Critical Infrastructure**: Flue Gas Desulphurization at Medupi Power Station
- 🌍 **Environmental Impact**: Emissions reduction technology for cleaner power
- 📋 **Complete Documentation**: Full tender bulletin with technical specifications
- ⏰ **Long-term Commitment**: Extended timeline from 2024 to 2026
- 🎯 **National Scope**: Infrastructure project with national significance

## 🚀 Getting Started

Ready to tap into Eskom's power grid of opportunities? Let's energize your setup! ⚡

### 📋 Prerequisites
- AWS CLI configured with appropriate credentials 🔑
- Python 3.9+ with pip 🐍
- Access to AWS Lambda and SQS services ☁️
- Understanding of power sector terminology 🏭

### 🔧 Local Development
1. **📁 Clone the repository**
2. **📦 Install dependencies**: `pip install -r requirements.txt`
3. **🧪 Run tests**: `python -m pytest`
4. **🔍 Test locally**: Use AWS SAM for local Lambda simulation

## 📦 Deployment

This Lambda function supports multiple deployment methods to power up your infrastructure! Choose the approach that best fits your workflow. ⚡

### 🚀 Method 1: Release Branch Deployment (Automated)

The simplest way to deploy! Our GitHub Actions workflow automatically handles the deployment when you create a release branch.

**Steps:**
1. **Create a release branch** from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b release/v1.0.0
   git push origin release/v1.0.0
   ```

2. **Automatic deployment** triggers via GitHub Actions workflow
3. **Verify deployment** in AWS Lambda console

**Benefits:** 🎯
- ✅ Zero manual configuration
- ✅ Consistent deployment process
- ✅ Automatic rollback on failure
- ✅ Integrated with CI/CD pipeline

### 🔧 Method 2: AWS SAM Deployment

Deploy using AWS SAM with the included `template.yml` for complete infrastructure management.

**Prerequisites:**
```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Verify installation
sam --version
```

**Deployment Steps:**
```bash
# 1. Build the SAM application
sam build --template-file template.yml

# 2. Deploy with guided setup (first time)
sam deploy --guided --template-file template.yml

# 3. Subsequent deployments
sam deploy --template-file template.yml
```

**Advanced SAM Options:**
```bash
# Deploy to specific environment
sam deploy --template-file template.yml --parameter-overrides Environment=production

# Deploy with custom stack name
sam deploy --template-file template.yml --stack-name eskom-function-prod

# Validate template before deployment
sam validate --template-file template.yml
```

**Benefits:** 🏗️
- ✅ Infrastructure as Code
- ✅ Complete stack management
- ✅ Environment-specific configurations
- ✅ Local testing capabilities

### 🛠️ Method 3: AWS Toolkit/CLI Deployment

Direct deployment using AWS CLI and toolkit for maximum control.

**Prerequisites:**
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Install AWS Lambda deployment tools
pip install boto3
```

**Deployment Steps:**

1. **Prepare deployment package:**
   ```bash
   # Create deployment directory
   mkdir deployment-package
   
   # Install dependencies
   pip install -r requirements.txt -t deployment-package/
   
   # Copy source code
   cp *.py deployment-package/
   
   # Create deployment zip
   cd deployment-package
   zip -r ../eskom-function.zip .
   cd ..
   ```

2. **Deploy new Lambda function:**
   ```bash
   # Create new function
   aws lambda create-function \
     --function-name eskom-tender-processor \
     --runtime python3.9 \
     --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
     --handler lambda_handler.lambda_handler \
     --zip-file fileb://eskom-function.zip \
     --timeout 300 \
     --memory-size 512
   ```

3. **Update existing Lambda function:**
   ```bash
   # Update function code
   aws lambda update-function-code \
     --function-name eskom-tender-processor \
     --zip-file fileb://eskom-function.zip
   
   # Update function configuration
   aws lambda update-function-configuration \
     --function-name eskom-tender-processor \
     --timeout 300 \
     --memory-size 512
   ```

4. **Configure environment variables:**
   ```bash
   aws lambda update-function-configuration \
     --function-name eskom-tender-processor \
     --environment Variables='{
       "SQS_QUEUE_URL":"https://sqs.region.amazonaws.com/account/queue-name",
       "API_TIMEOUT":"30",
       "BATCH_SIZE":"10"
     }'
   ```

5. **Set up triggers (if needed):**
   ```bash
   # Add CloudWatch Events trigger for scheduled execution
   aws events put-rule \
     --name eskom-scraper-schedule \
     --schedule-expression "rate(1 hour)"
   
   aws lambda add-permission \
     --function-name eskom-tender-processor \
     --statement-id scheduled-execution \
     --action lambda:InvokeFunction \
     --principal events.amazonaws.com \
     --source-arn arn:aws:events:region:account:rule/eskom-scraper-schedule
   
   aws events put-targets \
     --rule eskom-scraper-schedule \
     --targets Id=1,Arn=arn:aws:lambda:region:account:function:eskom-tender-processor
   ```

**Benefits:** ⚙️
- ✅ Maximum deployment control
- ✅ Custom configuration options
- ✅ Direct AWS service integration
- ✅ Scriptable for automation

### 🔧 Environment Variables

Configure these environment variables for optimal performance:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SQS_QUEUE_URL` | Target SQS queue for processed tenders | - | ✅ |
| `API_TIMEOUT` | Eskom API request timeout (seconds) | 30 | ❌ |
| `BATCH_SIZE` | Tenders per SQS batch | 10 | ❌ |
| `LOG_LEVEL` | Logging verbosity (INFO, DEBUG, ERROR) | INFO | ❌ |

### 🧪 Testing Your Deployment

Verify your deployment with these validation steps:

```bash
# Test Lambda function locally (SAM)
sam local invoke -e events/test-event.json --template-file template.yml

# Test deployed function
aws lambda invoke \
  --function-name eskom-tender-processor \
  --payload '{}' \
  response.json

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/eskom-tender-processor
```

### 🚨 Deployment Troubleshooting

<details>
<summary><strong>Common Deployment Issues</strong></summary>

**Issue**: Permission denied during deployment
**Solution**: Ensure your AWS credentials have Lambda and IAM permissions

**Issue**: Package too large for Lambda
**Solution**: Use Lambda layers for large dependencies or optimize package size

**Issue**: Environment variables not updating
**Solution**: Redeploy with explicit environment variable configuration

</details>

Choose the deployment method that best fits your development workflow. The release branch method is recommended for production environments, while AWS CLI deployment offers maximum flexibility for custom setups! ⚡

## 🧰 Troubleshooting

### 🚨 Power Grid Issues

<details>
<summary><strong>API Connection Failures</strong></summary>

**Issue**: Cannot connect to Eskom Tender Bulletin API.

**Solution**: Eskom's API can be temperamental during peak hours. Implement retry logic with exponential backoff. The power grid needs patience! ⚡

</details>

<details>
<summary><strong>Large Tender Processing</strong></summary>

**Issue**: Lambda timeouts on massive infrastructure projects.

**Solution**: Eskom deals in mega-projects! Increase Lambda timeout and memory allocation. Some power station retrofits have extensive documentation! 🏭

</details>

<details>
<summary><strong>Data Validation on Technical Specs</strong></summary>

**Issue**: Complex engineering tenders failing validation.

**Solution**: Eskom tenders often contain technical jargon and specifications. Update validation rules to handle power sector terminology and measurements! ⚙️

</details>

<details>
<summary><strong>SQS Quota Overruns</strong></summary>

**Issue**: Too many large tenders hitting SQS limits.

**Solution**: Eskom runs massive procurement cycles. Implement intelligent batching based on tender size and complexity! 📦

</details>

---

> Built with love, bread, and code by **Bread Corporation** 🦆❤️💻
