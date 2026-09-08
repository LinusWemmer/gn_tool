# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Inklusivomat": a Flask web app that rewrites German text into the *Inklusivum* — the gender-neutral
system of the Verein für geschlechtsneutrales Deutsch (https://geschlechtsneutral.net/gesamtsystem/).
Older code and the README still call it the "de-e system"; the two names refer to the same thing.

The repo is a **fork of ParZu** (https://github.com/rsennrich/parzu) with the app grafted on top.
Everything in `core/`, `preprocessor/`, `postprocessor/`, `statistics/`, `evaluation/`, `doc/`,
`parzu*.py`, `config.ini`, `changelog` is upstream ParZu (Prolog + Python dependency parser) and is
normally not touched. The Inklusivomat proper is `__init__.py`, `marking_tool.py`, `lexicon*.py`,
`sentence_data.py`, `templates/`, `static/`.

## Commands

Everything must be run **from the repository root** — `lexicon.py` opens `static/*.txt` via relative
paths at class-definition (import) time.

On this machine the dependencies live in a virtualenv outside the Dropbox tree, so use its
interpreter (`python3` alone is the system Python and has no Flask):

```bash
PY=~/.venvs/gn_tool/bin/python   # or: source ~/.venvs/gn_tool/bin/activate

$PY __init__.py                  # dev server on http://localhost:4000, Flask debug ON
$PY __init__.py run              # same, debug OFF
$PY -m unittest lexicontest      # end-to-end: input sentence -> expected Inklusivum output

# Docker (production image; runs redis + gunicorn on :80 via start_services.sh)
sudo docker build -t docker_image .
sudo docker run -p 80:80 -v /path/to/reports:/app/reports docker_image
```

Redis (the Flask session store, expected on localhost:6379) runs as a systemd service and starts at
boot — `systemctl status redis-server`. The `redis-server &` in the README/Dockerfile is only needed
where nothing supervises it.

`lexicontest.py` contains a single test method holding several hundred `(input, expected_output)`
pairs, so there is no finer-grained selection than the file. To debug one sentence, temporarily
narrow the `test_sentences` list. It imports from `__init__`, which instantiates the Flask app and a
ParZu parser at import time, so Flask/flask-session/redis and a working ParZu setup are needed even
for tests.

`markingtest.py` is **stale and fails** (last touched 2023-09-09, unchanged since). It hands
`Marking_Tool` the raw CoNLL lines without splitting them on tabs — unlike `get_parse` — and its
expected HTML predates the `div.checkbox-container` wrapper that `create_input_form` now emits. Fix
those two things before trusting it; do not read its failure as a regression.

### Local prerequisites

`install.sh` fetches clevertagger, Wapiti and the Zmorge transducer into `external/` and rewrites
`config.ini` (`taggercmd`, `smor_model`) to point at them. `config.ini` is gitignored, so a checkout
starts from `config.ini.example`. `key_config.py` (holding `SECRET_KEY`) is not in the repo either
but is required — `__init__.py` does `app.config.from_pyfile('key_config.py')`.

## Pipeline

`POST /parse` → `POST /mark` is the two-step user flow; `POST /translate_directly` chains them by
selecting every checkbox automatically.

1. **Preprocessing** (`__init__.py`), all string-level hacks applied before parsing:
   - `hack_for_ordinal_numbers` — `43. ` → `43-tägig rosa ` so ParZu does not split the sentence;
     undone by `undo_hack_for_ordinal_numbers` on the way out.
   - `split_prepositions` — `im`/`zum`/`beim`/… → `in dem`/`zu dem`/`bei dem`, since article and
     preposition must be neutralized separately. `Marking_Tool.neutralize_word` fixes the seams
     again afterwards: `zu` + `derm` is re-contracted to `zurm`, while `i`/`a`/`vo` fragments left
     over from an input `im`/`am`/`vom` are restored to `in`/`an`/`von` + `derm`.
   - `remove_special_character_gendering` — `Lehrer*innen`, `er/sie`, `Kolleg(inn)en` etc. are
     normalized to the plain feminine form so ParZu can tag them.
2. **Parse** — `get_parse` calls ParZu and returns, per sentence, a list of CoNLL columns split on
   tabs: `0:ID 1:FORM 2:LEMMA 3:CPOSTAG 4:POSTAG 5:FEATS 6:HEAD 7:DEPREL 8:PHEAD`.
3. **Reparse for "lonely" adjectives** — `search_lonely_adjectives` capitalizes adjectives that do
   not modify a noun (so `netten` in `einen netten und einen unfreundlichen Kollegen` can be
   neutralized) and swaps `glauben`→`schreiben`, `zeigen`→`sagen` (ParZu mis-tags their dative
   objects). If anything changed, the text is re-parsed and the substitutions are undone in
   `mark_nouns`.
4. **Marking** — `mark_nouns` builds one `Marking_Tool` per sentence and emits the HTML form via
   `get_marking_form`. Each `Marking_Tool.__dict__` is stored in the session as `markingtool{i}`,
   with the count in `sentence_number`.
5. **Neutralizing** — `/mark` rebuilds the `Marking_Tool`s from the session and calls
   `neutralize_nounphrase` for each checked box, then joins the result with `get_sentence`.

### The parse_list row convention (important)

`Marking_Tool` **appends two extra fields** to every CoNLL row via `find_realizations`:
`row[-2]` = the surface realization as it appeared in the original input (later overwritten with the
neutralized form), `row[-1]` = the trailing whitespace. Output is therefore just the concatenation of
`row[-2] + row[-1]` over all rows (`get_sentence`). `get_internal_sentence` instead reproduces the
*input* for re-parsing. Code addressing these fields uses negative indices; do not append further
columns.

`find_realizations` matches each parsed token back onto the raw input with a hand-written regex per
token shape — this is what lets the tool round-trip gendered spellings (`Lehrer:innen`, `ihre*seine`)
that were normalized away in step 1. Adding a new normalization in
`remove_special_character_gendering` usually requires a matching pattern here, or the function raises
`"The word ... could not be found in the input text"`.

### Checkbox id format

`sentenceNumber|wordPosition|componentIndex` (e.g. `0|2|34`). `wordPosition` is the 1-based CoNLL ID
of the noun-phrase head; `componentIndex` identifies which part of a compound noun the box belongs
to, so `Schulleiterin` can be neutralized component-wise. `/mark` groups all boxes sharing the first
two fields and passes the component indices to `neutralize_nounphrase`.

## Lexicon layer

`lexicon.py` (`Lexicon`) is a *static* class — never instantiate it; all state is class-level and
initialized at import. It holds the Inklusivum paradigms (`PRONOUNS`, `ARTIKEL_*`, `JEDER_PARADIGM`,
`EIN_PARADIGM`), irregular/neologism tables (`Oma`/`Opa`→`Owa`, `Bruder`/`Schwester`→`Geschwister`,
…), and the compound-noun analysis (`check_noun`, `check_composite_noun`, `make_neutralized_noun`).

`lexicon_fem.py` / `lexicon_neuter.py` mirror its structure for two special cases: when a noun is
rewritten to `-person` (`Feuerwehrmann` → `Feuerwehrperson`) the dependent words must become
**feminine**; when a `-sohn`/`-tochter` compound is rewritten (to `-kind`) they must become
**neuter**. This is driven
from `neutralize_nounphrase` via the `person` / `kind` flags returned by `make_neutralized_noun`.

### The five word lists in `static/` are index-parallel

`movierbare_Substantive.txt` (masculine), `_feminin.txt`, `_inklusivum.txt`, `_in_Komposita.txt`
and `_in_Komposita_alternativ.txt` are read into `Lexicon.MALE_NOUNS`, `FEMALE_NOUNS`,
`NEUTRAL_NOUNS`, `COMPOSITE_NOUNS`, `ALTERNATIVE_COMPOSITE_NOUNS` and are looked up **by shared line
index** (`Lexicon.NEUTRAL_NOUNS[j]` is the neutral form of `Lexicon.MALE_NOUNS[j]`). All five
currently have 4129 lines; **any edit must add or remove the same line in all five files at the same
position**, or unrelated nouns start translating into each other.

Lines are marked with `%` and `?` to disable matching while preserving the index (e.g. `%Mensch?` —
`%`/`?` never occur in real tokens). In `_in_Komposita_alternativ.txt`, a leading `%` means "no
alternative form"; such lines are skipped when building `ALTERNATIVE_COMPOSITE_NOUNS`, which keeps
`[line_index, form]` pairs rather than a flat list.

`static/Komposita-Skript.py` regenerates the two `_in_Komposita*` files from
`movierbare_Substantive.txt` (run it from inside `static/`). `static/substantivierte_adjektive.txt`
is a separate, non-parallel list of nominalized adjectives (`Verlobte`, `Jugendliche`, …).

`static/substantivierbare_adjektive.txt` holds the nominalized form of **every** German adjective
and participle (~32000 entries, `Reisende`, `Große`, …), regenerated by `static/Adjektiv-Skript.py`
from `/usr/share/dict/ngerman` via the Zmorge transducer. It only applies where ParZu reports an
unambiguous masculine or feminine — a neuter nominalized adjective denotes a thing (`das Gute`) —
so the curated list above stays responsible for the genitive and dative, where masculine and neuter
coincide. `Lexicon.NO_SUBST_ADJ` excludes deadjectival abstracts that are not persons (`die Tiefe`,
`die Ebene`, `die Weise`), matched by word ending so compounds are covered.

## Conventions

- Comments and user-facing strings are German; code identifiers are English. Keep that split.
- The code leans heavily on `print()` for tracing the parse; that is deliberate and matched by
  running the dev server in the foreground.
- Problem reports from `/report` are appended to `reports/reports.txt`. The path is chosen from the
  `EXECUTION_ENVIRONMENT` env var (`docker` → `/app/reports/…`, otherwise a hardcoded absolute path
  in `__init__.py`).
- `@app.errorhandler(Exception)` swallows every exception into a German error page plus a report
  form, so a broken change looks like a friendly message rather than a traceback — check the server
  log, or reproduce via `lexicontest`.
- Input is capped at 5000 characters in `/parse`.
