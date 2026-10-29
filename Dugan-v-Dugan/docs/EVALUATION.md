# Evaluation and research design

## Questions

Does a manuscript-grounded agent apply a defensible method on a new problem? How does its answer change when the evidence changes? After reading another book-agent's response, does it preserve a disagreement that still has reasons behind it?

Source fidelity and author fidelity are separate measurements. Pinned passages support a source-fidelity judgment. A claim about Patrick's own commitments requires his reviewed labels. A simulation's answer to a new case remains a forecast until matched against independent evidence of his response.

For the author-fidelity study, collect sealed answers before showing Patrick model outputs. Record the question, answer date, permissible uncertainty, and any subsequent correction. Comparing against his later judgment measures agreement on that sample; it does not establish personal identity or a uniquely determined counterfactual self.

## Human rubric

Use a 0 to 4 scale for each dimension. Zero indicates a clear failure; 2 indicates partially adequate work with a material gap; 4 indicates fully supported performance on the supplied case. Scores of 1 and 3 fall between the anchors. Record a short reason for every rating, especially a score of 0 or 4.

| Dimension | A score of 4 requires |
|---|---|
| `grounding` | Assertions stay within supplied evidence, with correct citations and clear uncertainty. |
| `method_transfer` | The answer applies an explicit, defensible reasoning procedure to the unfamiliar task and identifies a discriminating test or missing premise. |
| `evidence_update` | Changes follow probative evidence; justified stability survives irrelevant material or already-settled premises. |
| `attribution` | The answer preserves the distinction between a draft, a source claim, an inference, and personal author endorsement. |
| `dissent` | The final answer responds to peers' reasons and retains or resolves disagreement on evidentiary grounds. |

Style resemblance may be recorded separately. It contributes no points to these dimensions. Consensus is not an automatic success condition. Some relevant updates strengthen an ancillary historical fact while leaving the target normative inference unchanged; the fixtures deliberately include these cases.

Use two independent raters per final response, preferably including someone familiar with source criticism and someone familiar with the target technical domain. Reviewer IDs are pseudonyms. The code checks distinct IDs; the operator must establish reviewer independence. A large disagreement should trigger adjudication and a retained record of the original ratings.

The judge packet includes previous answers and peer responses where relevant. Metadata labels are removed and evidence IDs are replaced consistently. Manuscript language can reveal its origin; measure judge identity guesses when concealment matters. Keep scoring conditions and personal judgments frozen before unblinding.

A ratings file has this shape:

```json
{
  "schema": "dvd-ratings/0.1",
  "ratings": [
    {
      "item_id": "item-00001",
      "reviewer_id": "reviewer-A",
      "scores": {
        "grounding": 3,
        "method_transfer": 2,
        "evidence_update": 3,
        "attribution": 4,
        "dissent": 2
      },
      "reason": "An example annotation; replace with an actual blind judgment."
    }
  ]
}
```

Provide at least two distinct reviewer rows for every final-stage item. The scorer rejects missing pairs and incomplete coverage. It averages rater scores within an item, computes matched differences between conditions, then averages within case families. Families receive equal weight. Seed repetitions, evidence forks, and the book-agents are correlated measurements inside the family, so they are not counted as independent tasks.

The reported percentile bootstrap resamples family means. With only one family, the interval is null. On the public suite, all intervals are exploratory and conditional on the chosen raters and cases. No minimum effect, power claim, or population generalization has been established.

## Comparisons

Choose `method_transfer` as the primary outcome before a confirmatory run, and preserve the other dimensions as diagnostics. Compare the same base checkpoint, tokenizer, quantization, output cap, inference seed set, and retrieval settings. The provided scorer enforces matching run hashes, seeds, model revisions, and limits; operators must audit other driver settings.

The arm table in the README defines controlled comparisons. An adapter effect is the matched difference between `adapter` and `prompt`, or between `adapter_rag` and `rag`. A retrieval effect is the difference between `rag` and `prompt`. The `base` versus `prompt` comparison estimates the effect of the provisional lens instruction. Increased probability movement alone is insufficient to establish an improvement.

Suggested later ablations include shuffling manuscript labels, keeping vocabulary while scrambling argument structure, and swapping a source for a topically related corpus. Those controls are designs for future runs; v0.1 does not implement a trainer or those data transforms.

## Leakage and author review

The shipped cases are public development fixtures. Keep their families, paraphrases, and nearby synthetic variants out of any claimed held-out evaluation. For a confirmatory study, group source versions and derivative passages by document lineage before constructing splits. Freeze a new private suite, its rubric, and source cutoffs before training. A hash records an artifact's identity; it does not prove absence of pretraining contamination.

Train separately from source evaluation material when making a method-transfer claim. Keep reviewer corrections out of future test items unless they move explicitly into the development split. Log prompt changes and corpus edits. The current validator accepts the public development schema only; sealed-suite governance needs an explicit extension.

Unreviewed model-written material can enter a manuscript-fidelity experiment with that status recorded. Personal endorsement labels require review at the relevant claim or passage. A whole-book label must not silently confer approval on every generated sentence.

## Compactification connection

Let a task specification T contain the allowed questions, evidence interventions, and observable response fields. Two retained histories are behaviorally equivalent for T when every allowed continuation induces the same distribution over those observables. An encoding phi is sufficient for T only when histories with the same encoding remain equivalent under that definition.

The compression fixture supplies histories h1 and h2 with phi(h1) = phi(h2), followed by a task that requires different successful actions. That is a finite counterexample to sufficiency for the specified task family. Its conclusion depends on the supplied oracle and task scope. Neither successful finite tests nor a useful adapter establishes identity with a human author.

This benchmark supplies observable tests of selected distinctions across compression and debate. The connection to moral-history preservation remains a research question beyond the synthetic fixture.
