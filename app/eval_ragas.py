"""
RAG System Evaluation Module

Evaluates RAG system performance using RAGAS framework metrics:
faithfulness, answer relevancy, context precision, and context recall.
"""

import asyncio
import json
import os
import pandas as pd
from dotenv import load_dotenv
from ragas import evaluate
from ragas import SingleTurnSample, EvaluationDataset
from langchain_openai import ChatOpenAI
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.run_config import RunConfig
from .rag import answer_with_docs_async
from .constants import DEFAULT_OPENAI_MODEL

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize OpenAI LLM for RAGAS evaluation
oai_llm = ChatOpenAI(model=DEFAULT_OPENAI_MODEL)

def load_jsonl(path):
    """Load test dataset from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def print_eval_res(eval_result):
    """Display evaluation results in tabular format with averages."""
    scores = eval_result.scores
    
    # Print header
    eval_str = ' | Q | '
    for k in scores[0].keys():
        eval_str = eval_str + str(k) + ' | '
    print(eval_str)
    
    # Print scores per question
    for i, score in enumerate(scores):
        eval_str = ' | ' + str(i + 1) + ' | '
        for k in score.keys():
            eval_str = eval_str + str(score[k]) + ' | '
        print(eval_str)
    
    # Print averages
    res = eval_result.to_pandas()
    means = res.mean(numeric_only=True).to_dict()
    print("\n📈 Averages:")
    for k, v in means.items():
        print(f"- {k}: {v:.3f}")

async def evaluate_rag_system(test_path=None):
    """
    Evaluate RAG system using RAGAS framework.
    
    Queries RAG system with test questions and evaluates responses using
    faithfulness, answer_relevancy, context_precision, and context_recall metrics.
    
    Args:
        test_path (str, optional): Path to JSON test dataset. Defaults to 'seed/qna_test.json'.
    """
    # Load test dataset
    if test_path is None:
        test_path = os.path.join(os.path.dirname(__file__), '..', 'seed', 'qna_test.json')
    
    test_data = load_jsonl(test_path)
    results = []

    # Query RAG system for each test question
    for item in test_data:
        question = item["question"]
        reference_answer = item["answer"]
        
        answer, sources, contexts = await answer_with_docs_async(question)

        results.append(
            SingleTurnSample(
                user_input=question,
                response=answer,
                reference=reference_answer,
                retrieved_contexts=contexts,
            )
        )
    
    # Run RAGAS evaluation
    ds = EvaluationDataset(results)
    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
    run_config = RunConfig(max_workers=16, timeout=180)
    eval_result = evaluate(dataset=ds, metrics=metrics, llm=oai_llm, run_config=run_config)
    
    # Display results
    print("RAGAS Evaluation Results:")
    print_eval_res(eval_result)

if __name__ == "__main__":
    # Run evaluation: python -m app.eval_ragas
    asyncio.run(evaluate_rag_system())
