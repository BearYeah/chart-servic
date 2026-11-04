// Application adapter; upstream algorithms remain unchanged under vendor/horosa.
import { buildLocalBaziResult, getSelfZuo } from './vendor/horosa/utils/baziLunarLocal';
import { enrichChinese } from './chart_rules';
import { LunarUtil } from 'lunar-javascript';
import { calcZiwei } from './vendor/horosa/components/ziwei/ZiweiCalc';
import { ZWEngineOptions } from './vendor/horosa/components/ziwei/ziweiOptions';
import { ZWSchool } from './vendor/horosa/constants/ZWConst';
export function calculateChineseCharts(input) {
  const params = {
    date: input.birth_date.replaceAll('-', '/'), time: input.birth_time,
    zone: input.utc_offset, lon: input.longitude, lat: input.latitude,
    gpsLon: input.longitude, gpsLat: input.latitude, ad: 1,
    gender: input.gender === '男' ? 1 : 0,
    timeAlg: { clock: 1, mean: 3, apparent: 0 }[input.time_basis],
    after23NewDay: input.day_boundary === '23' ? 1 : 0,
    lateZiHourUseNextDay: input.day_boundary === '23' ? 1 : 0,
    phaseType: 2, southMonth: 'standard',
  };
  // Each request runs in an isolated process: school singletons cannot leak.
  ZWSchool.school = input.sihua_school;
  const bazi = buildLocalBaziResult(params).bazi;
  const ziwei = calcZiwei(params, {
    ...ZWEngineOptions, timeAlg: params.timeAlg,
    after23NewDay: params.after23NewDay,
    lateZiHourUseNextDay: params.lateZiHourUseNextDay,
    lateZi: input.day_boundary === '23' ? 'zi_chu' : 'zi_zheng',
    yearBoundary: input.ziwei_year_boundary,
    leapMonth: input.leap_month,
  });
  const pillar = (p = {}) => ({ ganzi: p.ganzi || '', stem: p.stem?.cell || '',
    branch: p.branch?.cell || '', shiShen: p.zhu === '日' ? '日元' : (LunarUtil.SHI_SHEN[bazi.fourColumns.day.stem.cell + p.stem?.cell] || p.stem?.relative || ''),
    hiddenStems: (p.stemInBranch || []).map(s => ({ stem: s.cell, shiShen: LunarUtil.SHI_SHEN[bazi.fourColumns.day.stem.cell + s.cell] || s.relative })),
    naYin: p.naying || '', changSheng: p.ganziPhase || '', xunKong: p.xunEmpty || '',
    selfZuo: getSelfZuo(p.stem?.cell, p.branch?.cell, 2), shenSha: p.shenSha || [] });
  const compact = {
    nongli: bazi.nongli,
    auxiliary: Object.fromEntries(['tai', 'ming', 'shen'].map(k => [k, pillar(bazi.fourColumns[k])])),
    fenYe: bazi.fenYe,
    pillars: Object.fromEntries(['year', 'month', 'day', 'time'].map(k => [k, pillar(bazi.fourColumns[k])])),
    startLuck: bazi.directTime, startLuckDescription: bazi.directInfo,
    luck: bazi.direction.map(d => ({ age: d.age, startYear: d.startYear, endYear: d.endYear,
      ...pillar(d.mainDirect),
      years: (d.subDirect || []).map(y => ({ year: y.year || y.startYear, age: y.age, ...pillar(y) })) })),
    wuxing: bazi.wuxingStat.scores,
  };
  delete ziwei.fourColumns;
  enrichChinese(compact, ziwei, input);
  return { bazi: compact, ziwei };
}
