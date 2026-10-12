#!/usr/bin/env python3
import json
import os
import urllib.parse

base_dir = '/Users/user/Downloads/Nuvio Collection'
backup_file = os.path.join(base_dir, 'nuvio-collections-profile-1-2026-10-12.json.backup')

with open(backup_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]

def get_dir_for_folder(folder_title):
    clean_title = folder_title.lower().replace('+', '').strip()
    mapping = {
        'les plus populaires de la semaine': 'Top Semaine',
        'les nouveautés': 'nouveaute',
        'les plus tendances': 'tendance',
        'les plus populaires': 'populaire',
        'les mieux notés': 'mieux note',
        'comédie': 'comedie',
        'français': 'francais',
        'guerre': 'guerre politique',
        'mystère': 'mystere',
        'noël': 'noel',
        'science-fiction': 'sci fi',
        'super-héros': 'super heros',
        'kids films': 'kids films',
        'kids séries': 'kids series',
        'animé': 'anime',
        '2020s': '2020',
        '2010s': '2010',
        '2000s': '2000',
        '1990s': '1990',
        '1980s': '1980',
        '1970s': '1970',
        'dc comics': 'dc',
        'le seigneur des anneaux & hobbit': 'seigneur des anneaux',
        'pirates des caraïbes': 'pirate des caraibes',
        'retour vers le futur': 'retour vers le futur',
        'rocky & creed': 'rocky',
        'western': 'westerns',
        'familial': 'famille',
        'k-drama': 'k drama',
        'x-men': 'x men'
    }
    if clean_title in mapping:
        return mapping[clean_title]
    for d in all_dirs:
        if d.lower() == clean_title:
            return d
    for d in all_dirs:
        if d.lower() in clean_title or clean_title in d.lower():
            return d
    return None

explicit_slots = {
    'kids films': {
        'coverImageUrl': 'kids-films-wide.webp',
        'titleLogoUrl': 'Kids-Films-Logo.webp',
        'heroBackdropUrl': 'Kids-films-hero.webp'
    },
    'kids series': {
        'coverImageUrl': 'kids-series-wide.webp',
        'titleLogoUrl': 'Kids-Series-Logo.webp',
        'heroBackdropUrl': 'kids-series-hero.webp'
    },
    'anime': {
        'coverImageUrl': 'anime-wide.webp',
        'titleLogoUrl': 'Anim-logo.webp',
        'heroBackdropUrl': 'Anim-hero.webp'
    }
}

CDN_BASE = 'https://cdn.jsdelivr.net/gh/Fubalt/nuvio-collection@main/'

total_slots_updated = 0
folder_results = []

for col in data:
    for folder in col.get('folders', []):
        ftitle = folder.get('title', '')
        dname = get_dir_for_folder(ftitle)
        assert dname is not None, f'Could not find dir for {ftitle}'
        
        dir_path = os.path.join(base_dir, dname)
        raw_files = []
        for f in os.listdir(dir_path):
            if not f.startswith('.'):
                st = os.stat(os.path.join(dir_path, f))
                raw_files.append((f, getattr(st, 'st_birthtime', st.st_mtime)))
        raw_files.sort(key=lambda x: x[1])
        
        gifs = [f[0] for f in raw_files if f[0].lower().endswith('.gif')]
        non_gifs = [f[0] for f in raw_files if not f[0].lower().endswith('.gif')]
        
        res = {'title': ftitle, 'dir': dname}
        
        # 1. coverImageUrl
        if folder.get('coverImageUrl'):
            if dname in explicit_slots and 'coverImageUrl' in explicit_slots[dname]:
                img = explicit_slots[dname]['coverImageUrl']
            else:
                img = non_gifs[0]
            quoted = urllib.parse.quote(f'{dname}/{img}', safe='/')
            folder['coverImageUrl'] = CDN_BASE + quoted
            res['coverImageUrl'] = img
            total_slots_updated += 1
            
        # 2. titleLogoUrl
        if folder.get('titleLogoUrl'):
            if dname in explicit_slots and 'titleLogoUrl' in explicit_slots[dname]:
                img = explicit_slots[dname]['titleLogoUrl']
            else:
                img = non_gifs[1] if len(non_gifs) > 1 else non_gifs[0]
            quoted = urllib.parse.quote(f'{dname}/{img}', safe='/')
            folder['titleLogoUrl'] = CDN_BASE + quoted
            res['titleLogoUrl'] = img
            total_slots_updated += 1
            
        # 3. heroBackdropUrl
        if folder.get('heroBackdropUrl'):
            if dname in explicit_slots and 'heroBackdropUrl' in explicit_slots[dname]:
                img = explicit_slots[dname]['heroBackdropUrl']
            else:
                img = non_gifs[2] if len(non_gifs) > 2 else non_gifs[-1]
            quoted = urllib.parse.quote(f'{dname}/{img}', safe='/')
            folder['heroBackdropUrl'] = CDN_BASE + quoted
            res['heroBackdropUrl'] = img
            total_slots_updated += 1
            
        # 4. focusGifUrl
        if folder.get('focusGifUrl'):
            if gifs:
                img = gifs[0]
                quoted = urllib.parse.quote(f'{dname}/{img}', safe='/')
                folder['focusGifUrl'] = CDN_BASE + quoted
                res['focusGifUrl'] = img
                total_slots_updated += 1
                
        folder_results.append(res)

target1 = os.path.join(base_dir, 'nuvio-collections-profile-1-2026-10-12.json')
with open(target1, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

target2 = '/Users/user/Downloads/nuvio-collections-profile-1-2026-10-12.json'
with open(target2, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"DONE! Successfully updated {total_slots_updated} slots across {len(folder_results)} folders.")
