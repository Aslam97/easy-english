"""Score the answers of one test round.

Usage: python3 tests/score.py tests/answers

The folder holds one folder for each skill (for example "no-skill").
Each of these folders holds the answers: t1.md, t2.ts, t3.md, and so on.
The script needs the wordfreq package: pip install wordfreq

The script measures what a reader sees:
- rare words that the writer added (not in the task text, not code)
- sentence length
- words from the avoid list of this skill (the list is ours, so this
  number favours this skill)
- dashes, semicolons and arrows that join ideas
- facts from the task that are still in the answer
"""

import json
import re
import sys
from pathlib import Path

from wordfreq import zipf_frequency

# Single words get the endings s / es / ed / d / ing. Phrases match as written.
AVOID_WORDS = [
    "surface", "land", "ship", "plumb", "hoist", "lift", "bail", "nuke",
    "wipe", "clobber", "tweak", "massage", "leverage", "utilize", "swallow",
    "unpack", "mint", "gate", "funnel", "route", "reconcile", "ensure",
    "mitigate", "encounter", "gotcha", "footgun", "pitfall", "brittle",
    "fragile", "robust", "stale", "caveat", "straightforward", "subsequently",
    "however", "nevertheless", "therefore", "thus", "hence", "additionally",
    "furthermore", "approximately", "sufficient", "via",
    # added after the research
    "scaffold", "populate", "guard", "mirror", "flip", "drift", "diverge",
    "probe", "squash", "grab", "bump", "punt", "seam", "blocker", "handoff",
    "verdict", "parity", "knob", "cruft", "substrate", "cleanly", "silently",
    "transient", "canonical", "authoritative", "verbatim", "decisive",
    "pre-existing", "dedup", "prod", "repro", "settle", "kill",
    "simply", "just", "easily", "obviously", "basically", "since", "once",
]
AVOID_PHRASES = [
    "wire up", "wired up", "wiring up", "hook up", "hooked up",
    "thread through", "threads through", "threaded through", "threads them through",
    "bail out", "short-circuit", "short circuit", "kick off", "kicks off",
    "spin up", "spins up", "fire off", "fires off", "tear down", "tears down",
    "blow away", "flesh out", "nail down", "pin down", "paper over",
    "papers over", "bubble up", "bubbles up", "delve into", "dive into",
    "dig into", "stamp out", "sharp edge", "load-bearing", "happy path",
    "under the hood", "out of the box", "on the fly", "sanity check",
    "prior to", "in order to", "e.g.", "i.e.",
    "tighten up", "pull in", "lean on", "blow up", "choke on", "push back",
    "figure out", "run into", "rule out", "blast radius", "source of truth",
    "escape hatch", "yak shaving", "belt and suspenders", "in lockstep",
    "key insight", "good catch", "etc.", "of course",
]
# Real technical terms that contain a word from the list.
ALLOWED_PHRASES = ["stale closure", "event bubbling", "guard clause", "race condition", "squash commits"]


IRREGULAR = {"hid": "hide", "sent": "send", "ran": "run", "kept": "keep",
             "wrote": "write", "written": "write", "found": "find"}


def base_forms(word: str) -> list[str]:
    """Return the word and its possible base forms (clicks -> click)."""
    word = re.sub(r"'s$", "", word)
    forms = [word, IRREGULAR.get(word, word)]
    for ending in ("s", "es", "d", "ed", "ing"):
        if word.endswith(ending) and len(word) > len(ending) + 2:
            stem = word[: -len(ending)]
            forms += [stem, stem + "e"]
            if len(stem) > 2 and stem[-1] == stem[-2]:
                forms.append(stem[:-1])  # stopped -> stop
    return forms



BENCH = Path(__file__).parent
RARE_BELOW = 4.0
MAX_WORDS = 20

DEV_WORDS = {
    "endpoint", "endpoints", "parser", "timeout", "backend", "frontend",
    "config", "runtime", "async", "boolean", "codebase", "repo", "regex",
    "payload", "middleware", "callback", "callbacks", "dataset", "plugin",
    "username", "login", "upload", "uploads", "download", "website", "online",
    "email", "app", "database", "server", "client", "browser", "keyboard",
    "url", "json", "http", "api", "css", "html", "sdk", "cli", "id", "ok",
    "readme", "markdown", "retry", "retries", "memoize", "memoized",
    "memoization", "debounce", "debounced", "render", "renders", "rerender",
    "virtualize", "virtualization", "dom", "csv", "pr", "commit", "node",
    "react", "jitter", "backoff", "abort", "aborted", "aborts", "param",
    "params", "props", "prop", "hook", "hooks", "inline", "pin", "usd",
    "cache", "cached", "caches", "deploy", "deploys", "deployed", "staging",
    "prod", "auth", "token", "tokens", "sql", "query", "queries", "diff",
    "unhandled", "undefined", "ttl", "config", "healthz",
}

