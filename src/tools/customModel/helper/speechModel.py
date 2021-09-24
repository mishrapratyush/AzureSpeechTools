from datetime import datetime

from requests.models import Response
from helper.project import ProjectHelper
import requests
import json
import logging
import time as systime
from helper import datasetEnum

logger = logging.getLogger(__name__)


class SpeechModelHelper:

    def __init__(self, speech_service_config):
        super().__init__()
        self.api_key = speech_service_config.api_key
        self.region = speech_service_config.region

        self.headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        self.headers['contenty-type'] = 'application/json'
        self.custom_models_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/models'
        self.basemodels_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/models/base'
        # self.basemodel_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/models/base/{1}'
        self.project_models_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/projects/{1}/models'
        
    def get_models(self, custom_headers, model_type, **kwargs):
        nextLink = kwargs.get('nextLink', None)
        if (nextLink is None):
            if(model_type.lower() == datasetEnum.ModelType.BaseModel.name.lower()):
                models_uri = self.basemodels_uri.format(self.region)
            else:
                models_uri = self.custom_models_uri.format(self.region)
        else:
            models_uri = nextLink

        response = requests.get(models_uri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error(response.status_code)
    
    def get_project_models(self, custom_headers, model_type, project_id, **kwargs):
        nextLink = kwargs.get('nextLink', None)
        if (nextLink is None):
            if(model_type.lower() == datasetEnum.ModelType.BaseModel.name.lower()):
                models_uri = self.basemodels_uri.format(self.region)
            elif (model_type.lower() == datasetEnum.ModelType.CustomModel.name.lower()):
                models_uri = self.custom_models_uri.format(self.region)
            else:
                models_uri = self.project_models_uri.format(self.region, project_id)
        else:
            models_uri = nextLink

        response = requests.get(models_uri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error(response.status_code)

    def filter_by_display_name(self, models_json, display_name, locale):
        for model in models_json['values']:
            if(str(model['displayName']).lower() == str(display_name).lower() 
                and str(model['locale']).lower() == str(locale).lower()):
                return model
        return None

    def get_model_by_display_name(self, custom_headers, model_type, display_name, locale):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        models_json = self.get_models(custom_headers, model_type)   
        
        model_json = self.filter_by_display_name(
            models_json,
            display_name,
            locale)

        while(model_json is None and '@nextLink' in models_json):
            
            models_json = self.get_models(
                custom_headers=custom_headers,
                model_type=model_type,
                nextLink=models_json['@nextLink'])
            
            model_json = self.filter_by_display_name(
                models_json,
                display_name,
                locale)

        return model_json

    def get_project_model_by_display_name(self, custom_headers, model_type, display_name, locale, project_id):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        models_json = self.get_project_models(custom_headers, model_type, project_id)   
        
        model_json = self.filter_by_display_name(
            models_json,
            display_name,
            locale)

        while(model_json is None and '@nextLink' in models_json):
            
            models_json = self.get_models(
                custom_headers=custom_headers,
                model_type=model_type,
                nextLink=models_json['@nextLink'])
            
            model_json = self.filter_by_display_name(
                models_json,
                display_name,
                locale)

        return model_json

    def create_model(self, custom_headers, postBody):
        for key in self.headers:
            custom_headers[key] = self.headers[key]
        
        models_uri = self.custom_models_uri.format(self.region)

        response = requests.post(models_uri, json.dumps(postBody), headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return (True, jsonObj)
        else:
            logger.error(response.status_code)
            return (False, None)

    def get_model_status(self, custom_headers, model_uri):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        response = requests.get(model_uri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj['status']
        else:
            logger.error(response.status_code)
            return None

    def create_training_model(self,
            custom_headers,
            base_model_uri,
            project_uri,
            dataset_uris,
            custom_model_locale,
            custom_model_display_name):
        
        datetime_str = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        custom_model_description = '{0} on {1}'.format(custom_model_display_name, datetime_str)

        post_body = {
            'baseModel': {
                'self': base_model_uri
            },
            'project': {
                'self': project_uri
            },
            "datasets": [ { 'self': uri } for uri in dataset_uris],
            'locale': custom_model_locale,
            'displayName': custom_model_display_name,
            'description': custom_model_description
            }

        model_result, model_response = self.create_model(custom_headers, post_body)

        if(model_result):
            # wait until data processing is complete
            model_status = model_response['status']
            while (model_status == 'Created' or model_status == 'Running'):
                systime.sleep(5)
                logger.info('Waiting for training model to be processed ... current status {0}'.format(model_status))
                model_status = self.get_model_status(custom_headers, model_response['self']) 
            
            if (model_status == 'Succeeded'):
                logger.info('Training model created successfully.')
                return True, model_response
            else:
                logger.info('Training model creation failed. Training model status: {0}'.format(model_status))
                return False, None
        else:
            return False, None
        return (model_result, model_response)

    def get_model_url(self, custom_headers, model_config, locale, project_id):

        model_display_name = model_config.get("DisplayName")
        model_type = datasetEnum.ModelType.ProjectModel.name
        model_locale = locale
        
        if (model_config.get("IsBaseModel") == "true"):
            model_type = datasetEnum.ModelType.BaseModel.name
        
        model = self.get_project_model_by_display_name(
            custom_headers,
            model_type,
            model_display_name,
            model_locale,
            project_id)
        
        if (model is None):
            logger.error('Unable to fetch details for the model: {0}.'.format(model_display_name))
            return

        return model['self']
    
    def link_project_to_model(self, custom_headers, model_json, project_json, service_config):
        for key in self.headers:
            custom_headers[key] = self.headers[key]
        custom_headers["Ocp-Apim-Subscription-Key"] = service_config.api_key

        post_body = {
            "project": {
                "self": project_json.get("self")
            }
        }
    
        request_uri = model_json.get("self")

        response = requests.patch(url=request_uri, data=json.dumps(post_body), headers=custom_headers)
        jsonObj = response.json()
        if(response.ok):
            return True, jsonObj
        else:
            logger.error(response.status_code, response.text)
            return False, jsonObj

    def copy_model(self, custom_headers, source_model_json, dest_project_json, dest_service_config):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        post_body = {
            "targetSubscriptionKey": dest_service_config.api_key
        }

        request_uri = source_model_json.get("links").get("copyTo")
        response = requests.post(url=request_uri, headers=custom_headers, data=json.dumps(post_body))
        jsonObj = response.json()
        if(response.ok):
            # check if the model finished copying
            dest_model_json = jsonObj
            model_status = dest_model_json["status"]
            while (model_status == 'NotStarted' or model_status == 'Running'):
                systime.sleep(5)
                logger.info('Waiting for model to be copied ... current status {0}'.format(model_status))

                headers = {
                    "Ocp-Apim-Subscription-Key": dest_service_config.api_key,
                    "contenty-type": "application/json"
                }
                response = requests.get(dest_model_json["self"], headers=headers)
                jsonObj = response.json()
                if(response):
                    model_status = jsonObj['status']
                else:
                    logging.error(response.status_code, response.text)
                    return False, None
            
            if (model_status == 'Succeeded'):
                logger.info('Model copied successfully.')
            else:
                logger.error('Model copy failed. Response: {0}'.format(response))
                return False, None
            
            # link the model to project
            success, patch_response = self.link_project_to_model(custom_headers, dest_model_json, dest_project_json, dest_service_config)
            if (success):
                logger.info(f"Model linked to project")
                return True, patch_response
            else:
                logger.error('Failed to link new model to destinaton project.', patch_response.status_code, patch_response.text)
                return False, jsonObj
        else:
            logger.error(response.status_code, response.text)
            return False, jsonObj
    