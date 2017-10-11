"""InstanceProfile class."""

import re
from splunk_instrumentation.splunklib import data as spldata
from splunk_instrumentation.constants import SPLUNKRC, VISIBILITY_FIELDS_BY_NAME
from splunk_instrumentation.indexing.query_runner import QueryRunner
from splunk_instrumentation.telemetry_conf_service import TelemetryConfService
from splunk_instrumentation.server_info_service import ServerInfoService
from splunk_instrumentation.deployment_id_manager import DeploymentIdManager
from splunk_instrumentation.service_bundle import ServiceBundle
from splunk_instrumentation.salt_manager import SaltManager


class InstanceProfile(object):
    """InstanceProfile.

    This class will retrive the instance's information.

    self.server_info = server information will be stored here
    self.visibility  = visibility information will be stored here
    """

    def __init__(self, splunkrc=SPLUNKRC, telemetryConfService=None, serverInfoService=None):
        """Constructor.
        It grabs a query_runner object according to the splunkrc params provided:
            - If splunkrc is a dictionary, it will instantiates a new QueryRuner object.
            - If given other object type, it will do Dependency Injection on query_runner
        """
        splunkrc = (splunkrc or SPLUNKRC)
        if type(splunkrc) is dict:
            self.query_runner = QueryRunner(splunkrc)
        else:
            self.query_runner = splunkrc

        self.profile = {}
        self.service = self.query_runner._splunkd.service
        if not telemetryConfService:
            self.telemetry_conf_service = TelemetryConfService(self.service)
        else:
            self.telemetry_conf_service = telemetryConfService

        if not serverInfoService:
            self.server_info_service = ServerInfoService(self.service)
        else:
            self.server_info_service = serverInfoService

        self.telemetry_conf_service.fetch()
        self.server_info_service.fetch()

        self.service_bundle = ServiceBundle(self.service,
                                            telemetry_conf_service=self.telemetry_conf_service,
                                            server_info_service=self.server_info_service)

        self.salt_manager = SaltManager(self.service_bundle)

        self.deployment_id_manager = DeploymentIdManager(
            self.service,
            telemetry_conf_service=self.telemetry_conf_service,
            server_info_service=self.server_info_service)

        self.roles = {role: True for role in self.server_info['server_roles']}

        # gets cluster info from endpoint
        self._load_json({"end_point": "cluster/config/config", "name": "cluster_config"})

        # if call fails set cluster_mode to disabled
        self.profile['cluster_mode'] = self._nested_get(self.profile, 'cluster_config.entry.content.mode', 'disabled')

        # gets search captian info from endpoint. noProxy is required so that it fails when instance is not the captain
        self._load_json({"end_point": "shcluster/captain/info", "name": "captain_info"}, noProxy=True, default={})

        # if captain/info returns a value it is caption  : overwrites server roles
        # this is failing so removing for the time being
        # self.roles['shc_captain'] = bool(self.profile.get('captain_info'))

        # if mode is not disabled then add in_cluster to roles   : overwrites server roles
        self.roles['in_cluster'] = not self.profile.get('cluster_mode') == 'disabled'
        #   overwrites server roles
        self.roles['cluster_master'] = self.profile.get('cluster_mode') == 'master'

        self._get_visibility()

    def opt_in_is_up_to_date(self):
        opt_in_version_str = self.telemetry_conf_service.content.get('optInVersion') or ''
        opt_in_version_acknowledged_str = self.telemetry_conf_service.content.get('optInVersionAcknowledged') or ''

        if not re.match('^[0-9]+$', opt_in_version_str):
            opt_in_version_str = None
        if not re.match('^[0-9]+$', opt_in_version_acknowledged_str):
            opt_in_version_acknowledged_str = None

        opt_in_version = int(opt_in_version_str) if opt_in_version_str else None
        opt_in_version_acknowledged = int(opt_in_version_acknowledged_str) if opt_in_version_acknowledged_str else None

        if not opt_in_version:
            # Should only happen if somebody removes the field manually
            # In that case, fall back to legacy behavior (ignore this check)
            return True

        if not opt_in_version_acknowledged:
            # Passed the check above, so we have a version number but no acknowledgement.
            # So, they're not up-to-date.
            return False

        return opt_in_version_acknowledged >= opt_in_version

    @property
    def server_info(self):
        return self.server_info_service.content

    def retry_transaction(self):
        self.telemetry_conf_service.retry_cluster_master_sync_transaction()

    def sync_deployment_id(self):
        self.deployment_id_manager.sync_deployment_id()

    def sync_salt(self):
        self.salt_manager.sync_with_cluster()

    def get_deployment_id(self):
        return self.deployment_id_manager.get_deployment_id()

    def _get_visibility(self):
        self.visibility = []
        for name, field in VISIBILITY_FIELDS_BY_NAME.iteritems():
            if int(self.telemetry_conf_service.content.get(field)):
                self.visibility.append(name)
        self.visibility.sort()

    def _nested_get(self, dic, path, default=0, separator='.'):
        """NestedGet.
        default path separator is .
        default value is 0
        """
        keys = path.split(separator)
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})

        if type(dic) is dict:
            return default
        return dic.get(keys[-1])

    def _load_json(self, endpoint, noProxy=False, default={}):
        '''
        calls endpoint['end_point'] and assigns the results to `self.profile[end_point['name']]`
        :param endpoint:
        :return:
        '''
        try:
            path = self._construct_path(endpoint, noProxy)
            payload = self.service.http.request(path,
                                                {'method': 'GET',
                                                 'headers': self.service._auth_headers}).get('body')
            if payload:
                result = (spldata.load(payload.read()))
                self.profile[endpoint['name']] = result['feed']
        # often if lisence does not permit this call it will return a 402 as exception
        except Exception:
            self.profile[endpoint['name']] = default
            return False

        return True

    def _construct_path(self, endpoint, noProxy):
        path = self.service.authority \
               + self.service._abspath(endpoint["end_point"], owner=self.query_runner._splunkd.namespace['owner'],
                                       app=self.query_runner._splunkd.namespace['app'])
        if (noProxy):
            path += "?noProxy=true"
        return path


def get_instance_profile(splunkrc=None, telemetryConfService=None, serverInfoService=None):
    get_instance_profile.instance = get_instance_profile.instance or InstanceProfile(
        splunkrc, telemetryConfService, serverInfoService)
    return get_instance_profile.instance


get_instance_profile.instance = None
