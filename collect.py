"""Collecte quotidienne : ne conserve que des cotes NGF explicitement vérifiées.
Configurer GRANGENT_SOURCE_URL et GRANGENT_JSON_LEVEL_KEY dans les secrets GitHub.
Le fournisseur doit renvoyer un JSON avec une cote NGF (mètres), pas une hauteur relative.
"""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

url = os.environ.get('GRANGENT_SOURCE_URL', '').strip()
key = os.environ.get('GRANGENT_JSON_LEVEL_KEY', '').strip()
if not url or not key:
    print('Source NGF non configurée : aucun relevé ajouté.')
    raise SystemExit(0)
if not url.startswith('https://'):
    raise ValueError('Source HTTPS obligatoire')
with urllib.request.urlopen(url, timeout=20) as response:
    obj = json.load(response)
for part in key.split('.'):
    obj = obj[int(part)] if isinstance(obj, list) else obj[part]
level = float(obj)
if not 400 <= level <= 425:
    raise ValueError('Cote hors plage plausible : vérification nécessaire')
path = Path('data/releves.json')
rows = json.loads(path.read_text(encoding='utf-8'))
today = dt.datetime.now(dt.timezone(dt.timedelta(hours=1))).date().isoformat()
rows = [r for r in rows if r['date'] != today]
rows.append({'date': today, 'level': level, 'origin': 'Automatique', 'note': 'Source NGF configurée et vérifiée par l’administrateur'})
path.write_text(json.dumps(sorted(rows, key=lambda r: r['date']), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Relevé ajouté', today, level)
