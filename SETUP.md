STEP 1: Create Resource Group and Storage Account on Microsoft Azure

1. Create Resource Group
$ az group create --name "20260708_Azure_RHEL_ZTP" --location "westus3"
{
  "id": "/subscriptions/(UUID)/resourceGroups/20260708_Azure_RHEL_ZTP",
  "location": "westus3",
  "managedBy": null,
  "name": "20260708_Azure_RHEL_ZTP",
  "properties": {
    "provisioningState": "Succeeded"
  },
  "tags": null,
  "type": "Microsoft.Resources/resourceGroups"
}

2. Create Storage Account
$ az storage account create --name "20260708azurerhelztp" --resource-group "20260708_Azure_RHEL_ZTP" --location "westus3" --sku Standard_LRS --kind StorageV2 --allow-blob-public-access true --https-only true --min-tls-version TLS1_2
{
  "accessTier": "Hot",
  "accountMigrationInProgress": null,
  "allowBlobPublicAccess": true,
  "allowCrossTenantReplication": false,
  "allowSharedKeyAccess": null,
  "allowSharedKeyAccessForServices": null,
  "allowedCopyScope": null,
  "azureFilesIdentityBasedAuthentication": null,
  "blobRestoreStatus": null,
  "creationTime": "2026-07-08T07:21:28.186877+00:00",
  "customDomain": null,
  "dataCollaborationPolicyProperties": null,
  "defaultToOAuthAuthentication": null,
  "dnsEndpointType": null,
  "dualStackEndpointPreference": null,
  "enableExtendedGroups": null,
  "enableHttpsTrafficOnly": true,
  "enableNfsV3": null,
  "encryption": {
    "encryptionIdentity": null,
    "keySource": "Microsoft.Storage",
    "keyVaultProperties": null,
    "requireInfrastructureEncryption": null,
    "services": {
      "blob": {
        "enabled": true,
        "keyType": "Account",
        "lastEnabledTime": "2026-07-08T07:21:28.514388+00:00"
      },
      "file": {
        "enabled": true,
        "keyType": "Account",
        "lastEnabledTime": "2026-07-08T07:21:28.514388+00:00"
      },
      "queue": null,
      "table": null
    }
  },
  "extendedLocation": null,
  "failoverInProgress": null,
  "geoPriorityReplicationStatus": null,
  "geoReplicationStats": null,
  "id": "/subscriptions/(UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Storage/storageAccounts/20260708azurerhelztp",
  "identity": null,
  "immutableStorageWithVersioning": null,
  "isHnsEnabled": null,
  "isLocalUserEnabled": null,
  "isSftpEnabled": null,
  "isSkuConversionBlocked": null,
  "keyCreationTime": {
    "key1": "2026-07-08T07:21:28.504215+00:00",
    "key2": "2026-07-08T07:21:28.504215+00:00"
  },
  "keyPolicy": null,
  "kind": "StorageV2",
  "largeFileSharesState": null,
  "lastGeoFailoverTime": null,
  "location": "westus3",
  "minimumTlsVersion": "TLS1_2",
  "name": "20260708azurerhelztp",
  "networkRuleSet": {
    "bypass": "None",
    "defaultAction": "Allow",
    "ipRules": [],
    "ipv6Rules": [],
    "resourceAccessRules": null,
    "virtualNetworkRules": []
  },
  "placement": null,
  "primaryEndpoints": {
    "blob": "https://20260708azurerhelztp.blob.core.windows.net/",
    "dfs": "https://20260708azurerhelztp.dfs.core.windows.net/",
    "file": "https://20260708azurerhelztp.file.core.windows.net/",
    "internetEndpoints": null,
    "ipv6Endpoints": null,
    "microsoftEndpoints": null,
    "queue": "https://20260708azurerhelztp.queue.core.windows.net/",
    "table": "https://20260708azurerhelztp.table.core.windows.net/",
    "web": "https://20260708azurerhelztp.z1.web.core.windows.net/"
  },
  "primaryLocation": "westus3",
  "privateEndpointConnections": [],
  "provisioningState": "Succeeded",
  "publicNetworkAccess": null,
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "routingPreference": null,
  "sasPolicy": null,
  "secondaryEndpoints": null,
  "secondaryLocation": null,
  "sku": {
    "name": "Standard_LRS",
    "tier": "Standard"
  },
  "statusOfPrimary": "available",
  "statusOfSecondary": null,
  "storageAccountSkuConversionStatus": null,
  "systemData": null,
  "tags": {},
  "type": "Microsoft.Storage/storageAccounts",
  "zones": null
}

