from fastapi import HTTPException, status

class TenantNotFound(HTTPException):
    def __init__(self, tenant: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f"Tenant '{tenant}' non trovato nel registry")

class TenantForbidden(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail="Tenant non autorizzato")

class SessionStoreUnavailable(HTTPException):
    def __init__(self):
        super().__init__(status_code=503, detail="Session store non disponibile")
