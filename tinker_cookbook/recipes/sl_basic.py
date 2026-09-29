import chz
import sys
from tinker_cookbook import cli_utils, model_info
from tinker_cookbook.recipes.chat_sl import chat_datasets
from tinker_cookbook.renderers import TrainOnWhat
from tinker_cookbook.supervised import train
from tinker_cookbook.supervised.data import FromConversationFileBuilder
from tinker_cookbook.supervised.types import ChatDatasetBuilderCommonConfig
import asyncio


def build_config_blueprint() -> chz.Blueprint[train.Config]:
    # model_name = "Qwen/Qwen3-8B"
    model_name = "Qwen/Qwen3.5-9B-Base"
    renderer_name = model_info.get_recommended_renderer_name(model_name)
    common_config = ChatDatasetBuilderCommonConfig(
        model_name_for_tokenizer=model_name,
        renderer_name=renderer_name,
        max_length=32768,
        batch_size=128,
        train_on_what=TrainOnWhat.ALL_ASSISTANT_MESSAGES,
    )
    dataset = chat_datasets.NoRobotsBuilder(common_config=common_config)
    if 0:  # To swap in your own dataset:
        dataset = FromConversationFileBuilder(
            common_config=common_config, file_path="/path/to/your/dataset.jsonl"
        )
        # ^^^ Create a dataset from a JSONL file in the same format as
        # tinker_cookbook/example_data/conversations.jsonl
    return chz.Blueprint(train.Config).apply(
        {
            "log_path": r"tinker_cookbook\training_logs\sl_basic_NoRobots_qwen3.5-9B-base",
            "model_name": model_name,
            "dataset_builder": dataset,
            "learning_rate": 2e-4,
            "lr_schedule": "linear",
            "num_epochs": 1,
            "eval_every": 8,
            "save_every": 8,
        }
    )


def main(config: train.Config):
    # Avoid clobbering log dir from your previous run:
    cli_utils.check_log_dir(config.log_path, behavior_if_exists="ask")
    asyncio.run(train.main(config))


if __name__ == "__main__":
    if sys.platform == "win32":
        # The default Proactor loop can crash the tinker client's background thread
        # (WinError 995 -> InvalidStateError); the selector loop avoids that bug.
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    blueprint = build_config_blueprint()
    blueprint.make_from_argv(sys.argv[1:])
    main(blueprint.make())
