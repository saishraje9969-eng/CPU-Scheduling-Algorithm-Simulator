"""CPU scheduling algorithms for OSLab.

All times are integer time units. Lower priority numbers mean higher priority.
Algorithms: FCFS, SJF (non-preemptive), SRTF (preemptive),
Priority (non-preemptive), and Round Robin.
"""

from collections import deque


def _validate(processes):
    if not processes:
        raise ValueError("Add at least one process before running a simulation.")

    seen = set()
    normalized = []
    for index, p in enumerate(processes, start=1):
        pid = str(p.get("pid", f"P{index}")).strip()
        if not pid:
            raise ValueError(f"Process {index}: process ID cannot be empty.")
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        seen.add(pid)

        try:
            arrival = int(p["arrival"])
            burst = int(p["burst"])
            priority = int(p.get("priority", 1))
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"{pid}: arrival, burst, and priority must be integers.")

        if arrival < 0:
            raise ValueError(f"{pid}: arrival time cannot be negative.")
        if burst <= 0:
            raise ValueError(f"{pid}: burst time must be greater than zero.")
        normalized.append({
            "pid": pid, "arrival": arrival, "burst": burst, "priority": priority
        })
    return normalized


def _coalesce(segments):
    """Merge adjacent segments for the same process (including idle)."""
    merged = []
    for seg in segments:
        if seg["end"] <= seg["start"]:
            continue
        if merged and merged[-1]["pid"] == seg["pid"] and merged[-1]["end"] == seg["start"]:
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(dict(seg))
    return merged


def _finish(processes, segments, algorithm):
    segments = _coalesce(segments)
    completion = {}
    first_start = {}
    for seg in segments:
        if seg["pid"] != "IDLE":
            first_start.setdefault(seg["pid"], seg["start"])
            completion[seg["pid"]] = seg["end"]

    rows = []
    for p in processes:
        pid = p["pid"]
        ct = completion[pid]
        tat = ct - p["arrival"]
        wt = tat - p["burst"]
        rt = first_start[pid] - p["arrival"]
        rows.append({
            **p, "completion": ct, "turnaround": tat,
            "waiting": wt, "response": rt
        })

    start_time = min(p["arrival"] for p in processes)
    end_time = max(r["completion"] for r in rows)
    elapsed = end_time - start_time
    busy = sum(s["end"] - s["start"] for s in segments if s["pid"] != "IDLE")
    metrics = {
        "average_waiting": sum(r["waiting"] for r in rows) / len(rows),
        "average_turnaround": sum(r["turnaround"] for r in rows) / len(rows),
        "average_response": sum(r["response"] for r in rows) / len(rows),
        "cpu_utilization": (busy / elapsed * 100) if elapsed else 0.0,
        "throughput": (len(rows) / elapsed) if elapsed else 0.0,
        "total_time": elapsed,
        "busy_time": busy,
    }
    return {
        "algorithm": algorithm,
        "processes": sorted(rows, key=lambda r: (r["arrival"], r["pid"])),
        "segments": segments,
        "metrics": metrics,
    }


def fcfs(processes):
    ps = sorted(_validate(processes), key=lambda p: (p["arrival"], p["pid"]))
    time = 0
    segments = []
    for p in ps:
        if time < p["arrival"]:
            segments.append({"pid": "IDLE", "start": time, "end": p["arrival"]})
            time = p["arrival"]
        segments.append({"pid": p["pid"], "start": time, "end": time + p["burst"]})
        time += p["burst"]
    return _finish(ps, segments, "FCFS")


def sjf(processes):
    ps = _validate(processes)
    remaining = {p["pid"]: p["burst"] for p in ps}
    by_id = {p["pid"]: p for p in ps}
    done = set()
    time = 0
    segments = []
    while len(done) < len(ps):
        available = [p for p in ps if p["pid"] not in done and p["arrival"] <= time]
        if not available:
            next_arrival = min(p["arrival"] for p in ps if p["pid"] not in done)
            if time < next_arrival:
                segments.append({"pid": "IDLE", "start": time, "end": next_arrival})
                time = next_arrival
            continue
        p = min(available, key=lambda x: (x["burst"], x["arrival"], x["pid"]))
        segments.append({"pid": p["pid"], "start": time, "end": time + p["burst"]})
        time += p["burst"]
        done.add(p["pid"])
    return _finish(ps, segments, "SJF (Non-preemptive)")


