from analytics_ingest.internal.schemas.configuration_schema import ConfigurationSchema
from analytics_ingest.internal.utils.mutations import GraphQLMutations


class ConfigurationService:
    def __init__(self, executor):
        self.executor = executor

    def create(self, config_dict):
        schema = ConfigurationSchema.from_variables(config_dict)
        return self.executor.execute(
            GraphQLMutations.create_configuration(),
            {"input": schema.model_dump()},
        )
