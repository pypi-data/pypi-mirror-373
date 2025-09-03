# openapi-dto-gen

Generate Java DTOs from OpenAPI/Swagger `components.schemas`.

This package provides a simple command-line tool that converts the `components.schemas` section of an OpenAPI/Swagger file into Java data transfer objects (DTOs). It supports basic type mapping, enum generation, flattened `allOf` inheritance, and optional Lombok annotations.

## Installation

Install via pip after downloading the distribution files:

```bash
pip install openapi-dto-gen-0.1.0-py3-none-any.whl
```

## Usage

Run the tool from the command line to generate DTOs:

```bash
openapi-to-dto \
  --in ./openapi.yaml \
  --out ./generated-src \
  --package com.example.dto \
  --lombok
```

* `--in` – Path to your OpenAPI YAML or JSON file.
* `--out` – Output directory for the generated `.java` files.
* `--package` – Java package name for the generated classes.
* `--lombok` – (optional) Add Lombok annotations (`@Data`, `@Builder`, etc.) to the classes.

## License

This project is provided under the MIT License; see the `LICENSE` file for details.