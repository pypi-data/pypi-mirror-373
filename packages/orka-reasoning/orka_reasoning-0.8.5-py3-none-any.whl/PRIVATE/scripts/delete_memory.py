# mypy: ignore-errors
import asyncio
import os
import sys
from datetime import UTC, datetime
from typing import Any, Dict, List, Set, Tuple

import redis.asyncio as redis

# Add the parent directory to sys.path to import orka modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from orka.memory.redis_logger import RedisMemoryLogger
from orka.memory.redisstack_logger import RedisStackMemoryLogger
from orka.memory_logger import create_memory_logger


async def cleanup_expired_memories() -> int:
    """
    Perform proper memory decay cleanup using the official memory loggers.
    Returns the number of cleaned memories.
    """
    print("=== Memory Decay Cleanup ===")

    try:
        # Create both RedisStack and Legacy Redis loggers
        loggers = []

        # RedisStack logger (port 6380)
        redisstack_logger = create_memory_logger(
            backend="redisstack",
            redis_url="redis://localhost:6380/0",
            decay_config={
                "enabled": True,
                "default_short_term_hours": 1.0,
                "default_long_term_hours": 24.0,
                "check_interval_minutes": 30,
            },
        )
        loggers.append(("RedisStack (6380)", redisstack_logger))

        # Legacy Redis logger (port 6379)
        redis_logger = create_memory_logger(
            backend="redis",
            redis_url="redis://localhost:6379/0",
            decay_config={
                "enabled": True,
                "default_short_term_hours": 1.0,
                "default_long_term_hours": 24.0,
                "check_interval_minutes": 30,
            },
        )
        loggers.append(("Legacy Redis (6379)", redis_logger))

        total_cleaned = 0
        for name, logger in loggers:
            print(f"\nCleaning {name}...")
            try:
                stats = logger.cleanup_expired_memories(dry_run=False)
                cleaned = stats.get("cleaned", 0)
                total_checked = stats.get("total_checked", 0)
                errors = stats.get("errors", [])

                print(f"Results for {name}:")
                print(f"  - Total checked: {total_checked}")
                print(f"  - Cleaned: {cleaned}")
                print(f"  - Errors: {len(errors)}")

                if errors:
                    print("  - Error details:")
                    for error in errors[:5]:  # Show first 5 errors
                        print(f"    * {error}")

                total_cleaned += cleaned

            except Exception as e:
                print(f"Error cleaning {name}: {e}")

            finally:
                try:
                    logger.close()
                except Exception:
                    pass

        print(f"\n[OK] Memory decay cleanup completed. Total cleaned: {total_cleaned}\n")
        return total_cleaned

    except Exception as e:
        print(f"Error during memory decay cleanup: {e}")
        return 0


