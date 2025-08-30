# pyorcasdk

## Introduction

pyorcasdk is a Python package designed to allow for easy software interaction with ORCA Series linear motors. The package is created using Python bindings on our C++ library, [orcaSDK](https://github.com/IrisDynamics/orcaSDK).

## Prerequisites

- Python 3.8 or greater
- pip
- A Windows or Linux device

## Installation

To install the package, execute this command into your command-line interface:

```
pip install pyorcasdk
```

## Documentation

This package is currently in beta, and doesn't yet have complete Python documentation. Despite this, there are learning resources available.

### Examples

Our [tutorial repo](https://github.com/IrisDynamics/orcaSDK_tutorials) contains examples for a set of common use cases for our motors with this library. 

### ORCA Documentation

Our [downloads page](https://irisdynamics.com/downloads) contains multiple files which are useful references for handling the hardware setup for your ORCA motor. The [ORCA Series Reference Manual](https://irisdynamics.com/hubfs/Website/Downloads/Orca/Approved/RM220115_Orca_Series_Reference_Manual.pdf) goes into great detail on all features available in the motor and how the features can be accessed.

### orcaSDK Documentation

Although it uses C++ syntax, there is [complete documentation for orcaSDK](https://github.com/IrisDynamics/orcaSDK/releases/latest). Because this package links directly to our C++ library, nearly all function names and types are identical across the two packages. The documentation for the C++ library might be useful if you need additional information.