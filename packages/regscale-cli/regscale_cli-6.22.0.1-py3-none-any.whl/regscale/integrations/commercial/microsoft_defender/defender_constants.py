"""
Module to store constants for Microsoft Defender for Cloud
"""

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
IDENTIFICATION_TYPE = "Vulnerability Assessment"
CLOUD_RECS = "Microsoft Defender for Cloud Recommendation"
APP_JSON = "application/json"
AFD_ENDPOINTS = "microsoft.cdn/profiles/afdendpoints"


RESOURCES_QUERY = """
resources
| where subscriptionId == "{SUBSCRIPTION_ID}"
| extend resourceName = name,
        resourceType = type,
        resourceLocation = location,
        resourceGroup = resourceGroup,
        resourceId = id,
        propertiesJson = parse_json(properties)
| extend ipAddress =
   case(
       resourceType =~ "microsoft.network/networkinterfaces", tostring(propertiesJson.ipConfigurations[0].properties.privateIPAddress),
       resourceType =~ "microsoft.network/publicipaddresses", tostring(propertiesJson.ipAddress),
       resourceType =~ "microsoft.compute/virtualmachines", tostring(propertiesJson.networkProfile.networkInterfaces[0].id),
       ""
   )
| project resourceName, resourceType, resourceLocation, resourceGroup, resourceId, ipAddress, properties
"""

CONTAINER_SCAN_QUERY = """
securityresources
| where type == 'microsoft.security/assessments'
| summarize by assessmentKey=name
| join kind=inner (
    securityresources
    | where type == 'microsoft.security/assessments/subassessments'
    | extend assessmentKey = extract('.*assessments/(.+?)/.*', 1, id)
    | where resourceGroup == '{RESOURCE_GROUP}'
) on assessmentKey
| project assessmentKey, subassessmentKey=name, id, parse_json(properties), resourceGroup, subscriptionId, tenantId
| extend description = properties.description,
    displayName = properties.displayName,
    resourceId = properties.resourceDetails.id,
    tag = properties.additionalData.artifactDetails.tags,
    resourceSource = properties.resourceDetails.source,
    category = properties.category,
    severity = properties.status.severity,
    code = properties.status.code,
    timeGenerated = properties.timeGenerated,
    remediation = properties.remediation,
    impact = properties.impact,
    vulnId = properties.id,
    additionalData = properties.additionalData
    | where resourceId startswith "/subscriptions"
| order by ['id'] asc
"""

DB_SCAN_QUERY = """
securityresources
| where type =~ "microsoft.security/assessments/subassessments"
| extend assessmentKey=extract(@"(?i)providers/Microsoft.Security/assessments/([^/]*)", 1, id), subAssessmentId=tostring(properties.id), parentResourceId= extract("(.+)/providers/Microsoft.Security", 1, id)
| extend resourceIdTemp = iff(properties.resourceDetails.id != "", properties.resourceDetails.id, extract("(.+)/providers/Microsoft.Security", 1, id))
| extend resourceId = iff(properties.resourceDetails.source =~ "OnPremiseSql", strcat(resourceIdTemp, "/servers/", properties.resourceDetails.serverName, "/databases/" , properties.resourceDetails.databaseName), resourceIdTemp)
| where assessmentKey =~ "{ASSESSMENT_KEY}"
| where subscriptionId == "{SUBSCRIPTION_ID}"
| project assessmentKey,
    subAssessmentId,
    resourceId,
    name=properties.displayName,
    description=properties.description,
    severity=properties.status.severity,
    status=properties.status.code,
    cause=properties.status.cause,
    category=properties.category,
    impact=properties.impact,
    remediation=properties.remediation,
    benchmarks=properties.additionalData.benchmarks
| where status == "Unhealthy"
"""
