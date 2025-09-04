from analytics_ingest.internal.schemas.network_schema import NetworkStatsSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations


def create_network(executor: GraphQLExecutor, config, variables: dict):
    stats = NetworkStatsSchema.from_variables(variables, config.vehicle_id)
    executor.execute(
        GraphQLMutations.create_network_stats_mutation(), {"input": stats.model_dump()}
    )
