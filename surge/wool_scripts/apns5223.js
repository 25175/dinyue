/*
 * APNs 5223 连通性检测（Surge [Script] type=generic，cron 每 10 分钟）
 * 仓库: https://github.com/25175/dinyue  路径: surge/wool_scripts/apns5223.js
 *
 * 原理：Surge 脚本 API 无原生 TCP 探测，这里用 HTTP 客户端向 APNs 的 5223 端口
 * 发起请求，依据 TCP 语义判定可达性：
 *   - 连接被拒/无法路由/被重置          → 端口不可达（判定 5223 被阻断）
 *   - 连接已建立但没有 HTTP 响应（超时） → 端口可达（APNs 不讲 HTTP，属正常）
 * 流量按当前 [Rule] 落到「Apple 通知」策略组，因此结果同时反映该组出口可用性。
 */

const APNS_HOSTS = ['17.57.145.25', '17.252.9.32'];
const PORT = 5223;
const TIMEOUT_MS = 8000;

function probe(ip) {
  return new Promise((resolve) => {
    const started = Date.now();
    $httpClient.get({ url: `http://${ip}:${PORT}/`, timeout: TIMEOUT_MS }, (error, response) => {
      const ms = Date.now() - started;
      if (error) {
        const msg = String(error).toLowerCase();
        const blocked = /refused|unreachable|reset|failed to connect|could not connect|network is down/.test(msg)
          && !/timeout|timed out/.test(msg);
        resolve({ ip, ok: !blocked, ms, detail: String(error) });
      } else {
        resolve({ ip, ok: true, ms, detail: `HTTP ${response ? response.status : '?'}` });
      }
    });
  });
}

!(async () => {
  const results = await Promise.all(APNS_HOSTS.map((ip) => probe(ip)));
  const okCount = results.filter((r) => r.ok).length;
  const title = okCount === results.length
    ? 'APNs 5223 正常'
    : okCount === 0
      ? 'APNs 5223 全部不可达'
      : 'APNs 5223 部分不可达';
  const body = results
    .map((r) => `${r.ok ? '✅' : '❌'} ${r.ip}:${PORT}  ${r.ms}ms  ${r.detail}`)
    .join('\n');
  const stamp = new Date().toLocaleString('zh-CN', { hour12: false });
  console.log(`${title}\n${body}\n${stamp}`);
  $notification.post('APNs5223检测', title, `${body}\n${stamp}`);
  $done({});
})().catch((e) => {
  console.log(`APNs5223检测 脚本异常: ${e}`);
  $notification.post('APNs5223检测', '脚本异常', String(e));
  $done({});
});