3. Create Blob Container
$ az storage container create --name "public" --account-name "20260708azurerhelztp" --public-access container --auth-mode login
{
  "created": true
}

STEP 2: Create the blueprint on RHEL Image Builder

1. Base settings

a) Details
- Name: 20260708_Azure_RHEL_ZTP
- Description: ZTP Practice

b) Image output
- Image type: Package mode
- Image source: Red Hat Enterprise Linux (RHEL) 10
- Architecture: x86_64

c) Target environments
- Miscellaneous formats > Bare metal - Installer (.iso)

d) Register
- Register later

e) Repeatable build
- Disable repeatable build

f) Security
- No additional policy or profile

2. Repositories and packages
- Add the following Individual packages:
gdm
gnome-session
gnome-shell
nautilus

2bis. Advanced settings
a) Time
- Timezone: Asia/Seoul
- NTP servers: kr.pool.ntp.org

b) Locale
- Languages: en_US.UTF-8
- Keyboard: us

c) Hostname
- rhel-ztp-edge

d) Kernel
- No change

e) Systemd services
- Enabled services: gdm
- Disabled services: leave blank
- Masked services: leave blank

f) Firewall
- Ports: 22:tcp
- Enabled services: sshd
- Disabled services: leave blank

g) Groups
- Name, Group ID: wheel, 10

h) Users
- Username & Password & SSH key & Gruops & Admin: rhel, (Your Preferred Password), (empty), wheel, Y

i) First boot configuration
#!/bin/bash
# Overwrite GDM config to force automatic graphical login for the ZTP demo

cat > /etc/gdm/custom.conf <<EOF
# GDM configuration storage
[daemon]
AutomaticLoginEnable=True
AutomaticLogin=rhel
WaylandEnable=True

[security]

[xdmcp]

[chooser]

[debug]
#Enable=true
EOF

# Restart the display manager to apply the auto-login immediately
systemctl restart gdm

3. Create Blueprint

4. Assign Contributor Role to Red Hat Image Builder in Azure
$ az ad sp list --filter "startswith(displayName, 'Red Hat')" --query "[].{Id:id, DisplayName:displayName}" --output jsonc
[
  {
    "DisplayName": "Red Hat Image Builder",
    "Id": "(RHIB-UUID)"
  }
]
$ az role assignment create --assignee "(RHIB-UUID)" --role "Contributor" --scope "/subscriptions/(Subscription-UUID)/resourcegroups/20260708_Azure_RHEL_ZTP"
{
  "condition": null,
  "conditionVersion": null,
  "createdBy": null,
  "createdOn": "2026-07-08T07:46:13.290502+00:00",
  "delegatedManagedIdentityResourceId": null,
  "description": null,
  "id": "/subscriptions/(Subscription-UUID)/resourcegroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Authorization/roleAssignments/(Role-UUID)",
  "name": "(Role-UUID)",
  "principalId": "(RHIB-UUID)",
  "principalType": "ServicePrincipal",
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "roleDefinitionId": "/subscriptions/(Subscription-UUID)/providers/Microsoft.Authorization/roleDefinitions/(Role-UUID)",
  "scope": "/subscriptions/(Subscription-UUID)/resourcegroups/20260708_Azure_RHEL_ZTP",
  "type": "Microsoft.Authorization/roleAssignments",
  "updatedBy": "(UUID3)",
  "updatedOn": "2026-07-08T07:46:14.909294+00:00"
}

