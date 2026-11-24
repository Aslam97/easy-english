# Task 6

Write the status update for my team from my notes. It goes into our team channel.

- finally landed the retry fix, it's gated behind `RETRY_V2` (off in prod for now)
- root cause: the token cache was stale after a deploy, so the auth middleware would bail out early and swallow the 401
- hoisted the cache config into `config/cache.ts` so both call sites stay in lockstep
- wired up a health check that surfaces the cache age on `/healthz`
- sanity-checked on staging: 0 errors in 2 h. blast radius is small, only the EU region uses this path
- footgun: `CACHE_TTL` is in seconds in one place and in ms in another. papered over with a conversion for now, the real fix is ticket AUTH-88
- next: flip the flag for 10% of prod traffic on Monday, bump to 100% by Friday if the error rate stays under 0.1%

# Task 7

Review this diff. Tell me the problems and how to fix each one. Note: `audit.log()` returns a Promise.

```diff
--- a/src/api/orders.ts
+++ b/src/api/orders.ts
@@ -12,6 +12,18 @@
 export async function getOrders(req: Request, res: Response) {
-  const orders = await db.query('SELECT * FROM orders WHERE user_id = $1', [req.user.id])
-  res.json(orders)
+  const status = req.query.status
+  const cacheKey = `orders:${status}`
+  const cached = cache.get(cacheKey)
+  if (cached) {
+    return res.json(cached)
+  }
+
+  const orders = await db.query(
+    `SELECT * FROM orders WHERE user_id = ${req.user.id} AND status = '${status}'`
+  )
+  cache.set(cacheKey, orders, 300)
+  audit.log('orders.read', req.user.id)
+  res.json(orders)
 }
```
