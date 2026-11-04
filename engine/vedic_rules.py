"""Explicit, bounded Jyotish rules adapted from Horosa (see notices).

These are chart classifications, not evidence that a predicted event is real.
Arudha uses classical seven sign lords; node dignities are intentionally unassigned.
"""
from datetime import datetime, timedelta
from itertools import combinations

SIGNS = ['白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼']
LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']
NAMES = dict(Sun='太阳', Moon='月亮', Mars='火星', Mercury='水星', Jupiter='木星', Venus='金星', Saturn='土星', Rahu='罗睺', Ketu='计都')
ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
YEARS = dict(zip(ORDER, [7, 20, 6, 10, 7, 18, 16, 19, 17]))
EXALT = dict(Sun=0, Moon=1, Mars=9, Mercury=5, Jupiter=3, Venus=11, Saturn=6)
MT = dict(Sun=(4, 0, 20), Moon=(1, 4, 30), Mars=(0, 0, 12), Mercury=(5, 16, 20), Jupiter=(8, 0, 10), Venus=(6, 0, 15), Saturn=(10, 0, 20))
FRIENDS = dict(Sun={'Moon', 'Mars', 'Jupiter'}, Moon={'Sun', 'Mercury'}, Mars={'Sun', 'Moon', 'Jupiter'}, Mercury={'Sun', 'Venus'}, Jupiter={'Sun', 'Moon', 'Mars'}, Venus={'Mercury', 'Saturn'}, Saturn={'Mercury', 'Venus'})
ENEMIES = dict(Sun={'Venus', 'Saturn'}, Moon=set(), Mars={'Mercury'}, Mercury={'Moon'}, Jupiter={'Mercury', 'Venus'}, Venus={'Sun', 'Moon'}, Saturn={'Sun', 'Moon', 'Mars'})
ORBS = dict(Moon=12, Mars=17, Mercury=14, Jupiter=11, Venus=10, Saturn=15)


def dignity(key, sign, degree):
    if key not in EXALT:
        return '节点尊贵未赋值（流派有分歧）'
    if sign == EXALT[key]:
        return '旺（擢升星座）'
    if sign == (EXALT[key] + 6) % 12:
        return '落陷'
    mt_sign, start, end = MT[key]
    if sign == mt_sign and start <= degree <= end:
        return '根本三角（沿用原项目度数区间）'
    lord = LORDS[sign]
    if lord == key:
        return '入庙（本垣）'
    if lord in FRIENDS[key]:
        return '友星座（自然关系）'
    if lord in ENEMIES[key]:
        return '敌星座（自然关系）'
    return '中性星座（自然关系）'


def arudha_sign(reference, lord_sign):
    """Inclusive equal-count rule; same/seventh landing corrected from landing."""
    landed = (2 * lord_sign - reference) % 12
    if (landed - reference) % 12 in (0, 6):
        landed = (landed + 9) % 12
    return landed


def exchanges(planets):
    classical = [p for p in planets if p['key'] in EXALT]
    return [{'planets': [a['name'], b['name']], 'signs': [a['sign'], b['sign']]}
            for a, b in combinations(classical, 2)
            if LORDS[a['sign_index']] == b['key'] and LORDS[b['sign_index']] == a['key']]


def cancellation_candidates(planets, asc):
    """Two declared structural conditions only, never a full Neechabhanga verdict."""
    by_key = {p['key']: p for p in planets}
    moon = by_key['Moon']['sign_index']
    rows = []
    for p in planets:
        key, sign = p['key'], p['sign_index']
        if key not in EXALT or sign != (EXALT[key] + 6) % 12:
            continue
        checks = []
        for label, lord in [('落陷星座主', LORDS[sign]), ('擢升星座主', LORDS[EXALT[key]])]:
            lord_sign = by_key[lord]['sign_index']
            for origin, origin_sign in [('上升', asc), ('月亮', moon)]:
                house = (lord_sign - origin_sign) % 12 + 1
                checks.append({'condition': f'{label}{NAMES[lord]}居{origin}角宫', 'house': house, 'matched': house in (1, 4, 7, 10)})
        rows.append({'planet': p['name'], 'checks': checks, 'verdict': '仅列候选条件；其他条件及格局效力未判定'})
    return rows


def dasha_window(dasha, as_of, years):
    end = as_of.replace(year=as_of.year + years, day=min(as_of.day, 28)) if as_of.month == 2 and as_of.day == 29 else as_of.replace(year=as_of.year + years)
    current_md = current_ad = None
    rows = []
    for md in dasha['periods']:
        ms, me = map(datetime.fromisoformat, (md['start'], md['end']))
        if ms <= as_of < me:
            current_md = {k: md[k] for k in ('lord', 'start', 'end')}
        for ad in md['subperiods']:
            start, stop = map(datetime.fromisoformat, (ad['start'], ad['end']))
            if ms <= as_of < me and start <= as_of < stop:
                current_ad = ad.copy()
            if stop <= as_of or start >= end:
                continue
            ad_key = next(k for k, v in NAMES.items() if v == ad['lord'])
            idx, cursor = ORDER.index(ad_key), start
            duration = stop - start
            for j in range(9):
                key = ORDER[(idx + j) % 9]
                next_time = stop if j == 8 else cursor + duration * (YEARS[key] / 120)
                if cursor < end and next_time > as_of:
                    rows.append({'md': md['lord'], 'ad': ad['lord'], 'pd': NAMES[key],
                                 'start': cursor.isoformat(timespec='seconds'), 'end': next_time.isoformat(timespec='seconds')})
                cursor = next_time
    covered = bool(rows) and datetime.fromisoformat(rows[0]['start']) <= as_of and datetime.fromisoformat(rows[-1]['end']) >= end
    return {'as_of': as_of.isoformat(timespec='seconds'), 'window_end': end.isoformat(timespec='seconds'),
            'current_md': current_md, 'current_ad': current_ad, 'pd': rows, 'complete': covered,
            'convention': '左闭右开；PD按AD时长乘各星年数/120。列出与窗口相交的完整运期（首尾不截断），时间为出生地固定UTC偏移。'}


