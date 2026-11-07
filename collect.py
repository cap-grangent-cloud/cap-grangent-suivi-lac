"""Collecte quotidienne Hub'Eau — Grangent. Mesure non certifiée NGF."""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

STATION = 'K060001001'
API = 'https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr'
PATH = Path('data/releves.json')


def main():
    query = urllib.parse.urlencode({'code_entite': STATION, 'grandeur_hydro': 'H', 'sort': 'desc', 'size': 1})
    req = urllib.request.Request(f'{API}?{query}', headers={'User-Agent': 'CAP-GRANGENT-suivi-lac/1.2', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    observations = payload.get('data') or []
    if not observations:
        raise RuntimeError('Aucune observation disponible : historique inchangé')
    obs = observations[0]
    if obs.get('code_station') != STATION or obs.get('grandeur_hydro') != 'H':
        raise ValueError('Station ou grandeur inattendue')
    raw = float(obs['resultat_obs'])
    level = raw / 1000
    if not 400 <= level <= 425:
        raise ValueError(f'Hauteur hors plage de contrôle : {level} m')
    stamp = dt.datetime.fromisoformat(obs['date_obs'].replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('Horodatage sans fuseau')
    now = dt.datetime.now(dt.timezone.utc)
    if not dt.timedelta(0) <= now - stamp <= dt.timedelta(hours=24):
        raise ValueError('Mesure trop ancienne ou future : aucune écriture')
    day = stamp.astimezone(ZoneInfo('Europe/Paris')).date().isoformat()
    PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else []
    if not isinstance(rows, list):
        raise ValueError('Historique JSON invalide')
    # Respecter les saisies manuelles existantes : pas de remplacement automatique.
    if any(r.get('date') == day and r.get('origin') != 'Automatique' for r in rows):
        print(f'Saisie manuelle conservée pour {day}; aucune modification')
        return
    rows = [r for r in rows if not (r.get('date') == day and r.get('origin') == 'Automatique')]
    rows.append({'date': day, 'level': round(level, 3), 'origin': 'Automatique',
                 'note': 'Hub’Eau/Vigicrues — référence NGF non confirmée ; donnée brute non qualifiée',
                 'date_obs': obs['date_obs'], 'station': STATION,
                 'qualification': obs.get('libelle_qualification_obs', 'Non renseignée')})
    rows.sort(key=lambda r: r['date'])
    temp = PATH.with_suffix('.json.tmp')
    temp.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, PATH)
    print(f'Relevé enregistré : {day} : {level:.3f} m ({obs["date_obs"]})')


if __name__ == '__main__':
    main()
