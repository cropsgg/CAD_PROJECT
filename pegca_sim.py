# pegca_sim.py
# Energy-Efficient VM Consolidation (PEGCA) — single-file simulator
# Follow the spec exactly. Do not add libraries or extra features.

import math
import random
import statistics as stats
from typing import List, Dict, Tuple

# -----------------------------
# Config (edit values only if asked)
# -----------------------------
class Config:
    def __init__(
        self,
        alpha: float = 0.6,
        low_usage_threshold: float = 30.0,  # CPU %
        target_util: float = 0.80,          # fraction of capacity
        hi_watermark: float = 0.90,         # fraction of capacity
        dt_hours: float = 1.0,
        cycles: int = 24,
        n_hosts: int = 20,
        n_vms: int = 120,
        seed: int = 7,
    ):
        self.alpha = alpha
        self.low_usage_threshold = low_usage_threshold
        self.target_util = target_util
        self.hi_watermark = hi_watermark
        self.dt_hours = dt_hours
        self.cycles = cycles
        self.n_hosts = n_hosts
        self.n_vms = n_vms
        self.seed = seed

# -----------------------------
# Data structures
# -----------------------------
class Host:
    def __init__(self, hid: int, cpu_cap: float = 100.0, mem_cap: float = 100.0,
                 power_idle_watts: float = 120.0, power_peak_watts: float = 300.0):
        self.id = hid
        self.cpu_cap = cpu_cap
        self.mem_cap = mem_cap
        self.status = "ON"
        self.power_idle_watts = power_idle_watts
        self.power_peak_watts = power_peak_watts

class VM:
    def __init__(self, vid: int, host_id: int, init_cpu: float, init_mem: float):
        self.id = vid
        self.host_id = host_id
        self.cpu_use_hist: List[float] = [init_cpu, init_cpu]
        self.mem_use_hist: List[float] = [init_mem, init_mem]
        self.pred_cpu: float = init_cpu
        self.pred_mem: float = init_mem

