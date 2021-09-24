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

def main():
    try:

        logger = logging.getLogger(__name__)
        
        with open('config.json', mode='r') as configFile:
            configJson = json.load(configFile)

        custom_headers = {}

        copy_model_config = configJson.get("CopyModel")
        source_config_json = copy_model_config.get("Source")
        dest_config_json = copy_model_config.get("Destination")

        #1 get source model details
        project_config = configuration.ProjectConfiguration(source_config_json.get("Project"))
        speech_service_config = configuration.SpeechServiceConfiguration(source_config_json.get("SpeechService"))

        project_helper = project.ProjectHelper(speech_service_config)
        success, project_json = project_helper.get_project_by_display_name(custom_headers, project_config)

        if(project_json is None):
            logger.error("project: {0} does not exist. Exiting.".format(project_config.display_name))
            return
        
        project_models_url = project_json.get("links").get("models")
        url_parts = project_models_url.split("projects")
        project_id = url_parts[1].split("models")[0].replace("/", "")
        
        dataset_display_name = source_config_json.get("CustomModel").get("DisplayName")
        dataset_locale = source_config_json.get("CustomModel").get("Locale")

        model_helper = speechModel.SpeechModelHelper(speech_service_config)

        source_data_model = model_helper.get_project_model_by_display_name(custom_headers, 
            model_type= datasetEnum.ModelType.CustomModel.name, 
            display_name=dataset_display_name, 
            locale=dataset_locale, 
            project_id=project_id)

        if(source_data_model is None):
            logger.error("Dataset: {0} does not exist in project {1}. Exiting".format(dataset_display_name, project_config.display_name))
            return
        
        # 2 get destination project details
        dest_project_config = configuration.ProjectConfiguration(dest_config_json.get("Project"))
        
        dest_speech_service_config = configuration.SpeechServiceConfiguration(dest_config_json.get('SpeechService'))
        dest_project_helper = project.ProjectHelper(dest_speech_service_config)
        success, dest_project_response = dest_project_helper.get_project_by_display_name(custom_headers, dest_project_config)
        if(not success):
            print("Exiting.")
            return
        
        # 3 copy & patch model
        model_helper = speechModel.SpeechModelHelper(speech_service_config)
        success, response = model_helper.copy_model(custom_headers, source_data_model, dest_project_response, dest_speech_service_config)

    except Exception as ex:
        logger.exception(ex)
        
    except KeyboardInterrupt:
        logger.critical("Execution stopped.")

if __name__ == "__main__":
    main()