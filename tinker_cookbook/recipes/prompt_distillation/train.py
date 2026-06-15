"""
CLI for prompt distillation training.
"""

import asyncio
import os
from datetime import datetime

import chz
from tinker_cookbook import cli_utils, model_info
from tinker_cookbook.recipes.prompt_distillation.eval import (
    PromptDistillationAccuracyEvaluatorBuilder,
)
from tinker_cookbook.renderers import TrainOnWhat
from tinker_cookbook.supervised import train
from tinker_cookbook.supervised.data import FromConversationFileBuilder
from tinker_cookbook.supervised.types import ChatDatasetBuilderCommonConfig
from tinker_cookbook.utils.lr_scheduling import LRSchedule
from tinker_cookbook.hyperparam_utils import get_lr

student_model = "Qwen/Qwen3-30B-A3B"

@chz.chz
class CLIConfig:
    # Required parameters
    file_path: str = "tinker_cookbook/training_data/prompt_distillation_lang.jsonl"
    log_path: str | None = None
    model_name: str = student_model
    load_checkpoint_path: str | None = None

    # Training parameters
    learning_rate: float = get_lr(student_model)
    lr_schedule: LRSchedule = "linear"
    num_epochs: int = 1

    # Model parameters
    lora_rank: int = 32

    # Infrastructure parameters
    base_url: str | None = None

    # Checkpointing and evaluation
    save_every: int = 20
    eval_every: int = 5

    # Dataset-specific parameters
    renderer_name: str | None = None
    ## how to build the training token mask
    train_on_what: TrainOnWhat = TrainOnWhat.LAST_ASSISTANT_MESSAGE
    max_length: int = 256
    batch_size: int = 64
    test_size: int = 165

    # Logging parameters
    wandb_project: str | None = None
    wandb_name: str | None = None

    behavior_if_log_dir_exists: cli_utils.LogdirBehavior = "ask"


def cli_main(cli_config: CLIConfig):
    # Build full config
    model_name = cli_config.model_name.replace("/", "-")
    date_and_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
    run_name = f"prompt_distillation-{model_name}-{cli_config.lora_rank}rank-{cli_config.learning_rate}lr-{cli_config.batch_size}batch-{date_and_time}"

    if cli_config.log_path is not None:
        log_path = cli_config.log_path
    else:
        log_path = f"tinker_cookbook/training_logs/prompt_distillation/{run_name}"

    if cli_config.wandb_name is not None:
        wandb_name = cli_config.wandb_name
    else:
        wandb_name = run_name

    # make sure the data file exists
    if not os.path.exists(cli_config.file_path):
        raise FileNotFoundError(f"Data file not found: {cli_config.file_path}")

    cli_utils.check_log_dir(log_path, behavior_if_exists=cli_config.behavior_if_log_dir_exists)

    renderer_name = cli_config.renderer_name or model_info.get_recommended_renderer_name(
        cli_config.model_name
    )

    common_config = ChatDatasetBuilderCommonConfig(
        model_name_for_tokenizer=cli_config.model_name,
        renderer_name=renderer_name,
        max_length=cli_config.max_length,
        batch_size=cli_config.batch_size,
        train_on_what=cli_config.train_on_what,
    )

    dataset = FromConversationFileBuilder(
        common_config=common_config,
        file_path=cli_config.file_path,
        test_size=cli_config.test_size,
    )

    evaluator_builders = []
    if cli_config.test_size > 0:
        evaluator_builders.append(
            PromptDistillationAccuracyEvaluatorBuilder(
                file_path=cli_config.file_path,
                model_name_for_tokenizer=cli_config.model_name,
                renderer_name=renderer_name,
                test_size=cli_config.test_size,
            )
        )

    config = train.Config(
        log_path=log_path,
        model_name=cli_config.model_name,
        load_checkpoint_path=cli_config.load_checkpoint_path,
        dataset_builder=dataset,
        learning_rate=cli_config.learning_rate,
        lr_schedule=cli_config.lr_schedule,
        num_epochs=cli_config.num_epochs,
        base_url=cli_config.base_url,
        wandb_project=cli_config.wandb_project,
        wandb_name=wandb_name,
        lora_rank=cli_config.lora_rank,
        save_every=cli_config.save_every,
        eval_every=cli_config.eval_every,
        evaluator_builders=evaluator_builders,
    )
    asyncio.run(train.main(config))


if __name__ == "__main__":
    chz.nested_entrypoint(cli_main)
