<a id="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://fbn-prd.lusid.com/configuration*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ApplicationMetadataApi* | [**list_access_controlled_resources**](docs/ApplicationMetadataApi.md#list_access_controlled_resources) | **GET** /api/metadata/access/resources | [EARLY ACCESS] ListAccessControlledResources: Get resources available for access control
*ConfigurationSetsApi* | [**add_configuration_to_set**](docs/ConfigurationSetsApi.md#add_configuration_to_set) | **POST** /api/sets/{type}/{scope}/{code}/items | [EARLY ACCESS] AddConfigurationToSet: Add a configuration item to an existing set
*ConfigurationSetsApi* | [**check_access_token_exists**](docs/ConfigurationSetsApi.md#check_access_token_exists) | **HEAD** /api/sets/personal/me | [DEPRECATED] CheckAccessTokenExists: Check the Personal Access Token exists for the current user
*ConfigurationSetsApi* | [**create_configuration_set**](docs/ConfigurationSetsApi.md#create_configuration_set) | **POST** /api/sets | [EARLY ACCESS] CreateConfigurationSet: Create a configuration set
*ConfigurationSetsApi* | [**delete_access_token**](docs/ConfigurationSetsApi.md#delete_access_token) | **DELETE** /api/sets/personal/me | [DEPRECATED] DeleteAccessToken: Delete any stored Personal Access Token for the current user
*ConfigurationSetsApi* | [**delete_configuration_item**](docs/ConfigurationSetsApi.md#delete_configuration_item) | **DELETE** /api/sets/{type}/{scope}/{code}/items/{key} | [EARLY ACCESS] DeleteConfigurationItem: Remove the specified configuration item from the specified configuration set
*ConfigurationSetsApi* | [**delete_configuration_set**](docs/ConfigurationSetsApi.md#delete_configuration_set) | **DELETE** /api/sets/{type}/{scope}/{code} | [EARLY ACCESS] DeleteConfigurationSet: Deletes a configuration set along with all their configuration items
*ConfigurationSetsApi* | [**generate_access_token**](docs/ConfigurationSetsApi.md#generate_access_token) | **PUT** /api/sets/personal/me | [DEPRECATED] GenerateAccessToken: Generate a Personal Access Token for the current user and stores it in the me token
*ConfigurationSetsApi* | [**get_configuration_item**](docs/ConfigurationSetsApi.md#get_configuration_item) | **GET** /api/sets/{type}/{scope}/{code}/items/{key} | GetConfigurationItem: Get the specific configuration item within an existing set
*ConfigurationSetsApi* | [**get_configuration_set**](docs/ConfigurationSetsApi.md#get_configuration_set) | **GET** /api/sets/{type}/{scope}/{code} | GetConfigurationSet: Get a configuration set, including all the associated metadata. By default secrets will not be revealed
*ConfigurationSetsApi* | [**get_system_configuration_items**](docs/ConfigurationSetsApi.md#get_system_configuration_items) | **GET** /api/sets/system/{code}/items/{key} | [EARLY ACCESS] GetSystemConfigurationItems: Get the specific system configuration items within a system set  All users have access to this endpoint
*ConfigurationSetsApi* | [**get_system_configuration_sets**](docs/ConfigurationSetsApi.md#get_system_configuration_sets) | **GET** /api/sets/system/{code} | GetSystemConfigurationSets: Get the specified system configuration sets, including all their associated metadata. By default secrets will not be revealed  All users have access to this endpoint
*ConfigurationSetsApi* | [**list_configuration_sets**](docs/ConfigurationSetsApi.md#list_configuration_sets) | **GET** /api/sets | [EARLY ACCESS] ListConfigurationSets: List all configuration sets summaries (I.e. list of scope/code combinations available)
*ConfigurationSetsApi* | [**update_configuration_item**](docs/ConfigurationSetsApi.md#update_configuration_item) | **PUT** /api/sets/{type}/{scope}/{code}/items/{key} | [EARLY ACCESS] UpdateConfigurationItem: Update a configuration item's value and/or description
*ConfigurationSetsApi* | [**update_configuration_set**](docs/ConfigurationSetsApi.md#update_configuration_set) | **PUT** /api/sets/{type}/{scope}/{code} | [EARLY ACCESS] UpdateConfigurationSet: Update the description of a configuration set


<a id="documentation-for-models"></a>
## Documentation for Models

 - [AccessControlledAction](docs/AccessControlledAction.md)
 - [AccessControlledResource](docs/AccessControlledResource.md)
 - [ActionId](docs/ActionId.md)
 - [ConfigurationItem](docs/ConfigurationItem.md)
 - [ConfigurationItemSummary](docs/ConfigurationItemSummary.md)
 - [ConfigurationSet](docs/ConfigurationSet.md)
 - [ConfigurationSetSummary](docs/ConfigurationSetSummary.md)
 - [CreateConfigurationItem](docs/CreateConfigurationItem.md)
 - [CreateConfigurationSet](docs/CreateConfigurationSet.md)
 - [IdSelectorDefinition](docs/IdSelectorDefinition.md)
 - [IdentifierPartSchema](docs/IdentifierPartSchema.md)
 - [Link](docs/Link.md)
 - [LusidProblemDetails](docs/LusidProblemDetails.md)
 - [LusidValidationProblemDetails](docs/LusidValidationProblemDetails.md)
 - [PersonalAccessToken](docs/PersonalAccessToken.md)
 - [ResourceId](docs/ResourceId.md)
 - [ResourceListOfAccessControlledResource](docs/ResourceListOfAccessControlledResource.md)
 - [ResourceListOfConfigurationItem](docs/ResourceListOfConfigurationItem.md)
 - [ResourceListOfConfigurationSet](docs/ResourceListOfConfigurationSet.md)
 - [ResourceListOfConfigurationSetSummary](docs/ResourceListOfConfigurationSetSummary.md)
 - [UpdateConfigurationItem](docs/UpdateConfigurationItem.md)
 - [UpdateConfigurationSet](docs/UpdateConfigurationSet.md)

