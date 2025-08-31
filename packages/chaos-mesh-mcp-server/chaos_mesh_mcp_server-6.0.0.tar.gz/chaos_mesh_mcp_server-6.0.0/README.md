# Chaos Mesh MCP Server

An MCP server that enables AI agents to perform chaos engineering through Chaos Mesh on EKS clusters.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Agent      │───▶│   MCP Server     │───▶│  EKS Cluster    │
│                 │    │                  │    │                 │
│ - Failure       │    │ - OIDC Auth      │    │ - Chaos Mesh    │
│   Scenarios     │    │ - K8s API Calls  │    │ - Workloads     │
│ - Experiment    │    │ - Experiment     │    │ - Monitoring    │
│   Planning      │    │   Management     │    │                 │
│ - Result        │    │                  │    │                 │
│   Analysis      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Features

### 1. Authentication and Authorization Management
- OIDC-based EKS cluster authentication
- RBAC permission validation
- Token renewal and management

### 2. Chaos Mesh Experiment Management
- Experiment creation and execution
- Experiment status monitoring
- Experiment termination and cleanup

### 3. Chaos Engineering Tools
- Pod failure injection
- Network failure simulation
- Storage failure testing
- Time and stress testing

## Installation and Setup

1. Install Chaos Mesh on EKS cluster
2. Configure OIDC provider
3. Set up RBAC permissions
4. Deploy MCP server

## Security Considerations

- Apply principle of least privilege
- Limit experiment scope
- Record audit logs
- Implement safety mechanisms
