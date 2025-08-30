[![Actions Status](https://github.com/pulumi/pulumi-null/workflows/master/badge.svg)](https://github.com/pulumi/pulumi-null/actions)
[![NPM version](https://img.shields.io/npm/v/@pulumi/null)](https://www.npmjs.com/package/@pulumi/null)
[![Python version](https://img.shields.io/pypi/v/pulumi_null)](https://pypi.org/project/pulumi_null)
[![NuGet version](https://img.shields.io/nuget/v/Pulumi.Null)](https://www.nuget.org/packages/Pulumi.Null)
[![PkgGoDev](https://pkg.go.dev/badge/github.com/pulumi/pulumi-null/sdk/go)](https://pkg.go.dev/github.com/pulumi/pulumi-null/sdk/go)
[![License](https://img.shields.io/github/license/pulumi/pulumi-null)](https://github.com/pulumi/pulumi-null/blob/master/LICENSE)

# Null Resource Provider

This provider is mainly used for ease of converting terraform programs to Pulumi.
For standard use in Pulumi programs, please use your programming language's implementation of null values.

The Null resource provider for Pulumi lets you use Null resources in your cloud programs.
To use this package, please [install the Pulumi CLI first](https://www.pulumi.com/docs/install/).

## Installing

This package is available in many languages in the standard packaging formats.

### Node.js (Java/TypeScript)

To use from JavaScript or TypeScript in Node.js, install using either `npm`:

    $ npm install @pulumi/null

or `yarn`:

    $ yarn add @pulumi/null

### Python

To use from Python, install using `pip`:

    $ pip install pulumi_null

### Go

To use from Go, use `go get` to grab the latest version of the library:

    $ go get github.com/pulumi/pulumi-null/sdk

### .NET

To use from .NET, install using `dotnet add package`:

    $ dotnet add package Pulumi.Null

<!-- If your provider has configuration, remove this comment and the comment tags below, updating the documentation. -->
<!--

## Configuration

The following Pulumi configuration can be used:

- `null:token` - (Required) The API token to use with Null. When not set, the provider will use the `NULL_TOKEN` environment variable.

-->

<!-- If your provider has reference material available elsewhere, remove this comment and the comment tags below, updating the documentation. -->
<!--

## Reference

For further information, please visit [Null reference documentation](https://example.com/null).

-->
