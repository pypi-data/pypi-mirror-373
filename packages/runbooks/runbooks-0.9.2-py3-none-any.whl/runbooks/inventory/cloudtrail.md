# CloudTrail: Accountability and Governance

??? info "python check_cloudtrail_status.py"

    | Parent Acct  | Account Number | Region    | Trail Name           | Trail Type | S3 Bucket                     |
    | ------------ | -------------- | --------- | -------------------- | ---------- | ----------------------------- |
    | 909135376185 | 909135376185   | us-east-1 | ams-tf-cloudtraillog | OrgTrail   | ams-cloudtrail-vector-all-org |

---

## How to identify WHO changed an AWS Resources, WHEN, and HOW it happened



??? note "🔎 Objective: Changed an AWS Security Group (sg-xxx) in an AWS account"

    > We need to know:

    - **Who** made the change
    - **When** it happened
    - **How** (what method/tool was used)
    - Optionally: **What** exactly was changed (rules added/removed/modified)


## ✅ Step-by-Step Forensic Workflow

### 🛠️ **1. Enable or Query AWS CloudTrail (Primary Source)**

CloudTrail is your **single source of truth** for who did what, when, and how in AWS.

#### 🔍 How to Query CloudTrail for SG Changes:
**Console:**
1. Go to **CloudTrail > Event History**
2. Set **Lookup Attribute** to:
   - **Event name**: `AuthorizeSecurityGroupIngress`, `AuthorizeSecurityGroupEgress`, `RevokeSecurityGroupIngress`, `RevokeSecurityGroupEgress`, or `UpdateSecurityGroupRuleDescriptions`
   - Or filter by **Resource Name**: `sg-xxx`
3. Set **Time Range** (last 7–30 days typically)

**Important Fields to Look At:**
| Field | Description |
|-------|-------------|
| **Event Time** | When the change occurred |
| **Event Name** | Type of operation (authorize/revoke/modify) |
| **User Identity** | IAM principal who initiated the change |
| **Access Key / Session Context** | Whether it was via console, CLI, or automation |
| **Source IP** | IP address where the change came from |
| **Event Source** | Always `ec2.amazonaws.com` for SG changes |
| **Request Parameters** | IP ranges, ports, protocols involved in the change |

> ✅ **Pro Tip**: If you're using **AWS Organizations**, query from the **Audit Account's CloudTrail**, or the central logging bucket if it's delivered via S3.

---

### 📜 **2. Use AWS Config for Historical Diff View**

If AWS Config is enabled for your account (highly recommended), it provides **resource-level history and diffs**.

#### 🔍 How to Use:
1. Go to **AWS Config > Resources**
2. Filter by **Resource Type**: *EC2 Security Group*
3. Search for **sg-xxx**
4. View **Configuration Timeline**:
   - You’ll see **before/after diffs**
   - You can pinpoint what rule (CIDR/port/protocol) was added or removed

> 🔐 **Bonus**: AWS Config also tells you **compliance status**, i.e., whether the change violated your internal security baselines.

---

### 📊 **3. Use Athena + CloudTrail Logs for Advanced Search (Optional)**

If your CloudTrail is delivered to S3 (recommended for long-term logging), you can:
- Use **Amazon Athena** with the **AWS CloudTrail partitioned schema**
- Run a SQL query like this:

```sql
SELECT
  eventTime,
  eventName,
  userIdentity.arn,
  sourceIPAddress,
  requestParameters.groupId,
  requestParameters.ipPermissions
FROM cloudtrail_logs
WHERE eventSource = 'ec2.amazonaws.com'
  AND requestParameters.groupId = 'sg-xxx'
  AND eventName IN (
    'AuthorizeSecurityGroupIngress',
    'RevokeSecurityGroupIngress',
    'AuthorizeSecurityGroupEgress',
    'RevokeSecurityGroupEgress'
)
ORDER BY eventTime DESC
```

---

### 🧑‍💻 **4. Correlate IAM User/Role Access**

Once you identify **who** made the change, validate:

- Was it a human user (`IAMUser`) or automated role (`IAMRole`, `AssumedRole`)?
- Was MFA enforced for human access?
- Did the user belong to a **delegated group (like `Admin`, `NetworkOps`)**?

