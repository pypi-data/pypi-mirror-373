# Strique Proto Schema
API contracts and Data Transfer Objects(DTO) in the form of Protocol Buffers for Strique binaries.

Protobuf provides a language agnostic way to define schema and contracts. The protbufs genertae language specific code during compilation and the language specific ojects are packaged and exported to different package registries.

## Versions
* `*.*.*-rc.*` - This is a snapshot version. Never use this in prod. This is for intermediate releases.
* `*.*.*` - This is for prod version.

## Java - Use maven strique package
Add strique proto package as a dependency in your pom.xml [using this package guide](https://github.com/DigiStrique-Solutions/strique-proto-schema/packages/2108552).

## Typescript/Javascript - Use npm strique package
* Create a Personal access token from developer settings of your github and give it read permissions to the package.
* Add following to `~/.npmrc`.
```
@digistrique-solutions:registry=https://npm.pkg.github.com/
//npm.plg.github.com/:_authToken=<Personal access token from above step>
```
* Use [this guide](https://github.com/DigiStrique-Solutions/strique-proto-schema/pkgs/npm/strique-proto-schema) to add the package to your TS/JS project.

## Python - Use pypi strique package
* Before installing the package, make sure you have Python and pip (Python's package installer) installed on your system.
* Install the Strique proto package: 
Use pip to install the strique-proto-schema package by running the following command:
```
pip install strique-proto-schema
```