import json
from pathlib import Path, PurePath
from helper import dataset, project, datasetEnum, speechModel, configuration
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
        
        # step 1 - select or create project:
        project_config = configuration.ProjectConfiguration(configJson.get('Project'))
        project_display_name = project_config.display_name
        
        speech_service_config = configuration.SpeechServiceConfiguration(configJson.get('SpeechService'))
        project_helper = project.ProjectHelper(speech_service_config)
        projects_json = project_helper.get_projects(custom_headers)
        project_json = project_helper.filter_by_displayname(projects_json, project_display_name)

        if(project_json is None):
            logger.warning("project: {0} does not exist. Creating Project".format(project_display_name))
            project_locale = project_config.locale
            project_description = project_config.description
            success, response = project_helper.create_project(custom_headers, project_display_name, project_locale, project_description)
            if (success):
                print(f'Project created successfully. Project_url: {response["self"]}')        
            else:
                print(f'Project creation failed. Exiting....')
                return
        else:
            print(f'Found project: {project_json["self"]}')

        project_models_url = project_json.get("links").get("models")
        url_parts = project_models_url.split("projects")
        project_id = url_parts[1].split("models")[0].replace("/", "")

        # Get dataset display names from config and find URI
        storage_config = configuration.StorageConfiguration(configJson.get('Storage'))
        dataset_helper = dataset.DatasetHelper(storage_config, speech_service_config, project_config)
        custom_model_config = configuration.CustomModelConfiguration(configJson.get('CustomModel'))

        dataset_uris = []
        for dataset_instance in custom_model_config.datasets:
            dataget_uri = dataset_helper.get_dataset_url_by_display_name({}, dataset_instance, custom_model_config.locale, project_id)
            dataset_uris.append(dataget_uri)
        
        # step 6 - create custom model based on a base model
        model_helper = speechModel.SpeechModelHelper(speech_service_config)

        base_model_config = configuration.BaseModelConfiguration(configJson.get('BaseModel'))
        
        base_model_display_name = base_model_config.display_name
        base_model_locale = base_model_config.locale
        
        base_model = model_helper.get_model_by_display_name(
            custom_headers,
            datasetEnum.ModelType.BaseModel.name,
            base_model_display_name,
            base_model_locale)
        
        if (base_model is None):
            logger.error('Unable to fetch details for the basemodel: {0}.'.format(base_model_display_name))
            return

        base_model_uri = base_model['self']
        custom_model_result, custom_model_response = model_helper.create_training_model(
            custom_headers=custom_headers,
            base_model_uri=base_model_uri,
            project_uri=project_json['self'],
            dataset_uris=dataset_uris,
            custom_model_locale=base_model_locale,
            custom_model_display_name=custom_model_config.display_name)            
        if(custom_model_result):
            logger.info('Custom training model created. Response: {0}'.format(custom_model_response))
        else:
            logger.error('Failed to create the training model. Response: {0}'.format(custom_model_response))

    except Exception as ex:
        logger.exception(ex)
        
    except KeyboardInterrupt:
        logger.critical("Execution stopped.")


if __name__ == "__main__":
    main()
