---
title: "Linux Systemd Explained"
date: 2022-10-20
categories: ["linux"]
tags: ["ssh", "rhel", "selinux"]
slug: "linux-systemd-explained"
summary: "Managing Linux services and boot with systemd"
---

# Controlling Services and the Boot Process


## What is systemd ?

systemd uses units to manage different types of objects. Some common unit types are listed
below:

| Type    | Description                                                                                                                                   |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Service | Represents system services. Used to start frequently accessed daemons, such as a web server.                                                  |
| Socket  | Represents IPC sockets monitored by systemd. Starts the daemon when a client connects. Useful for on-demand or delayed service start at boot. |
| Path    | Used to delay the activation of a service until a specific path condition is met.                                                             |

A specific file system change occurs. This is commonly used for services which use spool
directories such as a printing system.
The systemctl command is used to manage units. For example, display available unit types with
the `systemctl -t help command`

{{< highlight zsh >}}
systemctl -t help
{{< /highlight >}}

To list current running active services run 
{{< highlight zsh >}}
systemctl list-units --type=service

UNIT                               LOAD   ACTIVE SUB     DESCRIPTION                                                                  
accounts-daemon.service            loaded active running Accounts Service
alsa-state.service                 loaded active running Manage Sound Card State (restore and store)
atd.service                        loaded active running Deferred execution scheduler
auditd.service                     loaded active running Security Auditing Service
avahi-daemon.service               loaded active running Avahi mDNS/DNS-SD Stack
chronyd.service                    loaded active running NTP client/server
...Output Omitted...

{{< /highlight >}}

To specify a specific type for `LOAD`, `ACTIVE`, `SUB` use flag `--statue=` and specify the type needed., You can also add `--all` to show all services despite their state as the command by default shows **ONLY** active

Illustration for the output above

| Column      | Description                                                                                                                                                            |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| UNIT        | The service unit name.                                                                                                                                                 |
| LOAD        | Whether systemd properly parsed the unit's configuration and loaded the unit into memory.                                                                              |
| ACTIVE      | The high-level activation state of the unit. This indicates whether the unit has started successfully or not.                                                          |
| SUB         | The low-level activation state of the unit. Provides more detailed information about the unit, varying based on unit type, state, and how the unit is executed.        |
| DESCRIPTION | The short description of the unit.                                                                                                                                     |


Note that the running command `systemctl` without arguments show all active running units


{{< highlight zsh >}}
systemctl list-unit-files --type=service
{{< /highlight >}}

The command above list files shows enabled & disabled units, valid entries for the STATE
field are enabled, disabled, static, and masked. 

To show service status run `systemctl status UNIT.TYPE`

{{< highlight zsh >}}
systemctl status UNIT.service
{{< /highlight >}}

Check is service is enables, output values are`enabled`, `disabled`

{{< highlight zsh >}}
systemctl is-enabled sshd.service
{{< /highlight >}}

Check is service is active, output values are`active`, `inactive`

{{< highlight zsh >}}
systemctl is-active sshd.service
{{< /highlight >}}

Check is service is failed, output values are`active`, `failed`, `inactive`

{{< highlight zsh >}}
systemctl is-failed sshd.service
{{< /highlight >}}

## Manipulating units state

| Task                                                                        | UNIT                             |
|-----------------------------------------------------------------------------|----------------------------------|
| View detailed information about a unit state.                               | systemctl status UNIT            |
| Stop a service on a running system.                                         | systemctl stop UNIT              |
| Start a service on a running system.                                        | systemctl start UNIT             |
| Restart a service on a running system.                                      | systemctl restart UNIT           |
| Reload the configuration file of a running service.                         | systemctl reload UNIT            |
| Completely disable a service from being started, both manually and at boot. | systemctl mask UNIT              |
| Make a masked service available.                                            | systemctl unmask UNIT            |
| Configure a service to start at boot time.                                  | systemctl enable UNIT            |
| Disable a service from starting at boot time.                               | systemctl disable UNIT           |
| List units required and wanted by the specified unit.                       | systemctl list-dependencies UNIT |

## Rebooting and Shutting Down

To power off or reboot a running system from the command line, you can use the systemctl
command.

`systemctl poweroff` stops all running services, unmounts all file systems (or remounts them
read-only when they cannot be unmounted), and then powers down the system.

`systemctl reboot` stops all running services, unmounts all file systems, and then reboots the
system.

You can also use the shorter version of these commands, `poweroff` and `reboot`, which are
symbolic links to their systemctl equivalents.

## System boot targets


| Target            | Purpose                                                                          |
|-------------------|----------------------------------------------------------------------------------|
| graphical.target  | System supports multiple users, graphical- and text-based logins.                |
| multi-user.target | System supports multiple users, text-based logins only.                          |
| rescue.target     | sulogin prompt, basic system initialization completed.                           |
| emergency.target  | sulogin prompt, initramfs pivot complete, and system root mounted on / read only |

To get the default running target use
{{< highlight zsh >}}
systemctl get-default
{{< /highlight >}}

To change the default boot target use
{{< highlight zsh >}}
systemctl set-default TARGET_NAME
{{< /highlight >}}

Note that `TARGET_NAME` can only be 1 from the 4 types specified above.
