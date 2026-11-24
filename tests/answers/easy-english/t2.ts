// The most times that we send the request, including the first try.
const MAX_ATTEMPTS = 5
// The wait time after the first failed try. The wait time doubles after each failed try.
const BASE_DELAY_MS = 200
// The longest wait time between two tries, before we add the random part.
const MAX_DELAY_MS = 5000

/**
 * Sends a request with `fetch` and tries again when the request fails for a reason that can pass.
 *
 * The function tries again when the network fails, when the server returns a status of 500 or more,
 * or when the server returns 429 (too many requests). It waits longer after each failed try.
 * This gives the server time to get better.
 *
 * The function returns a response that is ok. It also returns a response with another status
 * below 500, for example 404, because a new try will not change that answer.
 *
 * @param url The address to request.
 * @param init The options for `fetch`. If `init.signal` is aborted, the function stops immediately.
 * @returns The first response that is ok or that is not worth a new try.
 * @throws The `AbortError` if the signal is aborted. Otherwise it throws the error of the last try
 * after all tries fail.
 */
export async function fetchWithRetry(url: string, init: RequestInit = {}): Promise<Response> {
  // We keep the error of the last try, so we can throw it when all tries fail.
  let lastError: unknown

  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    // Check the signal before each try. If the caller aborted during a wait, we do not send a new request.
    if (init.signal?.aborted) {
      throw new DOMException('Aborted', 'AbortError')
    }

    try {
      const response = await fetch(url, init)

      if (response.ok) {
        return response
      }

      // A status below 500 is an error of the client, for example 400 or 404.
      // A new try gives the same answer, so we return the response to the caller.
      // The status 429 is the exception, because the server asks us to try later.
      if (response.status < 500 && response.status !== 429) {
        return response
      }

      // The status is 500 or more, or it is 429. We save an error and try again after a wait.
      lastError = new Error(`HTTP ${response.status}`)
    } catch (error) {
      // The caller aborted the request on purpose. We do not try again, so we throw the error now.
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw error
      }

      // The error is probably a network error. We save it and try again after a wait.
      lastError = error
    }

    // The wait time doubles after each try: 200 ms, 400 ms, 800 ms, and so on, up to 5000 ms.
    // The random part of up to 100 ms stops many clients from sending their new requests at the same time.
    const delay = Math.min(BASE_DELAY_MS * 2 ** attempt, MAX_DELAY_MS) + Math.random() * 100
    await new Promise(function wait(resolve) {
      setTimeout(resolve, delay)
    })
  }

  // All tries failed, so we throw the error of the last try.
  throw lastError
}
