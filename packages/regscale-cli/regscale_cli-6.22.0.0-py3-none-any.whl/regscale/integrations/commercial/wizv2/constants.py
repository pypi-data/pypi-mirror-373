"""This module contains all the constants used in the Wiz SDK."""

from enum import Enum
from typing import List, Optional

from regscale.models import IssueSeverity, regscale_models

WIZ_POLICY_QUERY = """
query PolicyAssessmentsTable($filterBy: PolicyAssessmentFilters, $first: Int, $after: String) {
  policyAssessments(filterBy: $filterBy, first: $first, after: $after) {
    nodes {
      id
      policy {
        ... on CloudConfigurationRule {
          id
          shortId
          name
          ruleDescription: description
          severity
          graphId
          remediationInstructions
          risks
          threats
          securitySubCategories {
            ...SecuritySubCategoriesDetails
          }
        }
        ... on Control {
          id
          name
          description
          lastRunAt
          lastRunError
          lastSuccessfulRunAt
          severity
          risks
          threats
          securitySubCategories {
            ...SecuritySubCategoriesDetails
          }
        }
        ... on HostConfigurationRule {
          id
          name
          shortName
          remediationInstructions
          risks
          threats
          securitySubCategories {
            ...SecuritySubCategoriesDetails
          }
        }
      }
      result
      resource {
        id
        name
        type
        region
        tags { key value }
        subscription { id name externalId cloudProvider }
      }
      output {
        ... on Issue { id issueStatus: status }
        ... on ConfigurationFinding { id name cloudConfigurationFindingStatus: status remediation }
        ... on HostConfigurationRuleAssessment { id hostConfigurationRule: rule { id name shortName description remediationInstructions } }
      }
    }
    pageInfo { hasNextPage endCursor }
    totalCount
  }
}

fragment SecuritySubCategoriesDetails on SecuritySubCategory {
  description
  id
  resolutionRecommendation
  title
  externalId
  category { id name framework { id name enabled } }
}
"""

WIZ_FRAMEWORK_QUERY = """
query SecurityFrameworksTable($first: Int, $after: String, $filterBy: SecurityFrameworkFilters) {
  securityFrameworks(first: $first, after: $after, filterBy: $filterBy) {
    nodes { policyTypes ...SecurityFrameworkFragment }
    pageInfo { hasNextPage endCursor }
    totalCount
  }
}

fragment SecurityFrameworkFragment on SecurityFramework {
  id
  name
  description
  builtin
  enabled
  parentFramework { id name }
}
"""

# Comprehensive framework mappings with shorthand names for easy CLI usage
FRAMEWORK_MAPPINGS = {
    "wf-id-4": "NIST SP 800-53 Revision 5",
    "wf-id-48": "NIST SP 800-53 Revision 4",
    "wf-id-5": "FedRAMP (Moderate and Low levels)",
    "wf-id-17": "CIS Controls v7.1",
    "wf-id-24": "CIS Controls v8",
    "wf-id-6": "CIS AWS v1.2.0",
    "wf-id-7": "CIS AWS v1.3.0",
    "wf-id-32": "CIS AWS v1.4.0",
    "wf-id-45": "CIS AWS v1.5.0",
    "wf-id-84": "CIS AWS v2.0.0",
    "wf-id-98": "CIS AWS v3.0.0",
    "wf-id-197": "CIS AWS v4.0.0",
    "wf-id-50": "AWS Foundational Security Best Practices v1.0.0",
    "wf-id-124": "AWS Well-Architected Framework (Section 2 - Security)",
    "wf-id-8": "CIS Azure v1.3.0",
    "wf-id-35": "CIS Azure v1.4.0",
    "wf-id-52": "CIS Azure v1.5.0",
    "wf-id-74": "CIS Azure v2.0.0",
    "wf-id-100": "CIS Azure v2.1.0",
    "wf-id-196": "CIS Azure v2.1.0 (Latest)",
    "wf-id-40": "Azure Security Benchmark v3",
    "wf-id-9": "CIS GCP v1.1.0",
    "wf-id-36": "CIS GCP v1.2.0",
    "wf-id-53": "CIS GCP v1.3.0",
    "wf-id-85": "CIS GCP v2.0.0",
    "wf-id-25": "CIS AKS v1.0.0",
    "wf-id-68": "CIS AKS v1.2.0",
    "wf-id-75": "CIS AKS v1.3.0",
    "wf-id-93": "CIS AKS v1.4.0",
    "wf-id-162": "CIS AKS v1.5.0",
    "wf-id-218": "CIS AKS v1.6.0",
    "wf-id-23": "CIS EKS v1.0.1",
    "wf-id-67": "CIS EKS v1.1.0",
    "wf-id-86": "CIS EKS v1.2.0",
    "wf-id-18": "CIS Kubernetes v1.5.1",
    "wf-id-66": "CIS Kubernetes v1.6.1",
    "wf-id-87": "CIS Kubernetes v1.7.0",
    "wf-id-76": "SOC 2 Type I",
    "wf-id-16": "ISO/IEC 27001:2013",
    "wf-id-19": "PCI DSS v3.2.1",
    "wf-id-78": "PCI DSS v4.0",
    "wf-id-79": "GDPR",
    "wf-id-64": "CCPA/CPRA",
    "wf-id-77": "CCF (The Adobe Common Controls Framework)",
    "wf-id-70": "Canadian PBMM (ITSG-33)",
    "wf-id-111": "C5 - Cloud Computing Compliance Criteria Catalogue",
    "wf-id-161": "CAF (Cyber Assessment Framework by NCSC)",
    "wf-id-90": "APRA CPG 234",
    "wf-id-207": "CISA Security Requirements for EO 14117",
    "wf-id-214": "5Rs - Wiz for Data Security",
    "wf-id-225": "Wiz for Risk Assessment",
}

