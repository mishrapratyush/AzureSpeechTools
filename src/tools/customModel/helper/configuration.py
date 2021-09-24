class Configuration(object):

    def __init__(self, configJson):
        self.config_json = configJson
    
    def get_property(self, property_name):
        return self.config_json.get(property_name, None)


class SpeechServiceConfiguration(Configuration):
    def __init__(self, project_json):
        super().__init__(project_json)
    
    @property
    def region(self):
        return self.get_property('Region')
    
    @property
    def api_key(self):
        return self.get_property('ApiKey')


class ProjectConfiguration(Configuration):
    def __init__(self, project_json):
        if project_json is None:
            raise ValueError("Unable to parse Project information from config file. \nPlease check if Project is defined in the configuration file.")
        else:
            super().__init__(project_json)
    
    @property
    def display_name(self):
        return self.get_property('DisplayName')
    
    @property
    def locale(self):
        return self.get_property('Locale')
    
    @property
    def description(self):
        return self.get_property('Description')
    
    @property
    def create_project(self):
        return self.get_property('CreateProject')


class LanguageModelConfiguration(Configuration):
    def __init__(self, languagemodel_json):
        super().__init__(languagemodel_json)

    @property
    def dataset_display_name(self):
        return self.get_property('DatasetDisplayName')

    @property
    def file_path(self):
        return self.get_property('FilePath')


class PronunciationConfiguration(LanguageModelConfiguration):
    def __init__(self, pronunciation_json):
        super().__init__(pronunciation_json)

class AudioTranscriptConfiguration(LanguageModelConfiguration):
    def __init__(self, audio_transcript_json):
        super().__init__(audio_transcript_json)

class DatasetConfiguration(Configuration):
    def __init__(self, dataset_json):
        if dataset_json is None:
            raise ValueError("Unable to parse Dataset information from config file. \nPlease check if Dataset is defined in the configuration file.")
        else:
            super().__init__(dataset_json)

    @property
    def dataset_display_name(self):
        return self.get_property('DatasetDisplayName')

    @property
    def file_path(self):
        return self.get_property('FilePath')
    
    @property
    def kind(self):
        return self.get_property('Kind')

class BaseModelConfiguration(Configuration):
    def __init__(self, basemodel_json):
        super().__init__(basemodel_json)

    @property
    def display_name(self):
        return self.get_property('DisplayName')

    @property
    def locale(self):
        return self.get_property('Locale')


class CustomModelConfiguration(BaseModelConfiguration):
    def __init__(self, custom_model_json):
        super().__init__(custom_model_json)

    @property
    def datasets(self):
        return self.get_property('Datasets')


class EndpointConfiguration(BaseModelConfiguration):
    def __init__(self, end_point_json):
        super().__init__(end_point_json)


class StorageConfiguration(Configuration):
    def __init__(self, storage_Json):
        super().__init__(storage_Json)
    
    @property
    def default_endpoints_protocol(self):
        return self.get_property('DefaultEndpointsProtocol')

    @property
    def account_name(self):
        return self.get_property('AccountName')
    
    @property
    def account_key(self):
        return self.get_property('AccountKey')
    
    @property
    def endpoint_suffix(self):
        return self.get_property('EndpointSuffix')
    
    @property
    def container_name(self):
        return self.get_property('ContainerName')
    
    @property
    def sas_token_duration(self):
        return self.get_property('SasTokenDurationInHour')


class LoggerConfiguration(Configuration):
    def __init__(self, logger_json):
        super().__init__(logger_json)
    
    @property
    def handler(self):
        return self.get_property('Handler')
    
    @property
    def format_string(self):
        return self.get_property('Formatter')

    @property
    def log_level(self):
        return self.get_property('Level')


class TestConfiguration(Configuration):
    def __init__(self, testJson):
        super().__init__(testJson)

    @property
    def evaluations(self):
        return self.get_property('Evaluations')
