from __future__ import annotations

from typing import Any

from .taxonomy import (
    CURVE_TYPES,
    DEVICE_CLASSES,
    KNOWN_UNITS,
    MANUFACTURERS,
    MODULE_TOPOLOGIES,
    SOURCE_CATEGORIES,
    SOURCE_SUBTYPES,
    SOURCE_TYPES,
    TECHNOLOGIES,
)


REQUIRED_TOP_LEVEL = [
    "id",
    "manufacturer",
    "part_number",
    "technology",
    "device_class",
    "package",
    "ratings",
    "sources",
]


def validate_device_record(record: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in record:
            errors.append(f"Missing required field: {key}")

    source_ids = _validate_sources(record.get("sources"), errors, warnings)

    technology = record.get("technology")
    if technology not in TECHNOLOGIES:
        errors.append(f"Invalid technology '{technology}'. Expected one of {TECHNOLOGIES}.")

    device_class = record.get("device_class")
    if device_class not in DEVICE_CLASSES:
        errors.append(f"Invalid device_class '{device_class}'. Expected one of {DEVICE_CLASSES}.")

    if record.get("manufacturer") and record.get("manufacturer") not in MANUFACTURERS:
        warnings.append(
            f"manufacturer '{record.get('manufacturer')}' is not in the known manufacturer taxonomy."
        )

    _validate_package(record.get("package"), source_ids, errors)
    _validate_quantity_map(record.get("ratings"), "ratings", source_ids, errors, warnings)
    _validate_quantity_map(record.get("electrical"), "electrical", source_ids, errors, warnings)
    _validate_quantity_map(record.get("thermal"), "thermal", source_ids, errors, warnings)
    _validate_gan(record, source_ids, errors, warnings)
    _validate_module(record, source_ids, errors, warnings)
    _validate_curves(record.get("curves"), source_ids, errors, warnings)
    _validate_raw_data_packages(record.get("raw_data_packages"), source_ids, errors, warnings)

    return {"errors": errors, "warnings": warnings}


def _validate_sources(
    sources: Any,
    errors: list[str],
    warnings: list[str],
) -> set[str]:
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list.")
        return set()

    ids: set[str] = set()
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{path} must be an object.")
            continue
        source_id = source.get("id")
        if not source_id:
            errors.append(f"{path}.id is required.")
        elif source_id in ids:
            errors.append(f"Duplicate source id '{source_id}'.")
        else:
            ids.add(source_id)
        source_type = source.get("type")
        if source_type not in SOURCE_TYPES:
            errors.append(f"{path}.type '{source_type}' is not supported.")
        category = source.get("category")
        if not category:
            warnings.append(f"{path}.category is missing.")
        elif category not in SOURCE_CATEGORIES:
            errors.append(f"{path}.category '{category}' is not supported.")
        subtype = source.get("subtype")
        if subtype and subtype not in SOURCE_SUBTYPES:
            errors.append(f"{path}.subtype '{subtype}' is not supported.")
        if not source.get("title"):
            warnings.append(f"{path}.title is missing.")
        if category in {"third_party_characterization", "internal_measurement"}:
            if not source.get("lab"):
                warnings.append(f"{path}.lab is recommended for measurement sources.")
            if not source.get("traceability"):
                warnings.append(f"{path}.traceability is recommended for measurement sources.")
    return ids


def _validate_package(package: Any, source_ids: set[str], errors: list[str]) -> None:
    if not isinstance(package, dict):
        errors.append("package must be an object.")
        return
    if not package.get("name"):
        errors.append("package.name is required.")
    for key in ["isolation_voltage", "parasitic_inductance"]:
        if key in package:
            _validate_quantity(package[key], f"package.{key}", source_ids, errors, [])


def _validate_quantity_map(
    value: Any,
    path: str,
    source_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object.")
        return
    for key, item in value.items():
        _validate_quantity(item, f"{path}.{key}", source_ids, errors, warnings)


def _validate_quantity(
    quantity: Any,
    path: str,
    source_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not isinstance(quantity, dict):
        errors.append(f"{path} must be an object with value, unit, and source_id.")
        return
    if "value" not in quantity:
        errors.append(f"{path}.value is required.")
    elif not isinstance(quantity["value"], (int, float)):
        errors.append(f"{path}.value must be numeric.")
    unit = quantity.get("unit")
    if not unit:
        errors.append(f"{path}.unit is required.")
    elif unit not in KNOWN_UNITS:
        warnings.append(f"{path}.unit '{unit}' is not in the known unit list.")
    source_id = quantity.get("source_id")
    if not source_id:
        errors.append(f"{path}.source_id is required.")
    elif source_id not in source_ids:
        errors.append(f"{path}.source_id '{source_id}' does not match a source.")
    if "condition" not in quantity:
        warnings.append(f"{path}.condition is missing.")


def _validate_gan(
    record: dict[str, Any],
    source_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if record.get("technology") != "GaN":
        return
    gan = record.get("gan")
    if not isinstance(gan, dict):
        errors.append("GaN devices must include a gan object.")
        return
    if gan.get("structure") not in ["e_mode", "p_gan", "cascode", "d_mode", "unknown"]:
        errors.append("gan.structure must be one of e_mode, p_gan, cascode, d_mode, unknown.")
    for key in ["dynamic_rds_on_factor", "vgs_abs_max", "reverse_conduction_voltage"]:
        if key in gan:
            _validate_quantity(gan[key], f"gan.{key}", source_ids, errors, warnings)


def _validate_module(
    record: dict[str, Any],
    source_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if record.get("device_class") != "module":
        return
    module = record.get("module")
    if not isinstance(module, dict):
        errors.append("module devices must include a module object.")
        return
    if module.get("topology") not in MODULE_TOPOLOGIES:
        errors.append(f"module.topology must be one of {MODULE_TOPOLOGIES}.")
    if "die_count" in module:
        _validate_quantity(module["die_count"], "module.die_count", source_ids, errors, warnings)
    if "thermal_paths" in module and not isinstance(module["thermal_paths"], list):
        errors.append("module.thermal_paths must be a list.")


def _validate_curves(
    curves: Any,
    source_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if curves is None:
        return
    if not isinstance(curves, list):
        errors.append("curves must be a list.")
        return
    ids: set[str] = set()
    for index, curve in enumerate(curves):
        path = f"curves[{index}]"
        if not isinstance(curve, dict):
            errors.append(f"{path} must be an object.")
            continue
        curve_id = curve.get("id")
        if not curve_id:
            errors.append(f"{path}.id is required.")
        elif curve_id in ids:
            errors.append(f"Duplicate curve id '{curve_id}'.")
        else:
            ids.add(curve_id)
        if curve.get("type") not in CURVE_TYPES:
            errors.append(f"{path}.type '{curve.get('type')}' is not supported.")
        source_id = curve.get("source_id")
        if not source_id:
            errors.append(f"{path}.source_id is required.")
        elif source_id not in source_ids:
            errors.append(f"{path}.source_id '{source_id}' does not match a source.")
        _validate_axis(curve.get("x"), f"{path}.x", errors, warnings)
        _validate_axis(curve.get("y"), f"{path}.y", errors, warnings)
        points = curve.get("points")
        if not isinstance(points, list) or len(points) < 2:
            errors.append(f"{path}.points must contain at least two [x, y] pairs.")
        else:
            last_x = None
            for point_index, point in enumerate(points):
                if (
                    not isinstance(point, list)
                    or len(point) != 2
                    or not all(isinstance(v, (int, float)) for v in point)
                ):
                    errors.append(f"{path}.points[{point_index}] must be a numeric [x, y] pair.")
                    continue
                if last_x is not None and point[0] < last_x:
                    warnings.append(f"{path}.points are not monotonic in x.")
                    break
                last_x = point[0]


def _validate_axis(axis: Any, path: str, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(axis, dict):
        errors.append(f"{path} must be an object with label and unit.")
        return
    if not axis.get("label"):
        errors.append(f"{path}.label is required.")
    unit = axis.get("unit")
    if not unit:
        errors.append(f"{path}.unit is required.")
    elif unit not in KNOWN_UNITS:
        warnings.append(f"{path}.unit '{unit}' is not in the known unit list.")


def _validate_raw_data_packages(
    packages: Any,
    source_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if packages is None:
        return
    if not isinstance(packages, list):
        errors.append("raw_data_packages must be a list.")
        return
    for index, package in enumerate(packages):
        path = f"raw_data_packages[{index}]"
        if not isinstance(package, dict):
            errors.append(f"{path} must be an object.")
            continue
        if not package.get("id"):
            errors.append(f"{path}.id is required.")
        source_id = package.get("source_id")
        if not source_id:
            errors.append(f"{path}.source_id is required.")
        elif source_id not in source_ids:
            errors.append(f"{path}.source_id '{source_id}' does not match a source.")
        if not package.get("test_type"):
            errors.append(f"{path}.test_type is required.")
        if not package.get("artifacts"):
            warnings.append(f"{path}.artifacts is empty.")
