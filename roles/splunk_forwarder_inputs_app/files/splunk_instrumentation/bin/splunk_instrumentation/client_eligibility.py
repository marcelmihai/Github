import splunk_instrumentation.splunklib as splunklib
from splunk_instrumentation.service_bundle import ServiceBundle

def get_ui_eligibility(services):
    '''
    Is this node eligible to display the instrumentation UI?
    '''
    return get_eligibility(services, reject_cloud=True)

def get_swa_eligibility(services):
    '''
    Is this node eligible for swa instrumentation?
    '''
    return get_eligibility(services, reject_cloud=False)

def get_eligibility(services, reject_cloud=True):
    '''
    Determines whether the UI for the instrumentation app should be visible,
    including the initial opt-in modal and all settings/logs pages.
    This is determined by license type, and server roles.

    DOES NOT check user capabilities. This module should be usable from a
    scripted input, as well as from cherrypy. So we cannot make the
    assumption that a user is logged in. For this reason, that check is 
    handled in the instrumentation controller.
    '''

    instance_type = (services.server_info_service.content.get('instance_type') or '').lower()
    if reject_cloud and 'cloud' in instance_type:
        return {
            'is_eligible': False,
            'reason': 'UNSUPPORTED'
        }

    if services.server_info_service.content.get('isFree', '0') == '1':
        return {'is_eligible': True}

    if (check_server_roles_for_eligibility(
            services.server_info_service.content.get('server_roles'))):
        return {'is_eligible': True}
    else:
        return {
            'is_eligible': False,
            'reason': 'UNSUPPORTED'
        }

def check_server_roles_for_eligibility(server_roles):
    '''
    Args:
      - server_roles: A list of server roles (strings)

    Returns:
      True or False, indicating whether this server type is supported
    '''

    roles = {}
    for role in server_roles:
        roles[role] = True

    # The whitelist determines what nodes are even considered
    # for instrumentation eligibility. All nodes that contain
    # any of these server roles will be considered (but may
    # ultimately still be rejected based on the blacklist, etc.)
    whitelist = [
        # Search heads are the typical place to access the UI.
        'search_head',
        # Some search heads lack the search_head role and instead
        # report as shc_member or shc_captain
        'shc_member',
        'shc_captain',
        # Have to whitelist indexer to cover single instance deployments.
        # (A single instance is not a "search head" - search heads only
        #  exist when paired with separate indexers).
        'indexer'
    ]

    # The blacklist immediately rejects servers that have any of
    # the blacklisted roles.
    blacklist = [
        # The cluster master does not propagate conf settings to the search
        # heads, so we blacklist it for the UI to avoid inconsistent configurations
        # in the cluster.
        'cluster_master',
        # We've whitelisted indexers to handle the single instance case.
        # However, in a distributed deployment you should only be configuring
        # settings on the SH's (since they will propagate values correctly
        # within the cluster), so we'll blacklist cluster_slaves to catch
        # this case.
        'cluster_slave',
        # Heavyweight forwarder is never considered eligible.
        'heavyweight_forwarder'
    ]

    special_case_rejections = [
        # Any indexer that is a search peer is in a distributed environment.
        # In a distributed environment, the instrumentation UI must be accessed
        # by a search head. So we disable the UI if we see indexer and search_peer
        # roles, without the search_head role. The explicit check for the search_head
        # role was added to cover the DMC case, in which the search heads are themselves
        # made search peers of the DMC node, but should still show the UI.
        roles.get('indexer') and roles.get('search_peer') and not roles.get('search_head')
    ]

    if (any((roles.get(role) for role in whitelist)) and
            not any((roles.get(role) for role in blacklist)) and
            not any(special_case_rejections)):
        return True
    return False
