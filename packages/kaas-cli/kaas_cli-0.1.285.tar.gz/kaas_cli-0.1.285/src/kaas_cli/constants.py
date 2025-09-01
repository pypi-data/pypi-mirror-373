from pathlib import Path
from typing import Final

CONFIG_DIR_PATH: Final = Path(__file__).parent.parent / 'config'
CONFIG_FILE_PATH: Final = CONFIG_DIR_PATH / 'config.ini'
CONFIG_LOG_PATH: Final = CONFIG_DIR_PATH / 'kaas.log'
CONFIG_SESSION_PATH: Final = CONFIG_DIR_PATH / 'session.pkl'

GRAPHQL_URL: Final = '/graphql'
ORG_VAULT_CACHE_URLS: Final = '/api/orgs/{}/vaults/{}/caches/urls'
ORG_VAULT_CACHES_URL: Final = '/api/orgs/{}/vaults/{}/caches'

DEVICE_LOGIN_URL: Final = '/api/login/github/device'
USER_URL: Final = '/api/user/'

ORGANIZATIONS_URL: Final = '/api/orgs/'

VAULTS_ROOT_URL: Final = '/api/vaults'

UPLOAD_SUCCESS_MESSAGE: Final = 'Data successfully uploaded'
UPLOAD_FAILURE_MESSAGE: Final = 'Failed to upload file'

DEFAULT_DEV_SERVER_URL: Final = 'http://127.0.0.1:5000'
DEFAULT_PROD_SERVER_URL: Final = 'https://kaas.runtimeverification.com/'

DEFAULT_K_OUT_FOLDER: Final = './out'

KONTROL_JOB_URL: Final = '/api/orgs/{}/vaults/{}/jobs'
KONTROL_JOB_DETAILS_URL = '/api/jobs/{}'
