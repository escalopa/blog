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

**• Service** units have a .service extension and represent system services. This type of unit is
used to start frequently accessed daemons, such as a web server.

**• Socket** units have a .socket extension and represent inter-process communication (IPC)
sockets that systemd should monitor. If a client connects to the socket, systemd will start a
daemon and pass the connection to it. Socket units are used to delay the start of a service at
boot time and to start less frequently used services on demand.

**• Path** units have a .path extension and are used to delay the activation of a service until

a specific file system change occurs. This is commonly used for services which use spool
directories such as a printing system.
The systemctl command is used to manage units. For example, display available unit types with
the `systemctl -t help command`

```shell
$ systemctl -t help
```

To list current running active services run 
```shell
$ systemctl list-units --type=service

UNIT                               LOAD   ACTIVE SUB     DESCRIPTION                                                                  
accounts-daemon.service            loaded active running Accounts Service
alsa-state.service                 loaded active running Manage Sound Card State (restore and store)
atd.service                        loaded active running Deferred execution scheduler
auditd.service                     loaded active running Security Auditing Service
avahi-daemon.service               loaded active running Avahi mDNS/DNS-SD Stack
chronyd.service                    loaded active running NTP client/server
...Output Omitted...

```

To specify a specific type for `LOAD`, `ACTIVE`, `SUB` use flag `--statue=` and specify the type needed., You can also add `--all` to show all services despite their state as the command by default shows **ONLY** active

Illustration for the output above
| COLUMN | DESCRIPTION |
|---|---|
| UNIT | The service unit name. |
|LOAD |  Whether systemd properly parsed the unit's configuration and loaded the unit into memory.|
| ACTIVE | The high-level activation state of the unit. This information indicates whether the unit has started successfully or not.|
| SUB | The low-level activation state of the unit. This information indicates more detailed information about the unit. The information varies based on unit type, state, and how the unit is executed. |
|DESCRIPTION | The short description of the unit. |


Note that the running command `systemctl` without arguments show all active running units


```shell
$ systemctl list-unit-files --type=service

```
The command above list files shows enabled & disabled units, valid entries for the STATE
field are enabled, disabled, static, and masked. 

To show service status run `systemctl status UNIT.TYPE`
```shell
systemctl status UNIT.service
```

Check is service is enables, output values are`enabled`, `disabled`
```shell
$ systemctl is-enabled sshd.service
```

Check is service is active, output values are`active`, `inactive`
```shell
$ systemctl is-active sshd.service
```

Check is service is failed, output values are`active`, `failed`, `inactive`
```shell
$ systemctl is-failed sshd.service
```

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
```shell
$ systemctl get-default
```

To change the default boot target use
```shell 
$ systemctl set-default TARGET_NAME
```
Note that `TARGET_NAME` can only be 1 from the 4 types specified above.
