# easy-english

A skill for coding assistants. With this skill, the assistant writes English that non-native readers understand at the first reading.

The content stays the same. Only the words and the sentences get simpler.

## The problem

Coding assistants write good English. But good English is hard when English is your second language. It is full of picture words, idioms, and long sentences:

> Bail early if the selection is stale so we don't clobber the user's cursor.

If you translate this sentence word by word, it has no meaning. With this skill, the assistant writes:

> Stop here if the selection is old. This keeps the cursor in the same place.

More examples:

| Normal | With easy-english |
|---|---|
| This extension surfaces heading nodes and threads them through to the sidebar, which is the load-bearing piece of the table of contents. | This extension finds the heading nodes and passes them to the sidebar. The table of contents needs this part to work. |
| Good catch - the gotcha here is that the effect fires before the ref is populated, so we're racing the mount. | You are right. The effect runs before the ref has a value. So the code sometimes reads an empty ref. |

## What the skill does

- It uses common words. The reader needs about 3,000 English words and the technical terms of the subject.
- It replaces picture words, idioms, and verbs of two words that have a new meaning. The skill has a list of more than 55 such words, for example "surface", "wire up", and "load-bearing".
- It writes short, full sentences with one idea in each sentence.
- It keeps real technical terms, and it explains a hard word that must stay.
- It keeps every fact, number, and warning.
- It works in replies, Markdown files, code comments, commit messages, and pull request text.
- It does not change code, commands, or copied text.

The full rules are in [`skills/easy-english/SKILL.md`](skills/easy-english/SKILL.md).

## Install

### With the skills CLI

The [skills CLI](https://github.com/vercel-labs/skills) works with Claude Code, Codex, Cursor, OpenCode, and many other tools.

```bash
npx skills add Aslam97/easy-english
```

This command installs the skill into the current project. To install the skill for all your projects, add `-g`:

```bash
npx skills add Aslam97/easy-english -g
```

### By hand in Claude Code

```bash
git clone https://github.com/Aslam97/easy-english.git
mkdir -p ~/.claude/skills
cp -r easy-english/skills/easy-english ~/.claude/skills/
```

For one project only, copy the folder to `.claude/skills/` in that project.

### In the Claude app

1. Download this repository.
2. Make a ZIP file of the folder `skills/easy-english`.
3. In the app, open **Customize > Skills**.
4. Choose **Upload a skill** and select the ZIP file.

These steps can change. The help page [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) has the current steps.

### In other tools

Some tools have no skills. For such a tool, copy the text of [`SKILL.md`](skills/easy-english/SKILL.md) into its instruction file, for example `AGENTS.md`.

## Use

The assistant loads the skill when the skill fits the task. You can also ask for it:

- "Use easy English."
- "English is not my first language."

More options:

| You say | The skill does |
|---|---|
| "Simpler, please." | It writes sentences with fewer than 12 words. |
| "My first language is Indonesian." | It can add a translation after a hard word, one time. |
| "Stop easy English." | It writes in the normal style again. |

If you write in another language, the assistant answers in that language with the same rules.

## Make it always on

An assistant does not load a skill in every session. If you want the rules in every session, add these lines to your instruction file. In Claude Code this file is `CLAUDE.md`. Many other tools use `AGENTS.md`.

```markdown
## Writing style: easy English

English is not my first language. Use the easy-english skill for all text:
replies, Markdown files, code comments, commit messages, and PR text.

- Use common words. Keep real technical terms.
- No idioms and no picture words. Write "show", not "surface". Write "connect", not "wire up".
- Write short, full sentences. Put one idea in one sentence.
- Keep all facts, numbers, and warnings.
```

## Where the rules come from

The rules follow guides and research about writing for readers in all countries:

- [Google developer documentation style guide: Write for a global audience](https://developers.google.com/style/translation)
- [Microsoft Writing Style Guide: Writing tips for global content](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips)
- [ASD-STE100 Simplified Technical English](https://asd-ste100.org/about_STE.html), a standard for aircraft manuals
- [ISO 24495-1:2023 Plain language](https://www.iso.org/standard/78907.html)
- [New General Service List](https://www.newgeneralservicelist.com/new-general-service-list), a list of about 2,800 common English words
- [Schmitt et al. (2011)](https://www.lextutor.ca/cover/papers/schmitt_etal_2011.pdf), a study about the share of words that a reader must know
- [claudeisms](https://github.com/archiewood/claudeisms), a count of words that one coding assistant uses very often

## Test

The test has 7 writing tasks. Examples are a README section, code comments, a commit message, and a code review. Each skill wrote its answers in a new session. A separate session judged all answers and did not know which skill wrote them.

- With no skill, the reviewer found 48 reading problems in 5 tasks. With a skill, the reviewer found between 7 and 17.
- In round 2, this skill had 10 problems in the 5 main tasks. An older version of this skill had 17, and english-is-my-second-language had 19.
- The differences between the skills are small.
- No skill lost a fact from the tasks.

The test is small: one run for each skill, on one model. The method, the numbers, and the limits are in [`tests/README.md`](tests/README.md).

## Similar skills

- [english-is-my-second-language](https://github.com/BasmaAbouzied0/english-is-my-second-language) has the same goal and fewer rules. Two ideas in this skill come from it. One idea is the phrase that turns the skill off. The other idea is the translation into the first language of the reader.
- [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) follows the standard ASD-STE100. It is a good choice for exact technical documents.

## Contribute

Did your assistant write a sentence that is hard to read? Open an issue and paste the sentence. Hard words from issues go into the word list of the skill.

## License

[MIT](LICENSE)
