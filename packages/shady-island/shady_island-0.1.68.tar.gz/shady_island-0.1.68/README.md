# shady-island

[![Apache 2.0](https://img.shields.io/github/license/libreworks/shady-island)](https://github.com/libreworks/shady-island/blob/main/LICENSE)
[![npm](https://img.shields.io/npm/v/shady-island)](https://www.npmjs.com/package/shady-island)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/libreworks/shady-island/release/main?label=release)](https://github.com/libreworks/shady-island/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/libreworks/shady-island?sort=semver)](https://github.com/libreworks/shady-island/releases)
[![codecov](https://codecov.io/gh/libreworks/shady-island/branch/main/graph/badge.svg?token=OHTRGNTSPO)](https://codecov.io/gh/libreworks/shady-island)

Utilities and constructs for the AWS CDK.

## Features

* Create IPv6 CIDRs and routes for subnets in a VPC with the `CidrContext` construct.
* Set the `AssignIpv6AddressOnCreation` property of subnets in a VPC with the `AssignOnLaunch` construct.
* Properly encrypt a CloudWatch Log group with a KMS key and provision IAM permissions with the `EncryptedLogGroup` construct.
* Represent a deployment tier with the `Tier` class.
* Create a subclass of the `Workload` construct to contain your `Stack`s, and optionally load context values from a JSON file you specify.

## Documentation

* [TypeScript API Reference](https://libreworks.github.io/shady-island/api/)

## The Name

It's a pun. In English, the pronunciation of the acronym *CDK* sounds a bit like the phrase *seedy cay*. A seedy cay might also be called a *shady island*.