FRAMEWORK_SHORTCUTS = {
    "nist": "wf-id-4",
    "nist53r5": "wf-id-4",
    "nist53r4": "wf-id-48",
    "fedramp": "wf-id-5",
    "cis": "wf-id-24",
    "cisv8": "wf-id-24",
    "cisv7": "wf-id-17",
    "aws": "wf-id-197",
    "azure": "wf-id-196",
    "gcp": "wf-id-85",
    "k8s": "wf-id-87",
    "kubernetes": "wf-id-87",
    "eks": "wf-id-86",
    "aks": "wf-id-218",
    "soc2": "wf-id-76",
    "iso27001": "wf-id-16",
    "pci": "wf-id-78",
    "gdpr": "wf-id-79",
    "ccpa": "wf-id-64",
    "aws-foundational": "wf-id-50",
    "aws-wellarchitected": "wf-id-124",
    "azure-benchmark": "wf-id-40",
}

FRAMEWORK_CATEGORIES = {
    "NIST Frameworks": ["wf-id-4", "wf-id-48", "wf-id-5"],
    "CIS Controls": ["wf-id-17", "wf-id-24"],
    "AWS Security": [
        "wf-id-197",
        "wf-id-50",
        "wf-id-124",
        "wf-id-6",
        "wf-id-7",
        "wf-id-32",
        "wf-id-45",
        "wf-id-84",
        "wf-id-98",
    ],
    "Azure Security": [
        "wf-id-196",
        "wf-id-40",
        "wf-id-8",
        "wf-id-35",
        "wf-id-52",
        "wf-id-74",
        "wf-id-100",
    ],
    "Google Cloud Security": ["wf-id-85", "wf-id-9", "wf-id-36", "wf-id-53"],
    "Kubernetes Security": [
        "wf-id-87",
        "wf-id-86",
        "wf-id-218",
        "wf-id-18",
        "wf-id-23",
        "wf-id-25",
        "wf-id-66",
        "wf-id-67",
        "wf-id-68",
        "wf-id-75",
        "wf-id-93",
        "wf-id-162",
    ],
    "Industry Standards": ["wf-id-76", "wf-id-16", "wf-id-78", "wf-id-19"],
    "Privacy & Data Protection": ["wf-id-79", "wf-id-64", "wf-id-214"],
    "Government/Regulatory": ["wf-id-70", "wf-id-111", "wf-id-161", "wf-id-90", "wf-id-207"],
}

SBOM_FILE_PATH = "artifacts/wiz_sbom.json"
INVENTORY_FILE_PATH = "artifacts/wiz_inventory.json"
ISSUES_FILE_PATH = "artifacts/wiz_issues.json"
VULNERABILITY_FILE_PATH = "artifacts/wiz_vulnerabilities.json"
CLOUD_CONFIG_FINDINGS_FILE_PATH = "artifacts/wiz_cloud_config_findings.json"
HOST_VULNERABILITY_FILE_PATH = "artifacts/wiz_host_vulnerabilities.json"
DATA_FINDINGS_FILE_PATH = "artifacts/wiz_data_findings.json"
SECRET_FINDINGS_FILE_PATH = "artifacts/wiz_secret_findings.json"
NETWORK_EXPOSURE_FILE_PATH = "artifacts/wiz_network_exposures.json"
END_OF_LIFE_FILE_PATH = "artifacts/wiz_end_of_life.json"
EXTERNAL_ATTACK_SURFACE_FILE_PATH = "artifacts/wiz_external_attack_surface.json"
EXCESSIVE_ACCESS_FILE_PATH = "artifacts/wiz_excessive_access.json"
CONTENT_TYPE = "application/json"
RATE_LIMIT_MSG = "Rate limit exceeded"
PROVIDER = "Provider ID"
RESOURCE = "Resource Type"
CHECK_INTERVAL_FOR_DOWNLOAD_REPORT = 7
MAX_RETRIES = 100
ASSET_TYPE_MAPPING = {
    "ACCESS_ROLE": "Other",
    "ACCESS_ROLE_BINDING": "Other",
    "ACCESS_ROLE_PERMISSION": "Other",
    "API_GATEWAY": "Other",
    "APPLICATION": "Other",
    "AUTHENTICATION_CONFIGURATION": "Other",
    "BACKUP_SERVICE": "Other",
    "BUCKET": "Other",
    "CDN": "Other",
    "CERTIFICATE": "Other",
    "CICD_SERVICE": "Other",
    "CLOUD_LOG_CONFIGURATION": "Other",
    "CLOUD_ORGANIZATION": "Other",
    "COMPUTE_INSTANCE_GROUP": "Other",
    "CONFIG_MAP": "Other",
    "CONTAINER": "Other",
    "CONTAINER_GROUP": "Other",
    "CONTAINER_IMAGE": "Other",
    "CONTAINER_REGISTRY": "Other",
    "CONTAINER_SERVICE": "Other",
    "DAEMON_SET": "Other",
    "DATABASE": "Other",
    "DATA_WORKLOAD": "Other",
    "DB_SERVER": "Physical Server",
    "DEPLOYMENT": "Other",
    "DNS_RECORD": "Other",
    "DNS_ZONE": "Other",
    "DOMAIN": "Other",
    "EMAIL_SERVICE": "Other",
    "ENCRYPTION_KEY": "Other",
    "ENDPOINT": "Other",
    "FILE_SYSTEM_SERVICE": "Other",
    "FIREWALL": "Firewall",
    "GATEWAY": "Other",
    "GOVERNANCE_POLICY": "Other",
    "GOVERNANCE_POLICY_GROUP": "Other",
    "HOSTED_APPLICATION": "Other",
    "IAM_BINDING": "Other",
    "IP_RANGE": "Other",
    "KUBERNETES_CLUSTER": "Other",
    "KUBERNETES_CRON_JOB": "Other",
    "KUBERNETES_INGRESS": "Other",
    "KUBERNETES_INGRESS_CONTROLLER": "Other",
    "KUBERNETES_JOB": "Other",
    "KUBERNETES_NETWORK_POLICY": "Other",
    "KUBERNETES_NODE": "Other",
    "KUBERNETES_PERSISTENT_VOLUME": "Other",
    "KUBERNETES_PERSISTENT_VOLUME_CLAIM": "Other",
    "KUBERNETES_POD_SECURITY_POLICY": "Other",
    "KUBERNETES_SERVICE": "Other",
    "KUBERNETES_STORAGE_CLASS": "Other",
    "KUBERNETES_VOLUME": "Other",
    "LOAD_BALANCER": "Other",
    "MANAGED_CERTIFICATE": "Other",
    "MANAGEMENT_SERVICE": "Other",
    "NETWORK_ADDRESS": "Other",
    "NETWORK_INTERFACE": "Other",
    "NETWORK_ROUTING_RULE": "Other",
    "NETWORK_SECURITY_RULE": "Other",
    "PEERING": "Other",
    "POD": "Other",
    "PORT_RANGE": "Other",
    "PRIVATE_ENDPOINT": "Other",
    "PROXY": "Other",
    "PROXY_RULE": "Other",
    "RAW_ACCESS_POLICY": "Other",
    "REGISTERED_DOMAIN": "Other",
    "REPLICA_SET": "Other",
    "RESOURCE_GROUP": "Other",
    "SEARCH_INDEX": "Other",
    "SERVICE_ACCOUNT": "Other",
    "SUBNET": "Other",
    "SUBSCRIPTION": "Other",
    "SWITCH": "Network Switch",
    "VIRTUAL_DESKTOP": "Virtual Machine (VM)",
    "VIRTUAL_MACHINE": "Virtual Machine (VM)",
    "VIRTUAL_MACHINE_IMAGE": "Other",
    "VIRTUAL_NETWORK": "Other",
    "VOLUME": "Other",
    "WEB_SERVICE": "Other",
    "DATA_WORKFLOW": "Other",
}

