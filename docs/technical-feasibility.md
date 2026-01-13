# Technical Feasibility Summary ? GovAssure WebCAF (Sandbox)

## Purpose
Provide a business?friendly summary of the technical feasibility based on a sandbox test of the GovAssure WebCAF architecture with GOV.UK One Login (integration environment).

## Scope (what was tested)
- Sandbox deployment in Azure UK South
- Web application hosted on Azure Container Apps
- PostgreSQL Flexible Server for data storage
- Azure Key Vault for secrets
- Azure Container Registry for images
- GOV.UK One Login (integration) for authentication
- Terraform?based provisioning

This is an early?stage technical test and **not** a production?readiness assessment.

## Architecture components (sandbox)
- **App hosting:** Azure Container Apps
- **Data:** Azure Database for PostgreSQL Flexible Server
- **Secrets:** Azure Key Vault
- **Images:** Azure Container Registry (ACR)
- **Logging/metrics:** Log Analytics
- **Identity:** GOV.UK One Login (integration)
- **Reporting (optional):** Power BI can consume curated data extracts for dashboards

## Feasibility by topic (sandbox findings + recommended option)

### Security and compliance
- Sandbox confirms integration patterns: managed identity, Key Vault secrets, and TLS.
- Recommended option: enterprise Azure subscription, RBAC, security monitoring, and formal assurance reviews.

### Scalability
- Container Apps supports autoscaling; PostgreSQL can scale vertically.
- Recommended option: define expected load and run performance testing before sizing.

### Cost
- Sandbox costs are low but not indicative of production.
- Recommended option: estimate costs from expected traffic, database size, and log retention.

### Operations (ops)
- Terraform provisioning and container app jobs support repeatable deployments.
- Recommended option: CI/CD pipeline, runbooks, monitoring alerts, and support processes.

### Disaster recovery (DR)
- Sandbox does not include DR validation.
- Recommended option: define RTO/RPO, implement backups, and test restore procedures.

### Vendor lock?in
- Uses Azure managed services; app is containerized and portable.
- Recommended option: keep infrastructure as code and avoid unnecessary proprietary features.

### Data residency
- Sandbox is hosted in Azure UK South.
- Recommended option: confirm UK data residency requirements and enforce region controls.

### Reporting (Power BI)
- Power BI can be added as a reporting layer to provide dashboards for programme?level oversight.
- Recommended option: define a curated reporting dataset and governance for sensitive data.

## Current conclusion
The sandbox test demonstrates that the core architecture and One Login integration are technically feasible at a proof?of?concept level. Further validation is needed before any production decision.

## Recommended next steps
1. Align governance and security standards with the Azure Cloud team.
2. Establish CI/CD and a managed Terraform backend.
3. Complete performance testing and cost modelling.
4. Define DR objectives and validate backups/restore.
5. Confirm reporting requirements and Power BI dataset design.
