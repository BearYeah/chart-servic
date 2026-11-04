# 排盘功能的来源、许可与范围

本次新增本地排盘功能，并非独立原创的传统排盘算法，也不是原项目全部功能的完整复制。

## Horosa

- 来源：https://github.com/BearYeah/Horosa-Web-App-comprehensively-improved-Windows
- 固定提交：`f21b451b752ec5926ffe869216045963c12f4322`，非浮动跟踪 main。
- 原始工作目录：`local/workspace/Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/`。
- 项目声明许可：AGPL-3.0-only。完整原文保留于 `vendor/horosa/LICENSE`。
- 原作者与贡献者归属保留于上游。感谢 Horosa、Horace-Maxwell、BearYeah 及上游历法作者。
- `vendor/horosa/utils/`、`constants/`、`components/ziwei/`：33 个 JS/JSON 文件保持上游原文，不包含其 React 页面或网络请求代码。
- `vendor/horosa/varga.py`：来自 `astropy/astrostudy/india/varga.py` 的纯经度变换部分；仅删除不使用的 flatlib 导入和对象重定位部分，保留分盘规则。文件头标记修改。
- `charts.py` 的 Vimshottari 起运余量与主运／子运规则参考上游 `astropy/astrostudy/india/jyotish_engine.py`；改为确定性固定时区输出，至少9个主运，必要时延长到用户所选基准窗口；PD按AD时长乘星体年数／120计算，运期左闭右开。
- `vedic_rules.py` 的卡拉卡排序、自然友敌、燃烧阈值参考 `india/primitives.py`，尊贵分类参考 `india/jyotish_engine.py`；Arudha等数及原／对宫落点例外参考 `india/arudha.py`。此适配明确使用古典七曜宫主，不使用上游可选的节点双主取强规则；节点尊贵未赋值；落陷取消仅检查文中声明的两类候选条件，不宣称完整格局成立。
- 新增适配与模板层：`chart_entry.js`、`chart_rules.js`、`chart_runner.cjs`、`charts.py`、`vedic_rules.py`、`chart_templates.py`、`charts-ui.js`、`charts.css` 及 `server.py`/`app.js` 接入改动。`vendor/chart-engine.cjs` 是由保留的源码和历法库生成的本地运行包，不能标作原创或专有算法。

这不是法律意见。当前仅在本机开发，没有发布网站或替你选择商业许可。对外分发或网络服务前，应核对 AGPL 对衍生／组合程序、修改声明及对应源码提供的要求，不能仅保留一条署名就认为满足全部条件。如需闭源客户服务，应先处理授权方案。

## lunar-javascript 1.7.7

- 来源：https://github.com/6tail/lunar-javascript
- 版权所有：Copyright (c) 2018 6tail。
- 许可：MIT，完整文本保留于 `vendor/lunar-javascript-LICENSE`。
- 用于 Horosa 八字、农历与紫微历法层；打包在 `vendor/chart-engine.cjs` 中。`package-lock.json` 固定下载与完整性校验。

## pyswisseph 2.10.3.2 / Swiss Ephemeris

- 来源：https://github.com/astrorigin/pyswisseph ，https://www.astro.com/swisseph/ 。
- Python 包许可证全文保留于 `vendor/pyswisseph-LICENSE.txt`；使用前也应核对 Swiss Ephemeris 自身许可与商业许可选项。
- 星位使用 Swiss Ephemeris 内置 Moshier 算法，**未下载／使用原项目的外部星历文件，不声称逐位完全相同**。
- 此版本界面支持公历 1800—2199 年、Lahiri/Raman/Krishnamurti、整宫／上升等宫、平／真交点。极高纬度或时间边界仍需复核。
- 标准分盘采用上游 20 种定义（D1、D2、D3、D4、D5、D6、D7、D8、D9、D10、D11、D12、D16、D20、D24、D27、D30、D40、D45、D60），**不是 D1 至 D60 每一个整数都实现**。暂未接入原项目其余全部岁差、分盘变体、Yoga、Shadbala 和推运体系。

## 构建、运行与数据

- 用 Node.js 18+ 运行预先生成的本地中国术数内核；无需 Java、上游完整应用或外部排盘 API。
- 重建：`npm ci --ignore-scripts --cache .npm-cache`，然后 `npm run build:charts`。
- 印占依赖：用启动网站的 Python 执行 `python -m pip install -r requirements-charts.txt`。
- 经纬度采用手填或内置城市中心点；不调用地图，不自动推断历史夏令时。用户需确认出生当时 UTC 偏移。
- 排盘与三份结构化模板不发模型请求、不自动保存生辰。主动保存历史后，命盘、模板与计算选项随案例保存在本机。三次独立AI解读每次将对应体系模板发送到配置的模型；生成报告后可显式送入文章模式交叉分析／追问。原始命盘不直接用于交叉分析。
- 单元测试只用合成生辰与模拟模型，没有使用用户案例或真实 API Key。通过测试不等于所有流派、所有日期已获独立权威校验，也不证明预测有效。
