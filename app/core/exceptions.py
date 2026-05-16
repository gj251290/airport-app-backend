class AppError(Exception):
    """Clase base para todos los errores de la aplicación"""

    def __init__(self, message: str, code: str, status_code: int):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """Lanzada cuando un recurso solicitado no existe en la base de datos."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "RESOURCE_NOT_FOUND", 404)


class ConflictError(AppError):
    """Lanzada cuando una operación entra en conflicto con el estado actual"""

    def __init__(self, message: str = "Data conflict"):
        super().__init__(message, "DATA_CONFLICT", 409)


class ValidationError(AppError):
    """Lanzada cuando los datos de entrada no cumplen con las reglas de negocio"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, "VALIDATION_ERROR", 400)


class UnauthorizedError(AppError):
    """Lanzada cuando una solicitud requiere autenticacion valida"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED", 401)
