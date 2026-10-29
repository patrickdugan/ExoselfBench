# Protocol v0.1

## Experimental unit

A unit consists of a case, a manuscript profile, an inference seed, a model condition, and an evidence fork. The proposition being assessed stays fixed across turns so that a probability change has a stable referent.

For each case, every agent first answers independently. The runner then forks that answer into a relevant-evidence branch and a sham branch. Their order is randomized from the recorded seed. Both forks start from the same initial response; material from one fork never enters the other.

Each agent revises independently within a fork. Once all revisions are available, a synchronous peer round presents the other agents' frozen revisions. Every peer exchange uses those frozen responses. The runner never feeds an earlier final answer into a later agent's peer round. An agent sees its own retrieved passage before exchange. A passage cited by a peer becomes available during exchange so that its citation can be inspected.

There are five turns per profile per case: an initial answer, two evidence revisions, and two final peer responses. The 12-case demo therefore makes 180 mock calls. Live runs default to two cases and a 30-call ceiling.

## Actor boundary

Actors receive the proposition, question, supplied evidence, their previous answer, and any peer responses. Evaluator guidance and semantic branch labels stay outside actor requests. IDs such as `f0` describe execution bookkeeping. They carry no claim that evidence is probative.

Documents and peer text may contain hostile instructions. The task's system message classifies that material as data. Backend integrations must preserve that separation when formatting model messages. A generated answer has no authority to invoke tools or change benchmark files.

Every response contains exactly these fields:

```json
{
  "probability": 0.5,
  "decision": "defer",
  "justification": "A brief public justification with explicit evidentiary limits.",
  "evidence_ids": ["E0"],
  "limitations": ["The supplied record leaves a material premise unresolved."],
  "author_status": "simulation"
}
```

The response represents a public explanation. The benchmark requests no hidden reasoning trace. Decision and probability have separate purposes: a policy decision may depend on costs or duties beyond a belief probability. Human judges assess whether their relationship is explained.

Citation checks establish that a referenced evidence ID was supplied in this turn. Entailment, honest quotation, and relevance require substantive review. A model can still make unsupported statements in prose while satisfying the JSON schema.

## Driver contract

The bridge launches the explicitly configured local command with `shell=False`. Each invocation receives one JSON request on standard input and must emit one JSON envelope on standard output. Send diagnostic logs to standard error. Supply a positive timeout in seconds.

Request fields include `protocol`, `request_id`, `seed`, `arm`, `profile_id`, `model`, `limits`, and `task`. The `task` object contains the actual model-facing materials. Use `model` for dispatch and provenance; do not insert command definitions or the complete backend configuration into the prompt. The `base` condition ignores all profile lenses. Load an adapter only for `adapter` and `adapter_rag`, selecting its entry by `profile_id`.

Return:

```json
{
  "response": {
    "probability": 0.5,
    "decision": "defer",
    "justification": "The supplied material leaves the causal relationship unresolved.",
    "evidence_ids": ["E0"],
    "limitations": ["No intervention result was supplied."],
    "author_status": "simulation"
  },
  "usage": {"input_tokens": 120, "output_tokens": 48}
}
```

The counts above illustrate the envelope schema. The driver must report its actual usage. Keep secrets in environment variables and outside configuration files. Manifests persist the configuration for reproducibility.

For adapter conditions, each entry under `adapters` needs `sha256` and `training_manifest_sha256`. Add a path or engine-specific adapter name as needed by your driver. Record quantization and sampler settings in the backend configuration. The runner checks declaration syntax; the driver and deployment audit establish that the correct model was used.

## Retrieval and storage

The reference retriever splits a verified UTF-8 text into bounded character windows and selects the window with the greatest lexical overlap with the question. Ties prefer the earliest offset. This is a deterministic baseline with known limitations around synonyms and window boundaries. It performs no embedding retrieval or document parsing.

The manifest records exact hashes for the suite, profiles, runner, source snapshots, and model declarations. Paths resolve locally. The actor sees bounded excerpts with character-offset locators. The manuscript's review status travels with the excerpt.

The journal is flushed after every completed turn. It stores actor requests and responses as executed. Evaluator fork labels are added later to `records.json`; unfinished journals therefore contain no complete scoring assignment. Failure logs record an error class. Resume, distributed execution, and corpus extraction require later extensions.

## Scope

This version implements public synthetic development cases. It contains no trained Dugan model and no imported book passages. The model-proposed profile definitions are experimental hypotheses about useful specialist roles. Their accuracy must be checked against pinned manuscripts and author review.