SLANG_T6 = ["landed", "gated", "stale", "bail", "swallow", "hoist", "lockstep", "wired",
            "surfaces", "sanity", "blast radius", "footgun", "papered", "flip", "bump", "call sites"]

FACTS = {
    "t6": [
        ("flag RETRY_V2", r"RETRY_V2"),
        ("flag is off in production", r"\boff\b|disabled|not (yet )?(on|active|enabled)|turned off"),
        ("token cache was old after a deploy", r"cache"),
        ("401 was hidden", r"\b401\b"),
        ("config moved to config/cache.ts", r"config/cache\.ts"),
        ("health check /healthz", r"/healthz"),
        ("staging: 0 errors in 2 hours", r"\b(0|zero|no) errors"),
        ("2 hours", r"\b(2|two)[ -]?(h\b|hours)"),
        ("only the EU region", r"\bEU\b"),
        ("CACHE_TTL seconds and ms", r"CACHE_TTL"),
        ("ticket AUTH-88", r"AUTH-88"),
        ("10% on Monday", r"10 ?%"),
        ("Monday", r"Monday"),
        ("100% by Friday", r"100 ?%"),
        ("Friday", r"Friday"),
        ("error rate under 0.1%", r"0\.1 ?%"),
    ],
    "t7": [
        ("SQL injection", r"injection|parameter|placeholder|\$1"),
        ("cache key has no user id", r"cache key|cacheKey"),
        ("other users see the data", r"other user|another user|different user|wrong user|all users|every user|user A"),
        ("audit.log promise not awaited", r"await|\.catch|unhandled|reject"),
        ("status can be undefined", r"undefined|missing|not set|no status|empty"),
    ],
    "t1": [
        ("120 per minute", r"\b120\b"),
        ("burst of 20", r"\b20\b"),
        ("10 second window", r"\b10[ -]?(s\b|sec|second)"),
        ("HTTP 429", r"\b429\b"),
        ("Retry-After header", r"Retry-After"),
        ("60 seconds", r"\b60\b"),
        ("rolling window", r"rolling|sliding|moving|last 60|past 60|previous 60"),
        ("X-RateLimit-Remaining", r"X-RateLimit-Remaining"),
        ("Enterprise 600", r"\b600\b"),
        ("/v1/batch", r"/v1/batch"),
        ("max 50 items", r"\b50\b"),
        ("three times", r"\b(3|three)\b"),
        ("within 5 minutes", r"\b(5|five)[ -]?(min|minutes)"),
        ("blocked 15 minutes", r"\b(15|fifteen)[ -]?(min|minutes)"),
        ("support email", r"support@example\.com"),
    ],
    "t2": [
        ("429 is retried", r"429"),
        ("abort stops the loop", r"abort|cancel"),
        ("random extra delay", r"random|jitter"),
        ("delay doubles", r"doubl|twice|exponential|two times|2x|\* ?2|times 2|power"),
        ("delay has a maximum", r"5,?000|MAX_DELAY_MS|5 seconds|maximum|at most|never more|upper"),
        ("5 attempts", r"\b5\b|five|MAX_ATTEMPTS"),
        ("server errors are retried", r"5xx|500|server error"),
    ],
    "t3": [
        ("newline in a cell", r"newline|line break|\\n"),
        ("quotes", r"quot"),
        ("csv-parse", r"csv-parse"),
        ("version 5.5", r"5\.5"),
        ("exportRows", r"exportRows"),
        ("3 tests", r"\b(3|three)\b[^.\n]{0,25}tests?|tests?[^.\n]{0,30}\b(3|three)\b"),
        ("10,000 rows", r"10,?000|10k"),
        ("1.8 s now", r"1\.8"),
        ("1.2 s before", r"1\.2"),
        ("importRows not fixed", r"importRows"),
        ("ticket EXP-412", r"EXP-412"),
        ("Node 18", r"Node(\.js)?[^.\n]{0,12}18"),
        ("no breaking changes", r"breaking"),
    ],
    "t4": [
        ("useDeferredValue", r"useDeferredValue"),
        ("debounce 300 ms", r"\b300\b"),
        ("React.memo", r"React\.memo|memo\("),
        ("useCallback", r"useCallback"),
        ("useMemo", r"useMemo"),
        ("react-window", r"react-window"),
        ("about 20 rows", r"\b20\b"),
        ("2000 items", r"2,?000"),
        ("new function on each render", r"new function|new arrow|different function|new one|creates? (a|the|another)[^.\n]{0,20}function|function[^.\n]{0,30}(each|every) render"),
        ("filter runs on each render", r"filter"),
    ],
    "t5": [
        ("deadline 15 December 2026", r"15 December 2026|December 15,? 2026|2026-12-15"),
        ("utility bill", r"utility bill|electricity|water bill|gas bill"),
        ("bank statement", r"statement"),
        ("not older than 3 months", r"(three|3) months|90 days"),
        ("upload in the portal", r"portal|upload|online"),
        ("or bring to a branch", r"branch"),
        ("limit USD 500 per day", r"\b500\b"),
        ("incoming payments and card still work", r"incoming|receive|card (purchases|payments)|with (your|the) card"),
        ("no fee", r"no fee|free|no cost|not cost|not (have to |need to )?pay|no charge"),
        ("bank never asks for PIN", r"PIN"),
        ("call the number on the card", r"back of (your|the) card|number on (your|the) card"),
    ],
}


