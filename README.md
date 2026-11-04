# 排盘服务（Chart Service）

命理研究工作台的排盘部分，以 AGPL-3.0 开源。提供八字、紫微斗数和印度占星（含 Vimshottari 运期与行运表）的结构化排盘，通过 HTTP 返回 JSON。全部在本机计算，不调用任何模型或外部网络。

## 运行

需要 Python 3 和 Node.js（八字与紫微排盘由打包好的 `engine/vendor/chart-engine.cjs` 执行）。

```
pip install -r requirements.txt
python -X utf8 server.py
```

服务默认只监听 `127.0.0.1:8095`。可用的环境变量：

- `CHART_PORT`：监听端口。
- `CHART_SERVICE_TOKEN`：共享口令，调用方需要在请求头 `X-Chart-Token` 里带上。
- `CHART_SOURCE_URL`：本源代码的公开地址，会通过 `/v1/source` 返回。

## 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/v1/health` | 引擎是否可用 |
| GET | `/v1/source` | 许可证和源代码地址 |
| POST | `/v1/charts` | 出生资料 → 完整盘面（含三套盘的文字模板） |
| POST | `/v1/normalize` | 出生资料 → 规范化后的输入 |
| POST | `/v1/transits` | `{"chart_input": …}` → 印占行运表文字 |

出生资料无效时返回 400 `{"error", "field"}`，引擎出错时返回 503。

## 许可

- 本服务整体按 AGPL-3.0-only 发布，全文见 `LICENSE`。
- `engine/vedic_rules.py` 的部分规则参考了 horosa（AGPL-3.0），详见 `engine/THIRD_PARTY_NOTICES.md` 和 `engine/vendor/horosa/`。
- 农历与八字基础算法来自 lunar-javascript（MIT），印占星位使用 pyswisseph / Swiss Ephemeris（AGPL 或商业授权），许可文本都在 `engine/vendor/` 中。
- 对上游代码的改动见 `engine/THIRD_PARTY_NOTICES.md`。

本包导出于 2026-11-04。
