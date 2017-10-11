
import hashlib
import splunk.appserver.mrsparkle.lib.routes as routes
from splunk_instrumentation.splunkd import Splunkd
from splunk_instrumentation.deployment_id_manager import DeploymentIdManager
from splunk_instrumentation.telemetry_conf_service import TelemetryConfService
from splunk_instrumentation.service_bundle import ServiceBundle
from splunk_instrumentation.salt_manager import SaltManager
from splunk_instrumentation.packager.quick_draw import get_quick_draw
from splunk_instrumentation.metrics.metrics_schema import load_schema
from splunk_instrumentation.constants import INST_SCHEMA_FILE
from splunk_instrumentation.server_info_service import ServerInfoService
import splunk.auth
import json
import splunk.rest as rest


class SwaContext(object):
    '''
    Encapsulates all of the contextual data
    needed to render the SWA initialization script.
    '''
    salt = None
    deployment_id = ''
    send_anonymized_web_analytics = False
    user_id = ''
    swa_base_url = False
    schema = load_schema(INST_SCHEMA_FILE)
    server_uri = rest.makeSplunkdUri()
    qd = get_quick_draw()
    cds_url = qd.get('url')
    instance_guid = ''

    def should_load_swajs(self):
        '''
        Returns true if the telemetry conf file idicates we should be
        instrumentation the UI.
        '''
        return self.send_anonymized_web_analytics

    def to_dict(self):
        '''
        Returns the configuration items from this object in a dictionary.
        '''
        swa_js_url = routes.make_route('/static/app/splunk_instrumentation/build/pages/swa.js')

        result = {
            'swa_js_url': swa_js_url,
            'options': {
                'deploymentID': self.deployment_id,
                'userID': self.user_id,
                'version': self.schema.delivery.version,
                'instanceGUID': self.instance_guid,
                }
            }

        if self.swa_base_url:
            result['options']['url'] = routes.make_route(self.swa_base_url)
            result['options']['bundleDataFunction'] = 'json'
        else:
            result['options']['url'] = self.cds_url

        return result

    def update(self, cherrypy):
        '''
        Updates the volatile data members of the swa context.
        This method is hit each time an HTML page is hit, so the
        less work done here the better.
        '''
        splunkd = Splunkd(token=cherrypy.session.get('sessionKey'), server_uri=self.server_uri)

        telemetry_conf_service = TelemetryConfService(splunkd, is_read_only=True)
        telemetry_conf_service.fetch()

        # Specialize the telemetry_conf_service to be read only up front,
        # use the default construction for other services.
        services = ServiceBundle(splunkd, telemetry_conf_service=telemetry_conf_service)

        if not self.instance_guid:
            self.instance_guid = services.server_info_service.content['guid']

        salt_manager = SaltManager(services)
        self.salt = salt_manager.get_salt()

        deployment_id_manager = DeploymentIdManager(
            splunkd,
            telemetry_conf_service=telemetry_conf_service)

        self.deployment_id = deployment_id_manager.get_deployment_id() or ''

        self.swa_base_url = telemetry_conf_service.content.get('swaEndpoint')

        self.user_id = hashlib.sha256(self.salt + splunk.auth.getCurrentUser()['name']).hexdigest()
        
        self.send_anonymized_web_analytics = '0' != \
            telemetry_conf_service.content.get('sendAnonymizedWebAnalytics')


class SwaInitScriptRenderer(object):
    def __init__(self, cherrypy, context=None):
        self.cherrypy = cherrypy
        self.context = context or SwaContext()
    '''
    Handles rendering the SWA initialization script.
    '''
    template = '''
        <script>
            (function () {
                window._splunk_metrics_events = [];
                window._splunk_metrics_events.active = true;

                function onLoadSwa() {
                    new SWA(%(options)s);
                };

                document.addEventListener("DOMContentLoaded", function(event) {
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.src = '%(swa_js_url)s';
                    s.addEventListener('load', onLoadSwa);
                    var x = document.getElementsByTagName('script')[0];
                    x.parentNode.insertBefore(s, x);
                });
            }());
        </script>
    '''

    template_inactive = '''
          <script>
                window._splunk_metrics_events = {
                   push : function() {},
                   active: false,
                   }
          </script>
    '''

    def render(self):

        '''
        Renders the script template with the given context.
        The context must implement `to_dict`, which is called
        to retrieve the values for the template.
        '''

        if hasattr(self.cherrypy, 'session') and self.cherrypy.session is not None:
            self.context.update(self.cherrypy)

        if self.context.should_load_swajs():
            dic = self.context.to_dict()
            return self.template % ({'options': json.dumps(dic['options']), 'swa_js_url': dic['swa_js_url']})
        else:
            return self.template_inactive % self.context.to_dict()
