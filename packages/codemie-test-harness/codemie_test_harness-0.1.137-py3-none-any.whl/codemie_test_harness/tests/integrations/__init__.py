from codemie_sdk.models.integration import IntegrationType

integrations = [
    (IntegrationType.USER, True, IntegrationType.PROJECT),
    (IntegrationType.USER, True, None),
    (IntegrationType.USER, None, IntegrationType.PROJECT),
]
