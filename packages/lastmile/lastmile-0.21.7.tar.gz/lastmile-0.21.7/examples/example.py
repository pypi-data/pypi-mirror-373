#!/usr/bin/env -S rye run python

import os
from datetime import datetime

import pandas as pd

from lastmile.lib.auto_eval import Metric, AutoEval, BuiltinMetrics

# Use to deduplicate entity names per script run
NOW_DATE_STRING = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    client = AutoEval(
        # This is the default and can be omitted
        api_token=os.environ.get("LASTMILE_API_KEY"),
    )

    run_evaluation_examples(client)


def basic_example(client: AutoEval) -> None:
    input_df = pd.DataFrame(
        {
            "input": [
                "Can you tell me the weight limit for carry-on bags?",
                "What gate is my flight SA795 departing from?",
                "Can I bring my pet on the plane?",
            ],
            "output": [
                "The weight limit for carry-on bags is 7kg.",
                "Your flight SA795 is departing from JFK at 6:30PM.",
                "Yes, you can bring your pet, but it must fit under the seat in front of you and there is a pet fee.",
            ],
            "ground_truth": [
                "7kg",
                "SA795: JFK Terminal 4, Gate 42, 6:30PM departure",
                "Pets are not allowed on StrikeAir flights.",
            ],
        }
    )

    output_df = client.evaluate_data(input_df, BuiltinMetrics.FAITHFULNESS)
    print(output_df)
    #                                                input                                             output                                      ground_truth  Faithfulness_score
    # 0  Can you tell me the weight limit for carry-on ...         The weight limit for carry-on bags is 7kg.                                               7kg            0.998831
    # 1       What gate is my flight SA795 departing from?  Your flight SA795 is departing from JFK at 6:3...  SA795: JFK Terminal 4, Gate 42, 6:30PM departure            0.998952
    # 2                   Can I bring my pet on the plane?  Yes, you can bring your pet, but it must fit u...        Pets are not allowed on StrikeAir flights.            0.000892


def run_dataset_examples(client: AutoEval) -> None:
    # Create a dataset
    dataset_id = client.upload_dataset(
        name=f"My First Dataset, {NOW_DATE_STRING}",
        description="This is an example dataset",
        file_path="examples/halueval_sample.csv",
    )
    print(f"Successfully created dataset with id {dataset_id}")

    # Download the dataset
    new_dataset = client.download_dataset(dataset_id, "./test-downloaded.csv")
    print(f"Successfully downloaded dataset with {new_dataset.shape[0]} rows")

    # List datasets
    datasets = client.list_datasets()
    print(f"Found {len(datasets)} datasets")

    # List datasets with query filter
    filtered_datasets = client.list_datasets(query="My First Dataset")
    print(f"Found {len(filtered_datasets)} datasets with query filter")

    # Label the dataset with few-shot examples
    print("Labeling dataset with few-shot examples")
    client.label_dataset(
        dataset_id=dataset_id,
        prompt_template=BuiltinMetrics.FAITHFULNESS,
        few_shot_examples=pd.DataFrame(
            {
                "input": ["This is a test input"],
                "output": ["This is a test output"],
                "ground_truth": ["This is a test"],
                "label": [1],
            }
        ),
        wait_for_completion=True,
    )
    print("Successfully labeled dataset")

    # Delete the dataset
    client.delete_dataset(dataset_id)
    print(f"Successfully deleted dataset {dataset_id}")


def run_evaluation_examples(client: AutoEval) -> None:
    # Create eval project
    eval_project = client.create_project(
        name=f"My First Eval Project, {NOW_DATE_STRING}", description="An example eval project"
    )
    client.project_id = eval_project.id

    # List Metrics
    metrics = client.list_metrics()
    print(f"Found {len(metrics)} total metrics: {[m.name or m.id for m in metrics if m.name or m.id]}")

    # Evaluate data
    data_eval = client.evaluate_data(
        data=pd.DataFrame(
            {
                "input": ["This is a test input"],
                "output": ["This is a test output"],
                "ground_truth": ["This is a test"],
            }
        ),
        metrics=[BuiltinMetrics.FAITHFULNESS],
    )
    print(data_eval)

    # Create a dataset to evaluate
    dataset_id = client.upload_dataset(
        name=f"My First Eval Dataset, {NOW_DATE_STRING}",
        description="This is an example eval dataset",
        file_path="examples/halueval_sample.csv",
    )

    # Create an experiment
    experiment = client.create_experiment(
        name=f"My First Eval Experiment, {NOW_DATE_STRING}",
        description="This is an example eval experiment",
        metadata={"chunk_size": 100},
    )
    print(f"Created experiment with id {experiment.id}")

    # Evaluate dataset in the experiment
    dataset_eval = client.evaluate_dataset(
        dataset_id=dataset_id,
        metrics=[BuiltinMetrics.FAITHFULNESS, Metric(name="Relevance")],
        experiment_id=experiment.id,
        metadata={"model": "gpt-4o"},
    )
    print("Dataset Eval: ", dataset_eval)

    # Evaluate run in the experiment
    run_eval = client.create_evaluation_run(
        data=pd.DataFrame(
            {
                "input": ["This is a test input in an experiment"],
                "output": ["This is a test output in an experiment"],
                "ground_truth": ["This is a test in an experiment"],
            }
        ),
        experiment_id=experiment.id,
        metrics=[BuiltinMetrics.FAITHFULNESS, Metric(name="Relevance")],
        metadata={"model": "gpt-3.5-turbo"},
    )
    print("Run Eval: ", run_eval)

    # Run eval outside of an experiment
    standalone_eval = client.create_evaluation_run(
        data=pd.DataFrame(
            {
                "input": ["This is a standalone test input"],
                "output": ["This is a standalone test output"],
                "ground_truth": ["This is a standalone test"],
            }
        ),
        metrics=[Metric(id="cm2plr07q000ipkr4o8qhj4oe")],  # Faithfulness
        metadata={"model": "gpt-4"},
    )
    print("Standalone Eval: ", standalone_eval)


if __name__ == "__main__":
    main()
