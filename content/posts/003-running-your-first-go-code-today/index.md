---
title: "Running Your First Go Code Today"
date: 2022-11-24
categories: ["go"]
tags: ["setup"]
slug: "running-your-first-go-code-today"
summary: "Guide to installing Go and running your first program"
---

Today we will be setting the environment for needed to run golang code on your machine

## Installation

1. Download go runtime from the [main site](https://go.dev/dl/)

2. Remove the old go runtime(If you have go already installed)

```shell
$ rm -rf /usr/local/go
```

3. Unzip the download file into `/usr/local/` with the following command
   
```shell
$ tar -C /usr/local -xzf go1.19.3.linux-amd64.tar.gz
```

## Setup GOPATH

1. Add `GOPATH` to the `PATHS` by editing the shell source file

```
export PATH=PATH:/usr/local/go/bin
```

> Note: The shell source file is like `.bashrc`, `.zshrc`, It depends on the current running shell on your machine

Afterward to update the changes run

```shell
$ source SHELL_FILE
```

Now everything is set up the following command should work.

{{< alert >}}
**Note:** that the output version might differ on your machine.
{{< /alert >}}

```shell
$ go version
go version go1.19.2 linux/amd64
```

That's all for this article, Wish it was helpful.

If you have any questions or got stuck with some problems leave in the comments below or message me.