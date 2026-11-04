"""Three independent Markdown data sheets, not interpretations or AI instructions."""


def joined(items):
    return '、'.join(str(x) for x in items) or '无匹配（仅限已检查规则）'


def palace(p):
    return f"{p['name']}[{p['ganzi']}]" if p else '未定位'


def flights(rows):
    return '；'.join(f"{r['star']}化{r['hua']}入本命{palace(r['target'])}"
                     + (f"／当前层{r['targetRelative']}" if r.get('targetRelative') else '')
                     + (f"，对宫本命{palace(r['opposite'])}" + (f"／当前层{r['oppositeRelative']}" if r.get('oppositeRelative') else '') if r['hua'] == '忌' else '') for r in rows)


def hidden(p):
    return joined(f"{h['stem']}({h['shiShen']})" for h in p['hiddenStems'])


def header(name, r):
    i = r['input']
    return [f'# {name} · 程序计算结构化模板', '',
            '> 本文件是排盘数据，不是AI分析报告，不是现实事件验证。未计算不等于不存在；规则命中不等于吉凶成立。', '',
            '## 1. 基础信息与计算口径',
            f"- 性别：{i['gender']}；公历出生：{i['birth_date']} {i['birth_time']}。",
            f"- 出生地固定 UTC{i['utc_offset']:+g}；经度{i['longitude']}°，纬度{i['latitude']}°。未自动查询历史夏令时。",
            f"- 分析基准：{i['as_of_date']} 00:00（同一固定UTC偏移）；时间窗口：{i['forecast_years']}年。",
            f"- 数据版本：{r['version']}；Horosa计算源版本：{r['provenance']['commit']}。"]


def bazi_template(r):
    b, i = r['bazi'], r['input']
    n = b['nongli']
    lines = header('四柱八字', r) + [
        f"- 时间选择：{i['time_basis']}；换日：{i['day_boundary']}点；输入钟表时间{n['clockTime']}；真太阳时参考{n['solarTime']}；实际排盘历时{n['birth']}。",
        f"- 农历：{n['year']}年{n['month']}{n['day']}；节气：{n['jieqi']}，{n['jiedelta']}。",
        f"- 胎元：{b['auxiliary']['tai']['ganzi']}；命宫：{b['auxiliary']['ming']['ganzi']}；身宫：{b['auxiliary']['shen']['ganzi']}（原项目通行命身宫法）。",
        '- 月令司令／分野（原项目common表）：' + ('未计算' if not b.get('fenYe') else format_fenye(b['fenYe'])),
        f"- 季节旺衰：{joined(b['season']['states'])}；口径：{b['season']['basis']}。",
        '- 五行加权分布（算法权重，非预测准确率）：' + joined(f"{s['label']} {s['percent']}%" for s in b['wuxing']), '',
        '## 2. 四柱详细配置', f"- 长生口径：{b['rules']['phase']}。", f"- 藏干顺序：{b['rules']['hidden']}。", f"- 神煞口径：{b['rules']['shensha']}。"]
    for key, name in [('year', '年柱'), ('month', '月柱'), ('day', '日柱（地支作夫妻宫）'), ('time', '时柱')]:
        p = b['pillars'][key]
        lines += [f"### {name}：{p['ganzi']}", f"- 天干十神：{p['shiShen']}；地支藏干：{hidden(p)}。",
                  f"- 星运（日干长生）：{p['changSheng']}；自坐长生：{p['selfZuo']}。",
                  f"- 本柱旬空：{p['xunKong']}；纳音：{p['naYin']}；神煞：{joined(p['shenSha'])}。"]
    lines += ['', '## 3. 原局显式关系与墓库／空亡', f"- 范围：{b['rules']['relationships']}。"]
    lines += ['- ' + s for s in b['relations']] or ['- 已检查规则无匹配。']
    for f in b['structuralFlags']:
        lines.append(f"- {f['ganzi']}：日柱旬空命中={'是' if f['inDayVoid'] else '否'}；" +
                     (f"墓库对应={f['storageElement']}库；" if f['storageElement'] else '非辰戌丑未库支；') +
                     '藏干财官杀=' + joined(f"{h['stem']}({h['shiShen']})" for h in f['hiddenWealthOfficer']) + ('；本支为夫妻宫' if f['spousePalace'] else '') + '。')
    lines += [f"- 边界：{b['storageNote']}", '', '## 4. 大运与近期流年',
              f"- 起运：{b['startLuckDescription']}；首次起运历时{b['startLuck']}。",
              f"- 交接口径：{b['rules']['luck']}；日期在所选八字历时坐标中比较，不宣称天文级精度。"]
    for k, d in enumerate(b['luck'], 1):
        lines.append(f"- 第{k}步{d['ganzi']}：[{d['start']}, {d['end']})；虚岁标签{d['age']}—{d['age'] + 9}；天干{d['shiShen']}／藏干{hidden(d)}；纳音{d['naYin']}。")
    t = b['timeline']
    current = b['luck'][t['currentIndex']] if t['currentIndex'] >= 0 else None
    lines += [f"- 当前基准：{t['asOf']}；按所选八字时间换算为{t['anchorInChartTime']}；{t['year']} {t['ganzi']}年（立春年界）；年龄标签{t['nominalAge']}，{t['ageBasis']}。",
              f"- 当前大运：{current['ganzi'] if current else t['currentStatus']}；一年内换运：" + joined(f"{d['start']}进入{d['ganzi']}" for d in t['upcoming']) + '。',
              '- 近期流年（含基准所在干支年，不是逐年公历1月1日换年）：']
    lines += [f"  - {y['year']} {y['ganzi']}：天干{y['shiShen']}；藏干{hidden(y)}；纳音{y['naYin']}。" for y in t['years']]
    lines += ['', '## 5. 留给后续独立解读的内容', '- 格局成败、喜忌取用、合化条件、开闭库、婚财健康断语未自动判定；此模板不填入交叉分析。']
    return '\n'.join(lines) + '\n'


