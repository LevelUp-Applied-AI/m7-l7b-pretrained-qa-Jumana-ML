# Adversarial QA Probe — Analysis Memo

## 1. Hypothesis

- **Input pattern:** The context contains multiple entities of the same semantic type (e.g., two people, two dates, or two companies), where an incorrect entity is placed in a prominent position such as the beginning of the sentence.
- **Output pattern:** The model is expected to incorrectly predict the distractor entity or return an irrelevant span instead of the gold answer.
- **Why you hypothesize this:** DistilBERT-based models often rely on lexical overlap and entity-type matching rather than deep logical reasoning. I hypothesize that the model lacks the syntactic depth to distinguish between the "subject" and the "object" when both share the same entity class, leading to a proximity bias.

## 2. Set Design

- **Total examples:** 30
- **Tags used:** 
    - same-type-distractor: 22
    - temporal-confusion: 4
    - control: 4
- **Why these tags:** 
    - same-type-distractor tests if the model can resolve the correct entity when multiple valid candidates of the same type exist.
    - temporal-confusion targets the model's ability to handle chronological logic and multiple date references.
    - control establishes a performance baseline on simple extractive tasks without any misleading information.
- **Control examples:** 4 examples; they isolate the model's basic ability to extract a single clearly stated entity; they confirm the model's fundamental QA capabilities are intact.

## 3. Results

- **Aggregate EM:** 0.9667
- **Aggregate F1:** 0.9889
- **Lab 7B baseline:** EM 0.3440; F1 0.4611
- **Per-pattern_tag breakdown:**

| Pattern | n | EM | F1 | vs. baseline |
|---|---|---|---|---|
| same-type-distractor | 22 | 0.9545 | 0.9848 | +0.5237 |
| temporal-confusion | 4 | 1.0000 | 1.0000 | +0.5389 |
| control | 4 | 1.0000 | 1.0000 | +0.5389 |

Specific examples illustrating the patterns:

- **(EX_01)** Who is the CEO of Meta? → gold: Mark Zuckerberg, predicted: Mark Zuckerberg. Despite the early mention of Tim Cook, the model correctly identified the subject.
- **(EX_05)** Who founded Tesla? → gold: Martin Eberhard and Marc Tarpenning, predicted: Martin Eberhard and Marc Tarpenning. The model successfully bypassed Elon Musk as a distractor.
- **(EX_21)** What year did they move to London? → gold: 2018, predicted: 2018. The model correctly distinguished the move date from the previous residence date.

## 4. Production Defense

**Engineering Action:** Confidence-threshold filter that routes below-threshold queries to humans.

**Explanation:** While the model showed high robustness on this specific adversarial set, the massive gap between these results and the Lab 7B baseline (0.4611 F1) suggests that the model is highly sensitive to context noise. By implementing a confidence-threshold filter, we can identify predictions where the model's internal score is low—indicating high competition between multiple entities—and route those high-risk cases to human agents for manual verification to maintain production quality.