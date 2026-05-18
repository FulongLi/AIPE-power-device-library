TECHNOLOGIES = [
    "Si",
    "SiC",
    "GaN",
]

DEVICE_CLASSES = [
    "mosfet",
    "jfet",
    "hemt",
    "igbt",
    "diode",
    "module",
]

MANUFACTURERS = [
    "Alpha & Omega Semiconductor",
    "Analog Devices",
    "Diodes Incorporated",
    "EPC",
    "Fuji Electric",
    "GeneSiC",
    "Hitachi Energy",
    "Infineon",
    "IXYS",
    "Littelfuse",
    "Microchip",
    "Mitsubishi Electric",
    "Navitas",
    "Nexperia",
    "NXP",
    "onsemi",
    "Power Integrations",
    "Renesas",
    "ROHM",
    "Semikron Danfoss",
    "STMicroelectronics",
    "Texas Instruments",
    "Toshiba",
    "UnitedSiC",
    "Vishay",
    "WeEn",
    "Wolfspeed",
]

SOURCE_TYPES = [
    "datasheet",
    "application_note",
    "characterization_report",
    "raw_test_data",
    "measurement",
    "simulation",
    "estimate",
]

SOURCE_CATEGORIES = [
    "manufacturer_document",
    "manufacturer_model",
    "third_party_characterization",
    "internal_measurement",
    "simulation",
    "estimate",
]

SOURCE_SUBTYPES = [
    "datasheet_table",
    "datasheet_curve_digitized",
    "application_note",
    "spice_model",
    "plecs_model",
    "double_pulse_test",
    "curve_tracer",
    "thermal_transient",
    "gate_charge_test",
    "capacitance_test",
    "reverse_recovery_test",
    "raw_waveform",
    "post_processed_dataset",
    "manual_estimate",
]

CURVE_TYPES = [
    "iv_output",
    "iv_transfer",
    "capacitance",
    "switching_energy",
    "gate_charge",
    "soa",
    "thermal_impedance",
    "on_resistance_vs_temperature",
    "vce_sat_vs_temperature",
    "reverse_recovery",
]

MODULE_TOPOLOGIES = [
    "half_bridge",
    "full_bridge",
    "six_pack",
    "boost",
    "buck",
    "three_level",
    "custom",
]

KNOWN_UNITS = {
    "V",
    "A",
    "mA",
    "ohm",
    "mohm",
    "W",
    "kW",
    "C",
    "K",
    "J",
    "mJ",
    "uJ",
    "nC",
    "pF",
    "nF",
    "uF",
    "ns",
    "us",
    "ms",
    "s",
    "C/W",
    "K/W",
    "Hz",
    "kHz",
    "MHz",
    "count",
}

TAXONOMY = {
    "technologies": TECHNOLOGIES,
    "device_classes": DEVICE_CLASSES,
    "manufacturers": MANUFACTURERS,
    "source_types": SOURCE_TYPES,
    "source_categories": SOURCE_CATEGORIES,
    "source_subtypes": SOURCE_SUBTYPES,
    "curve_types": CURVE_TYPES,
    "module_topologies": MODULE_TOPOLOGIES,
    "known_units": sorted(KNOWN_UNITS),
}
