"""Batch-delete saved checkpoints on Tinker via the REST API.

The Tinker API has no single batch-delete endpoint, so this script lists your
checkpoints (either across all training runs or for a single run) and deletes
them with concurrent `delete_checkpoint` calls.

By default it runs in dry-run mode and only prints what *would* be deleted.
Pass --execute to actually delete.

Examples:
    # Show everything you own (no deletes)
    python -m tinker_cookbook.scripts.delete_checkpoints

    # Delete all sampler checkpoints for one run
    python -m tinker_cookbook.scripts.delete_checkpoints \
        --run-id my-run-id --type sampler --execute

    # Delete every training checkpoint you own (careful!)
    python -m tinker_cookbook.scripts.delete_checkpoints \
        --type training --execute
"""

import argparse
import logging
from zoneinfo import ZoneInfo

import tinker

logger = logging.getLogger(__name__)

PACIFIC = ZoneInfo("America/Los_Angeles")


def run_id_from_path(tinker_path: str) -> str:
    """Extract the training run id from a tinker:// checkpoint path."""
    return tinker_path.removeprefix("tinker://").split("/", 1)[0]


def format_pt(dt) -> str:
    """Format a tz-aware datetime in Pacific Time, human-readable."""
    if dt is None:
        return "?"
    return dt.astimezone(PACIFIC).strftime("%Y-%m-%d %I:%M %p %Z")


def base_model_for_run(rest_client, run_id: str, cache: dict) -> str:
    """Look up (and cache) the base model for a training run."""
    if run_id not in cache:
        try:
            tr = rest_client.get_training_run(run_id).result()
            cache[run_id] = tr.base_model
        except Exception:
            cache[run_id] = "?"
    return cache[run_id]


def list_all_user_checkpoints(rest_client, page_size: int = 100):
    """Page through every checkpoint owned by the current user."""
    checkpoints = []
    offset = 0
    while True:
        resp = rest_client.list_user_checkpoints(limit=page_size, offset=offset).result()
        checkpoints.extend(resp.checkpoints)
        cursor = resp.cursor
        if not cursor or cursor.offset + cursor.limit >= cursor.total_count:
            break
        offset += page_size
    return checkpoints


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--run-id",
        default=None,
        help="Only consider checkpoints for this training run. Omit to scan all your runs.",
    )
    parser.add_argument(
        "--type",
        choices=["training", "sampler"],
        default=None,
        help="Only delete checkpoints of this type. Omit to include both.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete. Without this flag the script only prints (dry run).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Pagination size when listing all user checkpoints (default 100).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    rest_client = tinker.ServiceClient().create_rest_client()

    if args.run_id:
        checkpoints = rest_client.list_checkpoints(args.run_id).result().checkpoints
    else:
        checkpoints = list_all_user_checkpoints(rest_client, page_size=args.page_size)

    if args.type:
        checkpoints = [c for c in checkpoints if c.checkpoint_type == args.type]

    if not checkpoints:
        logger.info("No matching checkpoints found.")
        return

    total_bytes = sum(getattr(c, "size_bytes", 0) or 0 for c in checkpoints)
    logger.info(
        f"{'Would delete' if not args.execute else 'Deleting'} "
        f"{len(checkpoints)} checkpoint(s), {total_bytes / 1e9:.2f} GB total:"
    )
    base_model_cache: dict = {}
    for c in checkpoints:
        gb = (c.size_bytes or 0) / 1e9
        base_model = base_model_for_run(rest_client, run_id_from_path(c.tinker_path), base_model_cache)
        logger.info(
            f"  [{c.checkpoint_type:8}] {gb:6.2f} GB  {format_pt(c.time):>22}  "
            f"{base_model:24}  {c.tinker_path}"
        )

    if not args.execute:
        logger.info("\nDry run only. Re-run with --execute to delete.")
        return

    # Fire off deletes concurrently, then wait + surface errors.
    futures = [rest_client.delete_checkpoint_from_tinker_path(c.tinker_path) for c in checkpoints]
    failures = 0
    for c, f in zip(checkpoints, futures):
        try:
            f.result()
        except Exception as e:
            failures += 1
            logger.error(f"  FAILED {c.tinker_path}: {e}")

    deleted = len(checkpoints) - failures
    logger.info(f"\nDeleted {deleted} checkpoint(s); {failures} failure(s).")


if __name__ == "__main__":
    main()
