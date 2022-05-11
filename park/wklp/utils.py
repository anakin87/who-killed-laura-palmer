from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
import os
import logging
import yaml

api_key_header = APIKeyHeader(name='api_key')
right_api_key=os.getenv('WKLP_API_KEY','mywonderfulapikey')


def check_authentication(api_key: str = Depends(api_key_header)):
    """
    Check authentication using API key
    """
    if api_key != right_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized")
            
    return True

def set_logger():
    with open('./configs/logging_config.yml', 'r') as fin:
        logging_config = yaml.load(fin, Loader=yaml.FullLoader)
    logging.config.dictConfig(logging_config)    