Use **AWS IAM > Access Analyzer** or **CloudTrail "userIdentity" block** for this.

> 🔐 If it's an assumed role like `DevOpsAssumeRole`, look for **"sessionContext > sessionIssuer > userName"** in CloudTrail to trace back the original IAM identity.

---

### 🔄 **5. Cross-Check via Change Management / ITSM**

If you're practicing good governance, you should have:
- A **JIRA ticket**, **ServiceNow request**, or **GitOps pull request** associated with the change
- Cross-reference **timestamp** and **user** from CloudTrail with ticket system logs
- If deployed via Terraform/CDK: check the commit history or CI/CD job logs

---

## 🔥 Security Best Practices Going Forward

| Practice | Why |
|---------|-----|
| ✅ Enable **CloudTrail org-wide** and deliver logs to central S3 | Full audit trail |
| ✅ Use **AWS Config** across accounts | Historical visibility of resource changes |
| ✅ Integrate **CloudTrail Insights** | Detect unusual activity like bulk security group changes |
| ✅ Tag SGs with `Owner`, `Environment`, `ChangeTicket` | Aids investigation |
| ✅ Enforce **IAM Conditions** for `ec2:AuthorizeSecurityGroupIngress` etc. | Only allow changes through approved paths |
| ✅ Use **GuardDuty** or **Security Hub** to flag risky changes (e.g., `0.0.0.0/0` open port) | Detection & alerting |

---

> **An enterprise-grade, fully automated solution** for **monitoring and alerting on AWS Security Group (`sg-xxx`) changes** with forensic-level visibility, real-time alerts, and infrastructure governance.

We're going to:

1. ✅ Deep dive: How to **use Athena with CloudTrail partitioned schema**
2. ✅ Craft **Athena queries** to detect SG changes
3. ✅ Configure **AWS Config rules** to enforce and detect policy violations
4. ✅ Build a **real-time alert workflow** using **EventBridge + SNS + Microsoft Teams**
5. ✅ Wrap with best practices for **automation, security, and audit-readiness**

---

## 🔍 PART 1: Use Amazon Athena with AWS CloudTrail Logs (Partitioned Schema)

Amazon Athena allows you to **query CloudTrail logs stored in S3 using SQL**, which is ideal for forensic investigations or continuous audits.

### ✅ Step-by-Step Setup

#### **Step 1 – Ensure CloudTrail is Delivered to S3**
If not already configured:
- Go to **CloudTrail > Trails**
- Ensure **S3 logging is enabled** and directed to a known bucket (e.g., `cloudtrail-logs-org-central`)
- Ideally use **organization trail** for centralized auditing

#### **Step 2 – Create Athena Table for CloudTrail Logs**

Use this sample schema to create an Athena table (you only need to do this once per account or org-wide audit bucket):

> ~~s3://<your-cloudtrail-bucket-name>/AWSLogs/<account-id>/CloudTrail/~~ --> s3://cloudtrail-logs-org-central/AWSLogs/~~Your_Management_Account_ID~~/CloudTrail/

s3://ams-cloudtrail-vector-all-org/AWSLogs/909135376185/CloudTrail/

