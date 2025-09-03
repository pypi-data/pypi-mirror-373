# ezga/io/resume.py
from __future__ import annotations
import os, re
from typing import Optional, Tuple, List
from sage_lib.partition.Partition import Partition

_GEN_DIR_RE = re.compile(r"^gen(\d+)$")

def _list_all_generations(output_path: str) -> List[int]:
    base = os.path.join(output_path, "generation")
    if not os.path.isdir(base):
        return []
    gens: List[int] = []
    for name in os.listdir(base):
        m = _GEN_DIR_RE.match(name)
        if m:
            try:
                gens.append(int(m.group(1)))
            except ValueError:
                pass
    gens.sort()
    return gens

def _load_generation_partition(output_path: str, gen: int) -> Partition:
    dir_path = os.path.join(output_path, "generation", f"gen{gen}", 'config.xyz')
    part = Partition()
    part.read_files(file_location=dir_path, source="xyz", verbose=True)
    return part

def _merge_into_dataset_dedup(population, containers) -> Tuple[int, int]:
    uniques, dups = population.filter_hash_collisions(
        individuals=list(containers), force_rehash=False
    )
    if uniques:
        population.partitions["dataset"].add(uniques)
        for s in uniques:
            population.hash_map.add_structure(s, force_rehash=False)
    return len(uniques), len(dups)

# -------- NEW: read & merge ALL gen{n} folders --------
def resume_from_all_folders(population, ctx, logger) -> bool:
    gens = _list_all_generations(population.output_path)
    if not gens:
        logger.info("Resume(all): no generation folders found; starting fresh.")
        return False

    total_added = total_dups = 0
    for g in gens:
        try:
            part = _load_generation_partition(population.output_path, g)
            added, dups = _merge_into_dataset_dedup(population, part.containers)
            total_added += added
            total_dups  += dups
            logger.info("Resume(all): gen%d → %d unique merged (%d duplicates skipped).", g, added, dups)
        except: pass
    last = gens[-1]
    try:
        ctx.set_generation(last + 1)
    except Exception:
        ctx.generation = last + 1
    ctx.prev_future = None
    ctx.break_early = False
    try:
        ctx.clear_timers()
    except Exception:
        pass

    logger.info(
        "Resume(all): merged %d unique total (%d duplicates) from %d generations. "
        "Continuing at generation %d.",
        total_added, total_dups, len(gens), ctx.generation
    )
    return True

# Existing single-folder resume (kept for other modes)
def resume_from_folders(population, ctx, logger) -> bool:
    gens = _list_all_generations(population.output_path)
    if not gens:
        logger.info("Resume: no generation folders found; starting fresh.")
        return False
    last = gens[-1]
    part = _load_generation_partition(population.output_path, last)
    added, dups = _merge_into_dataset_dedup(population, part.containers)
    logger.info(
        "Resume: merged %d unique structures (ignored %d duplicates) from gen%d into dataset.",
        added, dups, last
    )
    try:
        ctx.set_generation(last + 1)
    except Exception:
        ctx.generation = last + 1
    ctx.prev_future = None
    ctx.break_early = False
    try:
        ctx.clear_timers()
    except Exception:
        pass
    return True

# Entry point used by the engine
def resume_if_possible(population, ctx, logger, *, enabled: bool = True, mode: str = "folders_all") -> bool:
    if not enabled:
        logger.info("Resume disabled by config; starting fresh.")
        return False
    if mode == "folders_all":
        return resume_from_all_folders(population, ctx, logger)
    if mode == "folders":
        return resume_from_folders(population, ctx, logger)
    elif mode == "snapshot":
        from ..io.snapshot_recorder import GenerationSnapshotWriter
        try:
            state = GenerationSnapshotWriter.load_latest(population.output_path, tag="full")
        except Exception:
            return False
        population = state["population"]
        ctx = state["ctx"]
        logger.info("Resumed from snapshot at generation %d.", ctx.generation)
        ctx.prev_future = None
        ctx.break_early = False
        return True
    else:
        logger.warning("Unknown resume mode '%s'; skipping resume.", mode)
        return False
