def select_shard(lines, shard_index, shard_count):
    """Line number (counting from 0) % shard_count == shard_index."""
    if not (0 <= shard_index < shard_count):
        raise ValueError("SHARD_INDEX must be in [0, SHARD_COUNT)")
    return [ln for i, ln in enumerate(lines) if i % shard_count == shard_index]
