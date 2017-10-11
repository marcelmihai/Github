'''
Synopsis:

  splunk cmd python set_deployment_id.py -u SPLUNK_USER -p SPLUNK_PASSWORD --prefix PREFIX

Description:

  Sets the deployment ID for the instrumentation app via CLI. Intended for
  deployment automation purposes.

  Calls splunkd via the splunk-sdk, utilizing the same logic that generates
  the deployment ID in splunkweb during instrumentation opt-in via the web UI.

Expectations:

  SPLUNK_USER must have edit_telemetry_settings capability (the default for admin).
'''

import argparse
import sys
from splunk_instrumentation.splunkd import Splunkd
from splunk_instrumentation.deployment_id_manager import DeploymentIdManager

try:
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--user',
                        help='Splunk username',
                        required=True)

    parser.add_argument('-p', '--password',
                        help='Splunk password',
                        required=True)

    parser.add_argument('--prefix',
                        help='Desired prefix for the deployment ID',
                        required=False)

    args = parser.parse_args()

    splunkrc = {
        'username': args.user,
        'password': args.password
    }

    splunkd = Splunkd(**splunkrc)
    deployment_id_manager = DeploymentIdManager(splunkd)

    deploymentID = deployment_id_manager.get_deployment_id(no_create=True)

    if deploymentID is not None and deploymentID.startswith(args.prefix or ''):
        print("Deployment ID already initialized: %s" %
              deploymentID)
        # Only failures to set are considered error conditions.
        # So the exit code for an existing deployment ID is still 0.
        exit(0)
    else:
        deployment_id_manager.generate_new_deployment_id(prefix=args.prefix)
        deployment_id_manager.write_deployment_id_to_conf_file()
        print("Deployment ID successfully initialized: %s" %
              deployment_id_manager.get_deployment_id(no_create=True))
        exit(0)
except Exception as ex:
    sys.stderr.write(str(ex) + "\n")
    exit(1)
