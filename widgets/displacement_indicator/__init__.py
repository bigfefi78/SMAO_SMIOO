"""
Displacement Indicator Widget
"""

try:
    from widgets.displacement_indicator.displacement_indicator import DisplacementIndicator

    __all__ = ["DisplacementIndicator"]
    print("DisplacementIndicator importato correttamente")
except Exception as e:
    with open(r"F:/LAVORO/PRODAR/CLAUDIA/CARRELLI/carrelli elettrici/PYTHON/CARRELLI_SMAO_SMIOO/displacement_indicator_import_error_da_init.log", "w") as f:
        f.write(f"Errore durante l'importazione di DisplacementIndicator:\n{str(e)}")