5. Register Microsoft.Compute on subscription
$ az provider register --namespace "Microsoft.Compute" --subscription "(Subscription-UUID)"
Registering is still on-going. You can monitor using 'az provider show -n Microsoft.Compute'
$ az provider show --namespace "Microsoft.Compute" --query "registrationState" -o tsv
Registered

6. Manually Test Initial Build and Access the File
- Press the Build Button on RHEL Image Builder
- Generate offline token from https://access.redhat.com/management/api = (RED_HAT_OFFLINE_TOKEN)
- Generate short-lived access token to use in next query
$ curl --request POST --url https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token --header "Content-Type: application/x-www-form-urlencoded" --data grant_type=refresh_token --data client_id=rhsm-api --data refresh_token="(RED_HAT_OFFLINE_TOKEN)"
{"access_token":"(RED_HAT_ACCESS_TOKEN)","expires_in":900,"refresh_expires_in":0,"refresh_token":"(RED_HAT_REFRESH_TOKEN)","token_type":"Bearer","not-before-policy":0,"session_state":"(Session-UUID)","scope":"roles web-origins offline_access"}

- Use access token to see if build succeeded
$ curl --silent --request GET --url https://console.redhat.com/api/image-builder/v1/composes/(Compose-UUID) --header "Authorization: Bearer (RED_HAT_ACCESS_TOKEN)" --header "Content-Type: application/json" | jq .
{
  "image_status": {
    "status": "success",
    "upload_status": {
      "options": {
        "image_name": "composer-api-(Composer-UUID)"
      },
      "status": "success",
      "type": "azure"
    }
  },
  "request": {
    "bootc": {
      "reference": "quay.io/redhat-services-prod/insights-management-tenant/image-builder-bootc-foundry/rhel-10-azure:latest"
    },
    "client_id": "ui",
    "customizations": {
      "groups": [
        {
          "gid": 10,
          "name": "wheel"
        }
      ],
      "users": [
        {
          "groups": [
            "wheel"
          ],
          "hasPassword": true,
          "name": "rhel"
        }
      ]
    },
    "image_description": "ZTP Practice",
    "image_name": "20260708_Azure_RHEL_ZTP",
    "image_requests": [
      {
        "architecture": "x86_64",
        "image_type": "azure",
        "upload_request": {
          "options": {
            "tenant_id": "(Tenant-UUID)",
            "resource_group": "20260708_Azure_RHEL_ZTP",
            "subscription_id": "(Subscription-UUID)",
            "hyper_v_generation": "V2"
          },
          "type": "azure"
        }
      }
    ]
  }
}

- Find exact name of storage account that RHEL created to store the blob
$ az storage account list --resource-group "20260708_Azure_RHEL_ZTP" --query "[?starts_with(name, 'ib')].name" -o tsv
ib(IB-UUID)

- Give myself direct read access to the Data Plane (not recommended in production, this is a demo)
$ az role assignment create --assignee "$(az ad signed-in-user show --query id -o tsv)" --role "Storage Blob Data Reader" --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Storage/storageAccounts/ib(IB-UUID)"
{
  "condition": null,
  "conditionVersion": null,
  "createdBy": null,
  "createdOn": "2026-07-08T19:06:00.526704+00:00",
  "delegatedManagedIdentityResourceId": null,
  "description": null,
  "id": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Storage/storageAccounts/ib(IB-UUID)/providers/Microsoft.Authorization/roleAssignments/(Role-UUID)",
  "name": "(Role-UUID)",
  "principalId": "(Principal-UUID)",
  "principalType": "User",
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "roleDefinitionId": "/subscriptions/(Subscription-UUID)/providers/Microsoft.Authorization/roleDefinitions/(Role-Definition-UUID)",
  "scope": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Storage/storageAccounts/ib(IB-UUID)",
  "type": "Microsoft.Authorization/roleAssignments",
  "updatedBy": "(Principal-UUID)",
  "updatedOn": "2026-07-08T19:06:00.784706+00:00"
}

