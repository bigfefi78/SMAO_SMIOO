"""
Script per importare ELENCO.json nel database
"""

import json
from core import ProductsDB

# Carica JSON
with open("ELENCO.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Importa
db = ProductsDB("products.db")
count = db.import_from_json(data)

print(f"\n✓ Importati {count} prodotti!")

# Mostra statistiche
stats = db.get_stats()
print(f"\nTotale prodotti: {stats['total']}")
print("\nProdotti per tipo:")
for tipo, count in sorted(stats['by_type'].items()):
    print(f"  {tipo}: {count}")