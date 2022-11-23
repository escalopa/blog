---
title: "Running your first Golong code today"
description: "Setting Golang env before we start getting our hands dirty"
date: 2022-11-24T02:19:05+03:00
image: cover.png
hidden: false
categories:
    - Golang
comments: true
draft: true
---

# Welcome GOPHER!

Today we will be setting the env for needed to run golang code on your machine

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

## Setting up GOPATH

1. Add `GOPATH` to the `PATHS` by editing the shell source file

```
export PATH=PATH:/usr/local/go/bin
```

> Note: The shell source file is like `.bashrc`, `.zshrc`, It depends on the current running shell on your machine

Afterwards to update the changes run 
```shell
$ source SHELL_FILE
```

Now everything is set up the following command should work, Note that the output version might differ on your machine
```shell
$ go version
go version go1.19.2 linux/amd64
```

That's all for this article, Wish it was helpful.

If you have any questions or got stuch with some problems leave in the comments below or message me