- Check the file's name
$ az storage blob list --account-name "ib(IB-UUID)" --container-name "$(az storage container list --account-name "ib(IB-UUID)" --auth-mode login --query "[0].name" -o tsv)" --auth-mode login --output table
Name                                                   Blob Type    Blob Tier    Length       Content Type              Last Modified              Snapshot
-----------------------------------------------------  -----------  -----------  -----------  ------------------------  -------------------------  ----------
composer-api-(Build-UUID).vhd  PageBlob                  10737418752  application/octet-stream  2026-07-08T08:25:57+00:00
composer-api-(Build-UUID).vhd  PageBlob                  10737418752  application/octet-stream  2026-07-08T07:56:54+00:00
composer-api-(Build-UUID).vhd  PageBlob                  10737418752  application/octet-stream  2026-07-08T18:57:49+00:00

STEP 3: Create Azure Function and Achieve Sync with GitHub
- Create Azure Function on Azure Shell once
$ az storage account create --name "azurerhelztpfunction" --resource-group "20260708_Azure_RHEL_ZTP" --location "westus3" --sku Standard_LRS
{
  "accessTier": "Hot",
  "accountMigrationInProgress": null,
  "allowBlobPublicAccess": false,
  "allowCrossTenantReplication": false,
  "allowSharedKeyAccess": null,
  "allowSharedKeyAccessForServices": null,
  "allowedCopyScope": null,
  "azureFilesIdentityBasedAuthentication": null,
  "blobRestoreStatus": null,
  "creationTime": "2026-07-09T00:20:33.774796+00:00",
  "customDomain": null,
  "dataCollaborationPolicyProperties": null,
  "defaultToOAuthAuthentication": null,
  "dnsEndpointType": null,
  "dualStackEndpointPreference": null,
  "enableExtendedGroups": null,
  "enableHttpsTrafficOnly": true,
  "enableNfsV3": null,
  "encryption": {
    "encryptionIdentity": null,
    "keySource": "Microsoft.Storage",
    "keyVaultProperties": null,
    "requireInfrastructureEncryption": null,
    "services": {
      "blob": {
        "enabled": true,
        "keyType": "Account",
        "lastEnabledTime": "2026-07-09T00:20:34.101802+00:00"
      },
      "file": {
        "enabled": true,
        "keyType": "Account",
        "lastEnabledTime": "2026-07-09T00:20:34.101802+00:00"
      },
      "queue": null,
      "table": null
    }
  },
  "extendedLocation": null,
  "failoverInProgress": null,
  "geoPriorityReplicationStatus": null,
  "geoReplicationStats": null,
  "id": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Storage/storageAccounts/azurerhelztpfunction",
  "identity": null,
  "immutableStorageWithVersioning": null,
  "isHnsEnabled": null,
  "isLocalUserEnabled": null,
  "isSftpEnabled": null,
  "isSkuConversionBlocked": null,
  "keyCreationTime": {
    "key1": "2026-07-09T00:20:34.091680+00:00",
    "key2": "2026-07-09T00:20:34.091680+00:00"
  },
  "keyPolicy": null,
  "kind": "StorageV2",
  "largeFileSharesState": null,
  "lastGeoFailoverTime": null,
  "location": "westus3",
  "minimumTlsVersion": "TLS1_0",
  "name": "azurerhelztpfunction",
  "networkRuleSet": {
    "bypass": "None",
    "defaultAction": "Allow",
    "ipRules": [],
    "ipv6Rules": [],
    "resourceAccessRules": null,
    "virtualNetworkRules": []
  },
  "placement": null,
  "primaryEndpoints": {
    "blob": "https://azurerhelztpfunction.blob.core.windows.net/",
    "dfs": "https://azurerhelztpfunction.dfs.core.windows.net/",
    "file": "https://azurerhelztpfunction.file.core.windows.net/",
    "internetEndpoints": null,
    "ipv6Endpoints": null,
    "microsoftEndpoints": null,
    "queue": "https://azurerhelztpfunction.queue.core.windows.net/",
    "table": "https://azurerhelztpfunction.table.core.windows.net/",
    "web": "https://azurerhelztpfunction.z1.web.core.windows.net/"
  },
  "primaryLocation": "westus3",
  "privateEndpointConnections": [],
  "provisioningState": "Succeeded",
  "publicNetworkAccess": null,
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "routingPreference": null,
  "sasPolicy": null,
  "secondaryEndpoints": null,
  "secondaryLocation": null,
  "sku": {
    "name": "Standard_LRS",
    "tier": "Standard"
  },
  "statusOfPrimary": "available",
  "statusOfSecondary": null,
  "storageAccountSkuConversionStatus": null,
  "systemData": null,
  "tags": {},
  "type": "Microsoft.Storage/storageAccounts",
  "zones": null
}

