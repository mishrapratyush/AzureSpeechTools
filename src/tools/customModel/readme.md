# Overview
Scripts here are to help you with automating building and testing of custom speech model. All these can be done manually by using the [azure custom speech portal](https://speech.microsoft.com/)

Building a custom model involves five steps:
1. Project Setup
2. Upload Custom Dataset
3. Training a custom model
4. Testing a custom model
5. Evaluating the result of the test

And then iterating through the above steps until the desired result is achieved. For example, of custom speech model, the result could be that the word error rate (WER) has come down to a certain percentage.

This process is depicted in the diagram below:![custom model overview](/docs/images/overview.png)

## Project set up
To train a custom model, a project needs to be created. Use the speech portal to create a project (provide a name and description) and specify the locale in which this model needs to be built.

## Uploading Custom Dataset
For training and testing custom models you need to upload dataset, three types of datasets are supported:

1) Plain Text (Language Model)
2) Pronunciation
3) Audio + Human-labeled transcripts (Acoustic Model)

More information can be found here: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-custom-speech-test-and-train#data-types

## Creating a custom model for training

Once the project is ready, and datasets are uploaded. Azure speech allows modifying speech model in three ways:
1. Update the language model
2. Improve recognition of specific words
3. Acoustic model

A more detailed explaination of this can be found here: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-custom-speech-test-and-train

The scripts here use data to update the language model and improve recognition of specific words. Acoustic model is not updated.

## Evaluating the custom model
Review the Word Error Rate (WER) in the portal. WER is a combination of insertion, substitution and deletion. Custom models generally help with substitution. Insertions and deletions are genereally due bad audio quality

## Publishing the custom model
Once a custom model is built and tested and evaluated it needs to be published before it can be consumed by other applications. To publish your custom model, see *'How to use the code*' section below

## Code Organization
The source code is organized as following:
| root              |                   |               |
| :-------------    | :----------:      | :---------:   |
| readme.md         |                   |               |
| uploadDataset.py  |                   |               |
| trainModel.py     |                   |               |
| evaluateModel.py  |                   |               |
| publish.py        |                   |               |
| copyModel.py      |                   |               |
| templateconfig.json |                 |               |
|     _             |  helper           |               |
|                   |   configuration.py |              |
|                   |   dataset.py      |               |
|                   |   datasetEnum.py  |               |
|                   |   endpoint.py     |               |
|                   |   project.py      |               |
|                   |   speechmodel.py |                |
|   _               |   docs            |               |
|                   |   _               |     images    |
|                   |                   |   overview.png  |
|   _               |   data            |               |
|                   |                   |              |
|                   |                   |              |

## Pre-requisites
1. Login into azure portal and create speech service
2. Create a blob storage account
3. Login to custom speech studio and create a project to be used by the script below
   
## How to use the code
1. Gather sentences relevant to your domain and save them in a text file. For example in data\train folder
2. Create pronunciation file (specific words and how to pronounce them). For example in data\train folder
3. Rename templateconfig.json file to config.json
4. Update config.json file to point to the files created in steps 1 and 2 above
5. Update the storage section of the config to point to your storage account. This is where the datasets will be uploaded to
6. Update the SpeechService section of the config to point to your speech service
7. Run the uploadDataset.py file to upload the training datata
8. Run the trainModel.py file to create the training model
9. Perform testing and evaluation
10. Run the publish.py file to publish the trained model

## Configuration

The config.json file serves as a template for your workflow. Each top-level configuration defines a particular part of the workflow. Here are the details of the top level configurations:

### Project Configurations
1. "SpeechService" - This config allows the tools to connect to your speech service instance. The two required sub-configs here are "Region" and "ApiKey". Set this to you values found in speech studio.
2. "Project" - This config allows the tools to pick the project/workspace in your speech service that you want to work in. The two required sub-configs here are "DisplayName" (The name of your project in speech studio) and "Locale"
3. "Storage" - The tools here connect to an azure blob storage account for managing data. Once you've created an azure blob storage account. Fill in the details in this config. Some of the required sub-configs here are "AccountName", "AccountKey", "ContainerName" etc. (Please refer to the template configuration for all the required values).
4. "BaseModel" - Azure speech service provides a pre-trained base model that all custom models are built on. Here you can define the exact release of the base model that you want to base your custom model on.

### Train/Text Configuration

1. "Datasets" - The uploadDataset tool allows you to automatically define, create and upload datasets to the speech studio. You can define as many datasets as you want in this list. Each defined dataset contains - "FilePath" (Path to local file that you want to upload), "DatasetDisplayName" (The name of the dataset as seen on the Speech studio, this name is also used in the later stages of the workflow), "Kind" (One of three supported dataset types - Language, Pronunciation, Acoustic)
2. "CustomModel" - Defines the details of the custom model you want train. Required configurations include - "DisplayName" (Name of the custom model), "Locale", "Datasets" (List of datasets as that need to be included in training your customModel)
3. "TestConfig" - Defines the tests that need to be run on a trained custom model. This allows you to compare different custom models to base models. Here are some required configs - "DisplayName" (The name of the test), "Model1" (First model that needs to be tested and compared), "Model2" (Second model that needs to be tested and compared), "DatasetDisplayName" (The dataset that you want to run your tests against), "Locale"

### Deployment/End-Point management Configurations

1. "EndPoint" - Model deployed as a service, required configurations - "DisplayName" (Name of the service), "Locale"
2. "CopyModel" - Allows you to copy a deployed model in one region into other regions. "Source" defines the currently deployed model, "Destination" defines the new service in a different region that needs to be created. Each requires the Details of the speech service and project that is being referred defined in the config. (Please refer to the template config for details). (Note: a new project is automatically created in the destination service with the defined project details).
