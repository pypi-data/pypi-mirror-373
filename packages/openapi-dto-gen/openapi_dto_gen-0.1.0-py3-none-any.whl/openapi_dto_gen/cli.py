"""Command-line interface for the OpenAPI to Java DTO generator.

This module contains a `main` function that can be invoked as a console
script to convert OpenAPI/Swagger specification files into Java data
transfer objects (DTOs). The implementation is adapted from a standalone
script, reorganized into a package-friendly module.
"""

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Set, List

import yaml  # type: ignore

# Java reserved words; if a generated class or field collides with one of
# these identifiers, an underscore is appended to avoid compilation errors.
RESERVED = {
    "abstract","assert","boolean","break","byte","case","catch","char","class","const",
    "continue","default","do","double","else","enum","extends","final","finally","float",
    "for","goto","if","implements","import","instanceof","int","interface","long","native",
    "new","package","private","protected","public","return","short","static","strictfp","super",
    "switch","synchronized","this","throw","throws","transient","try","void","volatile","while",
    "record","var","yield","sealed","permits","non-sealed"
}


def to_pascal_case(name: str) -> str:
    """Convert an arbitrary string into PascalCase and ensure it is a valid Java identifier."""
    name = re.sub(r'[^0-9A-Za-z]+', ' ', name)
    parts = [p for p in name.strip().split(' ') if p]
    s = ''.join(p[:1].upper() + p[1:] for p in parts) or "ClassName"
    if s[0].isdigit():
        s = "_" + s
    if s in RESERVED:
        s = s + "_"
    return s


def to_camel_case(name: str) -> str:
    """Convert an arbitrary string into camelCase for Java field names."""
    if not name:
        return "field"
    name = re.sub(r'[^0-9A-Za-z]+', ' ', name)
    parts = [p for p in name.strip().split(' ') if p]
    if not parts:
        return "field"
    s = parts[0].lower() + ''.join(p[:1].upper() + p[1:] for p in parts[1:])
    if s[0].isdigit():
        s = "_" + s
    if s in RESERVED:
        s = s + "_"
    return s


def sanitize_identifier(name: str) -> str:
    """Sanitize a string so it can be used as a Java identifier (e.g. enum constants)."""
    s = re.sub(r'[^0-9A-Za-z_]', '_', name or "field")
    if s[0].isdigit():
        s = "_" + s
    if s in RESERVED:
        s = s + "_"
    return s


def last_ref_name(ref: str) -> str:
    """Return the last segment of a JSON pointer (e.g. '#/components/schemas/User' → 'User')."""
    return ref.split('/')[-1]


def is_enum_schema(schema: Dict[str, Any]) -> bool:
    """Determine whether a schema defines an enum at the top level."""
    return bool(schema) and ("enum" in schema) and isinstance(schema.get("enum"), list)