- Create the Azure Function App
$ az functionapp create --resource-group "20260708_Azure_RHEL_ZTP" --consumption-plan-location "westus3" --runtime python --runtime-version 3.11 --functions-version 4 --name "rhel-ztp-composer-app" --storage-account "azurerhelztpfunction" --os-type Linux
Your Linux function app 'rhel-ztp-composer-app', that uses a consumption plan has been successfully created but is not active until content is published using Azure Portal or the Functions Core Tools.
Error while trying to create and configure an Application Insights for the Function App. Please use the Azure Portal to create and configure the Application Insights, if needed.
{
  "autoGeneratedDomainNameLabelScope": null,
  "availabilityState": "Normal",
  "clientAffinityEnabled": false,
  "clientAffinityPartitioningEnabled": null,
  "clientAffinityProxyEnabled": false,
  "clientCertEnabled": false,
  "clientCertExclusionPaths": null,
  "clientCertMode": "Required",
  "cloningInfo": null,
  "containerSize": 0,
  "customDomainVerificationId": "(Domain-ID)",
  "dailyMemoryTimeQuota": 0,
  "daprConfig": null,
  "defaultHostName": "rhel-ztp-composer-app.azurewebsites.net",
  "dnsConfiguration": {
    "dnsAltServer": null,
    "dnsLegacySortOrder": null,
    "dnsMaxCacheTimeout": null,
    "dnsRetryAttemptCount": null,
    "dnsRetryAttemptTimeout": null,
    "dnsServers": null
  },
  "enabled": true,
  "enabledHostNames": [
    "rhel-ztp-composer-app.azurewebsites.net",
    "rhel-ztp-composer-app.scm.azurewebsites.net"
  ],
  "endToEndEncryptionEnabled": false,
  "extendedLocation": null,
  "functionAppConfig": null,
  "hostNameSslStates": [
    {
      "hostType": "Standard",
      "name": "rhel-ztp-composer-app.azurewebsites.net",
      "sslState": "Disabled",
      "thumbprint": null,
      "toUpdate": null,
      "virtualIp": null
    },
    {
      "hostType": "Repository",
      "name": "rhel-ztp-composer-app.scm.azurewebsites.net",
      "sslState": "Disabled",
      "thumbprint": null,
      "toUpdate": null,
      "virtualIp": null
    }
  ],
  "hostNames": [
    "rhel-ztp-composer-app.azurewebsites.net"
  ],
  "hostNamesDisabled": false,
  "hostingEnvironmentProfile": null,
  "httpsOnly": false,
  "hyperV": false,
  "id": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Web/sites/rhel-ztp-composer-app",
  "identity": null,
  "inProgressOperationId": null,
  "ipMode": "IPv4",
  "isDefaultContainer": null,
  "isXenon": false,
  "keyVaultReferenceIdentity": "SystemAssigned",
  "kind": "functionapp,linux",
  "lastModifiedTimeUtc": "2026-07-09T00:25:03.106666",
  "location": "westus3",
  "managedEnvironmentId": null,
  "maxNumberOfWorkers": null,
  "name": "rhel-ztp-composer-app",
  "outboundIpAddresses": "(IPs)",
  "outboundVnetRouting": {
    "allTraffic": false,
    "applicationTraffic": false,
    "backupRestoreTraffic": false,
    "contentShareTraffic": false,
    "imagePullTraffic": false
  },
  "possibleOutboundIpAddresses": "(IPs)",
  "publicNetworkAccess": "Enabled",
  "redundancyMode": "None",
  "repositorySiteName": "rhel-ztp-composer-app",
  "reserved": true,
  "resourceConfig": null,
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "scmSiteAlsoStopped": false,
  "serverFarmId": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Web/serverfarms/WestUS3LinuxDynamicPlan",
  "siteConfig": {
    "acrUseManagedIdentityCreds": false,
    "acrUserManagedIdentityId": null,
    "alwaysOn": false,
    "apiDefinition": null,
    "apiManagementConfig": null,
    "appCommandLine": null,
    "appSettings": null,
    "autoHealEnabled": null,
    "autoHealRules": null,
    "autoSwapSlotName": null,
    "azureStorageAccounts": null,
    "connectionStrings": null,
    "cors": null,
    "defaultDocuments": null,
    "detailedErrorLoggingEnabled": null,
    "documentRoot": null,
    "elasticWebAppScaleLimit": null,
    "experiments": null,
    "ftpsState": null,
    "functionAppScaleLimit": 0,
    "functionsRuntimeScaleMonitoringEnabled": null,
    "handlerMappings": null,
    "healthCheckPath": null,
    "http20Enabled": false,
    "http20ProxyFlag": null,
    "httpLoggingEnabled": null,
    "ipSecurityRestrictions": [
      {
        "action": "Allow",
        "description": "Allow all access",
        "headers": null,
        "ipAddress": "Any",
        "name": "Allow all",
        "priority": 2147483647,
        "subnetMask": null,
        "subnetTrafficTag": null,
        "tag": null,
        "vnetSubnetResourceId": null,
        "vnetTrafficTag": null
      }
    ],
    "ipSecurityRestrictionsDefaultAction": null,
    "javaContainer": null,
    "javaContainerVersion": null,
    "javaVersion": null,
    "keyVaultReferenceIdentity": null,
    "limits": null,
    "linuxFxVersion": "",
    "loadBalancing": null,
    "localMySqlEnabled": null,
    "logsDirectorySizeLimit": null,
    "machineKey": null,
    "managedPipelineMode": null,
    "managedServiceIdentityId": null,
    "metadata": null,
    "minTlsCipherSuite": null,
    "minTlsVersion": null,
    "minimumElasticInstanceCount": 0,
    "netFrameworkVersion": null,
    "nodeVersion": null,
    "numberOfWorkers": 1,
    "phpVersion": null,
    "powerShellVersion": null,
    "preWarmedInstanceCount": null,
    "publicNetworkAccess": null,
    "publishingUsername": null,
    "push": null,
    "pythonVersion": null,
    "remoteDebuggingEnabled": null,
    "remoteDebuggingVersion": null,
    "requestTracingEnabled": null,
    "requestTracingExpirationTime": null,
    "scmIpSecurityRestrictions": [
      {
        "action": "Allow",
        "description": "Allow all access",
        "headers": null,
        "ipAddress": "Any",
        "name": "Allow all",
        "priority": 2147483647,
        "subnetMask": null,
        "subnetTrafficTag": null,
        "tag": null,
        "vnetSubnetResourceId": null,
        "vnetTrafficTag": null
      }
    ],
    "scmIpSecurityRestrictionsDefaultAction": null,
    "scmIpSecurityRestrictionsUseMain": null,
    "scmMinTlsVersion": null,
    "scmType": null,
    "tracingOptions": null,
    "use32BitWorkerProcess": null,
    "virtualApplications": null,
    "vnetName": null,
    "vnetPrivatePortsCount": null,
    "vnetRouteAllEnabled": null,
    "webSocketsEnabled": null,
    "websiteTimeZone": null,
    "windowsFxVersion": null,
    "xManagedServiceIdentityId": null
  },
  "sku": "Dynamic",
  "slotSwapStatus": null,
  "sshEnabled": null,
  "state": "Running",
  "storageAccountRequired": false,
  "suspendedTill": null,
  "systemData": null,
  "tags": null,
  "targetSwapSlot": null,
  "trafficManagerHostNames": null,
  "type": "Microsoft.Web/sites",
  "usageState": "Normal",
  "virtualNetworkSubnetId": null,
  "workloadProfileName": null
}