RECOMMENDED_WIZ_INVENTORY_TYPES = [
    # Compute resources
    "CONTAINER",
    "CONTAINER_GROUP",
    "CONTAINER_IMAGE",
    "POD",
    "SERVERLESS",
    "SERVERLESS_PACKAGE",
    "VIRTUAL_DESKTOP",
    "VIRTUAL_MACHINE",
    "VIRTUAL_MACHINE_IMAGE",
    # Network and exposure
    "API_GATEWAY",
    "CDN",
    "CERTIFICATE",
    "DNS_RECORD",
    "ENDPOINT",
    "FIREWALL",
    "GATEWAY",
    "LOAD_BALANCER",
    "MANAGED_CERTIFICATE",
    "NETWORK_ADDRESS",
    "NETWORK_INTERFACE",
    "PRIVATE_ENDPOINT",
    "PRIVATE_LINK",
    "PROXY",
    "WEB_SERVICE",
    # Storage and data
    "BACKUP_SERVICE",
    "BUCKET",
    "DATABASE",
    "DATA_WORKLOAD",
    "DB_SERVER",
    "FILE_SYSTEM_SERVICE",
    "SECRET",
    "SECRET_CONTAINER",
    "STORAGE_ACCOUNT",
    "VOLUME",
    # Identity and access management
    "ACCESS_ROLE",
    # "ACCESS_ROLE_BINDING",
    "AUTHENTICATION_CONFIGURATION",
    "IAM_BINDING",
    "RAW_ACCESS_POLICY",
    "SERVICE_ACCOUNT",
    # Development and CI/CD
    "APPLICATION",
    "CICD_SERVICE",
    "CONFIG_MAP",
    "CONTAINER_REGISTRY",
    "CONTAINER_SERVICE",
    # Kubernetes resources
    "CONTROLLER_REVISION",
    "KUBERNETES_CLUSTER",
    "KUBERNETES_INGRESS",
    "KUBERNETES_NODE",
    "KUBERNETES_SERVICE",
    "NAMESPACE",
    # Infrastructure and management
    "CLOUD_LOG_CONFIGURATION",
    "CLOUD_ORGANIZATION",
    "DOMAIN",
    "EMAIL_SERVICE",
    "ENCRYPTION_KEY",
    "MANAGEMENT_SERVICE",
    "MESSAGING_SERVICE",
    "REGISTERED_DOMAIN",
    "RESOURCE_GROUP",
    "SERVICE_CONFIGURATION",
    "SUBNET",
    "SUBSCRIPTION",
    "VIRTUAL_NETWORK",
]

# This is the set of technology deploymentModels and CloudResource types which we
# map to the asset category Hardware (instead of Software) when the useWizHardwareTypes
# feature is enabled.
# So either things which are hardware-like, or which use technologies that, in turn,
# imply they are hardware-like.
# Note that using technology deploymentModels can grab things such as virutal machine
# image files in addition to actual virtual machines. While this doesn't fit with
# general concepts of "hardware", for the purposes of attestation, it is the correct
# choice, as we may be certifying a source image that dynamic resources are created from,
# rather than attempt to document a variable pool of auto-scaled resources.
DEFAULT_WIZ_HARDWARE_TYPES = [
    # CloudResource types
    "VIRTUAL_MACHINE",
    "VIRTUAL_MACHINE_IMAGE",
    "CONTAINER",
    "CONTAINER_IMAGE",
    "DB_SERVER",
    # technology deploymentModels
    "SERVER_APPLICATION",
    "CLIENT_APPLICATION",
    "VIRTUAL_APPLIANCE",
]

# This maps CPE part values to Asset categories.
CPE_PART_TO_CATEGORY_MAPPING = {
    "h": regscale_models.AssetCategory.Hardware,  # Hardware
    "a": regscale_models.AssetCategory.Software,  # Application
    "o": regscale_models.AssetCategory.Software,  # Other? Operating system? (includes OSs and firmware)
}