def task_sections() -> dict[str, str]:
    text = (BENCH / "tasks" / "tasks-1-to-5.md").read_text() + "\n" + (BENCH / "tasks" / "tasks-6-and-7.md").read_text()
    parts = re.split(r"^# Task (\d)\s*$", text, flags=re.M)
    sections = {}
    for i in range(1, len(parts), 2):
        sections[f"t{parts[i]}"] = parts[i + 1]
    # Task 5: only the question of the user counts as known words.
    # The hard words of the bank email must not be reused.
    sections["t5"] = sections["t5"].split(">")[0]
    sections["t6"] = sections["t6"].split("\n- ")[0]
    return sections


def known_words(section: str) -> set[str]:
    known = set()
    for word in re.findall(r"[A-Za-z][A-Za-z'-]*", section):
        for part in word.lower().split("-"):
            known.update(base_forms(part))
    return known


def prose_md(text: str, fence_prose: bool) -> list[str]:
    def fence(match: re.Match) -> str:
        lang = match.group(1).lower()
        if lang == "text" or (fence_prose and lang in {"", "md", "markdown", "gitcommit", "git"}):
            paragraphs = match.group(2).split("\n\n")
            return "\n\n".join(" ".join(p.split()) for p in paragraphs) + "\n"
        return ""

    text = re.sub(r"```(\w*)\n(.*?)```", fence, text, flags=re.S)
    text = re.sub(r"`[^`]*`", "CODE", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link words
    text = re.sub(r"\*\*|__|\*", "", text)
    blocks = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(">") or re.fullmatch(r"[|\-: ]+", line):
            continue
        if line.startswith("|"):
            blocks.extend(c.strip() for c in line.strip("|").split("|") if c.strip())
            continue
        line = re.sub(r"^(#+|[-*+]|\d+[.)])\s+", "", line)
        blocks.append(line)
    return blocks


def prose_ts(text: str) -> list[str]:
    blocks, current = [], []
    for line in text.splitlines():
        stripped = line.strip()
        inline = re.search(r"(?<![:'\"`])//\s?(.*)$", line)
        if stripped.startswith(("/**", "/*", "*")) and not stripped.startswith("*/"):
            content = re.sub(r"^/?\*+\s?", "", stripped).strip()
            content = re.sub(r"\*/$", "", content).strip()
            if content and not content.startswith("@"):
                current.append(content)
                continue
            if content.startswith("@"):
                current.append(re.sub(r"^@\w+\s*(\{[^}]*\})?\s*\w*\s*-?\s*", "", content))
                continue
        elif inline and inline.group(1).strip():
            current.append(inline.group(1).strip())
            if stripped.startswith("//"):
                continue
        if current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return [re.sub(r"`[^`]*`", "CODE", b) for b in blocks]


def strip_ts_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?<![:'\"`])//.*$", "", text, flags=re.M)
    return re.sub(r"\s+", "", text)


def sentences(block: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?:])\s+", block) if s.strip()]


def words(sentence: str) -> list[str]:
    return [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", sentence) if w != "CODE"]


def avoided(sentence: str) -> list[str]:
    lowered = sentence.lower()
    for allowed in ALLOWED_PHRASES:
        lowered = lowered.replace(allowed, " ")
    found = [p for p in AVOID_PHRASES if p in lowered]
    for word in AVOID_WORDS:
        if re.search(rf"\b{re.escape(word)}(s|es|d|ed|ing)?\b", lowered):
            found.append(word)
    return found


def rare(sentence: str, known: set[str]) -> list[str]:
    out = []
    for word in words(sentence):
        if word.isupper() or re.search(r"[a-z][A-Z]", word):
            continue  # acronym or code name
        for part in word.lower().split("-"):
            part = part.strip("'")
            if len(part) < 3 or part in DEV_WORDS:
                continue
            forms = base_forms(part)
            if any(f in known or f in DEV_WORDS for f in forms):
                continue
            if max(zipf_frequency(f, "en") for f in forms) < RARE_BELOW:
                out.append(part)
    return out


def score_file(task: str, path: Path, known: set[str], original_code: str) -> dict:
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".ts":
        blocks = prose_ts(raw)
        # Facts can be named by a constant, so search the comments with their code names.
        fact_text = "\n".join(re.findall(r"//.*$|/\*.*?\*/", raw, flags=re.M | re.S))
    else:
        blocks = prose_md(raw, fence_prose=(task == "t3"))
        fact_text = raw
    result = {"words": 0, "sentences": 0, "over20": 0, "longest": 0,
              "rare": [], "avoid": [], "joins": 0}
    for block in blocks:
        for sentence in sentences(block):
            count = len(words(sentence))
            if count == 0:
                continue
            result["words"] += count
            result["sentences"] += 1
            result["longest"] = max(result["longest"], count)
            if count > MAX_WORDS:
                result["over20"] += 1
            result["rare"] += rare(sentence, known)
            result["avoid"] += avoided(sentence)
            result["joins"] += len(re.findall(r"—|–|;|->|=>|→", sentence))
    facts = FACTS[task]
    missing = [name for name, pattern in facts if not re.search(pattern, fact_text, flags=re.I)]
    result["facts_total"] = len(facts)
    result["facts_missing"] = missing
    if task == "t6":
        prose = " ".join(blocks).lower()
        result["slang_left"] = [w for w in SLANG_T6 if w in prose]
    if path.suffix == ".ts":
        result["code_changed"] = strip_ts_comments(raw) != original_code
    return result


def main() -> int:
    round_dir = Path(sys.argv[1])
    configs = sys.argv[2:] or sorted(p.name for p in round_dir.iterdir() if p.is_dir())
    sections = task_sections()
    code = re.search(r"```ts\n(.*?)```", sections["t2"], flags=re.S).group(1)
    original_code = re.sub(r"\s+", "", code)
    table, details = [], {}
    for config in configs:
        total = {"words": 0, "sentences": 0, "over20": 0, "longest": 0, "rare": 0,
                 "avoid": 0, "joins": 0, "facts_total": 0, "facts_missing": 0}
        details[config] = {}
        for task in ("t1", "t2", "t3", "t4", "t5", "t6", "t7"):
            name = f"{task}.ts" if task == "t2" else f"{task}.md"
            path = round_dir / config / name
            if not path.exists():
                continue
            r = score_file(task, path, known_words(sections[task]), original_code)
            details[config][task] = r
            for key in ("words", "sentences", "over20", "joins", "facts_total"):
                total[key] += r[key]
            total["longest"] = max(total["longest"], r["longest"])
            total["rare"] += len(r["rare"])
            total["avoid"] += len(r["avoid"])
            total["facts_missing"] += len(r["facts_missing"])
        w = max(total["words"], 1)
        s = max(total["sentences"], 1)
        table.append({
            "config": config,
            "words": total["words"],
            "avg_sentence": round(total["words"] / s, 1),
            "pct_over20": round(100 * total["over20"] / s, 1),
            "longest": total["longest"],
            "rare_per_100": round(100 * total["rare"] / w, 2),
            "avoid_per_100": round(100 * total["avoid"] / w, 2),
            "joins_per_100": round(100 * total["joins"] / w, 2),
            "facts_kept": f"{total['facts_total'] - total['facts_missing']}/{total['facts_total']}",
        })
    header = ["config", "words", "avg_sentence", "pct_over20", "longest",
              "rare_per_100", "avoid_per_100", "joins_per_100", "facts_kept"]
    print(" | ".join(header))
    for row in table:
        print(" | ".join(str(row[h]) for h in header))
    print()
    for config in configs:
        for task, r in details[config].items():
            if isinstance(r, str):
                print(f"{config} {task}: {r}")
                continue
            notes = []
            if r["facts_missing"]:
                notes.append("missing facts: " + ", ".join(r["facts_missing"]))
            if r.get("code_changed"):
                notes.append("CODE CHANGED")
            if r["rare"]:
                notes.append("rare: " + ", ".join(sorted(set(r["rare"]))))
            if r.get("slang_left"):
                notes.append("slang left from the notes: " + ", ".join(r["slang_left"]))
            if r["avoid"]:
                notes.append("avoid list: " + ", ".join(sorted(set(r["avoid"]))))
            print(f"{config} {task}: {r['words']} words, {r['sentences']} sentences, "
                  f"over20={r['over20']}, longest={r['longest']}"
                  + ("".join("\n      " + n for n in notes)))
    (round_dir / "scores.json").write_text(json.dumps({"table": table, "details": details}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
