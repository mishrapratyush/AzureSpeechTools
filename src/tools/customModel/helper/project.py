import requests
import logging
import json

logger = logging.getLogger(__name__)


class ProjectHelper:

    def __init__(self, speech_service_config):
        super().__init__()

        self.region = speech_service_config.region
        self.apiKey = speech_service_config.api_key
        
        self.headers = {'Ocp-Apim-Subscription-Key': self.apiKey}
        self.headers['contenty-type'] = 'application/json'

        self.url_template = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/{1}'
        self.datasetsUri = self.url_template.format(self.region, 'datasets')
        self.projectsUri = self.url_template.format(self.region, 'projects')
           
    def get_projects(self, custom_headers):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        response = requests.get(self.projectsUri, headers=custom_headers)
        if(response.ok):
            jsonObj = response.json()
            return jsonObj
        else:
            logger.error(response.status_code, response.text)
            raise ValueError(response.text)

    def filter_by_displayname(self, projects_json, display_name):
        for project in projects_json['values']:
            if(project['displayName'] == display_name):
                return project
        return None

    def create_project(self, custom_headers, display_name, locale, description):
        for key in self.headers:
            custom_headers[key] = self.headers[key]

        postBody = {
            'locale': locale,
            'displayName': display_name,
            'description': description,
        }

        response = requests.post(url=self.projectsUri, data=json.dumps(postBody), headers=custom_headers)
        jsonObj = response.json()
        if(response.ok):
            return True, jsonObj
        else:
            logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
            return (False, jsonObj)
    
    def get_project_by_display_name(self, custom_headers, project_config):
        projects_json = self.get_projects(custom_headers)
        display_name = project_config.display_name
        project_json = self.filter_by_displayname(projects_json, display_name)
        
        if(project_json is None):
            if(project_config.create_project == "true"):
                logger.info("project: {0} does not exist. Creating Project".format(display_name))
                locale = project_config.locale
                description = project_config.description
                success, project_json = self.create_project(custom_headers, display_name, locale, description)
                if (success):
                    print(f'Project created successfully. Project_url: {project_json["self"]}')
                else:
                    print(f'Project creation failed. ')
                return success, project_json
            else:
                logger.warning(f"project: {display_name} does not exist and CreateProject is {project_config.create_project}.")
                return False, None
        else:
            print(f'Found project: {project_json["self"]}')
            return True, project_json