"""
Module 7 Week B — Tuesday Stretch (Honors): Adversarial QA Probe.

Reuses the QA pipeline + EM/F1 functions from `lab.py`. Implement the TODO
functions below; see the stretch page for full task description.
"""

import json
import os
import sys

import pandas as pd

# Import the lab's existing functions (we reuse build_qa_pipeline, predict_one,
# evaluate_qa, normalize_answer, exact_match, token_f1)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import lab  # noqa: E402


def load_adversarial_set(path: str = "stretch/tuesday/adversarial_set.csv") -> pd.DataFrame:
    """
    Load the adversarial test set CSV.

    Verifies columns: qid, question, context, gold_answer, pattern_tag.
    """
    # Read the CSV at the given path
    if not os.path.exists(path):
        raise FileNotFoundError(f"Adversarial set not found at: {path}")
    
    df = pd.read_csv(path)
    
    # Verify all five required columns exist
    required_columns = ["qid", "question", "context", "gold_answer", "pattern_tag"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Critical Error: Missing required column '{col}' in {path}")
            
    return df


def evaluate_adversarial(qa, df: pd.DataFrame) -> dict:
    """
    Run the QA pipeline on the adversarial set; compute aggregate + per-pattern metrics.

    Returns:
        {
          "em": float, "f1": float, "n": int,
          "per_pattern": { tag: {"em": float, "f1": float, "n": int}, ... },
          "predictions": [ ... lab.evaluate_qa-shaped entries plus pattern_tag ... ],
        }
    """
    # Call lab.evaluate_qa for the aggregate metrics + predictions list
    # Assuming lab.evaluate_qa returns {"em": float, "f1": float, "predictions": list}
    eval_result = lab.evaluate_qa(qa, df)
    
    predictions = eval_result["predictions"]
    
    # Enrich each prediction with its pattern_tag (lookup from df by qid)
    # Create a mapping for fast lookup: qid -> pattern_tag
    tag_map = dict(zip(df['qid'], df['pattern_tag']))
    
    for pred in predictions:
        pred["pattern_tag"] = tag_map.get(pred["qid"])
    
    # Compute per-pattern aggregates using a temporary DataFrame for grouping
    pred_df = pd.DataFrame(predictions)
    per_pattern_metrics = {}
    
    for tag, group in pred_df.groupby("pattern_tag"):
        per_pattern_metrics[tag] = {
            "em": float(group["em"].mean()),
            "f1": float(group["f1"].mean()),
            "n": int(len(group))
        }
    
    # Return the combined dict
    return {
        "em": float(eval_result["em"]),
        "f1": float(eval_result["f1"]),
        "n": len(df),
        "per_pattern": per_pattern_metrics,
        "predictions": predictions
    }


def main() -> None:
    """Load adversarial set, run evaluation, write predictions + metrics."""
    # Note: If running locally, ensure your working directory is the repo root
    # or adjust path to "adversarial_set.csv" if you are already in stretch/tuesday/
    csv_path = "stretch/tuesday/adversarial_set.csv"
    if not os.path.exists(csv_path):
        csv_path = "adversarial_set.csv" # Fallback for local execution

    df = load_adversarial_set(csv_path)
    qa = lab.build_qa_pipeline(lab.get_qa_model_name())
    result = evaluate_adversarial(qa, df)

    # Save outputs back to the stretch/tuesday directory
    output_dir = "stretch/tuesday/"
    if not os.path.exists(output_dir):
        output_dir = "" # Fallback

    pred_df = pd.DataFrame(result["predictions"])
    pred_df.to_csv(os.path.join(output_dir, "adversarial_predictions.csv"), index=False)

    metrics = {
        "em": result["em"],
        "f1": result["f1"],
        "n": result["n"],
        "per_pattern": result["per_pattern"],
        "model": lab.get_qa_model_name(),
    }
    with open(os.path.join(output_dir, "adversarial_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Aggregate EM = {result['em']:.4f}")
    print(f"Aggregate F1 = {result['f1']:.4f}")
    print(f"n = {result['n']}")
    print(f"Per-pattern breakdown:")
    for tag, stats in result["per_pattern"].items():
        print(f" - {tag}: F1={stats['f1']:.4f}, n={stats['n']}")


if __name__ == "__main__":
    main()