> create-cloudtrail_logs-table.sql

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS cloudtrail_logs (
  eventVersion STRING,
  eventTime TIMESTAMP,
  eventSource STRING,
  eventName STRING,
  awsRegion STRING,
  sourceIPAddress STRING,
  userAgent STRING,
  userIdentity STRUCT<
    type: STRING,
    principalId: STRING,
    arn: STRING,
    accountId: STRING,
    accessKeyId: STRING,
    userName: STRING,
    sessionContext: STRUCT<
      attributes: STRUCT<
        mfaAuthenticated: STRING,
        creationDate: STRING>,
      sessionIssuer: STRUCT<
        type: STRING,
        principalId: STRING,
        arn: STRING,
        accountId: STRING,
        userName: STRING>>>,
  requestParameters STRING,
  responseElements STRING,
  additionalEventData STRING,
  errorCode STRING,
  errorMessage STRING,
  requestID STRING,
  eventID STRING,
  readOnly STRING,
  eventType STRING,
  apiVersion STRING,
  managementEvent BOOLEAN,
  recipientAccountId STRING,
  sharedEventID STRING,
  vpcEndpointId STRING
)
PARTITIONED BY (`region` STRING, `year` STRING, `month` STRING, `day` STRING)
STORED AS PARQUET
LOCATION 's3://your-cloudtrail-logs/AWSLogs/<account-id>/CloudTrail/'
TBLPROPERTIES (
  "classification"="parquet",
  "projection.enabled"="true",
  "projection.region.type"="enum",
  "projection.region.values"="us-east-1,us-west-2,ap-southeast-2",
  "projection.year.type"="integer",
  "projection.year.range"="2024,2030",
  "projection.month.type"="integer",
  "projection.month.range"="1,12",
  "projection.day.type"="integer",
  "projection.day.range"="1,31",
  "storage.location.template"="s3://your-cloudtrail-logs/AWSLogs/<account-id>/CloudTrail/${region}/${year}/${month}/${day}/"
);
```

> Replace `<your-cloudtrail-bucket-name>` and `<account-id>` accordingly.

#### **Step 3 – Repair Partitions (very important)**

```sql
MSCK REPAIR TABLE cloudtrail_logs;
```

This loads available partitions into Athena for querying.

---

## 📊 PART 2: Craft Athena Query to Detect SG Changes

Here's an optimized, real-world Athena SQL query to detect all Security Group changes (`sg-xxx`):

```sql
SELECT
  eventTime,
  eventName,
  userIdentity.arn AS actor,
  userIdentity.sessionContext.sessionIssuer.userName AS assumedBy,
  sourceIPAddress,
  requestParameters,
  json_extract_scalar(requestParameters, '$.groupId') AS securityGroupId
FROM cloudtrail_logs
WHERE eventName IN (
    'AuthorizeSecurityGroupIngress',
    'RevokeSecurityGroupIngress',
    'AuthorizeSecurityGroupEgress',
    'RevokeSecurityGroupEgress',
    'UpdateSecurityGroupRuleDescriptionsEgress',
    'UpdateSecurityGroupRuleDescriptionsIngress'
  )
  AND json_extract_scalar(requestParameters, '$.groupId') = 'sg-xxx'
  AND year = '2025'
  AND month = '04'
ORDER BY eventTime DESC;
```

> ✅ **Customize** the `year` and `month` fields based on your timeframe. This is important for partition pruning and performance.

---

## 🛡️ PART 3: Use AWS Config to Detect Non-Compliant SG Changes

### ✅ AWS Config Setup

Ensure AWS Config is:
- **Enabled in the account or centrally via org**
- Recording **EC2:SecurityGroup** as a tracked resource

### 🔧 Create AWS Managed or Custom Rule

Use AWS Managed Rule: `INCOMING_SSH_DISABLED`, `RESTRICTED_INCOMING_TRAFFIC`, or create a **custom rule** (Lambda-backed) to detect violations like:

- **Ports open to 0.0.0.0/0**
- **New rules outside of allowed IP range**
- **Unauthorized source CIDRs**

### ✅ Example: Custom AWS Config Rule for CIDR Scope

You can use [AWS Config Rule example](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html) or build a custom rule in Python that flags any ingress rule with `0.0.0.0/0`.

---

## 🚨 PART 4: Automate Real-Time Alerting with EventBridge + SNS + MS Teams

### 🧱 Overview of Architecture

1. **EventBridge Rule** watches for specific `AuthorizeSecurityGroupIngress`, etc.
2. **SNS Topic** receives those events
3. **Lambda Function** transforms event into MS Teams format and posts via webhook

---

### 🔧 Step-by-Step: Setup

#### ✅ 1. Create EventBridge Rule

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventName": [
      "AuthorizeSecurityGroupIngress",
      "RevokeSecurityGroupIngress",
      "AuthorizeSecurityGroupEgress",
      "RevokeSecurityGroupEgress"
    ],
    "requestParameters.groupId": ["sg-xxx"]
  }
}
```

