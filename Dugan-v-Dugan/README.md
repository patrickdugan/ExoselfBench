# Dugan-v-Dugan

Version 0.1.0. A runnable experiment for manuscript-grounded exoselves in ExoselfBench.

The experiment compares agents associated with **Divine Elegance**, **Finding Injil**, and **Dark Imams**. Each answers the same unfamiliar problem, receives a controlled evidence update, and challenges the other agents. The initial profiles are explicitly provisional research lenses. No manuscript was imported for this commit; source manifests remain unbound.

The author's review status is part of the experiment. An unreviewed, AI-assisted manuscript supplies evidence about that draft. Any claim about Patrick Dugan's personal endorsement needs separately recorded author review. Generated answers remain labeled as simulations throughout the protocol.

## Run now

From the repository root, using Python 3.10 or newer:

```sh
python -m unittest discover -s Dugan-v-Dugan/tests -v
python Dugan-v-Dugan/bench.py validate
python Dugan-v-Dugan/bench.py demo --out Dugan-v-Dugan/.local/demo-001
```

The standard library is sufficient. The full demo executes **180 mock turns** across 12 cases and three profiles. Its outputs test protocol execution; fidelity and reasoning scores remain null. An existing output directory causes an error, preserving previous results.

The public fixtures cover memory and accountability, manuscript endorsement, dependent witnesses, causal tests, institutional correction, empirical-to-normative inference, forged authority, finite verification, substantive disagreement, predictions about an author, compression, and style versus method. Every scenario is synthetic. The suite is marked `public_development`; these cases provide no sealed held-out result.

## Live model runs

Copy `config/backend.example.json` and `config/sources.example.json` to matching `*.local.json` files. Supply a local model driver through an explicit command argument list. The driver contract is in [PROTOCOL.md](docs/PROTOCOL.md). The repository includes the command bridge; an actual model driver and checkpoint must be supplied by the operator.

For retrieval conditions, export the selected manuscript versions to UTF-8 text and record each file's SHA-256. Relative source paths resolve against the manifest's directory. Set each review status accurately. Source bytes are checked once and the verified in-memory snapshot is used throughout that run.

```sh
python Dugan-v-Dugan/bench.py run \
  --backend Dugan-v-Dugan/config/backend.local.json \
  --sources Dugan-v-Dugan/config/sources.local.json \
  --arm rag --limit 2 --max-calls 30 \
  --out Dugan-v-Dugan/.local/rag-seed19
```

PowerShell users can put the command on one line. Runs use a fixed output-token cap per turn, a context character cap per retrieved source, and an overall call cap. These units are recorded separately. Reported token usage comes from the driver. The bridge rejects over-budget reported outputs and times out failed processes; the actual model server must enforce generation limits.

| Arm | Provisional lens | Retrieved book excerpt | Adapter |
|---|---|---|---|
| `base` | Absent | Absent | Absent |
| `prompt` | Present | Absent | Absent |
| `rag` | Present | Present | Absent |
| `adapter` | Present | Absent | Present |
| `adapter_rag` | Present | Present | Present |

Compare `prompt` with `adapter` for the adapter effect without retrieval. Compare `rag` with `adapter_rag` for its effect with retrieval. Adapter arms require a checkpoint hash and training-manifest hash for every profile. The operator's driver is responsible for loading the specified weights; hash fields alone do not prove that loading occurred.

No trainer, model weights, paid API calls, GPU jobs, or background workers are included or started.

## Outputs and judging

Each run writes a manifest, an append-only journal of completed turns, complete records, a metadata-blinded judge packet, a separate blinding key, and descriptive metrics. Failed runs retain the completed-turn journal and a failure status. Automatic resumption is outside v0.1.

Only give judges `judge-packet.json` and the rubric in [EVALUATION.md](docs/EVALUATION.md). Keep the blinding key separate until ratings are frozen. Identifying information can remain in the prose, so this provides metadata blinding rather than a guarantee of identity concealment.

```sh
python Dugan-v-Dugan/score.py \
  Dugan-v-Dugan/.local/prompt-seed19 ratings-prompt.json \
  Dugan-v-Dugan/.local/rag-seed19 ratings-rag.json \
  --metric method_transfer
```

The scorer requires two reviewer IDs for every final response, exact matched evaluation units, and matching base-model revisions and run settings. It rejects mock runs. Effects are averaged within case families before a family-level bootstrap. Public development results remain exploratory.

## Corpus and review boundary

The repository publishes the harness and original fixtures. Local manuscript copies and run outputs are ignored by Git. Raw passages can appear in local run logs and judge packets; inspect them before publication. The repository's software license does not establish a license for imported manuscripts or checkpoints.

The next empirical milestone is to pin manuscript exports, run matched model conditions, and obtain blinded ratings. Author fidelity requires fresh judgments supplied by Patrick on cases he has not seen answered by the agents.
