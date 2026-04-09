"""
TEST STEP 3: Scansione Canali
"""

from core import SensorManager
from models import SMAOStatus

print("=" * 60)
print("TEST STEP 3: SCANSIONE CANALI")
print("=" * 60)

# ===== TEST 1: Creazione e inizializzazione =====
print("\n📋 TEST 1: Inizializzazione")
print("-" * 60)

manager = SensorManager()


# Callback per canali aggiornati
def on_channels_updated():
    print("🔔 CALLBACK: Liste canali aggiornate!")


manager.on_channels_updated(on_channels_updated)

status = manager.initialize()

if status != SMAOStatus.OK:
    print("⚠️  SMAO non disponibile, test interrotto")
    exit(1)

# ===== TEST 2: Scansione =====
print("\n📋 TEST 2: Scansione canali")
print("-" * 60)

active_count = manager.scan_channels()

print(f"\nCanali attivi trovati: {active_count}")

# ===== TEST 3: Visualizzazione canali =====
print("\n📋 TEST 3: Lista completa canali")
print("-" * 60)

all_channels = manager.get_all_channels()

print(f"Totale canali configurati: {len(all_channels)}\n")

for ch in all_channels:
    status_icon = "✓" if ch.is_active else "○"
    print(f"  {status_icon} {ch}")

# ===== TEST 4: Solo canali attivi =====
print("\n📋 TEST 4: Solo canali attivi")
print("-" * 60)

active_channels = manager.get_active_channels()

print(f"Canali attivi: {len(active_channels)}\n")

for ch in active_channels:
    print(f"  ✓ {ch}")
    print(f"     Driver: {ch.driver_name}, CH: {ch.channel_number}")
    print(f"     Range: {ch.min_range} → {ch.max_range} {ch.unit}")
    print(f"     Limiti: {ch.min_limit} → {ch.max_limit}")
    print()

# ===== TEST 5: Ricerca canale specifico =====
print("\n📋 TEST 5: Ricerca canale specifico")
print("-" * 60)

if len(all_channels) > 0:
    # Cerca il primo canale
    ch = manager.get_channel_by_user_number(1)

    if ch:
        print(f"Canale #1 trovato: {ch}")
        print(f"  Attivo: {ch.is_active}")
        print(f"  Label: {ch.label}")
    else:
        print("Canale #1 non trovato")
else:
    print("Nessun canale disponibile")

# ===== TEST 6: Statistiche =====
print("\n📋 TEST 6: Statistiche")
print("-" * 60)

print(f"Totale canali:  {len(all_channels)}")
print(f"Canali attivi:  {len(active_channels)}")
print(f"Canali inattivi: {len(all_channels) - len(active_channels)}")

if len(all_channels) > 0:
    percentuale = (len(active_channels) / len(all_channels)) * 100
    print(f"Percentuale attivi: {percentuale:.1f}%")

# ===== Shutdown =====
print("\n📋 Shutdown")
print("-" * 60)

manager.shutdown()

print("\n" + "=" * 60)
print("✅ TEST COMPLETATO")
print("=" * 60)
