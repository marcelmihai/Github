Ansible Role
==========================

splunk_cluster_slave
--------------------

# files
- cluster_slave_app

# Tasks

- Install cluster_slave_app
- Restart Splunk
  Required before configuring stanzas in the above app.
- Configure master_uri
- Restart Splunk