INVENTORY_QUERY = """
    query CloudResourceSearch(
    $filterBy: CloudResourceFilters
    $first: Int
    $after: String
  ) {
    cloudResources(
      filterBy: $filterBy
      first: $first
      after: $after
    ) {
      nodes {
        ...CloudResourceFragment
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
  fragment CloudResourceFragment on CloudResource {
    id
    name
    type
    subscriptionId
    subscriptionExternalId
    graphEntity{
      id
      providerUniqueId
      publicExposures(first: 5) {
          totalCount
      }
      name
      type
      projects {
        id
      }
      technologies {
        name
        deploymentModel
      }
      properties
      firstSeen
      lastSeen
    }
  }
"""
DATASOURCE = "Wiz"
SBOM_QUERY = """
    query ArtifactsGroupedByNameTable($filterBy: SBOMArtifactsGroupedByNameFilter, $first: Int, $after: String, $orderBy: SBOMArtifactsGroupedByNameOrder) {
  sbomArtifactsGroupedByName(
    filterBy: $filterBy
    first: $first
    after: $after
    orderBy: $orderBy
  ) {
    nodes {
      id
      type {
        ...SBOMArtifactTypeFragment
      }
      name
      validatedInRuntime
      artifacts(first: 0) {
        totalCount
      }
      versions(first: 500) {
        nodes {
          version
        }
      }
    }
    updatedAt
    pageInfo {
      endCursor
      hasNextPage
    }
    totalCount
  }
}
    fragment SBOMArtifactTypeFragment on SBOMArtifactType {
  group
  codeLibraryLanguage
  osPackageManager
  hostedTechnology {
    id
    name
    icon
  }
  plugin
}
"""

TECHNOLOGIES_FILE_PATH = "./artifacts/technologies.json"
AUTH0_URLS = [
    "https://auth.wiz.io/oauth/token",
    "https://auth0.gov.wiz.io/oauth/token",
    "https://auth0.test.wiz.io/oauth/token",
    "https://auth0.demo.wiz.io/oauth/token",
]
COGNITO_URLS = [
    "https://auth.app.wiz.io/oauth/token",
    "https://auth.gov.wiz.io/oauth/token",
    "https://auth.test.wiz.io/oauth/token",
    "https://auth.demo.wiz.io/oauth/token",
    "https://auth.app.wiz.us/oauth/token",
]
CREATE_REPORT_QUERY = """
    mutation CreateReport($input: CreateReportInput!) {
    createReport(input: $input) {
        report {
        id
        }
    }
    }
"""
REPORTS_QUERY = """
        query ReportsTable($filterBy: ReportFilters, $first: Int, $after: String) {
          reports(first: $first, after: $after, filterBy: $filterBy) {
            nodes {
              id
              name
              type {
                id
                name
              }
              project {
                id
                name
              }
              emailTarget {
                to
              }
              parameters {
                query
                framework {
                  name
                }
                subscriptions {
                  id
                  name
                  type
                }
                entities {
                  id
                  name
                  type
                }
              }
              lastRun {
                ...LastRunDetails
              }
              nextRunAt
              runIntervalHours
            }
            pageInfo {
              hasNextPage
              endCursor
            }
            totalCount
          }
        }
            fragment LastRunDetails on ReportRun {
          id
          status
          failedReason
          runAt
          progress
          results {
            ... on ReportRunResultsBenchmark {
              errorCount
              passedCount
              failedCount
              scannedCount
            }
            ... on ReportRunResultsGraphQuery {
              resultCount
              entityCount
            }
            ... on ReportRunResultsNetworkExposure {
              scannedCount
              publiclyAccessibleCount
            }
            ... on ReportRunResultsConfigurationFindings {
              findingsCount
            }
            ... on ReportRunResultsVulnerabilities {
              count
            }
            ... on ReportRunResultsIssues {
              count
            }
          }
        }
    """
DOWNLOAD_QUERY = """
    query ReportDownloadUrl($reportId: ID!) {
        report(id: $reportId) {
            lastRun {
                url
                status
            }
        }
    }
    """
RERUN_REPORT_QUERY = """
    mutation RerunReport($reportId: ID!) {
        rerunReport(input: {id: $reportId}) {
            report {
                id
                lastRun {
                    url
                    status
                }
            }
        }
    }
    """
ISSUE_QUERY = """query IssuesTable(
  $filterBy: IssueFilters
  $first: Int
  $after: String
  $orderBy: IssueOrder
) {
  issues:issuesV2(filterBy: $filterBy
    first: $first
    after: $after
    orderBy: $orderBy) {
    nodes {
      id
      sourceRule{
        __typename
        ... on Control {
          id
          name
          controlDescription: description
          resolutionRecommendation
          securitySubCategories {
            title
            externalId
            category {
              name
              framework {
                name
              }
            }
          }
        }
        ... on CloudEventRule{
          id
          name
          cloudEventRuleDescription: description
          sourceType
          type
        }
        ... on CloudConfigurationRule{
          id
          name
          cloudConfigurationRuleDescription: description
          remediationInstructions
          serviceType
        }
      }
      createdAt
      updatedAt
      dueAt
      type
      resolvedAt
      statusChangedAt
      projects {
        id
        name
        slug
        businessUnit
        riskProfile {
          businessImpact
        }
      }
      status
      severity
      entitySnapshot {
        id
        type
        nativeType
        name
        status
        cloudPlatform
        cloudProviderURL
        providerId
        region
        resourceGroupExternalId
        subscriptionExternalId
        subscriptionName
        subscriptionTags
        tags
        createdAt
        externalId
      }
      serviceTickets {
        externalId
        name
        url
      }
      notes {
        createdAt
        updatedAt
        text
        user {
          name
          email
        }
        serviceAccount {
          name
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}"""