#### ✅ 2. Create SNS Topic (e.g., `SGChangeAlerts`)

- In **SNS**, create a topic
- Add Lambda (below) as a subscriber

#### ✅ 3. Create MS Teams Incoming Webhook

- In MS Teams:
  - Go to a channel
  - Choose “Connectors” → “Incoming Webhook”
  - Name it, copy the **Webhook URL**

---

#### ✅ 4. Lambda Function to Post to MS Teams

Use a simple Python Lambda (add your webhook URL):

```python
import json
import urllib3

http = urllib3.PoolManager()
teams_webhook_url = "<YOUR_MS_TEAMS_WEBHOOK_URL>"

def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        detail = message.get('detail', {})

        sg_id = detail.get('requestParameters', {}).get('groupId', 'Unknown SG')
        event_name = detail.get('eventName', 'UnknownEvent')
        actor = detail.get('userIdentity', {}).get('arn', 'Unknown')
        region = detail.get('awsRegion', 'Unknown')
        source_ip = detail.get('sourceIPAddress', 'Unknown')

        msg = {
            "title": "⚠️ AWS Security Group Change Detected",
            "text": f"**Event**: {event_name}\n**SG**: {sg_id}\n**User**: {actor}\n**Region**: {region}\n**Source IP**: {source_ip}"
        }

        http.request('POST', teams_webhook_url, body=json.dumps(msg), headers={'Content-Type': 'application/json'})
```

- Attach basic execution policy (SNS invocation + logs)
- Test by triggering a manual SG change

---

## 🔄 PART 5: Best Practices for Automation & Audit Maturity

| Category | Best Practice |
|----------|----------------|
| **Logging** | Store CloudTrail in centralized, versioned, encrypted S3 bucket |
| **Query** | Partition Athena tables by `year/month/day` for efficiency |
| **Alerting** | Always include user identity, IP, region in alerts |
| **Tagging** | Tag SGs with `Owner`, `Environment`, `ChangeTicket` |
| **Governance** | Use SCPs and IAM boundaries to restrict unauthorized SG changes |
| **Forensics** | Store Athena queries in a shared repo; automate with scheduled queries for weekly audits |
| **Cost Optimization** | Use Amazon Athena scheduled queries + QuickSight dashboards instead of external tools |

---

## 🎯 Final Thoughts: Governance-Driven Cloud Security

This solution provides:
- **Immediate visibility** (EventBridge + Teams alerting)
- **Historical traceability** (CloudTrail + Athena)
- **Policy enforcement** (AWS Config + IAM/SCP)
- **Audit readiness** (Tagging + documentation + centralized logs)

By integrating these layers, you go beyond reaction and establish a **proactive, auditable, and secure cloud operating model**.

---

Absolutely. Let's take our time and raise the bar.

We are now enhancing the **Athena Query Suite** to support **real-time or near-real-time** analysis of **Critical Alerts** across:

1. 🔐 **Security**
2. 🌐 **Network**
3. 🏗️ **Infrastructure**
4. 💻 **EC2 Runtime**

---

## 🧠 Goal:

Design and implement **production-ready Athena SQL queries**, with **partition projection**, **structured access**, and **cost-efficient filtering**, for all **critical alert types**. These queries should:
- Align with **AWS best practices**
- Be easy to integrate with **scheduled queries, dashboards, or alert pipelines**
- Prioritize **precision, performance, and auditability**

---

## 🧩 Improvements Identified from Previous Athena Queries:

| Area | Original | To-Be |
|------|----------|-------|
| Filtering | Broad or unpartitioned | Partitioned by `year`, `month`, `day`, `region` |
| Identity Insight | Simple `userIdentity.arn` | Full `sessionContext.sessionIssuer.userName`, MFA check |
| Parameter Handling | `json_extract_scalar` | Structured `MAP` access (e.g. `requestParameters['groupId']`) |
| Output Fields | Too generic | Specific fields like `eventName`, `caller`, `ip`, `action`, `resourceId` |
| Extensibility | Hardcoded SG ID | Accepts any SG, port, or IP — makes it reusable |

---

## ✅ Let’s Now Write the Full Set of **Critical Athena Queries**

