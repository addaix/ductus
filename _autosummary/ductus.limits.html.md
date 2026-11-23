# ductus.limits

The measured limits of the shipped defaults: the one place their numbers live.

Every surface that states how often this package is wrong (the rendered report’s
footer, the MCP instructions, the OpenAPI description, the frontend’s panels through a
generated `limits.ts`) formats its text from here, and `tests/test_limits.py` checks
that the prose which cannot be formatted (README, the skills, the package docstring)
quotes the same numbers. Re-measure with `misc/measure_false_positives.py` and
`misc/measure_document_threshold.py` after any change to rules, weights or thresholds,
then change the numbers here, once.

They are operating characteristics of the instrument, measured on corpora of known
authorship, never a probability about a document.

```pycon
>>> f"about one in {DOCUMENT_ONE_IN}"
'about one in a hundred'
```

### Module Attributes

| [`SOURCE`](#ductus.limits.SOURCE)                         | Where the numbers come from.                                                                                                                                          |
|---------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`DOCUMENT_FALSE_ACCUSATION_RATE`](#ductus.limits.DOCUMENT_FALSE_ACCUSATION_RATE) | Human-written documents called `leans-machine` by the defaults (held-out non-native essays and the 350-document W&I+LOCNESS dev set, both granularities, rounded up). |
| [`DOCUMENT_ONE_IN`](#ductus.limits.DOCUMENT_ONE_IN)                | The same, as the natural frequency the interfaces use next to a verdict: "about one human-written document in {DOCUMENT_ONE_IN}".                                     |
| [`MACHINE_DOCUMENT_RECALL`](#ductus.limits.MACHINE_DOCUMENT_RECALL)        | the recall the rate above was bought with.                                                                                                                            |
| [`SENTENCE_FALSE_FLAG_RANGE`](#ductus.limits.SENTENCE_FALSE_FLAG_RANGE)      | Human-written sentences flagged `leans-machine`, across proficiency bands.                                                                                            |

### Functions

| [`as_typescript`](#ductus.limits.as_typescript)()   | The constants as a TypeScript module, for `frontend/src/generated/limits.ts`.   |
|--------------------------------------------------------------------|---------------------------------------------------------------------------------|

### ductus.limits.DOCUMENT_FALSE_ACCUSATION_RATE *= '0.9%'*

Human-written documents called `leans-machine` by the defaults (held-out non-native
essays and the 350-document W&I+LOCNESS dev set, both granularities, rounded up).

### ductus.limits.DOCUMENT_ONE_IN *= 'a hundred'*

The same, as the natural frequency the interfaces use next to a verdict:
“about one human-written document in {DOCUMENT_ONE_IN}”.

### ductus.limits.MACHINE_DOCUMENT_RECALL *= 'about 2%'*

the recall the
rate above was bought with.

* **Type:**
  Machine-written essays the document verdict calls `leans-machine`

### ductus.limits.SENTENCE_FALSE_FLAG_RANGE *= '0.4-2%'*

Human-written sentences flagged `leans-machine`, across proficiency bands.

### ductus.limits.SOURCE *= 'misc/docs/non-native-calibration.md'*

Where the numbers come from.

### ductus.limits.as_typescript()

The constants as a TypeScript module, for `frontend/src/generated/limits.ts`.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
