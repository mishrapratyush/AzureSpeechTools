import json
from helper import project, datasetEnum, speechModel, configuration, endpoint
import logging
import sys

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')


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
        
        # step 2 - get custom model details
        model_helper = speechModel.SpeechModelHelper(speech_service_config)
        custom_models_json = model_helper.get_models(custom_headers, datasetEnum.ModelType.CustomModel.name)

        custom_model_config = configuration.CustomModelConfiguration(configJson.get('CustomModel'))
        
        custom_model_display_name = custom_model_config.display_name
        custom_model_locale = custom_model_config.locale
        
        custom_model_json = model_helper.filter_by_display_name(
                models_json=custom_models_json,
                display_name=custom_model_display_name,
                locale=custom_model_locale)
        
        while(custom_model_json is None and '@nextLink' in custom_models_json):
            
            custom_models_json = model_helper.get_models(
                custom_headers=custom_headers,
                model_type=datasetEnum.ModelType.CustomModel.name,
                nextLink=custom_models_json['@nextLink'])
            
            custom_model_json = model_helper.filter_by_display_name(
                models_json=custom_models_json,
                display_name=custom_model_display_name,
                locale=custom_model_locale)

        if (custom_model_json is None):
            logger.error('Unable to fetch details for the custom model: {0}.'.format(custom_model_display_name))
            return

        # step 3 - publish custom model
        end_point_config = configuration.EndpointConfiguration(configJson.get('EndPoint'))
        end_point_helper = endpoint.EndpointHelper(speech_service_config, end_point_config)
        project_uri = project_json['self']
        custom_model_uri = custom_model_json['self']
        end_point_result, end_point_response = end_point_helper.create_end_point(
            custom_headers,
            custom_model_uri,
            project_uri)

        if(end_point_result):
            logger.info(end_point_response)

    except Exception as ex:
        logger.exception(ex)
        
    except KeyboardInterrupt:
        logger.critical("Execution stopped.")

if __name__ == "__main__":
    main()
