# Task 1

Write the "Rate limiting" section for the README.md of our HTTP API. Use these notes:

- 120 req/min per API key
- burst: up to 20 extra requests in any 10 s window
- over the limit -> HTTP 429 + `Retry-After` header (seconds)
- rolling 60 s window, NOT reset at the top of the minute
- every response has `X-RateLimit-Remaining`
- Enterprise plan: 600 req/min
- `/v1/batch`: each item counts as 1 request, max 50 items per call
- 3x 429 within 5 min => key blocked for 15 min
- higher limits: support@example.com

# Task 2

Add comments to this file: one doc comment for the function, and inline comments where they help. Explain what the code does and why. Do not change the code. Give me the full file.

```ts
const MAX_ATTEMPTS = 5
const BASE_DELAY_MS = 200
const MAX_DELAY_MS = 5000

export async function fetchWithRetry(url: string, init: RequestInit = {}): Promise<Response> {
  let lastError: unknown

  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    if (init.signal?.aborted) {
      throw new DOMException('Aborted', 'AbortError')
    }

    try {
      const response = await fetch(url, init)

      if (response.ok) {
        return response
      }

      if (response.status < 500 && response.status !== 429) {
        return response
      }

      lastError = new Error(`HTTP ${response.status}`)
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw error
      }

      lastError = error
    }

    const delay = Math.min(BASE_DELAY_MS * 2 ** attempt, MAX_DELAY_MS) + Math.random() * 100
    await new Promise(function wait(resolve) {
      setTimeout(resolve, delay)
    })
  }

  throw lastError
}
```

# Task 3

Write the commit message and the PR description for this change. Notes:

- bug: CSV export dropped rows when a cell had a newline inside quotes
- cause: we split the file on "\n" before we parsed the quotes
- fix: `exportRows()` now uses the streaming parser `csv-parse` 5.5
- added 3 tests
- perf: export of 10,000 rows takes 1.8 s now, 1.2 s before. slower but ok
- no breaking changes
- same bug is still in `importRows()`, ticket EXP-412, NOT fixed in this PR
- needs Node 18 or newer

# Task 4

why my react list re-render all items when i type in the search box? it is slow with 2000 items

(This is what you found in the code. Use it in your answer.)

- `SearchPage` keeps `query` in state, so each key press renders `SearchPage` again
- `items.filter(...)` runs on every render
- `<Row>` is not memoized
- `onSelect={(id) => select(id)}` is an inline arrow function: a new function on every render, so `React.memo` on `Row` alone would not help
- fixes: `useDeferredValue(query)` (or debounce 300 ms); `React.memo(Row)` together with `useCallback` for `onSelect`; `useMemo` for the filtered list
- with 2000 rows: virtualize with `react-window`, so only about 20 rows are in the DOM

# Task 5

I got this email from my bank. Can you explain what it means and what I must do?

> Dear Customer,
>
> As part of our periodic review, and in line with regulatory requirements, we are required to refresh the information we hold on file for you. Our records indicate that your proof of address is no longer current.
>
> To avoid any disruption to your account, kindly furnish a valid proof of address no later than 15 December 2026. Acceptable documents include a utility bill or a bank statement issued within the last three months. Documents may be uploaded via the secure portal or handed in at any branch.
>
> Should we not hear from you by the above date, outgoing transfers will be capped at USD 500 per day until the matter is resolved. Rest assured that incoming payments and card purchases will not be affected, and there is no fee for this process.
>
> Please note that we will never ask you to disclose your PIN or password. If in doubt, call the number on the back of your card.
>
> Yours faithfully,
> Customer Due Diligence Team
