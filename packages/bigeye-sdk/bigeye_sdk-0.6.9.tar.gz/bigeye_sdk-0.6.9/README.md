# Bigeye SDK

Bigeye SDK is a collection of protobuf generated code, functions, and models used to interact programmatically
with the Bigeye API.  Bigeye currently supports a Python SDK.  The main entry point is the DatawatchClient 
abstraction and, in this core package, a basic auth client has been implemented.  The abstract base class 
includes core functionality (methods to interact with the API) and each implementation should enable a 
different authorization methods.

## Install

```shell
pip install bigeye_sdk
```

## Basic Auth

Basic authorization credentials can be stored as Json either on disk or in a secrets/credentials manager.  This
format will be marshalled into an instance of [BasicAuthRequestLibApiConf](bigeye_sdk/authentication/api_authentication.py).

```json
{
    "base_url": "https://app.bigeye.com",
    "user": "",
    "password": ""
}
```