VULNERABILITY_QUERY = """
    query VulnerabilityFindingsTable($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String) {
  vulnerabilityFindings(
    filterBy: $filterBy
    first: $first
    after: $after
    orderBy: {direction: DESC}
  ) {
    nodes {
      id
      name
      detailedName
      description
      commentThread {
        comments(first:100) {
          edges {
            node {
              body,
              author {
                name
              }
            }
          }
        }
      },
      severity: vendorSeverity
      weightedSeverity
      status
      fixedVersion
      detectionMethod
      hasExploit
      hasCisaKevExploit
      cisaKevReleaseDate
      cisaKevDueDate
      firstDetectedAt
      lastDetectedAt
      resolvedAt
      score
      validatedInRuntime
      epssSeverity
      epssPercentile
      epssProbability
      dataSourceName
      fixDate
      fixDateBefore
      publishedDate
      projects{
        id
      }
      cvssv2 {
        attackVector
        attackComplexity
        confidentialityImpact
        integrityImpact
        privilegesRequired
        userInteractionRequired
      }
      cvssv3 {
        attackVector
        attackComplexity
        confidentialityImpact
        integrityImpact
        privilegesRequired
        userInteractionRequired
      }
      ignoreRules {
        id
      }
      layerMetadata {
        id
        details
        isBaseLayer
      }
      vulnerableAsset {
        ... on VulnerableAssetBase {
          id
          type
          name
          cloudPlatform
          subscriptionName
          subscriptionExternalId
          subscriptionId
          tags
          hasLimitedInternetExposure
          hasWideInternetExposure
          isAccessibleFromVPN
          isAccessibleFromOtherVnets
          isAccessibleFromOtherSubscriptions
        }
        ... on VulnerableAssetVirtualMachine {
          id
          type
          name
          cloudPlatform
          subscriptionName
          subscriptionExternalId
          subscriptionId
          tags
          operatingSystem
          imageName
          imageId
          imageNativeType
          hasLimitedInternetExposure
          hasWideInternetExposure
          isAccessibleFromVPN
          isAccessibleFromOtherVnets
          isAccessibleFromOtherSubscriptions
        }
        ... on VulnerableAssetServerless {
          id
          type
          name
          cloudPlatform
          subscriptionName
          subscriptionExternalId
          subscriptionId
          tags
          hasLimitedInternetExposure
          hasWideInternetExposure
          isAccessibleFromVPN
          isAccessibleFromOtherVnets
          isAccessibleFromOtherSubscriptions
        }
        ... on VulnerableAssetContainerImage {
          id
          type
          name
          cloudPlatform
          subscriptionName
          subscriptionExternalId
          subscriptionId
          tags
          hasLimitedInternetExposure
          hasWideInternetExposure
          isAccessibleFromVPN
          isAccessibleFromOtherVnets
          isAccessibleFromOtherSubscriptions
          repository {
            vertexId
            name
          }
          registry {
            vertexId
            name
          }
          scanSource
          executionControllers {
            ...VulnerableAssetExecutionControllerDetails
          }
        }
        ... on VulnerableAssetContainer {
          id
          type
          name
          cloudPlatform
          subscriptionName
          subscriptionExternalId
          subscriptionId
          tags
          hasLimitedInternetExposure
          hasWideInternetExposure
          isAccessibleFromVPN
          isAccessibleFromOtherVnets
          isAccessibleFromOtherSubscriptions
          executionControllers {
            ...VulnerableAssetExecutionControllerDetails
          }
        }
        ... on VulnerableAssetRepositoryBranch {
          id
          type
          name
          cloudPlatform
          repositoryId
          repositoryName
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
    fragment VulnerableAssetExecutionControllerDetails on VulnerableAssetExecutionController {
  id
  entityType
  externalId
  providerUniqueId
  name
  subscriptionExternalId
  subscriptionId
  subscriptionName
  ancestors {
    id
    name
    entityType
    externalId
    providerUniqueId
  }
}
"""
# CIS_BENCHMARK_QUERY
CLOUD_CONFIG_FINDING_QUERY = """
query CloudConfigurationFindingsTable($filterBy: ConfigurationFindingFilters, $first: Int, $after: String, $quick: Boolean) {
  configurationFindings(
    filterBy: $filterBy
    first: $first
    after: $after
    quick: $quick
  ) {
    nodes {
      id
      name
      analyzedAt
      firstSeenAt
      severity
      result
      status
      remediation
      source
      targetExternalId
      statusChangedAt
      ignoreRules {
        id
        tags {
          key
          value
        }
      }
      subscription {
        id
        name
        externalId
        cloudProvider
      }
      resource {
        id
        name
        type
        projects {
          id
          name
          riskProfile {
            businessImpact
          }
        }
      }
      rule {
        id
        shortId
        graphId
        name
        description
        remediationInstructions
        securitySubCategories {
          id
          title
          externalId
          category {
            id
            framework {
              id
              name
            }
            name
          }
        }
        tags {
          key
          value
        }
      }
    }
    maxCountReached
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
"""
HOST_VULNERABILITY_QUERY = """
query HostConfigurationFindingsTable($filterBy: HostConfigurationRuleAssessmentFilters, $orderBy: HostConfigurationRuleAssessmentOrder, $first: Int, $after: String) {
  hostConfigurationRuleAssessments(
    filterBy: $filterBy
    orderBy: $orderBy
    first: $first
    after: $after
  ) {
    nodes {
      id
      firstSeen
      analyzedAt
      updatedAt
      resource {
        id
        type
        name
        subscription {
          id
          name
          externalId
          cloudProvider
        }
      }
      result
      status
      ignoreRules {
        id
      }
      rule {
        id
        shortName
        description
        name
        severity
        securitySubCategories {
          ...SecuritySubCategoryDetails
        }
      }
      hasGraphObject
    }
    pageInfo {
      endCursor
      hasNextPage
    }
    maxCountReached
    totalCount
  }
}
fragment SecuritySubCategoryDetails on SecuritySubCategory {
  id
  title
  externalId
  description
  category {
    id
    name
    framework {
      id
      name
      enabled
    }
  }
}
"""
DATA_FINDING_QUERY = """
query DataFindingsGroupedByValueTable($groupBy: DataFindingsGroupedByValueField!, $after: String, $first: Int, $filterBy: DataFindingFilters, $orderBy: DataFindingsGroupedByValueOrder) {
  dataFindingsGroupedByValue(
    groupBy: $groupBy
    filterBy: $filterBy
    first: $first
    after: $after
    orderBy: $orderBy
  ) {
    nodes {
      categories
      location {
        countryCode
        state
      }
      regionCount
      graphEntityCount
      graphEntity {
        id
        name
        type
        properties
        projects {
          id
          name
          slug
          isFolder
        }
        issues(filterBy: {status: [OPEN, IN_PROGRESS]}) {
          criticalSeverityCount
          highSeverityCount
          mediumSeverityCount
          lowSeverityCount
          informationalSeverityCount
        }
      }
      cloudAccount {
        id
        name
        externalId
        cloudProvider
      }
      dataClassifiers {
        id
        name
        category
        matcherType
        severity
      }
      securitySubCategories {
        id
        title
        externalId
        description
        category {
          id
          name
          description
          framework {
            id
            name
            description
            enabled
          }
        }
      }
      findingsCount
      dataFindings(first: 5) {
        nodes {
          ...DataFindingDetails
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
fragment DataFindingDetails on DataFinding {
  id
  name
  dataClassifier {
    id
    name
    category
    securitySubCategories {
      id
      title
      externalId
      description
      category {
        id
        name
        description
        framework {
          id
          name
          description
          enabled
        }
      }
    }
  }
  cloudAccount {
    id
    name
    externalId
    cloudProvider
  }
  location {
    countryCode
    state
  }
  severity
  totalMatchCount
  uniqueMatchCount
  graphEntity {
    id
    name
    type
    properties
    projects {
      id
      name
      slug
      isFolder
    }
  }
  externalSource
}
"""


