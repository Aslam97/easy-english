// Maximum number of tries, including the first one.
const MAX_ATTEMPTS = 5
// Delay before the first retry. It doubles after each failed attempt.
const BASE_DELAY_MS = 200
// Upper limit for the exponential delay, so waits never grow too long.
const MAX_DELAY_MS = 5000

/**
 * Fetches a URL and retries when the failure is probably temporary.
 *
 * Retries happen on network errors, on 5xx responses, and on 429 (rate limit).
 * Other responses are returned right away, including 4xx errors such as 404,
 * because repeating the same request would give the same result.
 * The wait between tries grows exponentially (200 ms, 400 ms, 800 ms, ...)
 * up to MAX_DELAY_MS, with a small random extra time (jitter).
 *
 * If the request is aborted through `init.signal`, the AbortError is thrown
 * at once and no retry is made.
 *
 * @param url - The URL to request.
 * @param init - Normal `fetch` options, including an optional AbortSignal.
 * @returns The first response that is successful or not worth retrying.
 * @throws The last error (network error or `HTTP <status>`) after all
 *   attempts fail, or an AbortError if the request is aborted.
 */
export async function fetchWithRetry(url: string, init: RequestInit = {}): Promise<Response> {
  // Keeps the most recent failure so we can throw it after the last attempt.
  let lastError: unknown

  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    // Check the signal before each attempt. Without this, an abort that
    // happens during the delay below would still start a new request.
    if (init.signal?.aborted) {
      throw new DOMException('Aborted', 'AbortError')
    }

    try {
      const response = await fetch(url, init)

      // Success: return it.
      if (response.ok) {
        return response
      }

      // Client errors (4xx) will not fix themselves, so do not retry them.
      // 429 is the exception: it means "try again later".
      if (response.status < 500 && response.status !== 429) {
        return response
      }

      // 5xx or 429: remember the error and go to the retry delay.
      lastError = new Error(`HTTP ${response.status}`)
    } catch (error) {
      // The caller canceled the request on purpose. Do not retry.
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw error
      }

      // Other errors, such as network failures, may be temporary. Retry.
      lastError = error
    }

    // Exponential backoff: 200, 400, 800, ... capped at MAX_DELAY_MS.
    // The random 0-100 ms jitter stops many clients from retrying at the
    // same moment and hitting the server together.
    const delay = Math.min(BASE_DELAY_MS * 2 ** attempt, MAX_DELAY_MS) + Math.random() * 100
    await new Promise(function wait(resolve) {
      setTimeout(resolve, delay)
    })
  }

  // All attempts failed. Throw the last error so the caller can see the cause.
  throw lastError
}