def format_fenye(f):
    ruler = f.get('ruler') or {}
    # Keep exact raw table diagnostics in the JSON export; readable summary here.
    return f"司令干{ruler.get('gan', '未计算')}；节后{f.get('daysAfterJie', f.get('day', '见JSON'))}天；其余表参数见JSON。"


def ziwei_template(r):
    z, b, i = r['ziwei'], r['bazi'], r['input']
    hs = z['houses']
    lines = header('紫微斗数', r) + [
        f"- 阴阳性别：{'阳' if '甲丙戊庚壬'.find(z['yearGan']) >= 0 else '阴'}{i['gender']}；{z['wuxingJuText']}；命主{z['lifeMaster']}；身主{z['bodyMaster']}；子年斗君{z['zidou']}。",
        f"- 时间：{i['time_basis']}；钟表{z['nongli']['clockTime']}；真太阳时参考{z['nongli']['solarTime']}；实际排盘历时{z['nongli']['birth']}。",
        f"- 农历：{z['nongli']['year']}年{z['nongli']['month']}{z['nongli']['day']}；四柱：" + ' '.join(p['ganzi'] for p in b['pillars'].values()) + '。',
        f"- 年界：{i['ziwei_year_boundary']}；闰月：{i['leap_month']}；四化表：{i['sihua_school']}（沿用页面所选流派）。",
        f"- 命宫：{palace(hs[z['lifeHouseIndex']])}；身宫：{palace(hs[z['bodyHouseIndex']])}；来因宫：" + joined(palace(h) for h in hs if h['laiyin']) + '。',
        f"- 自化符号：{z['rules']['selfHua']}。", '', '## 2. 生年四化', '- ' + flights(z['birthFlights']), '', '## 3. 十二宫全量星曜（借星不当实星）']
    for h in sorted(hs, key=lambda h: (z['lifeHouseIndex'] - hs.index(h)) % 12):
        lines.append(f"### {palace(h)}" + (' · 身宫' if h['isBody'] else ''))
        for label, key in [('主星', 'starsMain'), ('辅星', 'starsAssist'), ('煞曜', 'starsEvil'), ('其他吉曜', 'starsOthersGood'), ('其他杂曜', 'starsOthersBad'), ('岁前／将前／博士杂曜', 'starsSmall')]:
            def star_text(s):
                flags = [f"生年{s['sihua']}" if s.get('sihua') else '']
                flags += ['↓' + f['hua'] for f in h['selfHua'] if f['star'] == s['name']]
                flags += ['↑' + f['hua'] for f in h['oppositeHua'] if f['star'] == s['name']]
                return s['name'] + (f"[{s['starlight']}]" if s.get('starlight') else '') + ''.join(f'[{x}]' for x in flags if x)
            lines.append(f"- {label}：" + (joined(star_text(s) for s in h[key]) if h[key] else '无此类星曜') + '。')
        if not h['starsMain']:
            lines.append('- 无主星（空宫），借对宫参照：' + joined(f"{s['name']}，来自{palace(s['source'])}" for s in h['borrowedMain']) + '；借星不是本宫实星，自化仍只按实星计算。')
        lines.append(f"- 十二长生：{h['phase']}；大限虚岁：{h['direction'][0]}—{h['direction'][1]}；小限虚岁：{joined(h['smallDirection'])}。")
    top = z['topology']
    lines += ['', '## 4. 空间拓扑与夫妻宫立太极', f"- 夫妻{palace(top['spouse'])}，对宫{palace(top['opposite'])}；三合{joined(palace(p) for p in top['trines'])}。",
              '- 财福线：' + joined(palace(p) for p in top['wealthFortune']) + '。', '- 子田线：' + joined(palace(p) for p in top['childrenProperty']) + '。']
    lines += [f"- 配偶之{p['relative']}＝本命{palace(p['natal'])}。" for p in top['spouseTaiji']]
    lines += ['', '## 5. 十二宫干飞化轨迹']
    lines += [f"- {palace(f['from'])}宫干{f['from']['ganzi'][0]}：{flights(f['flights'])}。" for f in z['palaceFlights']]
    t = z['timeline']
    lines += ['', '## 6. 大限与流年坐标', f"- 基准：{t['asOf']}；{t['year']} {t['ganzi']}年，虚岁{t['nominalAge']}；{t['status']}。", f"- 口径：{z['rules']['flow']}"]
    for label, scope in [('当前大限', t['current']), ('下一大限', t['next'])]:
        if not scope:
            lines.append(f'- {label}：不在已计算范围内。')
            continue
        lines += [f"- {label}：年界标签{scope['startYear']}—{scope['endYear']}，虚岁{scope['range'][0]}—{scope['range'][1]}；命宫叠本命{palace(scope['life'])}；夫妻叠本命{palace(scope['spouse'])}；福德叠本命{palace(scope['fortune'])}；田宅叠本命{palace(scope['property'])}。",
                  f"  - 大限命干：{flights(scope['lifeFlights'])}。", f"  - 大限夫妻干：{flights(scope['spouseFlights'])}。"]
    for y in t['years']:
        lines += [f"### {y['year']} {y['ganzi']}年（虚岁{y['nominalAge']}）",
                  f"- 流命叠本命{palace(y['life'])}／大限{y['lifeInDaxian'] or '未入限'}；流夫叠本命{palace(y['spouse'])}／大限{y['spouseInDaxian'] or '未入限'}；流田叠本命{palace(y['property'])}／大限{y['propertyInDaxian'] or '未入限'}。",
                  '- 流年干四化：' + flights(y['flights']) + '。']
    lines += ['', '## 7. 留给后续独立解读的内容', '- 飞化坐标不自动等同事件发生；组合吉凶、应期与现实解释留给后续独立分析，不直接带入交叉分析。']
    return '\n'.join(lines) + '\n'