SEVERITY_MAP = {
    "CRITICAL": IssueSeverity.High.value,
    "HIGH": IssueSeverity.High.value,
    "MEDIUM": IssueSeverity.Moderate.value,
    "LOW": IssueSeverity.Low.value,
    None: IssueSeverity.NotAssigned.value,
}

BEARER = "Bearer "


class WizVulnerabilityType(Enum):
    """Enum for Wiz vulnerability types."""

    HOST_FINDING = "host_finding"
    DATA_FINDING = "data_finding"
    VULNERABILITY = "vulnerability"
    CONFIGURATION = "configuration_finding"
    SECRET_FINDING = "secret_finding"
    END_OF_LIFE_FINDING = "end_of_life_finding"
    NETWORK_EXPOSURE_FINDING = "network_exposure_finding"
    EXTERNAL_ATTACH_SURFACE = "external_attack_surface"
    EXCESSIVE_ACCESS_FINDING = "excessive_access_finding"
    ISSUE = "issue"


def get_wiz_vulnerability_queries(project_id: str, filter_by: Optional[dict] = None) -> List[dict]:
    """Get the Wiz vulnerability queries.

    :param str project_id: The project ID
    :param Optional[dict] filter_by: Optional filter criteria
    :return: List of query configurations
    :rtype: List[dict]
    """
    if not filter_by:
        filter_by = {"projectId": [project_id]}

    return [
        {
            "type": WizVulnerabilityType.VULNERABILITY,
            "query": VULNERABILITY_QUERY,
            "topic_key": "vulnerabilityFindings",
            "file_path": VULNERABILITY_FILE_PATH,
            "asset_lookup": "vulnerableAsset",
            "variables": {
                "first": 200,
                "filterBy": filter_by,
                "fetchTotalCount": False,
            },
        },
        {
            "type": WizVulnerabilityType.CONFIGURATION,
            "query": CLOUD_CONFIG_FINDING_QUERY,
            "topic_key": "configurationFindings",
            "file_path": CLOUD_CONFIG_FINDINGS_FILE_PATH,
            "asset_lookup": "resource",
            "variables": {
                "first": 200,
                "quick": True,
                "filterBy": {
                    "rule": {},
                    "resource": {"projectId": [project_id]},
                },
            },
        },
        {
            "type": WizVulnerabilityType.HOST_FINDING,
            "query": HOST_VULNERABILITY_QUERY,
            "topic_key": "hostConfigurationRuleAssessments",
            "file_path": HOST_VULNERABILITY_FILE_PATH,
            "asset_lookup": "resource",
            "variables": {
                "first": 200,
                "filterBy": {
                    "resource": {"projectId": [project_id]},
                    "frameworkCategory": [],
                },
            },
        },
        {
            "type": WizVulnerabilityType.DATA_FINDING,
            "query": DATA_FINDING_QUERY,
            "topic_key": "dataFindingsGroupedByValue",
            "file_path": DATA_FINDINGS_FILE_PATH,
            "asset_lookup": "resource",
            "variables": {
                "first": 200,
                "filterBy": {"projectId": [project_id]},
                "orderBy": {"field": "FINDING_COUNT", "direction": "DESC"},
                "groupBy": "GRAPH_ENTITY",
            },
        },
        {
            "type": WizVulnerabilityType.SECRET_FINDING,
            "query": SECRET_FINDINGS_QUERY,
            "topic_key": "secretInstances",
            "file_path": SECRET_FINDINGS_FILE_PATH,
            "asset_lookup": "resource",
            "variables": {
                "first": 200,
                "fetchTotalCount": True,
                "filterBy": {"projectId": [project_id]},
                "orderBy": {"field": "RELATED_ISSUE_SEVERITY", "direction": "DESC"},
            },
        },
        {
            "type": WizVulnerabilityType.NETWORK_EXPOSURE_FINDING,
            "query": NETWORK_EXPOSURE_QUERY,
            "topic_key": "networkExposures",
            "file_path": NETWORK_EXPOSURE_FILE_PATH,
            "asset_lookup": "exposedEntity",
            "variables": {
                "first": 200,
                "filterBy": {
                    "type": ["PUBLIC_INTERNET"],
                },
            },
        },
        {
            "type": WizVulnerabilityType.END_OF_LIFE_FINDING,
            "query": END_OF_LIFE_QUERY,
            "topic_key": "vulnerabilityFindings",
            "file_path": END_OF_LIFE_FILE_PATH,
            "asset_lookup": "vulnerableAsset",
            "variables": {
                "first": 200,
                "orderBy": {"field": "TECHNOLOGY_END_OF_LIFE_DATE", "direction": "DESC"},
                "includeRelatedIssueAnalytics": True,
                "filterBy": {"isEndOfLife": True, "projectId": [project_id]},
            },
        },
        {
            "type": WizVulnerabilityType.EXTERNAL_ATTACH_SURFACE,
            "query": EXTERNAL_ATTACK_SURFACE_QUERY,
            "topic_key": "networkExposures",
            "file_path": EXTERNAL_ATTACK_SURFACE_FILE_PATH,
            "asset_lookup": "exposedEntity",
            "variables": {
                "first": 200,
                "filterBy": {
                    "type": ["PUBLIC_INTERNET"],
                },
            },
        },
        {
            "type": WizVulnerabilityType.EXCESSIVE_ACCESS_FINDING,
            "query": EXCESSIVE_ACCESS_QUERY,
            "topic_key": "excessiveAccessFindings",
            "file_path": EXCESSIVE_ACCESS_FILE_PATH,
            "asset_lookup": "scope",
            "variables": {
                "first": 200,
                "filterBy": {
                    "status": {"equals": ["OPEN"]},
                },
            },
        },
        # Note: EXCESSIVE_ACCESS_FINDING temporarily disabled due to 422 Unprocessable Entity error
        # This may indicate the feature is not available for all Wiz tenants or requires different permissions
    ]


