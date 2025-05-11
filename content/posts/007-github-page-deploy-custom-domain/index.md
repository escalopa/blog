---
title: "GitHub Page Deploy (Custom Domain)"
date: 2025-05-10
slug: "github-page-deploy-custom-domain"
summary: "Setting up domain configurations for GitHub Pages"
categories: ["deploy"]
tags: ["domain", "github"]
---

{{< lead >}}
Quick notes on how to set up domain configurations for GitHub Pages.
{{< /lead >}}

## Setup

### DNS provider

Set up the DNS records for your domain. Below are the records you need to add:

| Record Type              | Name | Value                   |
|:-------------------------|:-----|:------------------------|
| A                        | @    | 185.199.108.153         |
| A                        | @    | 185.199.109.153         |
| A                        | @    | 185.199.110.153         |
| A                        | @    | 185.199.111.153         |
| (optional for www) CNAME | www  | your-username.github.io |

### GitHub

1. Go to your repository settings.
2. Scroll down to the "GitHub Pages" section.
3. Under "Custom domain", enter your domain name (e.g., `escalopa.com`).
4. Click "Save".
5. If you want to use `www` (e.g., `www.escalopa.com`), check the box for "Enforce HTTPS".
6. Wait for a few minutes for the changes to propagate.

## Validate

{{< alert >}}
DNS changes **can take some time** to propagate. If you don't see the changes immediately, wait a few minutes and try again.
{{< /alert >}}

To validate your DNS settings, you can use the `dig` command.

This command queries DNS servers for information about a domain name.

Check your DNS settings with:

```bash
dig YOUR_DOMAIN_NAME  +noall +answer -t A
```

| Option        | Description                                                          |
|:--------------|:---------------------------------------------------------------------|
| `+noall`      | Suppresses or clear all display flags.                               |
| `+answer`     | Displays only the answer section of the response.                    |
| `-t A`        | Specifies the type of DNS record to query (in this case, A records). |

Example:

```bash
dig escalopa.com +noall +answer -t A
```

```text
escalopa.com.           3428    IN      A       185.199.108.153
escalopa.com.           3428    IN      A       185.199.111.153
escalopa.com.           3428    IN      A       185.199.109.153
escalopa.com.           3428    IN      A       185.199.110.153
```

If you have set up `www` CNAME, you can check it with:

```bash
dig www.YOUR_DOMAIN_NAME +noall +answer -t CNAME
```

Example:

```bash
dig www.escalopa.com +noall +answer -t CNAME
```

```text
www.escalopa.com.       3600    IN      CNAME   escalopa.github.io.
```