def priority_scheduling(processes):
    ps = _validate(processes)
    done = set()
    time = 0
    segments = []
    while len(done) < len(ps):
        available = [p for p in ps if p["pid"] not in done and p["arrival"] <= time]
        if not available:
            next_arrival = min(p["arrival"] for p in ps if p["pid"] not in done)
            if time < next_arrival:
                segments.append({"pid": "IDLE", "start": time, "end": next_arrival})
                time = next_arrival
            continue
        p = min(available, key=lambda x: (x["priority"], x["arrival"], x["pid"]))
        segments.append({"pid": p["pid"], "start": time, "end": time + p["burst"]})
        time += p["burst"]
        done.add(p["pid"])
    return _finish(ps, segments, "Priority (Non-preemptive)")


def srtf(processes):
    ps = _validate(processes)
    remaining = {p["pid"]: p["burst"] for p in ps}
    by_id = {p["pid"]: p for p in ps}
    completed = set()
    time = min(p["arrival"] for p in ps)
    segments = []

    while len(completed) < len(ps):
        available = [
            p for p in ps
            if p["arrival"] <= time and p["pid"] not in completed and remaining[p["pid"]] > 0
        ]
        if not available:
            next_arrival = min(p["arrival"] for p in ps if p["pid"] not in completed and remaining[p["pid"]] > 0)
            segments.append({"pid": "IDLE", "start": time, "end": next_arrival})
            time = next_arrival
            continue

        p = min(available, key=lambda x: (remaining[x["pid"]], x["arrival"], x["pid"]))
        segments.append({"pid": p["pid"], "start": time, "end": time + 1})
        remaining[p["pid"]] -= 1
        time += 1
        if remaining[p["pid"]] == 0:
            completed.add(p["pid"])

    return _finish(ps, segments, "SRTF (Preemptive)")


def round_robin(processes, quantum):
    ps = _validate(processes)
    try:
        quantum = int(quantum)
    except (TypeError, ValueError):
        raise ValueError("Round Robin time quantum must be a positive integer.")
    if quantum <= 0:
        raise ValueError("Round Robin time quantum must be greater than zero.")

    ps = sorted(ps, key=lambda p: (p["arrival"], p["pid"]))
    remaining = {p["pid"]: p["burst"] for p in ps}
    time = min(p["arrival"] for p in ps)
    i = 0
    ready = deque()
    segments = []
    completed = set()

    while len(completed) < len(ps):
        while i < len(ps) and ps[i]["arrival"] <= time:
            ready.append(ps[i])
            i += 1

        if not ready:
            if i < len(ps):
                next_time = ps[i]["arrival"]
                if time < next_time:
                    segments.append({"pid": "IDLE", "start": time, "end": next_time})
                    time = next_time
                continue
            break

        p = ready.popleft()
        run_for = min(quantum, remaining[p["pid"]])
        start = time
        end = time + run_for
        segments.append({"pid": p["pid"], "start": start, "end": end})
        time = end
        remaining[p["pid"]] -= run_for

        # Enqueue processes that arrived while this process was running.
        while i < len(ps) and ps[i]["arrival"] <= time:
            ready.append(ps[i])
            i += 1

        if remaining[p["pid"]] > 0:
            ready.append(p)
        else:
            completed.add(p["pid"])

    return _finish(ps, segments, f"Round Robin (q={quantum})")


ALGORITHMS = {
    "FCFS": fcfs,
    "SJF": sjf,
    "SRTF": srtf,
    "Priority": priority_scheduling,
}


def run_algorithm(name, processes, quantum=2):
    if name == "Round Robin":
        return round_robin(processes, quantum)
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown scheduling algorithm: {name}")
    return ALGORITHMS[name](processes)


def compare_algorithms(processes, quantum=2):
    results = [
        fcfs(processes),
        sjf(processes),
        srtf(processes),
        priority_scheduling(processes),
        round_robin(processes, quantum),
    ]
    return results
