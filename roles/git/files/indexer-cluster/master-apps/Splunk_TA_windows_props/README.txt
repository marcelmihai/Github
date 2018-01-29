Splunk Add-on for Windows
----------------------------------------
Author: Splunk
Source type(s): MonitorWare, NTSyslog, Snare, WinEventLog, DhcpSrvLog, WMI, WindowsUpdateLog, WinRegistry
Has index-time operations: true, this add-on must be placed on indexers
Input requirements: This add-on supports multiple sources; see the "Use this add-on" section for details.
Supported product(s): 
* Microsoft DHCP server
* Windows event logs (provided by Splunk, MonitorWare, NTSyslog, or Snare)
* Windows Update log
* Windows registry (via the Splunk's change monitoring system)
* Microsoft Internet Authentication Service (IAS)
 
New in this release:
--------------------------
- Bug fixes.
- Improvements for internationalization.
- Several Security Event Log field extractions that were in the add-ons included with the Splunk App for Windows Infrastructure have been moved to the Splunk Add-on for Windows. (MSAPP-2748)
- The Splunk Add-on for Windows no longer improperly appears in dashboards in the Splunk App for Enterprise Security. (MSAPP-1835)
- The WMI:UserAccountsSID source has been deprecated. The Splunk Add-on for Windows now uses the WMI:UserAccounts source. (MSAPP-2802)

Use this add-on:
----------------------------------------
Configuration: Manual
Ports for automatic configuration: None
Scripted input setup: Not applicable
 
 
The Splunk Add-on for Windows supports multiple products. The methods to incorporate each log type varies. Below is a breakdown of the various log types and how to enable them.
    
    _____________________________________
    Microsoft DHCP Server:
    The Microsoft DNS server stores Microsoft DHCP server logs in a text file. These files can be imported by monitoring the file directly and manually assigning a source type of DhcpSrvLog. By default, the logs are stored in %windir%\System32\Dhcp. See "Analyze DHCP Server log files" (http://technet.microsoft.com/en-us/library/dd183591(WS.10).aspx).
    
    _____________________________________
    Windows Event Logs:
    Windows event logs can be collected with a Splunk forwarder, remotely via WMI, or by accepting them via a third party syslog daemon (such as Snare or Monitorware). If using syslog, add a data input that corresponds to the product that forwards the logs.
 
Here is an example input (in transforms.conf) that processes Windows Event Log data from Snare:
    
         [source::udp:514]
         SHOULD_LINEMERGE=false
         TRANSFORMS-force_sourcetype_for_snare_syslog = force_sourcetype_for_snare
         TRANSFORMS-force_host_for_snare_syslog = force_host_for_snare
         TRANSFORMS-force_source_for_snare_syslog = force_source_for_snare
    
    To obtain Windows event logs from deployed Splunk forwarders, see deployment-apps/README
    To obtain Windows event logs via WMI, configure WMI through the Splunk Enterprise documentation: http://docs.splunk.com/Documentation/Splunk/latest/Data/MonitorWMIdata
   
    ** To collect Windows event logs via NTSyslog, do the following:
    1.  Disable the replication blacklist for ntsyslog_mappings.csv in $SPLUNK_HOME/etc/apps/Splunk_TA_windows/local/distsearch.conf:
    [replicationBlacklist]
    nontsyslogmappings = 
    
    2.  Enable the following setting in $SPLUNK_HOME/etc/apps/Splunk-TA-windows/local/props.conf:
    [source::NTSyslog:Security]
    LOOKUP-2action_EventCode_for_ntsyslog = ntsyslog_mappings NTSyslogID OUTPUTNEW action,EventCode,EventCode as signature_id
    
    _____________________________________
    Windows Update Logs:
    The Splunk Add-on for Windows automatically discovers Windows update logs within Windows event logs. Read "Windows event logs."
   
    _____________________________________
    Microsoft Internet Authentication Service (IAS):
    The Splunk Add-on for Windows automatically discovers Microsoft Internet Authentication Service logs within Windows event logs. Read "Windows Event Logs."
    
    _____________________________________
    Windows Registry:
    See http://docs.splunk.com/Documentation/Splunk/latest/Data/MonitorWindowsregistrydata for information on how to monitor the Registry.
   

 Copyright (C) 2005-2014 Splunk Inc. All Rights Reserved.
