param name string
param location string = resourceGroup().location
param tags object = {}

param env array = []

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8003
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: name
          env: env
        }
      ]
    }
  }
}

output uri string = containerApp.properties.configuration.ingress.fqdn