async def delete_memories() -> int:
    """
    Delete all OrKa-related memory keys from both Redis instances.
    Returns the number of deleted keys.
    """
    print("=== Full Memory Deletion ===")

    # Connect to both Redis instances
    redis_instances: List[Tuple[str, str, redis.Redis]] = []
    total_deleted = 0

    try:
        # Initialize Redis connections
        for redis_url, description in [
            ("redis://localhost:6379", "Legacy Redis (6379)"),
            ("redis://localhost:6380", "RedisStack (6380)"),
        ]:
            try:
                client = redis.from_url(redis_url, decode_responses=True)
                await client.ping()
                redis_instances.append((redis_url, description, client))
                print(f"[OK] Connected to {description}")
            except Exception as e:
                print(f"[SKIP] Cannot connect to {description}: {e}")

        # Define patterns for different types of memory keys
        patterns = [
            # Legacy memory streams
            "orka:memory:*",
            "orka:memory:stream:*",
            "orka:memory:index:*",
            # RedisStack memory entries
            "orka_memory:*",
            "orka_memory_idx:*",
            "orka_memory_index:*",
            # Vector memories and indices
            "mem:*",
            "memory:*",
            "vector:*",
            "idx:*",
            "index:*",
            # Fork and orchestration keys
            "fork:*",
            "orka:fork:*",
            "orka_fork:*",
            # Search indices
            "enhanced_memory_idx",
            "orka_enhanced_memory",
            "orka_vector_index",
            # Any other OrKa keys
            "orka:*",
            "orka_*",
            # Catch-all patterns
            "*memory*orka*",
            "*orka*memory*",
        ]

        # Process each Redis instance
        for redis_url, description, client in redis_instances:
            print(f"\n--- Cleaning {description} ---")
            instance_keys: Set[str] = set()

            # Collect keys matching our patterns
            for pattern in patterns:
                try:
                    keys = await client.keys(pattern)
                    instance_keys.update(keys)
                except Exception as e:
                    print(f"[WARN] Error searching pattern {pattern}: {e}")

            if not instance_keys:
                print(f"No OrKa memory keys found in {description}.")
                continue

            print(f"Found {len(instance_keys)} OrKa-related keys in {description}:")

            # Show sample of keys (first 20)
            keys_to_show = sorted(instance_keys)[:20]
            for key in keys_to_show:
                try:
                    key_type = await client.type(key)
                    print(f"  - {key} (type: {key_type})")
                except Exception:
                    print(f"  - {key} (unknown type)")

            if len(instance_keys) > 20:
                print(f"  ... and {len(instance_keys) - 20} more keys")

            # Delete keys in batches
            batch_size = 100
            key_list = list(instance_keys)
            deleted_count = 0
            failed_count = 0

            for i in range(0, len(key_list), batch_size):
                batch = key_list[i : i + batch_size]
                try:
                    # Use pipeline for batch deletion
                    pipe = client.pipeline()
                    for key in batch:
                        pipe.delete(key)
                    results = await pipe.execute()

                    batch_deleted = sum(1 for result in results if result)
                    batch_failed = len(results) - batch_deleted

                    deleted_count += batch_deleted
                    failed_count += batch_failed

                    print(
                        f"[OK] Batch {i // batch_size + 1}: Deleted {batch_deleted}, Failed {batch_failed}"
                    )

                except Exception as e:
                    failed_count += len(batch)
                    print(f"[ERROR] Batch deletion failed: {e}")

            print(f"\nDeletion complete for {description}!")
            print(f"Successfully deleted: {deleted_count} keys")
            if failed_count > 0:
                print(f"Failed to delete: {failed_count} keys")

            # Verify deletion
            remaining_keys: Set[str] = set()
            for pattern in patterns:
                try:
                    keys = await client.keys(pattern)
                    remaining_keys.update(keys)
                except Exception:
                    pass

            if remaining_keys:
                print(f"\nWarning: {len(remaining_keys)} keys still remain in {description}:")
                for key in sorted(remaining_keys)[:10]:
                    print(f"  - {key}")
                if len(remaining_keys) > 10:
                    print(f"  ... and {len(remaining_keys) - 10} more")
            else:
                print(
                    f"\n[OK] All OrKa memory keys have been successfully deleted from {description}!"
                )

            total_deleted += deleted_count

    except Exception as e:
        print(f"Error during deletion process: {e}")

    finally:
        # Close Redis connections
        for _, _, client in redis_instances:
            try:
                await client.aclose()
            except Exception:
                pass

    return total_deleted


async def main() -> None:
    """Main function that performs both decay cleanup and full deletion."""
    print("OrKa Memory Cleanup Script")
    print("=" * 50)

    # Step 1: Perform proper memory decay cleanup first
    decay_deleted = await cleanup_expired_memories()

    # Step 2: Perform full deletion of all remaining OrKa keys
    full_deleted = await delete_memories()

    print("\n" + "=" * 50)
    print("CLEANUP SUMMARY")
    print(f"Expired memories removed by decay cleanup: {decay_deleted}")
    print(f"Total keys removed by full deletion: {full_deleted}")
    print("[OK] Memory cleanup completed successfully!")

    if full_deleted == 0 and decay_deleted == 0:
        print("\n[INFO] No memories found to delete. System is already clean!")


if __name__ == "__main__":
    asyncio.run(main())
