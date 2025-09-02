class InjectionException(RuntimeError):
    def __init__(self, dependency: str):
        message = (
            f'"{dependency}" is required as '
            "Configurable Field for the runnable."
            "Please check that its called with config fields"
        )
        super().__init__(message)
