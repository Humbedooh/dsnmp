## OID and status values configuration


#################################
####### Generic UNIX OIDs #######
#################################

## CPU statistics
unix_cpu_load = ".1.3.6.1.4.1.2021.10.1.3"
unix_cpu_idle = ".1.3.6.1.4.1.2021.11.11.0"
unix_cpu_number_of_cores = ".1.3.6.1.2.1.25.3.2.1.3"
unix_cpu_core_load = ".1.3.6.1.2.1.25.3.3.1.2"
unix_cpu_systimes = ".1.3.6.1.4.1.2021.11"

## Memory statistics
unix_memory_free = ".1.3.6.1.4.1.2021.4.11.0"
unix_memory_buffered = ".1.3.6.1.4.1.2021.4.14.0"
unix_memory_total = ".1.3.6.1.4.1.2021.4.5.0"
unix_memory_used = ".1.3.6.1.4.1.2021.4.6.0"

## Uptime
unix_uptime = ".1.3.6.1.2.1.1.3.0"

## Disk statistics
unix_disk_mountpoint = ".1.3.6.1.4.1.2021.9.1.2"
unix_disk_pct = ".1.3.6.1.4.1.2021.9.1.9"

## Operating system
unix_os = ".1.3.6.1.2.1.1.1.0"



##################################
####### Dell specific OIDs #######
##################################

## Machine information
dell_machine_product_name = "1.3.6.1.4.1.674.10892.1.300.10.1.9.1"
dell_machine_service_tag = "1.3.6.1.4.1.674.10892.1.300.10.1.11.1"
dell_machine_global_status = "1.3.6.1.4.1.674.10892.1.200.10.1.2.1"
dell_machine_cooling = '1.3.6.1.4.1.674.10892.1.200.10.1.44.1'
dell_machine_batteries = '1.3.6.1.4.1.674.10892.1.200.10.1.52.1'
dell_machine_temperatures = '1.3.6.1.4.1.674.10892.1.200.10.1.24.1'
dell_machine_temperature_values = "iso.3.6.1.4.1.674.10892.1.700.20.1.6.1"
dell_machine_temperature_sensornames = "iso.3.6.1.4.1.674.10892.1.700.20.1.8.1"


## Power Supply Unit
dell_psu_status = ".1.3.6.1.4.1.674.10892.1.200.10.1.9"


## CPU Statistics
dell_cpu_names = "1.3.6.1.4.1.674.10892.1.1100.30.1.23.1"
dell_cpu_cores = "1.3.6.1.4.1.674.10892.1.1100.30.1.17.1"


## RAID Information
dell_raid_global_status = ".1.3.6.1.4.1.674.10893.1.20.110.13"
dell_raid_volumes = ".1.3.6.1.4.1.674.10893.1.20.140.1.1.2"
dell_raid_disk_states = ".1.3.6.1.4.1.674.10893.1.20.140.1.1.4"
dell_raid_disk_status = ".1.3.6.1.4.1.674.10893.1.20.130.4.1.23" #Use combined status
dell_raid_disk_name = ".1.3.6.1.4.1.674.10893.1.20.130.4.1.25"

## OS Disks
dell_disk_status = ".1.3.6.1.4.1.674.10893.1.20.130.4.1.4"



## Memory information
dell_memory_status = ".1.3.6.1.4.1.674.10892.1.200.10.1.27.1"
dell_memory_dimm_status = ".1.3.6.1.4.1.674.10892.1.200.10.1.28.1"



## Disk information
dell_disk_location = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.2"
dell_disk_vendor = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.3"
dell_disk_prodno = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.6"
dell_disk_serial = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.7"


dell_log_dates = "iso.3.6.1.4.1.674.10892.1.300.40.1.8.1"
dell_log_entries = "iso.3.6.1.4.1.674.10892.1.300.40.1.5.1"



##################################
####### Dell specific OIDs #######
##################################

## DellStatus
dell_status_standard = {
     1: 'other',
     2: 'unknown',
     3: 'Okay',
     4: 'Non-critical',
     5: 'Critical'
}

## Dell Disk Status
dell_status_disk = {
        0: 'Unknown',
        1: 'Ready (not assigned)',
        2: 'FAILED',
        3: 'Online and assigned',
        4: 'OFFLINE',
        6: 'DEGRADED',
        7: 'Resilvering',
        11: 'REMOVED',
        13: 'Online (Passthrough)',
        15: 'Resynching',
        24: 'Rebuilding',
        25: 'No media',
        26: 'Formatting',
        28: 'Diagnostics running',
        35: 'Initializing',
        38: 'Resynching Paused',
        52: 'Permanently Degraded',
        54: 'Degraded Redundancy'
    }