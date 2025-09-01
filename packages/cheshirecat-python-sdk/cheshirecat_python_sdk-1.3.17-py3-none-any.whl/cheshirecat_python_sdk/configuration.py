from pydantic import BaseModel


class Configuration(BaseModel):
    """
    Class containing all the configuration options and variables used by the package
    """
    host: str = "localhost"
    port: int = 1865
    auth_key: str = ""
    secure_connection: bool = False