def get_wiz_issue_queries(project_id: str, filter_by: Optional[dict] = None) -> List[dict]:
    """Get the Wiz issue queries.

    :param str project_id: The project ID
    :param Optional[dict] filter_by: Optional filter criteria
    :return: List of query configurations
    :rtype: List[dict]
    """
    if not filter_by:
        filter_by = {"project": project_id, "status": ["OPEN", "IN_PROGRESS"]}

    return [
        {
            "type": WizVulnerabilityType.ISSUE,
            "query": ISSUE_QUERY,
            "topic_key": "issues",
            "file_path": ISSUES_FILE_PATH,
            "variables": {
                "first": 200,
                "filterBy": filter_by,
                "fetchTotalCount": True,
                "fetchIssues": True,
                "fetchSecurityScoreImpact": False,
                "fetchThreatDetectionDetails": False,
                "fetchActorsAndResourcesGraphEntities": False,
                "fetchCloudAccountsAndCloudOrganizations": False,
                "fetchMultipleSourceRules": False,
                "groupBy": "SOURCE_RULE",
                "groupOrderBy": {"field": "SEVERITY", "direction": "DESC"},
                "orderBy": {"direction": "DESC", "field": "SEVERITY"},
            },
        },
    ]


SECRET_FINDINGS_QUERY = """query SecretFindingsTable($after: String, $first: Int, $filterBy: SecretInstanceFilters, $orderBy: SecretInstanceOrder, $fetchTotalCount: Boolean = true) {
  secretInstances(
    filterBy: $filterBy
    first: $first
    after: $after
    orderBy: $orderBy
  ) {
    nodes {
      id
      name
      type
      confidence
      severity
      isEncrypted
      isManaged
      externalId
      status
      firstSeenAt
      lastSeenAt
      lastModifiedAt
      lastUpdatedAt
      resolvedAt
      validationStatus
      passwordDetails {
        isComplex
        length
        entropy
      }
      rule {
        id
        name
        type
        validityCheckSupported
        isAiPowered
      }
      projects {
        id
        name
        slug
        isFolder
      }
      secretDataEntities {
        id
        name
        type
        properties
      }
      relatedIssueAnalytics {
        issueCount
        informationalSeverityCount
        lowSeverityCount
        mediumSeverityCount
        highSeverityCount
        criticalSeverityCount
      }
      resource {
        ...SecretFindingResourceDetails
        cloudAccount {
          id
          externalId
          name
          cloudProvider
        }
        tags {
          key
          value
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount @include(if: $fetchTotalCount)
  }
}

    fragment SecretFindingResourceDetails on SecretInstanceResource {
  id
  name
  type
  externalId
  status
  nativeType
  region
  typedProperties {
    ... on SecretInstanceResourceRepositoryBranch {
      repository {
        id
        name
      }
    }
  }
}

# variables:
# {
#   "fetchTotalCount": true,
#   "first": 20,
#   "filterBy": {},
#   "orderBy": {
#     "field": "RELATED_ISSUE_SEVERITY",
#     "direction": "DESC"
#   }
# }
"""


NETWORK_EXPOSURE_QUERY = """query NetworkExposuresTable($filterBy: NetworkExposureFilters, $first: Int, $after: String) {
  networkExposures(filterBy: $filterBy, first: $first, after: $after) {
    nodes {
      id
      exposedEntity {
        id
        name
        type
        properties
      }
      accessibleFrom {
        id
        name
        type
        properties
      }
      sourceIpRange
      destinationIpRange
      portRange
      appProtocols
      networkProtocols
      path {
        id
        name
        type
        properties
      }
      customIPRanges {
        id
        name
        ipRanges
      }
      firstSeenAt
      applicationEndpoints {
        id
        name
        type
        properties
      }
      type
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}

# variables:
# {
#   "first": 20,
#   "filterBy": {
#     "type": [
#       "PUBLIC_INTERNET"
#     ],
#     "publicInternetExposureFilters": {}
#   }
# }
"""

