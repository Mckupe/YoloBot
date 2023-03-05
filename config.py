from pydantic import BaseSettings

class Settings(BaseSettings):
    TOKEN:str
    PATHS:str
    class Config:
        env_file = '.env'
        
settings = Settings(_env_file='.env', _env_file_encoding='utf-8')