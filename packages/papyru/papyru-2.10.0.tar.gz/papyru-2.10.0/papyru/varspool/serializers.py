from os import path

from papyru import JSONSchemaValidator, Serializer, Validator

from .types import Job, JobStatusHistory

SCHEMA_DIR = path.join(path.dirname(__file__), 'assets')


class JobValidator(Validator):
    schema_validator = JSONSchemaValidator('%s/Job.json' % SCHEMA_DIR)

    def validate(self, representation):
        self.schema_validator.validate(representation)

        return representation


class JobSerializer(Serializer):
    validator = JobValidator()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_instance(self, representation: dict) -> Job:
        return Job.from_dict(representation)


class JobStatusHistoryValidator(Validator):
    schema_validator = JSONSchemaValidator(
        '%s/JobStatusHistory.json' % SCHEMA_DIR)

    def validate(self, representation):
        self.schema_validator.validate(representation)

        return representation


class JobStatusHistorySerializer(Serializer):
    validator = JobStatusHistoryValidator()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_instance(self, representation: dict) -> JobStatusHistory:
        return JobStatusHistory.from_dict(representation)