def enrich(vedic, value):
    planets = vedic['planets']
    by_key = {p['key']: p for p in planets}
    asc = int(vedic['ascendant']['longitude'] // 30)
    sun = by_key['Sun']['longitude']
    scheme = value['karaka_scheme']
    keys = list(EXALT) + (['Rahu'] if scheme == '8' else [])
    ordered = sorted(keys, key=lambda k: 30 - by_key[k]['longitude'] % 30 if k == 'Rahu' else by_key[k]['longitude'] % 30, reverse=True)
    labels = ['AK', 'AmK', 'BK', 'MK', 'PiK', 'PK', 'GK', 'DK'] if scheme == '8' else ['AK', 'AmK', 'BK', 'MK', 'PK', 'GK', 'DK']
    degrees = [30 - by_key[k]['longitude'] % 30 if k == 'Rahu' else by_key[k]['longitude'] % 30 for k in ordered]
    tied = any(abs(a - b) < 1e-7 for a, b in combinations(degrees, 2))
    vedic['karakas'] = [{'label': label, 'key': key, 'name': NAMES[key], 'ranking_degree': deg} for key, label, deg in zip(ordered, labels, degrees)]
    vedic['karaka_tie'] = tied
    for p in planets:
        p['karaka'] = None if tied else next((r['label'] for r in vedic['karakas'] if r['key'] == p['key']), None)
        p['dignity'] = dignity(p['key'], p['sign_index'], p['degree'])
        orb = ORBS.get(p['key'])
        if p['retrograde']:
            orb = {'Mercury': 12, 'Venus': 8}.get(p['key'], orb)
        distance = abs((p['longitude'] - sun + 180) % 360 - 180)
        p['combustion'] = {'applicable': orb is not None, 'orb': orb, 'distance': round(distance, 6), 'combust': orb is not None and distance < orb}
    vedic['ascendant']['lord'] = NAMES[LORDS[asc]]
    vedic['arudhas'] = []
    for h in range(1, 13):
        reference = (asc + h - 1) % 12
        lord = LORDS[reference]
        landed = arudha_sign(reference, by_key[lord]['sign_index'])
        vedic['arudhas'].append({'label': 'AL' if h == 1 else 'UL' if h == 12 else f'A{h}',
                                'reference_house': h, 'reference_sign': SIGNS[reference], 'calculation_lord': NAMES[lord],
                                'sign': SIGNS[landed], 'sign_index': landed, 'house': (landed - asc) % 12 + 1,
                                'lord': NAMES[LORDS[landed]], 'co_sign_planets': [p['name'] for p in planets if p['sign_index'] == landed]})
    for num, varga in vedic['vargas'].items():
        varga['lord'] = NAMES[LORDS[varga['ascendant_index']]]
        for p in varga['planets']:
            p['dignity'] = dignity(p['key'], p['sign_index'], p['degree'])
            p['vargottama'] = num != '1' and p['sign_index'] == by_key[p['key']]['sign_index']
    d9 = vedic['vargas']['9']
    vedic['patterns'] = {'d1_exchanges': exchanges(planets), 'd9_exchanges': exchanges(d9['planets']),
                         'd1_cancellation_candidates': cancellation_candidates(planets, asc),
                         'd9_cancellation_candidates': cancellation_candidates(d9['planets'], d9['ascendant_index']),
                         'coverage': '已检查古典七曜星座主互换、D1/D9同星座、两类落陷取消候选条件；其他特殊格局未计算，不能把未检出解释为不存在。'}
    anchor = datetime.fromisoformat(value['as_of_date'] + 'T00:00:00').replace(tzinfo=datetime.fromisoformat(vedic['dasha']['periods'][0]['start']).tzinfo)
    vedic['timeline'] = dasha_window(vedic['dasha'], anchor, value['forecast_years'])
    vedic['rules'] = {'karaka': f'{scheme}星制；罗睺用30°减星座内度数；精度内同度则卡拉卡未定，不任意定AK/DK',
                      'arudha': '古典七曜宫主，不使用天蝎/水瓶节点副主。等数法；落原宫/对宫时从落点起第十座。点位宫号按整宫星座关系，即使D1显示为等宫制。',
                      'dignity': '旺/落陷→原项目根本三角度数→本垣→自然友敌；节点尊贵不指定。分盘度数用于该分盘分类，不当作真实天文角距。',
                      'combustion': '仅D1实际黄经角距；月12、火17、水14（逆12）、木11、金10（逆8）、土15度，严格小于阈值；日和节点不判燃烧。'}
