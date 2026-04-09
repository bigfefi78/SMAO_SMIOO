"""
TEST STEP 2: Inizializzazione SensorManager
"""

from core import SensorManager
from models import SMAOStatus

print("=" * 60)
print("TEST STEP 2: SENSOR MANAGER BASE")
print("=" * 60)

# ===== TEST 1: Creazione istanza =====
print("\n📋 TEST 1: Creazione SensorManager")
print("-" * 60)

manager = SensorManager()
print(f"Stato iniziale: {manager.status.name}")
print(f"È connesso? {manager.is_connected()}")

# ===== TEST 2: Callback status changed =====
print("\n📋 TEST 2: Registrazione callback")
print("-" * 60)


def on_status_changed(new_status: SMAOStatus):
    """Questa funzione viene chiamata quando lo stato cambia"""
    print(f"🔔 CALLBACK: Stato cambiato → {new_status.name}")


manager.on_status_changed(on_status_changed)
print("✓ Callback registrata")

# ===== TEST 3: Inizializzazione =====
print("\n📋 TEST 3: Inizializzazione SMAO")
print("-" * 60)

status = manager.initialize()

print(f"\nRisultato inizializzazione: {status.name}")
print(f"È connesso? {manager.is_connected()}")

# ===== TEST 4: Informazioni driver (solo se connesso) =====
if manager.is_connected():
    print("\n📋 TEST 4: Lettura driver")
    print("-" * 60)

    manager.get_drivers_info()
else:
    print("\n⚠️  TEST 4: SALTATO (SMAO non connesso)")

# ===== TEST 5: Shutdown =====
print("\n📋 TEST 5: Shutdown")
print("-" * 60)

manager.shutdown()
print(f"Stato finale: {manager.status.name}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETATO")
print("=" * 60)