---

### 🔐 **1. Security Alerts**

---

#### 🔸 A. Unauthorized API Calls (Brute Force, Exploitation Attempts)

> UnauthorizedOperation.sql

```sql
SELECT
  eventTime,
  userIdentity.arn AS user_arn,
  sourceIPAddress,
  awsRegion,
  eventName,
  errorCode
FROM cloudtrail_logs
WHERE eventName = 'UnauthorizedOperation'
  AND year = '2025'
  AND month = '04'
  AND day BETWEEN '01' AND '08'
ORDER BY eventTime DESC;
```

> 📌 **Improvement**: Could also add `errorCode IN ('AccessDenied', 'UnauthorizedOperation')` to catch more cases.

---

#### 🔸 B. Root Account Usage

> RootAccountUsage.sql

```sql
SELECT
  eventTime,
  eventName,
  sourceIPAddress,
  userIdentity.arn AS user_arn,
  userAgent
FROM cloudtrail_logs
WHERE userIdentity.type = 'Root'
  AND year = '2025'
  AND month = '04'
  AND day BETWEEN '01' AND '08'
ORDER BY eventTime DESC;
```

> ✅ Use `userIdentity.type = 'Root'` — most accurate method to detect root usage across API calls.

---

#### 🔸 C. Security Group Rule Changes

> SecurityGroupRuleChanges.sql

```sql
SELECT
  eventTime,
  userIdentity.arn AS user,
  eventName,
  requestParameters['groupId'] AS securityGroupId,
  requestParameters['ipPermissions'] AS modifiedPermissions,
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventName IN (
  'AuthorizeSecurityGroupIngress',
  'RevokeSecurityGroupIngress',
  'AuthorizeSecurityGroupEgress',
  'RevokeSecurityGroupEgress',
  'UpdateSecurityGroupRuleDescriptionsIngress',
  'UpdateSecurityGroupRuleDescriptionsEgress'
)
  AND year = '2025'
  AND month = '04'
  AND day BETWEEN '01' AND '08'
ORDER BY eventTime DESC;
```

---

#### 🔸 D. IAM Policy/Role Changes

```sql
SELECT
  eventTime,
  eventName,
  userIdentity.arn AS user,
  requestParameters['roleName'] AS role,
  requestParameters['policyDocument'] AS newPolicy,
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventName IN (
  'PutRolePolicy', 'AttachRolePolicy', 'CreatePolicy',
  'CreateRole', 'UpdateAssumeRolePolicy'
)
  AND year = '2025'
  AND month = '04'
  AND day BETWEEN '01' AND '08'
ORDER BY eventTime DESC;
```

---

#### 🔸 E. Port 22/3389 Open to 0.0.0.0/0

```sql
SELECT
  eventTime,
  userIdentity.arn AS user,
  requestParameters['groupId'] AS sg_id,
  requestParameters['ipPermissions'] AS permissions,
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventName IN ('AuthorizeSecurityGroupIngress')
  AND requestParameters['ipPermissions'] LIKE '%0.0.0.0/0%'
  AND (
    requestParameters['ipPermissions'] LIKE '%22%' OR
    requestParameters['ipPermissions'] LIKE '%3389%'
  )
  AND year = '2025'
  AND month = '04'
  AND day BETWEEN '01' AND '08'
ORDER BY eventTime DESC;
```

---

### 🌐 **2. Network Alerts**

---

#### 🔸 A. NAT Gateway or Internet Gateway Failures (CloudTrail-Based)

CloudTrail doesn't capture health-check failure natively. Use **CloudWatch logs + SNS** for real-time alerts. But you can **detect removal** of NAT/IGW:

```sql
SELECT
  eventTime,
  eventName,
  userIdentity.arn AS user,
  requestParameters['gatewayId'] AS gateway_id,
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventName IN ('DeleteNatGateway', 'DetachInternetGateway')
  AND year = '2025'
  AND month = '04'
  AND day BETWEEN '01' AND '08'
ORDER BY eventTime DESC;
```

---

#### 🔸 B. VPC Flow Logs — Suspicious Connections (JOIN with parsed Flow Logs)

