from linq.schema import workflow_api

APITaskInput = (
    workflow_api.ActionTaskInput
    | workflow_api.CodeTaskInput
    | workflow_api.ConditionalInput
    | workflow_api.RepeatedInput
    | workflow_api.DataConnectorInput
)
APITask = (
    workflow_api.ActionTask
    | workflow_api.CodeTask
    | workflow_api.Conditional
    | workflow_api.Repeated
    | workflow_api.DataConnector
)

APIDataInput = (
    workflow_api.TaskOutputReferenceInput
    | workflow_api.ReferenceDataInput
    | workflow_api.StaticDataInput
    | workflow_api.ParameterReferenceInput
)
APIData = (
    workflow_api.TaskOutputReference
    | workflow_api.ReferenceData
    | workflow_api.StaticData
    | workflow_api.ParameterReference
)
