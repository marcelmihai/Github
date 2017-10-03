Ansible Role
=====================

cluster_master
---------------------

Configure a Splunk server to be a cluster master.

# Files

- cluster_master_app

# Dependencies

- splunk_forwarder_inputs_app

  Installed into master-apps/

# Tasks:

- Install cluster_master_app

- Restart splunk

- Set pass4SymmKey

- Set indexer discovery pass4SymmKey

- Restart Splunk