This requires **VPC Flow Logs** parsed via **Athena + Glue**. Sample query pattern:

```sql
SELECT *
FROM vpc_flow_logs_parquet
WHERE dstaddr IN ('1.2.3.4', '8.8.8.8')
  AND dstport IN (22, 3389, 3306)
  AND action = 'ACCEPT'
  AND day BETWEEN '2025-04-01' AND '2025-04-08'
ORDER BY start DESC;
```

---

### 🏗️ **3. Infrastructure Monitoring Alerts**

> These are best handled via **CloudWatch alarms**, but some are detectable via Athena from CloudTrail as *resource state changes*.

---

#### 🔸 A. Auto Scaling Group Launch Failures

```sql
SELECT
  eventTime,
  userIdentity.arn,
  eventName,
  errorMessage,
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventSource = 'autoscaling.amazonaws.com'
  AND eventName = 'CreateAutoScalingGroup'
  AND errorCode IS NOT NULL
  AND year = '2025'
  AND month = '04'
ORDER BY eventTime DESC;
```

---

#### 🔸 B. Backup Failure (AWS Backup)

```sql
SELECT
  eventTime,
  eventName,
  userIdentity.arn,
  requestParameters['backupVaultName'],
  errorMessage
FROM cloudtrail_logs
WHERE eventSource = 'backup.amazonaws.com'
  AND eventName = 'StartBackupJob'
  AND errorCode IS NOT NULL
  AND year = '2025'
  AND month = '04'
ORDER BY eventTime DESC;
```

---

### 💻 **4. EC2 Instance Alerts**

---

#### 🔸 A. Unexpected Stop or Termination

```sql
SELECT
  eventTime,
  userIdentity.arn,
  eventName,
  requestParameters['instanceId'],
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventSource = 'ec2.amazonaws.com'
  AND eventName IN ('StopInstances', 'TerminateInstances')
  AND year = '2025'
  AND month = '04'
ORDER BY eventTime DESC;
```

---

#### 🔸 B. EC2 Status Check Failure (Indirect Detection)

You can track `DescribeInstanceStatus` calls or hook into **CloudWatch Alarm**. Sample from CloudTrail:

```sql
SELECT
  eventTime,
  userIdentity.arn,
  eventName,
  requestParameters['instanceId'],
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventSource = 'ec2.amazonaws.com'
  AND eventName = 'DescribeInstanceStatus'
  AND year = '2025'
  AND month = '04'
ORDER BY eventTime DESC;
```

---

## 🧱 Implementation Tips

- Automate Athena queries via **Scheduled Queries (daily/hourly)**
- Export results to **S3 + QuickSight** or **alert on non-empty results**
- Pair with **EventBridge rules** for real-time alerts
- Use **Lambda** to format and send alert messages to:
  - **MS Teams / Slack / Email**
  - Custom dashboards

---

## ✅ Summary Table of Enhanced Queries

| Alert Type | Query Name | Detection Method |
|------------|------------|------------------|
| Security | Unauthorized API Calls | CloudTrail via Athena |
| Security | Root Account Usage | `userIdentity.type = 'Root'` |
| Security | SG Rule Changes | `eventName` in SG Ops |
| Security | IAM Policy Changes | `PutRolePolicy`, etc. |
| Security | Public SSH/RDP | `ipPermissions` contains `0.0.0.0/0` |
| Network | NAT/IGW Delete | `DeleteNatGateway`, `DetachInternetGateway` |
| Network | VPC Flow Anomaly | Join with VPC logs |
| Infra | ASG Fail | CloudTrail errorCode on `CreateAutoScalingGroup` |
| Infra | AWS Backup Fail | `StartBackupJob` with error |
| EC2 | Unexpected Stop | `StopInstances`, `TerminateInstances` |
| EC2 | Status Check Fail | `DescribeInstanceStatus` queries |

---

> TODO: Let’s turn this into a full-scale, automated DevSecOps solution.

- **Terraform/CDK to create scheduled Athena queries + alerts?**
- A ready-made **QuickSight security dashboard?**
- A **GitHub repo** for these SQL files + alert infrastructure?

---
