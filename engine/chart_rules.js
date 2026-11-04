// Deterministic extensions. Upstream modules remain unchanged and hash-verified.
import { Solar, LunarUtil } from 'lunar-javascript';
import { buildLocalNongliLite } from './vendor/horosa/utils/baziLunarLocal';
import { getActiveSiHuaGan } from './vendor/horosa/constants/ZWConst';
import { isLaiyinPalace } from './vendor/horosa/components/ziwei/ziweiSchools';
const G = '甲乙丙丁戊己庚辛壬癸', Z = '子丑寅卯辰巳午未申酉戌亥';
const E = ['木', '火', '土', '金', '水'];
const H = ['命宫', '兄弟宫', '夫妻宫', '子女宫', '财帛宫', '疾厄宫', '迁移宫', '交友宫', '官禄宫', '田宅宫', '福德宫', '父母宫'];
const GROUPS = ['starsMain', 'starsAssist', 'starsEvil', 'starsOthersGood', 'starsOthersBad', 'starsSmall'];
const mod = (n, d) => (n % d + d) % d;
const element = g => E[Math.floor(G.indexOf(g) / 2)];
function flowPillar(gz, dayGan) {
  return { ganzi: gz, shiShen: LunarUtil.SHI_SHEN[dayGan + gz[0]],
    hiddenStems: (LunarUtil.ZHI_HIDE_GAN[gz[1]] || []).map(g => ({ stem: g, shiShen: LunarUtil.SHI_SHEN[dayGan + g] })),
    naYin: LunarUtil.NAYIN[gz], xunKong: LunarUtil.getXunKong(gz) };
}
// A date-only anchor means 00:00 in the entered fixed birth-place offset.
function anchorLunar(date, offset) {
  const [y, m, d] = date.split('-').map(Number);
  const instant = new Date(Date.UTC(y, m - 1, d) + (8 - offset) * 3600000);
  return Solar.fromYmdHms(instant.getUTCFullYear(), instant.getUTCMonth() + 1, instant.getUTCDate(), instant.getUTCHours(), instant.getUTCMinutes(), 0).getLunar();
}
function localLunar(date) {
  const [y, m, d] = date.split('-').map(Number);
  return Solar.fromYmdHms(y, m, d, 0, 0, 0).getLunar();
}
function anniversary(text, years) {
  const [date, time] = text.split(' '), [y, m, d] = date.split('-').map(Number);
  const ny = y + years, last = new Date(Date.UTC(ny, m, 0)).getUTCDate();
  return `${ny}-${String(m).padStart(2, '0')}-${String(Math.min(d, last)).padStart(2, '0')} ${time}`;
}
export function baziRelations(pillars) {
  const keys = ['year', 'month', 'day', 'time'], names = ['年柱', '月柱', '日柱', '时柱'];
  const out = [];
  const rules = [
    ['天干五合', 'stem', ['甲己', '乙庚', '丙辛', '丁壬', '戊癸']],
    ['天干冲（甲庚乙辛丙壬丁癸口径）', 'stem', ['甲庚', '乙辛', '丙壬', '丁癸']],
    ['六合', 'branch', ['子丑', '寅亥', '卯戌', '辰酉', '巳申', '午未']],
    ['六冲', 'branch', ['子午', '丑未', '寅申', '卯酉', '辰戌', '巳亥']],
    ['六害／穿', 'branch', ['子未', '丑午', '寅巳', '卯辰', '申亥', '酉戌']],
    ['六破', 'branch', ['子酉', '丑辰', '寅亥', '卯午', '巳申', '未戌']],
    ['暗合（通禄合三组）', 'branch', ['寅丑', '午亥', '卯申']],
  ];
  for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) {
    const a = pillars[keys[i]], b = pillars[keys[j]], at = `${names[i]}${a.ganzi}／${names[j]}${b.ganzi}`;
    for (const [label, part, pairs] of rules) if (pairs.some(p => p === a[part] + b[part] || p === b[part] + a[part])) out.push(`${at}：${label}`);
    const ea = E.indexOf(element(a.stem)), eb = E.indexOf(element(b.stem));
    if (mod(ea + 2, 5) === eb) out.push(`${at}：${a.stem}克${b.stem}`);
    if (mod(eb + 2, 5) === ea) out.push(`${at}：${b.stem}克${a.stem}`);
    if (a.branch === b.branch && '辰午酉亥'.includes(a.branch)) out.push(`${at}：${a.branch}${b.branch}自刑`);
    if (['子卯', '寅巳', '巳申', '申寅', '丑戌', '戌未', '未丑'].some(p => p === a.branch + b.branch || p === b.branch + a.branch)) out.push(`${at}：相刑（含三刑两支关系，未断成局）`);
  }
  const branches = new Set(keys.map(k => pillars[k].branch));
  for (const [kind, groups] of [['三合', ['申子辰水', '亥卯未木', '寅午戌火', '巳酉丑金']], ['三会', ['亥子丑水', '寅卯辰木', '巳午未火', '申酉戌金']]]) {
    for (const group of groups) {
      const hits = [...group.slice(0, 3)].filter(z => branches.has(z));
      if (hits.length === 3) out.push(`${group.slice(0, 3)}：${kind}${group[3]}齐备（不等于已合化）`);
      else if (kind === '三合' && hits.length === 2) out.push(`${hits.join('')}：三合${group[3]}两支，缺${[...group.slice(0, 3)].find(z => !branches.has(z))}（不标完整三合局）`);
    }
  }
  return out;
}
export function enrichChinese(b, z, input) {
  const day = b.pillars.day, date = input.as_of_date || input.birth_date, count = input.forecast_years || 5;
  b.rules = { phase: '阳顺阴逆，星运以日干、自坐以本柱干', hidden: '依 lunar-javascript 藏干表原序；不统一强贴本中余标签', shensha: '原项目年干支主位＋月柱基组', relationships: '仅本命四柱；不混入胎元命身宫；相合不等于合化', luck: '沿用原项目 getYun 默认起运法；十年按首次起运时间逐十个公历年递推，闰日截到月末；左闭右开' };
  b.relations = baziRelations(b.pillars);
  const monthZhi = b.pillars.month.branch;
  const ruling = '寅卯'.includes(monthZhi) ? 0 : '巳午'.includes(monthZhi) ? 1 : '申酉'.includes(monthZhi) ? 3 : '亥子'.includes(monthZhi) ? 4 : 2;
  b.season = { basis: '月支四季法，辰戌丑未按土旺；非精细节气交接旺衰', states: ['旺', '相', '休', '囚', '死'].map((s, i) => E[mod(ruling + [0, 1, -1, -2, 2][i], 5)] + s) };
  b.structuralFlags = Object.entries(b.pillars).map(([key, p]) => ({ pillar: key, ganzi: p.ganzi,
    inDayVoid: day.xunKong.includes(p.branch), spousePalace: key === 'day',
    storageElement: ({ 辰: '水', 戌: '火', 丑: '金', 未: '木' })[p.branch] || null,
    hiddenWealthOfficer: p.hiddenStems.filter(h => ['正财', '偏财', '正官', '七杀', '财', '才', '官', '杀'].includes(h.shiShen)) }));
  b.storageNote = '只列辰水、戌火、丑金、未木之墓库对应与日柱旬空命中；土墓流派、开闭库、入墓成败未作判定。藏干含财官不等于财官入墓；日支不会命中自身旬空。';
  b.luck.forEach((d, i) => { d.start = anniversary(b.startLuck, i * 10); d.end = anniversary(b.startLuck, (i + 1) * 10); });
  const anchor = buildLocalNongliLite({date:date.replaceAll('-', '/'), time:'00:00:00', zone:input.utc_offset,
    lon:input.longitude, lat:input.latitude, gender:input.gender === '男' ? 1 : 0,
    timeAlg:{clock:1,mean:3,apparent:0}[input.time_basis], ad:1}).bazi.nongli.birth;
  const l = anchorLunar(date, input.utc_offset), year = l.getSolar().getYear();
  const gz = l.getYearInGanZhiExact(), gzYear = mod(year - 4, 60) === LunarUtil.JIA_ZI.indexOf(gz) ? year : year - 1;
  const currentIndex = b.luck.findIndex(d => d.start <= anchor && anchor < d.end);
  const birthYear = Number(input.birth_date.slice(0, 4));
  const birthGzYear = mod(birthYear - 4, 60) === LunarUtil.JIA_ZI.indexOf(b.pillars.year.ganzi) ? birthYear : birthYear - 1;
  b.timeline = { asOf: date, anchorInChartTime: anchor, year: gzYear, ganzi: gz, nominalAge: gzYear - birthGzYear + 1,
    ageBasis: '立春干支年标签减出生立春干支年标签＋1（非周岁）', currentIndex,
    currentStatus: currentIndex >= 0 ? '已入大运' : anchor < b.startLuck ? '未起运' : '超出已计算大运范围',
    upcoming: b.luck.filter(d => d.start >= anchor && d.start < anniversary(anchor, 1)).map(d => ({ ganzi: d.ganzi, start: d.start })),
    years: Array.from({ length: count }, (_, i) => ({ year: gzYear + i, ...flowPillar(G[mod(gzYear + i - 4, 10)] + Z[mod(gzYear + i - 4, 12)], day.stem) })) };
  const table = getActiveSiHuaGan(), stars = i => GROUPS.flatMap(k => z.houses[mod(i, 12)][k] || []);
  const palace = i => { i = mod(i, 12); return { index: i, name: z.houses[i].name, ganzi: z.houses[i].ganzi }; };
  const relative = (i, origin) => H[mod(origin - i, 12)];
  const mapAt = (stem, origin) => (table[stem] || []).map((star, n) => {
    const i = z.houses.findIndex((_, i) => stars(i).some(s => s.name === star));
    return { hua: '禄权科忌'[n], star, target: i < 0 ? null : palace(i), opposite: i < 0 ? null : palace(i + 6),
      targetRelative: i < 0 || origin == null ? null : relative(i, origin), oppositeRelative: i < 0 || origin == null ? null : relative(mod(i + 6, 12), origin) };
  });
  z.houses.forEach((h, i) => {
    h.laiyin = isLaiyinPalace(h.ganzi, z.yearGan);
    h.selfHua = mapAt(h.ganzi[0]).filter(f => f.target?.index === i);
    h.oppositeHua = mapAt(z.houses[mod(i + 6, 12)].ganzi[0]).filter(f => f.target?.index === i);
    h.borrowedMain = h.starsMain.length ? [] : z.houses[mod(i + 6, 12)].starsMain.map(s => ({ ...s, source: palace(i + 6) }));
  });
  z.birthFlights = mapAt(z.yearGan);
  z.palaceFlights = z.houses.map((h, i) => ({ from: palace(i), flights: mapAt(h.ganzi[0]) }));
  const spouse = mod(z.lifeHouseIndex - 2, 12);
  z.topology = { spouse: palace(spouse), opposite: palace(spouse + 6), trines: [palace(spouse + 4), palace(spouse + 8)],
    wealthFortune: [palace(z.lifeHouseIndex - 4), palace(z.lifeHouseIndex - 10)], childrenProperty: [palace(z.lifeHouseIndex - 3), palace(z.lifeHouseIndex - 9)],
    spouseTaiji: H.map((name, k) => ({ relative: name, natal: palace(spouse - k) })) };
  const nl = localLunar(date), yg = input.ziwei_year_boundary === 'lichun' ? l.getYearInGanZhiExact() : nl.getYearInGanZhi();
  const civilYear = Number(date.slice(0, 4)), zy = mod(civilYear - 4, 60) === LunarUtil.JIA_ZI.indexOf(yg) ? civilYear : civilYear - 1;
  const bornYear = Number(input.birth_date.slice(0, 4));
  // Recover the selected natal year label, including Jan/Feb before its boundary.
  const natalYear = mod(bornYear - 4, 60) === LunarUtil.JIA_ZI.indexOf(z.yearGan + z.yearZi) ? bornYear : bornYear - 1;
  const nominalAge = zy - natalYear + 1;
  const scope = i => i < 0 ? null : { life: palace(i), spouse: palace(i - 2), fortune: palace(i - 10), property: palace(i - 9),
    range: z.houses[i].direction, startYear: natalYear + z.houses[i].direction[0] - 1, endYear: natalYear + z.houses[i].direction[1] - 1,
    lifeFlights: mapAt(z.houses[i].ganzi[0], i), spouseFlights: mapAt(z.houses[mod(i - 2, 12)].ganzi[0], i) };
  const idx = z.houses.findIndex(h => nominalAge >= h.direction[0] && nominalAge <= h.direction[1]);
  const nextAge = idx >= 0 ? z.houses[idx].direction[1] + 1 : nominalAge < z.wuxingJu ? z.wuxingJu : null;
  z.timeline = { asOf: date, year: zy, ganzi: yg, nominalAge, yearBoundary: input.ziwei_year_boundary, current: scope(idx),
    status: idx >= 0 ? '已入大限' : nominalAge < z.wuxingJu ? '童限／未入大限' : '超出已计算大限范围',
    next: scope(z.houses.findIndex(h => h.direction[0] === nextAge)),
    years: Array.from({ length: count }, (_, n) => { const y = zy + n, age = y - natalYear + 1, fi = mod(y - 4, 12), gz = G[mod(y - 4, 10)] + Z[fi];
      const di = z.houses.findIndex(h => age >= h.direction[0] && age <= h.direction[1]);
      return { year: y, ganzi: gz, nominalAge: age, life: palace(fi), spouse: palace(fi - 2), property: palace(fi - 9),
        lifeInDaxian: di < 0 ? null : relative(fi, di), spouseInDaxian: di < 0 ? null : relative(mod(fi - 2, 12), di), propertyInDaxian: di < 0 ? null : relative(mod(fi - 9, 12), di), flights: mapAt(gz[0], fi) }; }) };
  z.rules = { selfHua: '[↓X]本宫干引发本宫星；[↑X]对宫干引发本宫星；仅符号定位，不判吉凶', flow: '流年以太岁地支立命宫；宫名逆布。大限沿用本命星曜和宫干，不额外重安流曜；年界沿用所选设置。流年表含基准所在干支年。', borrow: '借对宫仅作参照，不将借星当成本宫实星' };
}
