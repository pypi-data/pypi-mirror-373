class MoxnSchemaValidationError(Exception):
    """Raised when a schema fails validation"""

    def __init__(self, prompt_id: str, version_id: str, schema: str, detail: str):
        self.prompt_id = prompt_id
        self.version_id = version_id
        self.schema = schema
        self.detail = detail
        super().__init__(
            f"Schema validation failed for prompt {prompt_id} (version {version_id}): {detail}"
        )


class MoxnCodegenError(Exception):
    """Base class for codegen-related errors"""

    pass
