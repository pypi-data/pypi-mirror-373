class GraphQLMutations:
    @staticmethod
    def create_configuration():
        return """
            mutation createConfiguration($input: CreateConfigurationInput!) {
                createConfiguration(input: $input) {
                    id
                    deviceId
                    vehicleId
                    organizationId
                    fleetId
                }
            }
        """

    @staticmethod
    def create_message():
        return """
             mutation createMessage($input: CreateMessageInput!) {
                createMessage(input: $input) {
                    id
                    arbId
                    name
                    networkName
                    ecuId
                    ecuName
                    fileId
                }
            }
        """

    @staticmethod
    def upsert_signal_data():
        return """
            mutation UpsertSignalData($input: UpsertSignalDataInput) {
                upsertSignalData(input: $input) {
                    configurationId
                    messageId
                    messageName
                    name
                    paramType
                    unit
                }
            }
        """

    @staticmethod
    def upsert_gps_data():
        return """
             mutation UpsertGpsData($input: UpsertGpsDataInput) {
                upsertGpsData(input: $input) {
                    deviceId
                    fleetId
                    vehicleId
                    id
                    organizationId
                }
            }
        """

    @staticmethod
    def create_network_stats_mutation():
        return """
            mutation createNetworkStats($input: CreateNetworkStatsInput!) {
                createNetworkStats(input: $input) {
                    name
                    vehicleId
                    uploadId
                    totalMessages
                    matchedMessages
                    unmatchedMessages
                    errorMessages
                    longMessageParts
                    minTime
                    maxTime
                    rate
                }
            }
        """

    @staticmethod
    def upsert_dtc_mutation():
        return """
            mutation UpsertDtcData($input: [UpsertDtcDataInput]) {
                upsertDtcData(input: $input) {
                    configurationId
                    messageId
                }
            }
        """
