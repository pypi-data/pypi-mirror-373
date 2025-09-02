# MCP EKS Infrastructure Tools

This document describes the Model Context Protocol (MCP) tools available for EKS cluster auditing and infrastructure analysis.

## Overview

The EKS Infrastructure MCP Server provides tools to retrieve and analyze Amazon EKS cluster information for auditing and reporting purposes.

## Tools

### 1. getListOfCluster

**Description:** Retrieves all EKS clusters in the AWS account.

**Use Cases:**
- Generate audit summaries or reports when cluster information is not available
- List all EKS clusters in the account
- Initial discovery for cluster analysis

**Parameters:** None

**Returns:** JSON string containing list of EKS clusters

**Example Response:**
```json
[
  "cluster-1",
  "cluster-2",
  "production-cluster"
]
```

### 2. getEksInfra

**Description:** Fetches comprehensive EKS cluster infrastructure details including API endpoint, logging configuration, version, encryption settings, and node group information.

**Use Cases:**
- Generate detailed audit reports for specific clusters
- Analyze cluster infrastructure configuration
- Security and compliance assessments

**Parameters:**
- `cluster_name` (string, required): Name of the EKS cluster to analyze

**Returns:** Structured JSON with complete cluster information

**Example Response:**
```json
{
  "cluster_name": "my-cluster",
  "status": "ACTIVE",
  "version": "1.28",
  "endpoint": "https://xxx.eks.region.amazonaws.com",
  "roleArn": "arn:aws:iam::account:role/eks-service-role",
  "vpc_config": {
    "subnetIds": ["subnet-xxx", "subnet-yyy"],
    "securityGroupIds": ["sg-xxx"]
  },
  "logging": {
    "clusterLogging": [
      {
        "types": ["api", "audit"],
        "enabled": true
      }
    ]
  },
  "encryptionConfig": [],
  "node_groups": {
    "nodegroup-1": {
      "version": "1.28",
      "status": "ACTIVE",
      "capacityType": "ON_DEMAND",
      "scalingConfig": {
        "minSize": 1,
        "maxSize": 3,
        "desiredSize": 2
      },
      "instanceTypes": ["t3.medium"],
      "subnets": ["subnet-xxx"],
      "remoteAccess": null,
      "amiType": "AL2_x86_64"
    }
  }
}
```

## Setup

### Locally

1. Set the `AWS_PROFILE` environment variable to specify the AWS profile to use
2. Ensure proper AWS credentials and permissions for EKS access
3. Run the MCP server: `python mpc_eks_infra.py`

### UVX

You need to install UV if not already installed

```bash
# For Linux and MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Config your MCP servers in Claude Desktop, Cursor, ChatGPT Copilot, Github Copilot and other supported AI clients, e.g.

```json
{
  "mcpServers": {
    "aws-eks-infra": {
      "command": "uvx",
      "args": [
        "eks-infra-mcp"
      ],
      "env": {
        "AWS_PROFILE": "<your-aws_profile>"
      }
    }
  }
}
```

## Usage Workflow

1. **Discovery:** Use `getListOfCluster` to identify available clusters
2. **Analysis:** Use `getEksInfra` with specific cluster names for detailed information
3. **Reporting:** Process the returned JSON data for audit reports and compliance checks

## Error Handling

Both tools return error information in JSON format when exceptions occur:
```json
{
  "error": "Error description"
}
```