- Manually Turn on Application Insights in Azure GUI
Go to Function App > Monitoring > Application Insights and press "Turn on Application Insights"

- Assign Identity to Function App
$ az functionapp identity assign --name "rhel-ztp-composer-app" --resource-group "20260708_Azure_RHEL_ZTP"
{
  "principalId": "(Principal-UUID)",
  "tenantId": "(Tenant-UUID)",
  "type": "SystemAssigned",
  "userAssignedIdentities": null
}

- Grant Function App accesss to resource group
$ PRINCIPAL_ID=$(az functionapp identity show --name "rhel-ztp-composer-app" --resource-group "20260708_Azure_RHEL_ZTP" --query principalId -o tsv)
$ az role assignment create --assignee "$PRINCIPAL_ID" --role "Storage Blob Data Contributor" --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/20260708_Azure_RHEL_ZTP"
{
  "condition": null,
  "conditionVersion": null,
  "createdBy": null,
  "createdOn": "2026-07-09T05:20:06.121743+00:00",
  "delegatedManagedIdentityResourceId": null,
  "description": null,
  "id": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Authorization/roleAssignments/(Role-UUID)",
  "name": "(Role-UUID)",
  "principalId": "(Principal-UUID)",
  "principalType": "ServicePrincipal",
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "roleDefinitionId": "/subscriptions/(Subscription-UUID)/providers/Microsoft.Authorization/roleDefinitions/(Role-Definition-UUID)",
  "scope": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP",
  "type": "Microsoft.Authorization/roleAssignments",
  "updatedBy": "(Some-UUID)",
  "updatedOn": "2026-07-09T05:20:06.345754+00:00"
}

