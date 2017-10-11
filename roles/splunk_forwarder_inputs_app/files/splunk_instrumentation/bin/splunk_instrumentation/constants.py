import random

import json
import os
import sys
import splunk.rest as rest
from datetime_util import utcNow

LAST_READ_TIME_FILE = '.last_read'

COLLECTION_NAME = "instrumentation"
INSTRUMENTATION_SOURCETYPE = 'splunk_telemetry'
INSTRUMENTATION_INDEX_NAME = '_telemetry'
AUDIT_INDEX_NAME = '_telemetry'
AUDIT_SOURCETYPE = "splunk_telemetry_log"

INST_PRE_EXECUTE_SLEEP = 60

INST_VERSION = 1

# QUICKDRAW_URL is the QUICKDRAW_URL to hit
# DEFAULT_QUICKDRAW is the default url returned if we request QUICKDRAW_URL
DEFAULT_QUICKDRAW = {"url": "https://e1345286.api.splkmobile.com/1.0/e1345286"}
if os.environ.get('DEFAULT_QUICKDRAW'):
    DEFAULT_QUICKDRAW = {"url": os.environ.get('DEFAULT_QUICKDRAW')}
QUICKDRAW_URL = os.environ.get('QUICKDRAW_URL') or "https://quickdraw.splunk.com/telemetry/destination"
INST_DEBUG_LEVEL = os.environ.get('INST_DEBUG_LEVEL') or "ERROR"

INST_MODE = os.environ.get('INST_MODE') or "INPUT"
# INST_MODE = os.environ.get('INST_MODE') or "PROD"
INST_NO_COLLECT = os.environ.get('INST_NO_COLLECT') or False
INST_NO_SEND = os.environ.get('INST_NO_SEND') or False
INST_COLLECT_DATE = os.environ.get('INST_COLLECT_DATE') or False
INST_SCHEMA_FILE = os.environ.get('INST_SCHEMA_FILE') or os.path.dirname(os.path.realpath(__file__)) + '/schema.json'
INST_EXECUTION_ID = os.environ.get('INST_EXECUTION_ID') or "".join(random.choice('0123456789ABCDEF') for i in range(30))
INST_EXECUTION_START_TIME = utcNow()
INST_KV_OWNER = "nobody"

INST_APP_NAME = "splunk_instrumentation"

INST_PROFILE_OWNER = "nobody"
INST_PROFILE_APP = "splunk_instrumentation"

INST_LICENSE_TYPES = ['anonymous', 'license']

SPLUNKD_URI = rest.makeSplunkdUri()
SPLUNKRC = {"token": os.environ.get('INST_TOKEN') or None,
            "server_uri": os.environ.get('INST_SERVER_URI') or SPLUNKD_URI
            }

VISIBILITY_FIELDS_BY_NAME = {
    "license": "sendLicenseUsage",
    "anonymous": "sendAnonymizedUsage"
}

VISIBILITY_CONF_FIELDS = [
    'sendLicenseUsage',
    'sendAnonymizedUsage'
]

CLUSTER_MASTER_REQUIRED_CONF_FIELDS = VISIBILITY_CONF_FIELDS + ['deploymentID', 'swaEndpoint', 'telemetrySalt']

ENDPOINTS = {
    'APP_INFO': {
        'INFO': 'telemetry/general',
        'READONLY_INFO': 'configs/conf-telemetry/general',
        'RETRY': 'telemetry/general/retryEdit'
    },
    'SERVER_INFO': 'server/info',
    'KV_STORE': {
        'DEPLOYMENT_ID': 'storage/collections/data/instrumentation/instrumentation_deploymentID'
    },
    'MASTER_SETTINGS': 'telemetry/general/masterSettings'
}

path = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../')
sys.path.append(path)
sys.path.append(os.environ.get('SPLUNK_HOME') + '/etc/apps/framework/contrib/splunk-sdk-python')

# loads dev setup
if INST_MODE == "DEV":
    if not os.environ.get("SPLUNK_DB"):
        os.environ['SPLUNK_DB'] = os.environ.get('SPLUNK_HOME') + '/var/lib/splunk'
    INST_PRE_EXECUTE_SLEEP = 1
    if not os.environ.get('INST_KEY'):
        rc_file = os.path.dirname(os.path.realpath(__file__)) + '/splunkrc.json'
        SPLUNKRC = json.loads(open(rc_file, 'r').read())
