import sys
import time

import splunk_instrumentation.splunklib as splunklib
from splunk_instrumentation.splunkd import Splunkd
from splunk_instrumentation.service_bundle import ServiceBundle
from splunk_instrumentation.deployment_id_manager import DeploymentIdManager
import splunk_instrumentation.constants as constants
import splunk_instrumentation.client_eligibility as client_eligibility
from splunk_instrumentation.salt_manager import SaltManager

token = sys.stdin.read().rstrip()
splunkd = Splunkd(token=token, server_uri=constants.SPLUNKD_URI)

services = ServiceBundle(splunkd)
salt_manager = SaltManager(services)

# Cloud provisioning sets their own deployment
# ID's after starting splunk. But just in case
# we're stuck with the value from this script,
# let's use the correct prefix.
prefix = None
if services.server_info_service.is_cloud():
    prefix = 'CLOUD'
    if services.server_info_service.is_lite():
        prefix += 'LIGHT'

# Migration of the deployment ID from V1 of instrumentation
# requires waiting until the KV store is ready. We'll give
# it 5 minutes, then proceed without out.
t_start = time.time()
status = services.server_info_service.content.get('kvStoreStatus')
while status == 'starting' and (time.time() - t_start) < (5 * 60):
    time.sleep(10)
    services.server_info_service.fetch()
    status = services.server_info_service.content.get('kvStoreStatus')

deployment_id_manager = DeploymentIdManager(
    services.splunkd,
    telemetry_conf_service=services.telemetry_conf_service,
    server_info_service=services.server_info_service,
    prefix=prefix
)

# "Managed" Variable Sync Strategy
# --------------------------------
#
# Managed variables have complex lifecycles, and require
# synchronization among multiple nodes in a splunk deployment.
# This leads to their abstraction behind "manager" class interfaces.
#
# The strategy for syncing them is as follows:
# 
# * On Splunk start (when this script is triggered):
# ** Pull (or "sync") whatever value is at the cluster master,
#    overwriting any local value.
# *** Since configuring clustering often requires a splunk restart,
#     this provides immediate sync up when clustering is enabled.
# ** Call the getter for the managed value.
# *** The getters are designed to generate a new value
#     if one does not yet exist (perhaps this is a new installation,
#     and there was no cluster master to read from).
#
# * On read (when the value is required to perform a task, or to create an event)
# ** Only call the getter.
# ** Typically, it is looked up in the conf file, and created anew if needed.
# ** Special handling may apply, see the corresponding manager class.
# ** If a new value is created, it *must* be passed to the telemetry endpoint
#    to be persisted. Only this endpoint ensures replication to the cluster master.
#
# * On nightly scripted input
# ** Again, the value is pulled from the cluster master if possible
# ** This ensures liveness in the system, such that disagreements about
#    these values can eventually be resolved by conforming to the choice
#    of a single node. Basically, each night, the last search head to
#    replicate a choice to the cluster master the prior day will have won,
#    and all search heads will agree.
# ** In case there is no cluster master, it's usally a single instance,
#    or the existing conf file replication is relied upon for syncing
#    the managed values.

salt_manager.sync_with_cluster()
salt_manager.get_salt()

deployment_id_manager.sync_deployment_id()
deployment_id_manager.get_deployment_id()
