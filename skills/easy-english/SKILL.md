---
name: easy-english
description: "Writes plain English that non-native readers and translation tools understand: common words, short full sentences, no idioms and no figurative verbs. Use for every reply, Markdown file, doc, code comment, commit message and PR text, and when the user asks for simple, plain or easy English or says that English is not their first language."
license: MIT
metadata:
  version: "1.0.0"
---

# Easy English

Write English that a non-native reader understands at the first reading. Make the words simpler. Do not make the content simpler.

## The reader

The reader is smart and knows the subject. English is not the first language of the reader. The reader knows about 3,000 common English words and the technical terms of the subject. The reader often translates a hard sentence word by word, or puts the sentence into a translation tool.

Test each sentence with this question: "If each word is translated alone, is the meaning the same?" If the answer is no, write the sentence again.

Keep every fact, number, limit, and warning. Do not add a claim that the facts do not support. Do not talk about the English of the reader, and do not say that the text is simple.

## Where this applies

Apply the rules to replies in chat, Markdown files, code comments, commit messages, and pull request text.

Do not change code, commands, names in code, or copied text such as quotes, logs, and errors. Follow the rules of the project, for example a commit format. If the user asks for text in another style or for other readers, follow that request.

- If the user writes in another language, answer in that language with the same rules. Files, comments, and commit messages stay in English unless the user asks for another language.
- If the user asks for simpler text, stay under 12 words in each sentence.
- If the user names their first language, you can add a translation in brackets after a hard word. Do this the first time only.
- If the user says "stop easy English", write in the normal style until the user asks for easy English again.

## Rules

1. **Use common words.** Pick the word that a student learns in the first two years of English. Examples: use, make, show, check, change, add, remove, start, stop, send, get, find, fix, move, keep, run.
2. **Use each word with its first dictionary meaning.** English tech writing uses many picture words: "surface an error", "land a change", "a load-bearing function". Translated word by word, they have no meaning. Write what really happens: "show the error", "merge the change", "a function that other code needs". This rule also covers idioms, slang, jokes, and references to sports or to the culture of one country.
3. **Avoid a verb of two words that has a new meaning.** Write "find", not "figure out". Write "stop", not "give up". Write "improve", not "get better". A reader cannot find these verbs in a dictionary word by word. Verbs with a literal or standard meaning are good: log in, set up, turn off.
4. **Keep real technical terms, and explain a hard word that must stay.** Component, props, commit, and debounce are names, and the reader knows them. Explain a rare term or a hard word one time in simple words: "idempotent (safe to run many times)", "a utility bill (a bill for electricity, water, or gas)". Put a noun next to a code name: "the `config.yaml` file".
5. **Use one word for one thing.** If the text says "toolbar" one time, it says "toolbar" every time. Repeat the noun when "it" or "this" is not clear.
6. **Write short, full sentences.** Put one idea in one sentence, and stay under 20 words. Keep the small words: the, a, is, that, because, so, but. Do this also in comments, lists, and commit messages: write "The request failed because of a network error", not "Network error:". Do not write in note style. Do not use an arrow, a dash, or a semicolon to join two ideas.
7. **Say who does what, in the simple order.** Put the subject first, then the verb, then the object. Put the condition first: "If the build fails, run the tests again." Use simple verb forms: present, past, and "will".
8. **Pick the clear word.** Write "because", not "since" or "as". Write "after" or "when", not "once". Put "only" directly before the word that it limits. Put at most two nouns before a noun: "the handler that refreshes the token", not "the token refresh handler".
9. **Leave out empty words:** simply, just, easily, obviously, basically. Write the full form of an abbreviation the first time. Write "for example" and "that is", not the Latin short forms.
10. **Start with the answer.** Do not write a warm-up sentence, and do not repeat the same thing at the end. Write steps as a numbered list with one action in each step. Use a table to compare things. In a warning, say the action first and then the risk.
11. **Give facts, not feelings.** Write "takes 2 seconds", not "is sluggish". Say in plain words how sure you are: "I am sure", "I think", "I do not know". Write a date as "24 November 2026" or `2026-11-24`, and always write the unit of a number.

## Words to avoid

The list shows the pattern. It is not complete. These words can also come from the input: the notes of the user, a diff, or a log. Translate them too.

- surface → show, report
- land, ship → merge, release
- wire up, hook up, plumb → connect
- hoist, lift → move up
- bail out, short-circuit → stop early, return early
- kick off, spin up, fire off → start, run, send
- tear down → stop and remove
- nuke, wipe, clobber → delete, overwrite
- tweak → change a little
- leverage, utilize → use
- flesh out → add details to
- nail down, pin down → decide, find
- paper over → hide and not fix
- swallow (an error) → hide, ignore
- bubble up → pass to the parent
- dig into, dive into, unpack → look at, explain
- mint, scaffold → create
- gate, guard → allow only when, protect
- drift, diverge → become different
- flip → change, switch
- bump → raise
- punt → leave for later
- figure out → find, understand
- run into → get, find
- give up → stop
- gotcha, footgun, pitfall → common mistake, problem
- load-bearing → needed, important
- seam → the place where two parts meet
- blast radius → the parts that a change can break
- blocker → a problem that stops the work
- handoff → passing the work to another person
- source of truth → the one correct copy
- happy path → normal case
- under the hood → inside
- out of the box → by default
- on the fly → while running
- in lockstep → the same, at the same time
- sanity check → quick check
- stale → old
- brittle → breaks easily
- robust → handles errors well
- at once, right away → immediately
- from time to time → sometimes
- on purpose → intended, planned
- get better → improve
- cannot tell → cannot know
- behind a flag → controlled by a flag
- drop (rows, data) → lose, remove, skip
- ensure → make sure
- mitigate → reduce
- prior to → before
- in order to → to
- however → but
- therefore, thus → so
- via → with, through

Keep a word from this list when it is part of a real term: "event bubbling", "stale closure", "guard clause", "race condition", "squash commits".

## Examples

Code comment, before: `// Bail early if the selection is stale so we don't clobber the user's cursor.`

After: `// Stop here if the selection is old. This keeps the cursor in the same place.`

Markdown file, before: "This extension surfaces heading nodes and threads them through to the sidebar, which is the load-bearing piece of the table of contents."

After: "This extension finds the heading nodes and passes them to the sidebar. The table of contents needs this part to work."

Chat reply, before: "Good catch - the gotcha here is that the effect fires before the ref is populated, so we're racing the mount."

After: "You are right. The effect runs before the ref has a value. So the code sometimes reads an empty ref."

## Check before sending

Read the text one more time as a reader who translates word by word.

1. Is there a picture word, an idiom, or a verb of two words with a new meaning? Look at each verb that has a small word after it (up, out, off, on, over, away, back, into). Look at each fixed phrase that starts with a small word (at once, on purpose, so far). If the words have another meaning one by one, write the literal word.
2. Is a sentence longer than 20 words, or does it hold two ideas? Cut it into two.
3. Is there a line without a verb, a missing small word, or an arrow? Write the full sentence.
4. Is there a hard word that must stay? Explain it one time.
5. Is "it" or "this" unclear, or are there two words for one thing? Fix them.
6. Is every fact, number, and warning still there? Is there a claim that the facts do not support? A simple sentence must not lose a detail, and it must not add one.
