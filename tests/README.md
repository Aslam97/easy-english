# Test of the skill

This folder holds a small test of the easy-english skill. It also holds the tasks and the script, so you can run the test again.

## Method

1. A user gives 7 writing tasks. The tasks are in the folder [`tasks`](tasks).
2. Each skill writes its answers in a new session of Claude Sonnet. The session knows only the skill and the tasks.
3. The script [`score.py`](score.py) counts rare words, long sentences, and the facts that each answer keeps.
4. A separate session reads all answers under random file names. It lists each hard word and each hard sentence for a reader who knows about 3,000 English words.

The tasks:

| Task | Kind of text |
|---|---|
| 1 | A README section from short notes |
| 2 | Comments for a TypeScript function |
| 3 | A commit message and a pull request text |
| 4 | A chat reply about a slow React list |
| 5 | A chat reply that explains a formal email from a bank |
| 6 | A status update from notes with a lot of slang |
| 7 | A review of a diff with several problems |

## Results

The numbers are the problems that the blind reviewer found: hard words plus hard sentences. Lower is better.

Compare the numbers only inside one column. Each round had its own reviewer session, and the reviewer of round 2 was stricter.

| Skill | Size in tokens | Round 1, tasks 1 to 5 | Round 2, tasks 1 to 5 | Round 2, tasks 6 and 7 |
|---|---|---|---|---|
| No skill | 0 | 48 | not tested | not tested |
| [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) 2.1.2 | 2,000 | 17 | not tested | 12 |
| [english-is-my-second-language](https://github.com/BasmaAbouzied0/english-is-my-second-language) | 1,100 | 10 | 19 | 7 |
| An older, longer version of this skill | 3,500 | 9 | 17 | 5 |
| This skill in 10 lines | 350 | 7 | not tested | 7 |
| This skill | 2,200 | not tested | 10 | 6 |

The script found that every skill kept every fact of the tasks.

## What the test shows

- Every skill of this kind helps a lot. The problems went from 48 to between 7 and 17.
- A longer skill is not better. A version of this skill with 10 lines was almost as good as a version with 3,500 tokens. So this skill is now shorter.
- The word list helps when the input has slang. In task 6, the versions with the word list replaced all slang words.
- The other skills have other goals. SimpleEnglish is made for exact technical documents, and this test does not measure that.

## Limits

- Each skill ran one time, on one model. A second run can give other numbers.
- The reviewer is also a language model. A human reader can have another opinion.
- The author of this skill wrote the tasks.
- The test sessions had a saved user preference for simple English in their context. Each session was told to ignore it. So the result for "no skill" is maybe better than in normal use.
- english-is-my-second-language had fewer hard words than this skill in round 2 (4 and 7). It had more hard sentences (15 and 3).
- The answers in [`answers/easy-english`](answers/easy-english) come from the version before the last three small changes. The last changes are a check for small idioms, five new words in the list, and one more example.

## Run the script

```bash
pip install wordfreq
python3 tests/score.py tests/answers
```

The script prints one line for each folder in `tests/answers`. To test another skill, add a folder with its answers (`t1.md`, `t2.ts`, `t3.md`, and so on).
