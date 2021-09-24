import requests
import json
import logging
import time as systime
from . import configuration
from datetime import datetime, timedelta
from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class DatasetHelper:

    def __init__(self, storage_config, speech_service_config, project_config):
        super().__init__()
        
        self.region = speech_service_config.region
        self.api_key = speech_service_config.api_key
        
        self.storage_container_name = storage_config.container_name
        self.storage_account_name = storage_config.account_name
        self.storage_account_key = storage_config.account_key
        self.storage_endpoints_protocol = storage_config.default_endpoints_protocol
        self.storage_endpoint_suffix = storage_config.endpoint_suffix
        self.storage_sas_token_duration = storage_config.sas_token_duration

        self.locale = project_config.locale

        self.headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        self.headers['contenty-type'] = 'application/json'
        self.url_template = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/{1}/'
        self.datasets_uri = self.url_template.format(self.region, 'datasets')
        self.project_datasets_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/projects/{1}/datasets'
        self.files_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/datasets/{1}/files'

    def get_datasets(self, custom_headers):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        response = requests.get(self.datasets_uri, headers=custom_headers)

        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
            return None
   
    def get_dataset_files(self, custom_headers, datasetId):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        getFilesUri = self.files_uri.format(self.region, datasetId)
        response = requests.get(getFilesUri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
            return None

    def upload_dataset(self, custom_headers, postBody):
        for key in self.headers:
            custom_headers[key] = self.headers[key]
        
        response = requests.post(self.datasets_uri, json.dumps(postBody), headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            logger.info('Uploaded dataset {0} to speech service.'.format(jsonObj['self']))
            return (True, jsonObj)
        else:
            logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
            return (False, None)

    def upload_file_to_blobstorage(self, file_path, blob_name):
        
        try:
            connection_string = "DefaultEndpointsProtocol={0};AccountName={1};AccountKey={2};EndpointSuffix={3}".format(
                self.storage_endpoints_protocol,
                self.storage_account_name,
                self.storage_account_key,
                self.storage_endpoint_suffix
                )

            blob_client = BlobClient.from_connection_string(
                connection_string,
                container_name=self.storage_container_name,
                blob_name=blob_name)

            with open(file_path, mode='rb') as dataFile:
                result = blob_client.upload_blob(dataFile, overwrite=True)

                logger.info('File {0} uploaded to blob container {1}.'.format(file_path, self.storage_container_name))
                return (True, result)
        
        except FileNotFoundError as ex:
            ex.status_code = 404
            return (False, ex)

        except AzureError as ex:
            return (False, ex)
    
        except Exception as ex:
            return (False, ex)
    
    def get_sas_token_for_blob(self, blob_name):
        try:
            sas_duration = int(self.storage_sas_token_duration)
            expiry_time = datetime.utcnow() + timedelta(hours=sas_duration)

            sas_token = generate_blob_sas(
                account_name=self.storage_account_name,
                account_key=self.storage_account_key,
                container_name=self.storage_container_name,
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True),
                expiry=expiry_time
            )
            
            blob_url = '{0}://{1}.blob.{2}/{3}/{4}?{5}'.format(
                self.storage_endpoints_protocol,
                self.storage_account_name,
                self.storage_endpoint_suffix,
                self.storage_container_name,
                blob_name,
                sas_token
            )

            logger.info('sas token genereated for blob {}'.format(blob_name))
            return True, blob_url

        except Exception as ex:
            return (False, ex)

    def get_dataset_status(self, custom_headers, datset_uri):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        response = requests.get(datset_uri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
            return None

    def create_dataset(self, dataset_name, file_path, dataset_kind, project_uri, custom_headers):
        file_parts = file_path.split("\\")
        file_name = file_parts[len(file_parts)-1]
        now = datetime.utcnow()
        blob_name = '{0}/{1}/{2}/{3}'.format(now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), file_name)

        blob_result, blob_response = self.upload_file_to_blobstorage(file_path, blob_name)
        if(blob_result):
            sas_result, sas_response = self.get_sas_token_for_blob(blob_name=blob_name)
            if(sas_result):

                datetime_str = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                dataset_description = '{0} on {1}'.format(dataset_name, datetime_str)

                uploadBody = {
                    'kind': dataset_kind,
                    'contentUrl': sas_response,
                    'locale': self.locale,
                    'displayName': dataset_name,
                    'description': dataset_description,
                    'project':
                        {
                            'self': project_uri
                        }
                    }

                upload_result, upload_response = self.upload_dataset(custom_headers, uploadBody)

                if(upload_result):
                    # wait until data processing is complete
                    dataset_status = 'NotStarted'
                    while (dataset_status == 'NotStarted' or dataset_status == 'Running'):
                        systime.sleep(5)
                        logger.info('Waiting for dataset to be processed ... current status {0}'.format(dataset_status))
                        jsonResponse = self.get_dataset_status(custom_headers, upload_response['self']) 
                        dataset_status = jsonResponse['status']
                    
                    if (dataset_status == 'Succeeded'):
                        logger.info('Dataset processed successfully.')
                        return True, upload_response
                    else:
                        logger.error('Datset creation failed. Response: {0}'.format(jsonResponse))
                        return False, None
                else:
                    return False, None
            else:
                logger.error('Failed to generate sas token for blob: {0}'.format(blob_name))
                logger.info(sas_response)
                return False, None
        else:
            logger.error('Failed to upload file to blob storage.')
            logger.info(blob_response)
            return False, None

    def filter_by_display_name(self, dataset_json, display_name, locale):    
        for dataset in dataset_json['values']:
            if(str(dataset['displayName']).lower() == str(display_name).lower() 
                and str(dataset['locale']).lower() == str(locale).lower()):
                return dataset
        return None

    def get_project_datasets(self, custom_headers, project_id, **kwargs):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        nextLink = kwargs.get('nextLink', None)

        if (nextLink is None):
            request_uri = self.project_datasets_uri.format(self.region, project_id)
        else:
            request_uri = nextLink
        
        response = requests.get(request_uri, headers=custom_headers)

        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
            return None

    def get_project_dataset_by_display_name(self, custom_headers, display_name, locale, project_id):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        datasets_json = self.get_project_datasets(custom_headers, project_id)   
        
        dataset_json = self.filter_by_display_name(
            datasets_json,
            display_name,
            locale)

        while(dataset_json is None and '@nextLink' in datasets_json):
            
            datasets_json = self.get_project_datasets(
                custom_headers=custom_headers,
                project_id=project_id,
                nextLink=dataset_json['@nextLink'])
            
            dataset_json = self.filter_by_display_name(
                datasets_json,
                display_name,
                locale)

        return dataset_json

    def get_dataset_url_by_display_name(self, custom_headers, display_name, locale, project_id):
            
        dataset_json = self.get_project_dataset_by_display_name(custom_headers, display_name, locale, project_id)
        if (dataset_json is None):
            return
        else:
            return dataset_json["self"]
