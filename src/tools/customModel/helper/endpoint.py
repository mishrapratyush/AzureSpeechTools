from datetime import datetime
import json
import logging
import requests
import time as systime

logger = logging.getLogger(__name__)


class EndpointHelper:

    def __init__(self, speech_service_config, end_point_config):
        super().__init__()

        self.region = speech_service_config.region
        self.apiKey = speech_service_config.api_key

        self.headers = {'Ocp-Apim-Subscription-Key': self.apiKey}
        self.headers['contenty-type'] = 'application/json'
        self.url_template = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/endpoints/{1}'
        self.end_points_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/endpoints'
        self.end_point_config = end_point_config

    def get_end_point_status(self, custom_headers, end_point_uri):
        jsonObj = self.get_end_point_by_uri(custom_headers=custom_headers, end_point_uri=end_point_uri)
        return jsonObj['status']

    def get_end_point_by_uri(self, custom_headers, end_point_uri):
        for key in self.headers:
            custom_headers[key] = self.headers[key]
        
        response = requests.get(end_point_uri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error(response.status_code)

    def filter_by_displayname(self, models_json, display_name):
        for model in models_json['values']:
            if(model['displayName'] == display_name):
                return model
        return None

    def create_end_point(self, custom_headers, custom_model_uri, project_uri):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        datetime_str = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        end_point_description = '{0} on {1}'.format(self.end_point_config.display_name, datetime_str)
        upload_body = {
            'model': {
                'self': custom_model_uri
            },
            "properties": {
                "loggingEnabled": 'true'
            },
            'locale': self.end_point_config.locale,
            'displayName': self.end_point_config.display_name,
            'description': end_point_description,
            'project':
                {
                    'self': project_uri
                }
            }
        end_points_uri = self.end_points_uri.format(self.region)
        response = requests.post(end_points_uri, headers=custom_headers, data=json.dumps(upload_body))

        if(response.ok):
            jsonObj = response.json()

            # wait until data processing is complete
            end_point_status = jsonObj['status']
            while (end_point_status == 'NotStarted' or end_point_status == 'Running'):
                systime.sleep(5)
                logger.info('Waiting for endpoint to be processed ... current status {0}'.format(end_point_status))
                response = self.get_end_point_by_uri(custom_headers, jsonObj['self'])
                end_point_status = response['status']

            if (end_point_status == 'Succeeded'):
                logger.info('Endpoint processed successfully.')
                return True, response
            else:
                logger.error('Endpoint creation failed. Endpoint status: {0}. Response: {1}'.format(end_point_status, response))
                return False, None
        else:
            logger.error('StatusCode:{0}. Response: {1}'.format(response.status_code, response.text))

        
