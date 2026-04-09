"""
TEST STEP 1: Verifica modelli base
"""

from models import SMAOStatus, ChannelStatus, ChannelInfo

print("=" * 60)
print("TEST STEP 1: MODELLI BASE")
print("=" * 60)

# ===== TEST 1: Enumerazioni =====
print("\n📋 TEST 1: Enumerazioni")
print("-" * 60)

status = SMAOStatus.OK
print("SMAOStatus.ON_OK:")
print(f"  - Nome: {status.name}")
print(f"  - Valore: {status.value}")
print(f"  - Rappresentazione: {status}")

ch_status = ChannelStatus.CS_OK
print("\nChannelStatus.CS_OK:")
print(f"  - Nome: {ch_status.name}")
print(f"  - Valore: {ch_status.value}")

# ===== TEST 2: ChannelInfo - Creazione base =====
print("\n📋 TEST 2: Creazione ChannelInfo")
print("-" * 60)

channel1 = ChannelInfo(
    driver_name="KEYENCE", channel_number=1, user_channel_number=1, is_active=True
)

print(f"Canale 1: {channel1}")
print(f"  - Label: {channel1.label}")
print(f"  - Unit: {channel1.unit}")
print(f"  - Range: {channel1.min_range} → {channel1.max_range}")

# ===== TEST 3: ChannelInfo - Con personalizzazione =====
print("\n📋 TEST 3: ChannelInfo personalizzato")
print("-" * 60)

channel2 = ChannelInfo(
    driver_name="KEYENCE",
    channel_number=2,
    user_channel_number=2,
    is_active=True,
    label="T-01",  # Etichetta custom
    unit="mm",  # Unità custom
    min_range=-50.0,
    max_range=50.0,
    decimals=3,
)

print(f"Canale 2: {channel2}")
print(f"  - Label: {channel2.label}")
print(f"  - Unit: {channel2.unit}")
print(f"  - Decimals: {channel2.decimals}")

# ===== TEST 4: Lista di canali =====
print("\n📋 TEST 4: Lista di canali")
print("-" * 60)

channels = [
    ChannelInfo("KEYENCE", 1, 1, is_active=True, label="T-01"),
    ChannelInfo("KEYENCE", 2, 2, is_active=False),
    ChannelInfo("MICRO_EPSILON", 1, 3, is_active=True, label="T-03"),
]

print("Tutti i canali:")
for ch in channels:
    print(f"  {ch}")

print("\nSolo canali attivi:")
active = [ch for ch in channels if ch.is_active]
for ch in active:
    print(f"  {ch}")

# ===== TEST 5: Serializzazione =====
print("\n📋 TEST 5: Serializzazione (to_dict / from_dict)")
print("-" * 60)

# Converti in dizionario
data = channel2.to_dict()
print(f"Dizionario: {data}")

# Ricrea da dizionario
channel_restored = ChannelInfo.from_dict(data)
print(f"Canale ricreato: {channel_restored}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETATO")
print("=" * 60)
