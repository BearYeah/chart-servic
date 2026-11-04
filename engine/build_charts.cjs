const esbuild = require('esbuild');
const path = require('node:path');
require('./verify_chart_sources.cjs');
esbuild.buildSync({
  entryPoints: [path.join(__dirname, 'chart_entry.js')],
  outfile: path.join(__dirname, 'vendor', 'chart-engine.cjs'),
  bundle: true, platform: 'node', format: 'cjs', target: 'node18',
  banner: { js: '// Horosa-derived chart engine — AGPL-3.0-only. See THIRD_PARTY_NOTICES.md and vendor/horosa/LICENSE.\n// Includes lunar-javascript (MIT). Rebuild: npm ci --ignore-scripts && npm run build:charts' },
  legalComments: 'inline',
});
console.log('Chart engine bundled. Source modules retained in vendor/horosa.');
