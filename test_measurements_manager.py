"""
Test manuale MeasurementsManager
"""

from core import MeasurementsManager
from models import Measurement, MeasurementType, MeasurementStatus

# Crea manager
manager = MeasurementsManager("test_measurements.json")

# Crea misura di test
test_measurement = Measurement(
    name="Test Misura",
    type=MeasurementType.CUSTOM,
    channels=["T-01", "T-02"],
    formula="{T-01} - {T-02}",
    status=MeasurementStatus.ERROR,
)

print("=" * 60)
print("TEST SALVATAGGIO")
print("=" * 60)

# Salva
result = manager.save_measurements([test_measurement])
print(f"Risultato salvataggio: {result}")

print("\n" + "=" * 60)
print("TEST CARICAMENTO")
print("=" * 60)

# Carica
loaded = manager.load_measurements()
print(f"Misure caricate: {len(loaded)}")

if loaded:
    m = loaded[0]
    print(f"  Nome: {m.name}")
    print(f"  Canali: {m.channels}")
    print(f"  Formula: {m.formula}")
    print(f"  ID: {m.id}")

print("\n✓ Test completato!")
