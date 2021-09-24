import json
from pathlib import Path, PurePath
from helper import dataset, project, configuration
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
            logger.error("project: {0} does not exist, please check project name in configuration".format(project_display_name))
            return
        

        # step 2 - parse through all the defined datasets
        datasets = configJson.get('Datasets')
        storage_config = configuration.StorageConfiguration(configJson.get('Storage'))
        dataset_helper = dataset.DatasetHelper(storage_config, speech_service_config, project_config)


        for dataset_instance in datasets:
            dataset_config = configuration.DatasetConfiguration(dataset_instance)
            file_path = dataset_instance.get("FilePath")

            file_path = PurePath(str(Path.cwd()) + dataset_config.file_path)
            if(not Path(str(file_path)).exists()):
                logger.error('File: {0} does not exist'.format(str(file_path)))
                return

            result, response = dataset_helper.create_dataset(
            dataset_config.dataset_display_name,
            str(file_path),
            dataset_config.kind,
            project_json['self'],
            custom_headers)

            if(not result):
                logger.error('Failed to create dataset. Response: {0}'.format(response))
                return

    except Exception as ex:
        logger.exception(ex)
        
    except KeyboardInterrupt:
        logger.critical("Execution stopped.")


if __name__ == "__main__":
    main()