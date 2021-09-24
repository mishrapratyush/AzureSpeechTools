import requests
import json
from pathlib import Path, PurePath

from requests.models import Response
from helper import dataset, project, datasetEnum, speechModel, configuration
import logging
import sys
import time as systime

logging.basicConfig(stream=sys.stdout, 
                    level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')

logger = logging.getLogger(__name__)

def create_evaluation(configJson, model1_url, model2_url, dataset_url, project_url, locale, display_name, description):
    speech_service_config = configuration.SpeechServiceConfiguration(configJson.get('SpeechService'))
    request_uri = 'https://{0}.api.cognitive.microsoft.com/speechtotext/v3.0/evaluations'
    post_body = {
        'model1': {
            'self': model1_url
        },
        'model2': {
            'self': model2_url
        },
        'dataset': {
            'self': dataset_url
        },
        'project': {
            'self': project_url
        },
        'locale': locale,
        'displayName': display_name,
        'description': description
    }

    headers = {
        'Ocp-Apim-Subscription-Key': speech_service_config.api_key,
        'contenty-type': 'application/json'
    }
    request_uri = request_uri.format(speech_service_config.region)

    response = requests.post(request_uri, json.dumps(post_body), headers=headers)
    if(response.ok):
        jsonObj = response.json()
        logger.info('Started evaluations {0}.'.format(jsonObj['self']))
        return (True, jsonObj)
    else:
        logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
        return (False, None)

def get_evaluation_status(configJson, evaluation_uri):
    speech_service_config = configuration.SpeechServiceConfiguration(configJson.get('SpeechService'))

    headers = {
        'Ocp-Apim-Subscription-Key': speech_service_config.api_key,
        'contenty-type': 'application/json'
    }

    response = requests.get(url=evaluation_uri, headers=headers)
    jsonObj = response.json()
    if(response.ok):
        return (True, jsonObj)
    else:
        logger.error('Status code: {0}. Response text: {1}'.format(response.status_code, response.text))
        return (False, jsonObj)

def main():
    try:

        logger = logging.getLogger(__name__)
        
        with open('config.json', mode='r') as configFile:
            configJson = json.load(configFile)

        custom_headers = {}

        # step 1 - select project:
        project_config = configuration.ProjectConfiguration(configJson.get('Project'))
        project_display_name = project_config.display_name

        speech_service_config = configuration.SpeechServiceConfiguration(configJson.get('SpeechService'))
        project_helper = project.ProjectHelper(speech_service_config)
        projects_json = project_helper.get_projects(custom_headers)
        project_json = project_helper.filter_by_displayname(projects_json, project_display_name)

        if(project_json is None):
            logger.error("project: {0} does not exist".format(project_display_name))
            return
        
        project_models_url = project_json.get("links").get("models")
        url_parts = project_models_url.split("projects")
        project_id = url_parts[1].split("models")[0].replace("/", "")
        
        model_helper = speechModel.SpeechModelHelper(speech_service_config)

        storage_config = configuration.StorageConfiguration(configJson.get('Storage'))
        dataset_helper = dataset.DatasetHelper(storage_config, speech_service_config, project_config)

        evaluations_config = configuration.TestConfiguration(configJson.get('TestConfig'))
        evaluations = evaluations_config.evaluations

        for eval in evaluations:
            model1_url = model_helper.get_model_url(custom_headers, eval.get("Model1"), eval.get("Locale"), project_id)
            model2_url = model_helper.get_model_url(custom_headers, eval.get("Model2"), eval.get("Locale"), project_id)
            dataset_url = dataset_helper.get_dataset_url_by_display_name(custom_headers, eval.get("DatasetDisplayName"), eval.get("Locale"), project_id)
            project_url = project_json.get("self")

            print(f'model1: {model1_url}\nmodel2: {model2_url}\ndataset: {dataset_url}\nproject: {project_url}')
            success, result = create_evaluation(configJson, 
                model1_url, 
                model2_url, 
                dataset_url, 
                project_url, 
                eval.get("Locale"), 
                eval.get("DisplayName"), 
                eval.get("Description")
            )
            if(success):
                # wait until processing is complete
                evaluation_status = 'NotStarted'
                while (evaluation_status == 'NotStarted' or evaluation_status == 'Running'):
                    systime.sleep(10)
                    logger.info('Waiting for evaluation to be processed ... current status {0}'.format(evaluation_status))
                    status, jsonResponse = get_evaluation_status(configJson, result['self']) 
                    evaluation_status = jsonResponse['status']
                
                if (evaluation_status == 'Succeeded'):
                    logger.info('Evaluation processed successfully.')
                    logger.info(jsonResponse['properties'])
                else:
                    logger.error('Evaluation failed. Response: {0}'.format(jsonResponse))
            else:
                logger.info('Evaluation failed. Response: {0}'.format(result))

    except Exception as ex:
        logger.exception(ex)
        
    except KeyboardInterrupt:
        logger.critical("Execution stopped.")


if __name__ == "__main__":
    main()