- Enable SCM to retrieve actual credentials needed to push from GitHub to Function App
$ az resource update --resource-group "20260708_Azure_RHEL_ZTP" --namespace "Microsoft.Web" --resource-type "basicPublishingCredentialsPolicies" --parent "sites/rhel-ztp-composer-app" --name "scm" --set properties.allow=true --api-version 2022-03-01
{
  "extendedLocation": null,
  "id": "/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP/providers/Microsoft.Web/sites/rhel-ztp-composer-app/basicPublishingCredentialsPolicies/scm",
  "identity": null,
  "kind": null,
  "location": "West US 3",
  "managedBy": null,
  "name": "scm",
  "plan": null,
  "properties": {
    "allow": true
  },
  "resourceGroup": "20260708_Azure_RHEL_ZTP",
  "sku": null,
  "tags": null,
  "type": "Microsoft.Web/sites/basicPublishingCredentialsPolicies"
}

- Retrieve Deployment XML Profile
$ az functionapp deployment list-publishing-profiles --name "rhel-ztp-composer-app" --resource-group "20260708_Azure_RHEL_ZTP" --xml
<publishData><publishProfile profileName="rhel-ztp-composer-app - Web Deploy" publishMethod="MSDeploy" publishUrl="rhel-ztp-composer-app.scm.azurewebsites.net:443" msdeploySite="rhel-ztp-composer-app" userName="REDACTED" userPWD="REDACTED" destinationAppUrl="http://rhel-ztp-composer-app.azurewebsites.net" SQLServerDBConnectionString="REDACTED" mySQLDBConnectionString="" hostingProviderForumLink="" controlPanelLink="https://portal.azure.com" webSystem="WebSites"><databases /></publishProfile><publishProfile profileName="rhel-ztp-composer-app - FTP" publishMethod="FTP" publishUrl="ftps://waws-prod-usw3-003.ftp.azurewebsites.windows.net/site/wwwroot" ftpPassiveMode="True" userName="REDACTED" userPWD="REDACTED" destinationAppUrl="http://rhel-ztp-composer-app.azurewebsites.net" SQLServerDBConnectionString="REDACTED" mySQLDBConnectionString="" hostingProviderForumLink="" controlPanelLink="https://portal.azure.com" webSystem="WebSites"><databases /></publishProfile><publishProfile profileName="rhel-ztp-composer-app - Zip Deploy" publishMethod="ZipDeploy" publishUrl="rhel-ztp-composer-app.scm.azurewebsites.net:443" userName="REDACTED" userPWD="REDACTED" destinationAppUrl="http://rhel-ztp-composer-app.azurewebsites.net" SQLServerDBConnectionString="REDACTED" mySQLDBConnectionString="" hostingProviderForumLink="" controlPanelLink="https://portal.azure.com" webSystem="WebSites"><databases /></publishProfile></publishData>