END_OF_LIFE_QUERY = """query EndOfLifeFindingsTable($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String, $orderBy: VulnerabilityFindingOrder = {direction: DESC, field: CREATED_AT}, $includeRelatedIssueAnalytics: Boolean = false) {
  vulnerabilityFindings(
    filterBy: $filterBy
    first: $first
    after: $after
    orderBy: $orderBy
  ) {
    nodes {
      ...VulnerabilityFindingFragment
      technologyEndOfLifeAt
      relatedIssueAnalytics @include(if: $includeRelatedIssueAnalytics) {
        ...VulnerabilityFindingRelatedIssueAnalyticsFragment
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

    fragment VulnerabilityFindingFragment on VulnerabilityFinding {
  id
  name
  detailedName
  description
  severity
  status
  fixedVersion
  detectionMethod
  firstDetectedAt
  lastDetectedAt
  resolvedAt
  validatedInRuntime
  hasTriggerableRemediation
  dataSourceName
  fixDate
  fixDateBefore
  publishedDate
  version
  isOperatingSystemEndOfLife
  recommendedVersion
  locationPath
  artifactType {
    ...SBOMArtifactTypeFragment
  }
  projects {
    id
    name
    slug
    isFolder
  }
  ignoreRules {
    id
  }
  layerMetadata {
    id
    details
    isBaseLayer
  }
  vulnerableAsset {
    ... on VulnerableAssetBase {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      nativeType
      externalId
      providerUniqueId
    }
    ... on VulnerableAssetVirtualMachine {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      operatingSystem
      imageName
      imageId
      imageNativeType
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      computeInstanceGroup {
        id
        externalId
        name
        replicaCount
        tags
      }
      nativeType
    }
    ... on VulnerableAssetServerless {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      nativeType
    }
    ... on VulnerableAssetContainerImage {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      repository {
        vertexId
        name
      }
      registry {
        vertexId
        name
      }
      scanSource
      executionControllers {
        ...VulnerableAssetExecutionControllerDetails
      }
      nativeType
      tagReferences
    }
    ... on VulnerableAssetContainer {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      executionControllers {
        ...VulnerableAssetExecutionControllerDetails
      }
      nativeType
    }
    ... on VulnerableAssetRepositoryBranch {
      id
      type
      name
      cloudPlatform
      repositoryId
      repositoryName
      nativeType
    }
    ... on VulnerableAssetEndpoint {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      nativeType
    }
    ... on VulnerableAssetPaaSResource {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      nativeType
    }
    ... on VulnerableAssetVirtualMachineImage {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      hasLimitedInternetExposure
      hasWideInternetExposure
      isAccessibleFromVPN
      isAccessibleFromOtherVnets
      isAccessibleFromOtherSubscriptions
      nativeType
    }
    ... on VulnerableAssetNetworkAddress {
      subscriptionId
      subscriptionName
      subscriptionExternalId
      tags
      address
      addressType
    }
    ... on VulnerableAssetCommon {
      id
      type
      name
      cloudPlatform
      subscriptionName
      subscriptionExternalId
      subscriptionId
      tags
      nativeType
    }
  }
}


    fragment SBOMArtifactTypeFragment on SBOMArtifactType {
  group
  codeLibraryLanguage
  osPackageManager
  hostedTechnology {
    id
    name
    icon
  }
  plugin
  custom
}


    fragment VulnerableAssetExecutionControllerDetails on VulnerableAssetExecutionController {
  id
  entityType
  externalId
  providerUniqueId
  name
  subscriptionExternalId
  subscriptionId
  subscriptionName
  ancestors {
    id
    name
    entityType
    externalId
    providerUniqueId
  }
}


    fragment VulnerabilityFindingRelatedIssueAnalyticsFragment on VulnerabilityFindingRelatedIssueAnalytics {
  issueCount
  informationalSeverityCount
  lowSeverityCount
  mediumSeverityCount
  highSeverityCount
  criticalSeverityCount
}

# variables:
# {
#   "orderBy": {
#     "field": "TECHNOLOGY_END_OF_LIFE_DATE",
#     "direction": "DESC"
#   },
#   "includeRelatedIssueAnalytics": true,
#   "first": 30,
#   "filterBy": {
#     "isEndOfLife": true
#   }
# }
"""

EXTERNAL_ATTACK_SURFACE_QUERY = """query NetworkExposuresTable($filterBy: NetworkExposureFilters, $first: Int, $after: String) {
  networkExposures(filterBy: $filterBy, first: $first, after: $after) {
    nodes {
      id
      exposedEntity {
        id
        name
        type
        properties
      }
      accessibleFrom {
        id
        name
        type
        properties
      }
      sourceIpRange
      destinationIpRange
      portRange
      appProtocols
      networkProtocols
      path {
        id
        name
        type
        properties
      }
      customIPRanges {
        id
        name
        ipRanges
      }
      firstSeenAt
      applicationEndpoints {
        id
        name
        type
        properties
      }
      type
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}"""

EXCESSIVE_ACCESS_QUERY = """query ExcessiveAccessFindingsTable($filterBy: ExcessiveAccessFindingFilters, $first: Int, $after: String) {
  excessiveAccessFindings(filterBy: $filterBy, first: $first, after: $after) {
    nodes {
      ...ExcessiveAccessFindingDetails
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}

    fragment ExcessiveAccessFindingDetails on ExcessiveAccessFinding {
  id
  projects {
    id
    name
    slug
    isFolder
  }
  name
  status
  severity
  remediationType
  excessiveServices
  hasUnusedAdminPermissions
  hasUnusedHighPermissions
  hasUnusedDataPermissions
  builtInPolicyRemediationName
  scope {
    graphEntity {
      id
      name
      type
      properties
    }
  }
  description
  documentationUrl
  remediationInstructions
  principal {
    graphEntity {
      id
      name
      type
      properties
    }
    cloudAccount {
      id
      name
      externalId
      cloudProvider
    }
  }
  context {
    graphEntity {
      id
      name
      type
      properties
    }
  }
  relatedIssueAnalytics {
    issueCount
    criticalSeverityCount
    highSeverityCount
    mediumSeverityCount
    lowSeverityCount
  }
}

# variables:
# {
#   "first": 20,
#   "filterBy": {
#     "status": {
#       "equals": [
#         "OPEN"
#       ]
#     }
#   }
# }
"""
