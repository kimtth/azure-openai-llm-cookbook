targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param resourceGroupName string = ''

var abbrs = {
  resourcesResourceGroups: 'rg'
  webStaticSites: 'stapp'
  appContainerApps: 'app'
}

var tags = {
  'azd-env-name': environmentName
}

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}-${environmentName}'
  location: location
  tags: tags
}

module backend 'core/host/container-app.bicep' = {
  name: 'backend'
  scope: rg
  params: {
    name: '${abbrs.appContainerApps}-backend-${environmentName}'
    location: location
    tags: tags
    env: [
      {
        name: 'AZURE_AI_PROJECT_ENDPOINT'
        value: ''
      }
      {
        name: 'MODEL_DEPLOYMENT_NAME'
        value: ''
      }
    ]
  }
}

module frontend 'core/host/staticwebapp.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: '${abbrs.webStaticSites}-${environmentName}'
    location: location
    tags: tags
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
