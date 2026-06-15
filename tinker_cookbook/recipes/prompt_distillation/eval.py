import asyncio
import json
import logging
import re
from dataclasses import dataclass

import chz
import datasets
import tinker

from tinker_cookbook import renderers
from tinker_cookbook.eval.evaluators import SamplingClientEvaluator
from tinker_cookbook.tokenizer_utils import get_tokenizer

_LABEL_PATTERN = re.compile(r"\b(ar|de|el|en|es|fr|hi|ru|tr|ur|vi|zh|ot)\b", re.IGNORECASE)
logger = logging.getLogger(__name__)


def _extract_label(text: str) -> str | None:
    match = _LABEL_PATTERN.search(text.strip())
    if match is None:
        return None
    return match.group(1).lower()


@dataclass
class _EvalExample:
    prompt: tinker.ModelInput
    gold_label: str


class PromptDistillationAccuracyEvaluator(SamplingClientEvaluator):
    def __init__(
        self,
        examples: list[_EvalExample],
        model_name_for_tokenizer: str,
        renderer_name: str,
        max_tokens: int = 4,
        max_parallel_tasks: int = 16,
        request_timeout_s: float = 30.0,
    ):
        self.examples = examples
        self.max_tokens = max_tokens
        self.max_parallel_tasks = max_parallel_tasks
        self.request_timeout_s = request_timeout_s
        self.tokenizer = get_tokenizer(model_name_for_tokenizer)
        self.renderer = renderers.get_renderer(renderer_name, self.tokenizer)

    async def __call__(self, sampling_client: tinker.SamplingClient) -> dict[str, float]:
        if not self.examples:
            return {
                "test/accuracy": 0.0,
                "test/pred_invalid_rate": 1.0,
                "test/pred_timeout_rate": 0.0,
            }

        sampling_params = tinker.SamplingParams(
            max_tokens=self.max_tokens,
            temperature=0.0,
            top_p=1.0,
            top_k=-1,
            stop=self.renderer.get_stop_sequences(),
        )
        semaphore = asyncio.Semaphore(self.max_parallel_tasks)

        async def evaluate_one(example: _EvalExample) -> tuple[bool, bool, bool]:
            async with semaphore:
                try:
                    response = await asyncio.wait_for(
                        sampling_client.sample_async(
                            prompt=example.prompt, sampling_params=sampling_params, num_samples=1
                        ),
                        timeout=self.request_timeout_s,
                    )
                except TimeoutError:
                    return False, True, True
                except Exception:
                    logger.exception("Accuracy eval sampling request failed")
                    return False, True, False
            pred_text = self.tokenizer.decode(response.sequences[0].tokens)
            pred_label = _extract_label(pred_text)
            if pred_label is None:
                return False, True, False
            return pred_label == example.gold_label, False, False

        tasks = [asyncio.create_task(evaluate_one(example)) for example in self.examples]
        num_correct = 0
        num_invalid = 0
        num_timeout = 0
        total = len(tasks)
        completed = 0

        try:
            for finished_task in asyncio.as_completed(tasks):
                correct, invalid, timed_out = await finished_task
                num_correct += int(correct)
                num_invalid += int(invalid)
                num_timeout += int(timed_out)
                completed += 1
                if completed % 20 == 0 or completed == total:
                    logger.info("Prompt distillation eval progress: %s/%s", completed, total)
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()

        return {
            "test/accuracy": num_correct / total,
            "test/pred_invalid_rate": num_invalid / total,
            "test/pred_timeout_rate": num_timeout / total,
        }


@chz.chz
class PromptDistillationAccuracyEvaluatorBuilder:
    file_path: str
    model_name_for_tokenizer: str
    renderer_name: str
    test_size: int
    n_eval: int | None = 64
    shuffle_seed: int = 0
    max_tokens: int = 4
    max_parallel_tasks: int = 16
    request_timeout_s: float = 30.0

    def __call__(self) -> PromptDistillationAccuracyEvaluator:
        if self.test_size <= 0:
            return PromptDistillationAccuracyEvaluator(
                examples=[],
                model_name_for_tokenizer=self.model_name_for_tokenizer,
                renderer_name=self.renderer_name,
                max_tokens=self.max_tokens,
                max_parallel_tasks=self.max_parallel_tasks,
                request_timeout_s=self.request_timeout_s,
            )

        tokenizer = get_tokenizer(self.model_name_for_tokenizer)
        renderer = renderers.get_renderer(self.renderer_name, tokenizer)

        with open(self.file_path, encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
        dataset = datasets.Dataset.from_list(rows).shuffle(seed=self.shuffle_seed)
        test_rows = dataset.take(min(self.test_size, len(dataset))).to_list()
        if self.n_eval is not None:
            test_rows = test_rows[: min(self.n_eval, len(test_rows))]

        eval_examples: list[_EvalExample] = []
        for row in test_rows:
            messages = row.get("messages", [])
            assistant_indices = [
                idx for idx, message in enumerate(messages) if message.get("role") == "assistant"
            ]
            if not assistant_indices:
                continue

            target_idx = assistant_indices[-1]
            target_content = messages[target_idx].get("content", "")
            if not isinstance(target_content, str):
                continue

            gold_label = _extract_label(target_content)
            if gold_label is None:
                continue

            prompt_messages = messages[:target_idx]
            prompt = renderer.build_generation_prompt(prompt_messages, role="assistant")
            eval_examples.append(_EvalExample(prompt=prompt, gold_label=gold_label))

        return PromptDistillationAccuracyEvaluator(
            examples=eval_examples,
            model_name_for_tokenizer=self.model_name_for_tokenizer,
            renderer_name=self.renderer_name,
            max_tokens=self.max_tokens,
            max_parallel_tasks=self.max_parallel_tasks,
            request_timeout_s=self.request_timeout_s,
        )
