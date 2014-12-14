dsnmp
=====

Dell (OpenManage) SNMP monitoring system with HipChat and email integration.

Originally created for the Apache Software Foundation. 
As such, there may still be ASF-centric checks and logic in the code that you may need to change to suit your own needs.


## Checks ##

### The following standard UNIX checks are valid:

 - `load`:        5, 10, 15 min load averages (alerts if 15 min is above what N cores can provide for. Triggers after 45 min of this)
 - `cpuidle`:     Shows how much cpu is idle at the time. Does not trigger alerts
 - `memfree`:     Shows how much memory (including buffers) is free. Alerts if <100mb free.
 - `uptime`:      Shows uptime. Does not trigger an alert
 - `memory`:      Shows the total amount of memory installed. Does not trigger an alert, unless faulty memory is detected (Dell specific)
 - `cores`:       Lists the number of CPU cores found on the system. Does not trigger alerts
 - `spac`e:       Lists the available partitions on the disk if >= 75% space used. Triggers an alert if >=75% space used on a partition.
 
 
 ### The following Dell specific checks are valid:
 
 - `perc`:        Displays the status of the PERC RAID controller and its volumes. Alerts if a volume is degraded or otherwise compromised
 - `array`:       Displays the status of the OS arrays. Alerts if a disk is in a wrong state (degraded, faulted, offline etc)
 - `disks`:       Displays the state of each disk in the machine. Alerts if a disk is not online or passthrough.
 - `psu`:         Displays the status of the Power Supply Unit. Alerts if PSU is in a bad state.
 - `prod`:        Displays the product name and service tag of a machine. Does not trigger alerts
 - `memory`:      Displays the amount of installed memory, and if a dimm is faulted, also triggers an alert.
 - `status`:      Displays the combined status of the entire machine. Alerts if status is not okay. Does not explain why.
 - `cooling`:     Displays the combined status of the cooling devices in the machine. Alerts if devices are not working.
 - `battery`:     Displays the combined battery status of the machine. Alerts if any batteries are not working.
 - `temperature`: Displays the overall temperature status.


 # HipChat commands ##
 To trigger a check via HipChat (assuming the daemon is running), use the following syntax:
 `#snmp $host $check`.
 For example: `#snmp server1 disks`.
 