def merge_allOf(schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten an `allOf` schema into a single object schema by merging properties and required fields."""
    allof_list = schema.get("allOf", [])
    combined: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    for part in allof_list:
        if "$ref" in part:
            ref_name = last_ref_name(part["$ref"])
            base = components.get(ref_name, {})
            base_expanded = expand_allOf(base, components)
            combined = merge_object_schemas(combined, base_expanded)
        else:
            part_expanded = expand_allOf(part, components)
            combined = merge_object_schemas(combined, part_expanded)
    # After merge, also merge any sibling properties alongside allOf
    sibling = {k: v for k, v in schema.items() if k != "allOf"}
    combined = merge_object_schemas(combined, sibling)
    return combined


def merge_object_schemas(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two object-like schemas, combining their properties and required fields."""
    out = dict(a)
    if b.get("type") == "object" or "properties" in b or "additionalProperties" in b:
        out.setdefault("type", "object")
        out.setdefault("properties", {})
        # merge properties
        out["properties"] = {**out["properties"], **b.get("properties", {})}
        # merge required (union)
        req_a = set(out.get("required", []) or [])
        req_b = set(b.get("required", []) or [])
        out["required"] = sorted(req_a | req_b)
        # merge additionalProperties
        if "additionalProperties" in b:
            out["additionalProperties"] = b["additionalProperties"]
    else:
        # if b is not object-like, overlay fields
        out = {**out, **b}
    return out


def expand_allOf(schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively expand any allOf composition in the provided schema."""
    if "allOf" in schema:
        return merge_allOf(schema, components)
    return schema


def map_primitive(schema: Dict[str, Any]) -> Tuple[str, Set[str], List[str]]:
    """Map a primitive OpenAPI schema to a Java type, its imports, and doc comments."""
    t = schema.get("type")
    fmt = schema.get("format")
    comments: List[str] = []

    # Enums at property-level → use String, document allowed values
    if is_enum_schema(schema):
        comments.append(f"Allowed values: {', '.join(map(str, schema['enum']))}")
        return ("String", set(), comments)

    if t == "string":
        if fmt == "date":
            return ("LocalDate", {"java.time.LocalDate"}, comments)
        if fmt == "date-time":
            return ("OffsetDateTime", {"java.time.OffsetDateTime"}, comments)
        if fmt in ("byte", "binary"):
            return ("byte[]", set(), comments)
        return ("String", set(), comments)

    if t == "integer":
        if fmt == "int64":
            return ("Long", set(), comments)
        # default to 32-bit
        return ("Integer", set(), comments)

    if t == "number":
        if fmt == "float":
            return ("Float", set(), comments)
        if fmt == "double":
            return ("Double", set(), comments)
        return ("BigDecimal", {"java.math.BigDecimal"}, comments)

    if t == "boolean":
        return ("Boolean", set(), comments)

    if t == "array":
        items = schema.get("items", {}) or {}
        inner, imps, comm = to_java_type(items)
        return (f"List<{inner}>", imps | {"java.util.List"}, comments + comm)

    if t == "object":
        addl = schema.get("additionalProperties", None)
        if addl is True or addl is None:
            # free-form
            return ("Map<String, Object>", {"java.util.Map"}, comments)
        if isinstance(addl, dict):
            inner, imps, comm = to_java_type(addl)
            return (f"Map<String, {inner}>", imps | {"java.util.Map"}, comments + comm)
        # explicit properties (will be handled by caller)
        return ("Map<String, Object>", {"java.util.Map"}, comments)

    # oneOf/anyOf → fallback to Object
    for k in ("oneOf", "anyOf"):
        if k in schema:
            options = []
            for opt in schema[k]:
                if "$ref" in opt:
                    options.append(last_ref_name(opt["$ref"]))
                else:
                    if "type" in opt:
                        options.append(opt["type"])
            if options:
                comments.append(f"{k} possible types: {', '.join(options)}")
            return ("Object", set(), comments)

    # $ref handled outside
    return ("Object", set(), comments)


def to_java_type(schema: Dict[str, Any]) -> Tuple[str, Set[str], List[str]]:
    """Determine the Java type for an OpenAPI schema, recursively resolving $ref."""
    if "$ref" in schema:
        return (to_pascal_case(last_ref_name(schema["$ref"])), set(), [])
    return map_primitive(schema)


def collect_top_level_enums(components: Dict[str, Any]) -> Dict[str, List[str]]:
    """Collect all top-level enum schemas under components.schemas."""
    enums: Dict[str, List[str]] = {}
    for name, sch in (components or {}).items():
        if is_enum_schema(sch):
            enums[name] = sch["enum"]
    return enums


def class_javadoc(description: str | None) -> str:
    """Create a Javadoc block for a class from its description."""
    if not description:
        return ""
    lines = description.strip().splitlines()
    body = "\n".join(f" * {ln}" for ln in lines)
    return f"/**\n{body}\n */\n"


def field_javadoc(description: str | None, extra_comments: List[str]) -> str:
    """Create a Javadoc block for a field from its description and extra notes."""
    notes: List[str] = []
    if description:
        notes.extend(description.strip().splitlines())
    notes.extend(extra_comments or [])
    if not notes:
        return ""
    body = "\n".join(f"     * {ln}" for ln in notes)
    return f"    /**\n{body}\n     */\n"


def generate_enum_java(name: str, values: List[Any], package: str) -> str:
    """Generate source code for a Java enum given its values."""
    cls_name = to_pascal_case(name)
    consts = []
    for v in values:
        if isinstance(v, str):
            c = sanitize_identifier(v.upper())
        else:
            c = "V_" + sanitize_identifier(str(v).upper())
        consts.append(c)
    constants = ",\n    ".join(consts)
    return f"""package {package};

public enum {cls_name} {{
    {constants};
}}
"""


def generate_class_java(
    name: str,
    schema: Dict[str, Any],
    package: str,
    use_lombok: bool,
) -> Tuple[str, Set[str]]:
    """Generate source code for a Java class based on the provided schema."""
    cls_name = to_pascal_case(name)
    imports: Set[str] = set()
    description = schema.get("description")
    props = (schema.get("properties") or {})

    # Determine type: if not object-like and no properties and no additionalProperties
    if schema.get("type") not in (None, "object") and not props and not schema.get("additionalProperties"):
        # nothing to emit for non-object top-levels
        return ("", set())

    # Collect fields
    fields_src: List[str] = []
    for raw_name, prop in props.items():
        java_name = to_camel_case(raw_name)
        jtype, imps, comments = to_java_type(prop or {})
        imports |= imps
        fdesc = prop.get("description")
        # nullable? prefer wrappers already; add note
        if prop.get("nullable") or prop.get("x-nullable"):
            comments.append("nullable")
        # Build field
        ann_json = f'    @JsonProperty("{raw_name}")\n'
        jdoc = field_javadoc(fdesc, comments)
        fields_src.append(
            f"{jdoc}{ann_json}    private {jtype} {java_name};"
        )

    # additionalProperties only object → map DTO
    addl = schema.get("additionalProperties")
    addl_block = ""
    if addl is True:
        imports.add("java.util.Map")
        addl_block = '    @JsonIgnore\n    private Map<String, Object> additionalProperties;\n'
    elif isinstance(addl, dict):
        jt, imps, _ = to_java_type(addl)
        imports |= imps | {"java.util.Map"}
        addl_block = f'    @JsonIgnore\n    private Map<String, {jt}> additionalProperties;\n'

    # imports
    base_imports = {"com.fasterxml.jackson.annotation.JsonInclude",
                    "com.fasterxml.jackson.annotation.JsonProperty",
                    "com.fasterxml.jackson.annotation.JsonIgnore"}
    imports |= base_imports

    lombok_imports: Set[str] = set()
    lombok_annotations = ""
    if use_lombok:
        lombok_imports = {
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "lombok.AllArgsConstructor",
            "lombok.Builder"
        }
        lombok_annotations = "@Data\n@NoArgsConstructor\n@AllArgsConstructor\n@Builder\n"

    # Compose imports block
    imports_block = ""
    if imports or lombok_imports:
        all_imps = sorted(list(imports | lombok_imports))
        imports_block = "\n".join(f"import {imp};" for imp in all_imps) + "\n\n"

    # Compose class
    jdoc = class_javadoc(description)
    fields_str = "\n\n".join(fields_src + ([addl_block] if addl_block else []))

    src = f"""package {package};

{imports_block}{jdoc}@JsonInclude(JsonInclude.Include.NON_NULL)
{lombok_annotations}public class {cls_name} {{

{fields_str}
}}
"""
    return (src, imports)


def build_schema_for_class(raw_schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Expand any allOf composition for a top-level schema before generating code."""
    s = expand_allOf(raw_schema, components)
    # If $ref at top-level (rare), replace with referenced schema
    if "$ref" in s:
        ref_name = last_ref_name(s["$ref"])
        s = expand_allOf(components.get(ref_name, {}), components)
    return s


def main() -> None:
    """Entry point for the command-line interface."""
    ap = argparse.ArgumentParser(description="Generate Java DTOs from OpenAPI (Swagger) YAML/JSON.")
    ap.add_argument("--in", dest="infile", required=True, help="Path to OpenAPI YAML/JSON")
    ap.add_argument("--out", dest="outdir", required=True, help="Output directory for .java files")
    ap.add_argument("--package", dest="package", required=True, help="Java package, e.g. com.example.dto")
    ap.add_argument("--lombok", dest="lombok", action="store_true", help="Use Lombok annotations")
    args = ap.parse_args()

    # Load OpenAPI spec
    with open(args.infile, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    # Extract components.schemas
    components = ((spec or {}).get("components") or {}).get("schemas") or {}
    if not components:
        print("No components.schemas found. Nothing to do.")
        return

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Emit top-level enums
    enums = collect_top_level_enums(components)
    for name, values in enums.items():
        src_enum = generate_enum_java(name, values, args.package)
        (outdir / f"{to_pascal_case(name)}.java").write_text(src_enum, encoding="utf-8")

    # Emit classes
    for name, schema in components.items():
        if is_enum_schema(schema):
            continue  # enum already emitted
        cls_schema = build_schema_for_class(schema, components)
        src_class, _ = generate_class_java(name, cls_schema, args.package, args.lombok)
        if src_class.strip():
            (outdir / f"{to_pascal_case(name)}.java").write_text(src_class, encoding="utf-8")

    print(f"Done. Wrote files to: {outdir}")


if __name__ == "__main__":
    main()