# -----------------------------
# Utility functions (internal)
# -----------------------------
def _bounded(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def synth_drift(t: int) -> float:
    """Simple diurnal-like drift."""
    return 10.0 * math.sin(2 * math.pi * (t % 24) / 24.0) + random.uniform(-8.0, 8.0)

def predict_ema(vm: VM, alpha: float) -> None:
    vm.pred_cpu = alpha * vm.cpu_use_hist[-1] + (1 - alpha) * vm.cpu_use_hist[-2]
    vm.pred_mem = alpha * vm.mem_use_hist[-1] + (1 - alpha) * vm.mem_use_hist[-2]

def loads_predicted(hosts: List[Host], vms: List[VM]) -> Tuple[Dict[int, float], Dict[int, float]]:
    cpu = {h.id: 0.0 for h in hosts if h.status == "ON"}
    mem = {h.id: 0.0 for h in hosts if h.status == "ON"}
    for vm in vms:
        hid = vm.host_id
        if hid in cpu:
            cpu[hid] += vm.pred_cpu
            mem[hid] += vm.pred_mem
    return cpu, mem

def first_fit(vm: VM, on_hosts: List[Host],
              cpu_loads: Dict[int, float], mem_loads: Dict[int, float],
              target_util: float) -> Host | None:
    for h in on_hosts:
        # CPU and MEM must remain <= target * capacity
        if (cpu_loads[h.id] + vm.pred_cpu) <= (h.cpu_cap * target_util) and \
           (mem_loads[h.id] + vm.pred_mem) <= (h.mem_cap * target_util):
            return h
    return None

def any_high_watermark(cpu_loads: Dict[int, float], on_hosts: List[Host], hi_watermark: float) -> bool:
    caps = {h.id: h.cpu_cap for h in on_hosts if h.status == "ON"}
    for hid, load in cpu_loads.items():
        cap = caps.get(hid, 0.0)
        if cap > 0 and load > cap * hi_watermark:
            return True
    return False

def active_hosts(hosts: List[Host]) -> List[Host]:
    return [h for h in hosts if h.status == "ON"]

def off_hosts(hosts: List[Host]) -> List[Host]:
    return [h for h in hosts if h.status == "OFF"]

# -----------------------------
# Core simulation
# -----------------------------
def simulate(cfg: Config) -> Dict[str, float]:
    random.seed(cfg.seed)

    hosts = [Host(hid=i) for i in range(cfg.n_hosts)]
    # Evenly distribute VMs at start
    vms = []
    for i in range(cfg.n_vms):
        hid = i % cfg.n_hosts
        init_cpu = random.uniform(10.0, 60.0)
        init_mem = _bounded(init_cpu * 0.8, 5.0, 80.0)
        vms.append(VM(i, hid, init_cpu, init_mem))

    total_kwh = 0.0
    total_migrations = 0
    total_breaches = 0

    for t in range(cfg.cycles):
        # 1) Update observed usage with simple drift (kept lightweight)
        for vm in vms:
            d = synth_drift(t)
            new_cpu = _bounded(vm.cpu_use_hist[-1] + d, 0.0, 100.0)
            new_mem = _bounded(vm.mem_use_hist[-1] + d * 0.8, 0.0, 100.0)
            vm.cpu_use_hist.append(new_cpu)
            vm.mem_use_hist.append(new_mem)

        # 2) Predict with EMA
        for vm in vms:
            predict_ema(vm, cfg.alpha)

        # 3) Select low-usage candidates (CPU)
        cands = [vm for vm in vms if vm.pred_cpu <= cfg.low_usage_threshold]

        # 4) Plan greedy fit-first to target
        on = active_hosts(hosts)
        cpu_loads, mem_loads = loads_predicted(on, vms)
        plan: List[Tuple[int, int, int]] = []  # (vm_id, src, dst)

        # Sort descending by predicted CPU
        for vm in sorted(cands, key=lambda x: x.pred_cpu, reverse=True):
            dst = first_fit(vm, on, cpu_loads, mem_loads, cfg.target_util)
            if dst is not None and dst.id != vm.host_id:
                plan.append((vm.id, vm.host_id, dst.id))
                cpu_loads[dst.id] += vm.pred_cpu
                mem_loads[dst.id] += vm.pred_mem

        # 5) Execute migrations (simulated)
        for (vm_id, src, dst) in plan:
            vms[vm_id].host_id = dst
        total_migrations += len(plan)

        # 6) Shutdown: hosts with no VMs -> OFF
        has_vm = {h.id: False for h in on}
        for vm in vms:
            if vm.host_id in has_vm:
                has_vm[vm.host_id] = True
        for h in on:
            if not has_vm[h.id]:
                h.status = "OFF"

        # 7) Energy saved this cycle: all OFF hosts accumulate savings
        off = off_hosts(hosts)
        total_kwh += sum(h.power_idle_watts for h in off) * cfg.dt_hours / 1000.0

        # 8) Monitoring & feedback
        on = active_hosts(hosts)  # recalc after shutdown
        cpu_loads, _ = loads_predicted(on, vms)
        breach = any_high_watermark(cpu_loads, on, cfg.hi_watermark)
        if breach:
            total_breaches += 1
            # Adjust placement policy slightly (relax packing)
            cfg.target_util = max(0.70, round(cfg.target_util - 0.02, 3))

    # Summary metrics (predicted util on ON hosts in final state)
    on = active_hosts(hosts)
    cpu_loads, _ = loads_predicted(on, vms)
    caps = {h.id: h.cpu_cap for h in on}
    utils = [cpu_loads[hid] / caps[hid] for hid in cpu_loads if caps[hid] > 0]

    util_mean = round(stats.mean(utils), 4) if utils else 0.0
    util_p95 = round(stats.quantiles(utils, n=20)[-1], 4) if len(utils) >= 20 else (max(utils) if utils else 0.0)

    result = {
        "energy_kwh_total": round(total_kwh, 3),
        "migrations_total": total_migrations,
        "hosts_off_final": len(off_hosts(hosts)),
        "util_mean_final": util_mean,
        "util_p95_final": util_p95,
        "hi_watermark_breaches": total_breaches,
        "final_target_util": round(cfg.target_util, 3),
    }
    return result

if __name__ == "__main__":
    cfg = Config(
        alpha=0.6,
        low_usage_threshold=30.0,
        target_util=0.80,
        hi_watermark=0.90,
        dt_hours=1.0,
        cycles=24,
        n_hosts=20,
        n_vms=120,
        seed=7,
    )
    out = simulate(cfg)
    print(out)