def vedic_template(r):
    v = r['vedic']
    a = v['ascendant']
    lines = header('印度占星 Jyotish', r) + [f"- 恒星黄道；岁差{v['ayanamsa']} {v['ayanamsa_degrees']}°；D1宫制{v['house_system']}；交点{v['node_type']}。",
             f"- 印占按原始民用出生时间转UTC：{v['utc']}，不重复作真太阳时修正；星历：{v['ephemeris']}。",
             f"- 卡拉卡：{v['rules']['karaka']}。", f"- 尊贵：{v['rules']['dignity']}。", f"- 燃烧：{v['rules']['combustion']}。", '',
             '## 2. D1根盘星体与上升', f"- 上升：{a['sign']} {a['degree']}°；{a['nakshatra']['name']} 第{a['nakshatra']['pada']}足；守护星{a['lord']}。"]
    for p in v['planets']:
        c = p['combustion']
        burn = (f"{'燃烧' if c['combust'] else '未燃烧'}，距日{c['distance']}°／阈值<{c['orb']}°" if c['applicable'] else '不适用燃烧规则')
        lines.append(f"- {p['name']}（{p['karaka'] or '不分配卡拉卡'}）：第{p['house']}宫·{p['sign']} {p['degree']}°；{p['nakshatra']['name']} 第{p['nakshatra']['pada']}足；{p['dignity']}；{'逆行' if p['retrograde'] else '顺行'}；{burn}。")
    lines += ['', '## 3. Jaimini核心要素与Arudha', f"- 卡拉卡同度冲突：{'存在，AK/DK未定' if v['karaka_tie'] else '未检出'}。"]
    lines += [f"- {k['label']}：{k['name']}，排序用度{k['ranking_degree']:.7f}°" + ('（同度未定，仅保留候选顺序）' if v['karaka_tie'] else '') + '。' for k in v['karakas']]
    lines += [f"- Arudha口径：{v['rules']['arudha']}"]
    lines += [f"- {p['label']}：整宫第{p['house']}宫·{p['sign']}；落点宫主{p['lord']}；同星座星体{joined(p['co_sign_planets'])}（只表示同星座，不表示同度合相）；计算原宫主{p['calculation_lord']}。" for p in v['arudhas']]
    d9 = v['vargas']['9']
    lines += ['', '## 4. D9九分盘', f"- 上升{d9['ascendant']}，D9命主{d9['lord']}；分盘均按整宫关系布宫。"]
    lines += [f"- {p['name']}：第{p['house']}宫·{p['sign']} {p['degree']}°；{p['dignity']}；D1/D9同星座={'是' if p['vargottama'] else '否'}。" for p in d9['planets']]
    lines += ['', '## 5. 特殊联动检查', '- ' + v['patterns']['coverage']]
    for num in ('d1', 'd9'):
        lines += [f"- {num.upper()}七曜星座互换：" + joined('与'.join(p['planets']) + '（' + '／'.join(p['signs']) + '）' for p in v['patterns'][num + '_exchanges']) + '。']
        candidates = v['patterns'][num + '_cancellation_candidates']
        lines.append(f"- {num.upper()}落陷取消检查：" + ('无落陷七曜，无需执行此项检查。' if not candidates else '以下仅为候选条件，不是完整落陷取消结论。'))
        for p in candidates:
            lines.append(f"  - {p['planet']}：" + '；'.join(c['condition'] + ('＝命中' if c['matched'] else '＝未命中') for c in p['checks']) + '。')
    t = v['timeline']
    lines += ['', '## 6. Vimshottari运期与时间锚点', f"- D1月亮起运；年长{v['dasha']['year_days']}天；出生首运余额{v['dasha']['first_balance_years']:.8f}年。", '- ' + t['convention'], f"- 基准{t['as_of']}；窗口至{t['window_end']}；覆盖完整={'是' if t['complete'] else '否，超出已计算时间范围，不外推缺失运期'}。"]
    for label, p in [('当前MD', t['current_md']), ('当前AD', t['current_ad'])]:
        lines.append(f"- {label}：{p['lord']}，{p['start']} 至 {p['end']}。" if p else f'- {label}：不在已计算范围内。')
    lines += [f"- {p['md']}／{p['ad']}／{p['pd']}：[{p['start']}, {p['end']})。" for p in t['pd']]
    lines += ['', '## 7. 留给后续独立解读的内容', '- 运期与星体状态不等于现实事件。未实现的特殊格局、格局成败与现实解释留给后续独立分析；本模板不直接进入交叉分析。']
    return '\n'.join(lines) + '\n'


def render_templates(result):
    return {'bazi': bazi_template(result), 'ziwei': ziwei_template(result), 'vedic': vedic_template(result)}
