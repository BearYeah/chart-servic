// JSON-only stdin/stdout bridge. No network, eval, shell, credentials or logging of birth data.
const fs = require('node:fs');
try {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const { calculateChineseCharts } = require('./vendor/chart-engine.cjs');
  process.stdout.write(JSON.stringify(calculateChineseCharts(input)));
} catch (error) {
  process.stderr.write(`Chart calculation failed: ${error.message}`);
  process.exitCode = 1;
}