- Copy Paste the extracted XML block to GitHub Repository > Settings > Secrets and variables > Actions as secret named `AZURE_FUNC_PUBLISH_PROFILE`

- Create the Service Principal with `Contributor` rights that GitHub Actions will use
$ az ad sp create-for-rbac --name "github-actions-rhel-ztp-deployer" --role contributor --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/20260708_Azure_RHEL_ZTP --json-auth
Option '--sdk-auth' has been deprecated and will be removed in a future release.
Creating 'contributor' role assignment under scope '/subscriptions/(Subscription-UUID)/resourceGroups/20260708_Azure_RHEL_ZTP'
The output includes credentials that you must protect. Be sure that you do not include these credentials in your code or check the credentials into your source control. For more information, see https://aka.ms/azadsp-cli
{
  "clientId": "(Client-UUID)",
  "clientSecret": "(Client-Secret)",
  "subscriptionId": "(Subscription-UUID)",
  "tenantId": "(Tenant-UUID)",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}

- Copy Paste the JSON to GitHub Repository > Settings > Secrets and variables > Actions as secret named `AZURE_CREDENTIALS`
-- RHIB
RH_API_TOKEN = (Offline Generated Token)
RHEL_BLUEPRINT_ID = (Blueprint-UUID)
(Using method above, derive a temporary access token from your offline token)
$ curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "https://console.redhat.com/api/image-builder/v1/blueprints"
{"data":[{"description":"ZTP Practice","id":"(Blueprint-UUID)","last_modified_at":"2026-07-08T07:31:41Z","name":"20260708_Azure_RHEL_ZTP","version":1}],"links":{"first":"/api/image-builder/v1.0/blueprints?limit=100\u0026offset=0","last":"/api/image-builder/v1.0/blueprints?limit=100\u0026offset=0"},"meta":{"count":1}}

- Code the files in the repository

- Set up the following Environment Variables in Function Apps:
RHEL_IB_API_URL = https://console.redhat.com/api/image-builder/v1
-- Azure
IB_STORAGE_ACCOUNT_NAME = ib(IB-UUID)
AZURE_TENANT_ID = $ az account show --query tenantId --output tsv
AZURE_SUBSCRIPTION_ID = $ az account show --query id --output tsv
-- SMTP
SMTP_SERVER: smtp-mail.outlook.com
SMTP_PORT: 587
SMTP_USER: (Your outlook.com email address)
SMTP_PASS: (Your Microsoft App Password, create at https://account.live.com/proofs/Manage/additional)
NOTIFICATION_EMAIL: (Your outlook.com email address)

- Create GitHub repository and commit, which syncs to our Function App

STEP 4. Configure OpenWRT Router and .iPXE file
- Factory Reset OpenWRT Router

- Push rc.local file to Router, so that it the Router always serves the latest files upon reboot

STEP 5. Test on actual laptop
- Connect OpenWRT Router and Laptop directly using Ethernet, and set the Laptop to prioritize Network Booting(PXE Booting) if necessary