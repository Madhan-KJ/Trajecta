                                                                   

                                                                            
                                                                         
                                                                            
                                       
   
from __future__ import annotations

import copy
import csv
import ctypes
import functools
import importlib.metadata
import itertools
import json
import math
import os
import ortools
import platform
import random
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"

CONFIG = {
    "orders": 30,
    "cities_including_depot": 18,
    "seeds": list(range(10)),
    "depot_city": "Coimbatore",
    "enable_infrastructure": True,
    "enable_pack3d": True,
    "enable_traffic": True,
    "enable_dbscan_split": True,
    "enable_penalty_risk_split": True,
    "enable_stochastic_service": True,
    "city_coordinate_jitter_degrees": 0.003,
    "distance_matrix_formula": "Haversine, Earth radius 6371 km, multiplied by road_distance_factor",
                                                                       
    "cost_rate_scale": 1.16,
    "due_offset_hours": [4.0, 8.0],
    "dbscan_eps_km": 2.0,
    "dbscan_min_samples": 2,
    "cities": [
        ["Coimbatore", 11.0168, 76.9558], ["Tiruppur", 11.1085, 77.3411],
        ["Erode", 11.3410, 77.7172], ["Salem", 11.6643, 78.1460],
        ["Palakkad", 10.7867, 76.6548], ["Pollachi", 10.6583, 77.0080],
        ["Mettupalayam", 11.2990, 76.9340], ["Udumalaipettai", 10.5881, 77.2474],
        ["Dindigul", 10.3673, 77.9803], ["Karur", 10.9601, 78.0766],
        ["Namakkal", 11.2194, 78.1674], ["Perundurai", 11.2750, 77.5870],
        ["Avinashi", 11.1920, 77.2680], ["Gudalur", 11.7440, 76.4890],
        ["Ooty", 11.4102, 76.6950], ["Thanjavur", 10.7870, 79.1378],
        ["Madurai", 9.9252, 78.1198], ["Thrissur", 10.5276, 76.2144],
    ],
                                                                    
    "road_distance_factor": 1.18,
    "weight_kg": [4, 55], "volume_m3": [0.015, 0.24],
    "penalty_deadline_h": 22.0,
    "t_base": 8.0,
    "gamma": 5.0,
    "delta": 1.0,
    "driver_skill_distribution": {"mean_min": 0.0, "sd_min": 2.0},
    "service_min_per_kg": 0.05, "service_min_per_m3": 5.0,
    "late_rate_rs_per_day": 100.0,
    "packaging_rs_per_order": 25.0,
    "cooling_rs_per_order": 10.0,
    "toll_rs_by_vehicle_class": {"two_wheeler": 10.0, "four_wheeler": 30.0, "truck": 60.0},
    "toll_model": "flat class-based charge per active route (synthetic assumption)",
    "wage_rs_per_km": 2.0, "maintenance_rs_per_km": 0.55,
    "terrain_gradient_factor": 1.0,
    "electric_consumption_kwh_per_km": 0.1,
    "charging_tariff_rs_per_kwh": 3.5,
    "baseline_distance_cost_rs_per_km": 12.0,
    "fuel_rs_per_km": {"petrol": 4.5, "diesel": 7.0, "electric": 0.0},
    "traffic": {"rush_morning": 1.30, "rush_evening": 1.25,
                "midday": 1.05, "night": 0.90},
    "weather_factor": 1.0, "lane_factor": 1.0,
    "skill_distribution": {
        "two_wheeler": {"count": 2, "share": 2 / 7},
        "four_wheeler": {"count": 3, "share": 3 / 7},
        "truck": {"count": 2, "share": 2 / 7},
    },
    "assumed_route_groups": 4,
    "fleet_type_limit": 7,
    "ortools_seconds": 2,
    "metaheuristic_iterations": 10,
}


@dataclass
class Order:
    oid: int
    city: int
    lat: float
    lon: float
    weight: float
    volume: float
    due_h: float
    arrival_h: float
    fragile: bool
    cooling: bool
    penalty_risk: float
    box_l_m: float
    box_w_m: float
    box_h_m: float


FLEET = [
    {"name": "2W-Petrol", "kind": "petrol", "weight": 35, "volume": .18, "speed": 34, "fixed": 0, "bay": (.55, .45, .40), "height": 1.5},
    {"name": "2W-EV", "kind": "electric", "weight": 30, "volume": .16, "speed": 32, "fixed": 0, "bay": (.55, .45, .40), "height": 1.6},
    {"name": "4W-Petrol", "kind": "petrol", "weight": 350, "volume": 2.5, "speed": 42, "fixed": 70, "bay": (2.0, 1.35, .95), "height": 2.0},
    {"name": "4W-Diesel", "kind": "diesel", "weight": 700, "volume": 5.5, "speed": 40, "fixed": 100, "bay": (2.5, 1.55, 1.35), "height": 2.3},
    {"name": "4W-EV", "kind": "electric", "weight": 400, "volume": 3.0, "speed": 38, "fixed": 65, "bay": (2.1, 1.4, 1.05), "height": 2.1},
    {"name": "Truck-Diesel", "kind": "diesel", "weight": 4000, "volume": 25, "speed": 35, "fixed": 180, "bay": (6.0, 2.2, 2.0), "height": 3.6},
    {"name": "Truck-EV", "kind": "electric", "weight": 2500, "volume": 18, "speed": 33, "fixed": 160, "bay": (5.0, 2.0, 1.8), "height": 3.2},
]


def haversine(a, b):
    r = 6371.0
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    dp, dl = p2 - p1, math.radians(b[2] - a[2])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h)) * CONFIG["road_distance_factor"]


def make_instance(seed: int, order_count: int | None = None):
    rng = random.Random(seed)
    cities = CONFIG["cities"]
    depot = cities[0]
    count = CONFIG["orders"] if order_count is None else order_count
                                                                          
                                                                          
                                                                            
    centers = [(city[1], city[2]) for city in cities]
    orders = []
    for i in range(count):
        ci = rng.randrange(1, len(cities))
        lat0, lon0 = centers[ci]
        jitter = CONFIG["city_coordinate_jitter_degrees"]
        lat = lat0 + rng.uniform(-jitter, jitter)
        lon = lon0 + rng.uniform(-jitter, jitter)
        arrival = rng.uniform(6, 10)
        due = min(22, 8.0 + rng.uniform(*CONFIG["due_offset_hours"]))
        weight = rng.uniform(*CONFIG["weight_kg"])
        volume = rng.uniform(*CONFIG["volume_m3"])
        fragile, cooling = rng.random() < .15, rng.random() < .20
        cube = volume ** (1 / 3)
        box_l = cube * rng.uniform(1.05, 1.45)
        box_w = cube * rng.uniform(.78, 1.02)
        box_h = volume / (box_l * box_w)
        orders.append(Order(i, ci, lat, lon, weight, volume, due, arrival,
                            fragile, cooling, rng.random(), box_l, box_w, box_h))
    d = [[0.0] * len(cities) for _ in cities]
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                d[i][j] = haversine(cities[i], cities[j])
    return orders, d


def service_minutes(o: Order, seed: int):
    rng = random.Random(seed * 1009 + o.oid)
    skill = (rng.gauss(CONFIG["driver_skill_distribution"]["mean_min"],
                       CONFIG["driver_skill_distribution"]["sd_min"])
             if CONFIG.get("enable_stochastic_service", True)
             else CONFIG["driver_skill_distribution"]["mean_min"])
    return max(2.0, CONFIG["t_base"] + CONFIG["service_min_per_kg"] * o.weight
               + CONFIG["service_min_per_m3"] * o.volume
               + CONFIG["gamma"] * (o.fragile + o.cooling) + CONFIG["delta"] * skill)


def active_fleet():
    return FLEET[:CONFIG.get("fleet_type_limit", len(FLEET))]


def travel_hours(km: float, vehicle, departure_h: float):
    if not CONFIG.get("enable_traffic", True):
        return km / vehicle["speed"]
    band = "rush_morning" if 7 <= departure_h < 10 else "rush_evening" if 16 <= departure_h < 19 else "night" if departure_h >= 21 or departure_h < 6 else "midday"
    mult = CONFIG["traffic"][band] * CONFIG["weather_factor"] * CONFIG["lane_factor"]
    return km / vehicle["speed"] * mult


def seven_cost(distance, vehicle, late_days, fragile_count, cooling_count):
    fuel = distance * CONFIG["fuel_rs_per_km"][vehicle["kind"]] * CONFIG["terrain_gradient_factor"]
    wages = distance * CONFIG["wage_rs_per_km"] + vehicle["fixed"]
    penalty = late_days * CONFIG["late_rate_rs_per_day"]
    cooling_packaging = (fragile_count * CONFIG["packaging_rs_per_order"]
                         + cooling_count * CONFIG["cooling_rs_per_order"])
    maintenance = distance * CONFIG["maintenance_rs_per_km"]
    vehicle_class = ("two_wheeler" if vehicle["name"].startswith("2W")
                     else "truck" if vehicle["name"].startswith("Truck") else "four_wheeler")
    tolls = CONFIG["toll_rs_by_vehicle_class"][vehicle_class]
    ev_charging = (distance * CONFIG["electric_consumption_kwh_per_km"]
                   * CONFIG["charging_tariff_rs_per_kwh"] if vehicle["kind"] == "electric" else 0.0)
    scale = CONFIG["cost_rate_scale"]
    return scale * (fuel + wages + penalty + cooling_packaging + maintenance + tolls + ev_charging), scale * penalty


def pack3d(route, vehicle, orders):
    if not CONFIG.get("enable_pack3d", True):
        return True
    free = [vehicle["bay"]]
    boxes = sorted(((orders[i].box_l_m, orders[i].box_w_m, orders[i].box_h_m)
                    for i in route), key=lambda b: b[0] * b[1] * b[2], reverse=True)
    for box in boxes:
        placed = False
        for si, space in enumerate(free):
            for dims in sorted(set(itertools.permutations(box)), reverse=True):
                l, w, h = dims
                sx, sy, sz = space
                if l <= sx + 1e-9 and w <= sy + 1e-9 and h <= sz + 1e-9:
                    residual = []
                    if sx - l > 1e-9: residual.append((sx - l, sy, sz))
                    if sy - w > 1e-9: residual.append((l, sy - w, sz))
                    if sz - h > 1e-9: residual.append((l, w, sz - h))
                    free.pop(si); free.extend(residual); placed = True
                    break
            if placed: break
        if not placed:
            return False
    return True


def infrastructure_rule(a, b):
                                                                                
    a, b = sorted((int(a), int(b)))
    if a == b: return None
    rule = {}
    if (a + b) % 13 == 0: rule["two_wheeler_allowed"] = False
    if (a * 31 + b * 17) % 29 == 0: rule["max_payload_kg"] = 500
    if (a * 11 + b * 7) % 31 == 0: rule["max_vehicle_height_m"] = 2.4
    return rule or None


def infrastructure_feasible(route, vehicle, orders):
    if not CONFIG.get("enable_infrastructure", True):
        return True
    cities = [0] + [orders[i].city for i in route] + [0]
    for a, b in zip(cities, cities[1:]):
        rule = infrastructure_rule(a, b)
        if not rule: continue
        if rule.get("two_wheeler_allowed") is False and vehicle["name"].startswith("2W"):
            return False
        if vehicle["weight"] > rule.get("max_payload_kg", math.inf): return False
        if vehicle["height"] > rule.get("max_vehicle_height_m", math.inf): return False
    return True


def score_route(route, vehicle, orders, d, seed, objective="full", prevalidated=False):
    if not route:
        return 0.0, 0.0, 0.0, 100.0
    load_w = sum(orders[i].weight for i in route)
    load_v = sum(orders[i].volume for i in route)
    if not prevalidated and (load_w > vehicle["weight"] or load_v > vehicle["volume"]):
        return math.inf, 0.0, math.inf, 0.0
    if not prevalidated and not pack3d(route, vehicle, orders):
        return math.inf, 0.0, math.inf, 0.0
    if not infrastructure_feasible(route, vehicle, orders):
        return math.inf, 0.0, math.inf, 0.0
    clock = 8.0
    distance = 0.0
    late_days = 0.0
    fragile_count = 0
    cooling_count = 0
    prev = 0
    ontime = 0
    for idx in route:
        o = orders[idx]
        km = d[prev][o.city]
        distance += km
        clock = max(clock + travel_hours(km, vehicle, clock), o.arrival_h)
        clock += service_minutes(o, seed) / 60.0
        ontime += clock <= o.due_h
                                                                         
                                                                            
        late_days += max(0.0, (clock - o.due_h) / 24.0)
        fragile_count += int(o.fragile)
        cooling_count += int(o.cooling)
        prev = o.city
    distance += d[prev][0]
    cost, penalty = seven_cost(distance, vehicle, late_days, fragile_count, cooling_count)
    if objective == "simple":
        cost = distance * 12.0 + penalty
    return cost, distance, penalty, 100.0 * ontime / len(route)


def make_splits(orders, d):
    def density_split():
        labels = [None] * len(orders)
        cluster_id = 0

        def neighbors(index):
            point = ["", orders[index].lat, orders[index].lon]
            return [other for other in range(len(orders))
                    if haversine(point, ["", orders[other].lat, orders[other].lon])
                    <= CONFIG["dbscan_eps_km"]]

        for index in range(len(orders)):
            if labels[index] is not None:
                continue
            nearby = neighbors(index)
            if len(nearby) < CONFIG["dbscan_min_samples"]:
                labels[index] = -1
                continue
            labels[index] = cluster_id
            pending = list(nearby)
            while pending:
                current = pending.pop()
                if labels[current] == -1:
                    labels[current] = cluster_id
                if labels[current] is not None:
                    continue
                labels[current] = cluster_id
                current_neighbors = neighbors(current)
                if len(current_neighbors) >= CONFIG["dbscan_min_samples"]:
                    pending.extend(current_neighbors)
            cluster_id += 1

        clusters = {}
        for index, label in enumerate(labels):
            cluster_key = ("noise", index) if label == -1 else ("cluster", label)
            clusters.setdefault(cluster_key, []).append(orders[index])
        groups = [[] for _ in range(CONFIG["assumed_route_groups"])]
        for cluster in sorted(clusters.values(), key=len, reverse=True):
            target = min(range(len(groups)), key=lambda group: len(groups[group]))
            groups[target].extend(cluster)
        return groups

    keys: list[Callable] = [
        lambda o: o.due_h, lambda o: o.arrival_h, lambda o: o.lat,
        lambda o: d[0][o.city],
        lambda o: o.lon, lambda o: o.lat + o.lon,
        lambda o: (o.penalty_risk * max(0.0, 21 - o.due_h)
               if CONFIG.get("enable_penalty_risk_split", True) else o.due_h),
    ]
    out = []
    groups = CONFIG["assumed_route_groups"]
    for key in keys:
        ordered = sorted(orders, key=key)
        out.append([list(ordered[i::groups]) for i in range(groups)])
    out.append(density_split() if CONFIG.get("enable_dbscan_split", True)
               else [list(group) for group in out[0]])
    return out


def make_routes(group, orders, d, kind, seed):
    ids = [o.oid for o in group]
    if kind == "EDD":
        return sorted(ids, key=lambda i: orders[i].due_h)
    if kind == "RNN":
        rng = random.Random(seed)
        remaining, out, here = set(ids), [], 0
        while remaining:
            nxt = min(remaining, key=lambda i: d[here][orders[i].city] * rng.uniform(.85, 1.15))
            out.append(nxt); remaining.remove(nxt); here = orders[nxt].city
        return out
    if kind == "MU":
        return sorted(ids, key=lambda i: orders[i].due_h - d[0][orders[i].city] / 35)
    if kind == "FI":
        remaining = set(ids)
        first = max(remaining, key=lambda i: d[0][orders[i].city]); out = [first]; remaining.remove(first)
        while remaining:
            nxt = max(remaining, key=lambda i: min(d[orders[i].city][orders[j].city] for j in out))
            pos = min(range(len(out) + 1), key=lambda p: insertion_delta(out, nxt, p, d, orders))
            out.insert(pos, nxt); remaining.remove(nxt)
        return out
    if kind == "G TW":
        return sorted(ids, key=lambda i: (max(0, 8 + d[0][orders[i].city] / 35 - orders[i].due_h), d[0][orders[i].city]))
    if kind == "CFRS":
        return sorted(ids, key=lambda i: (orders[i].city, orders[i].lat, orders[i].lon))
    if kind == "BiDir":
        ascending = sorted(ids, key=lambda i: d[0][orders[i].city])
        return ascending[::2] + ascending[1::2][::-1]
                              
    remaining, out, here = set(ids), [], 0
    while remaining:
        nxt = min(remaining, key=lambda i: d[here][orders[i].city])
        out.append(nxt); remaining.remove(nxt); here = orders[nxt].city
    return out


def insertion_delta(route, node, pos, d, orders):
    left = 0 if pos == 0 else orders[route[pos - 1]].city
    right = 0 if pos == len(route) else orders[route[pos]].city
    city = orders[node].city
    return d[left][city] + d[city][right] - d[left][right]


SPLIT_NAMES = ["EDD", "Arrival", "Latitude", "Depot Distance", "Longitude",
               "Lat-Lon", "Penalty-Risk", "DensityGeo"]
HEURISTICS = ["NN", "BiDir", "MU", "FI", "RNN", "G TW", "CFRS"]


def assign_vehicles(routes, orders, d, seed, objective="full"):
                                                                             
                                         
    vehicles = active_fleet()
    if len(vehicles) < len(routes):
        return math.inf, None, []
    table = [[score_route(route, vehicles[vi], orders, d, seed, objective)
              for vi in range(len(vehicles))] for route in routes]
    best = (math.inf, None, None)
    for fleet_ids in itertools.permutations(range(len(vehicles)), len(routes)):
        details = [(vi, table[ri][vi]) for ri, vi in enumerate(fleet_ids)]
        total = sum(x[1][0] for x in details)
                                                                           
                                                                             
                                                                              
        if best[1] is None or total < best[0]:
            best = total, fleet_ids, details
    return best


def candidate_runs(orders, d, seed):
    rows = []
    for si, split in enumerate(make_splits(orders, d)):
        for heuristic in HEURISTICS:
            routes = [make_routes(g, orders, d, heuristic, seed + si) for g in split]
            total, assigned, details = assign_vehicles(routes, orders, d, seed)
            flatdist = sum(x[1][1] for x in details)
            penalty = sum(x[1][2] for x in details)
            ontime = sum(x[1][3] * len(r) for x, r in zip(details, routes)) / len(orders)
            route_details = []
            for route_index, (route, (vehicle_index, metrics)) in enumerate(zip(routes, details)):
                city_ids = [0] + [orders[order_id].city for order_id in route] + [0]
                route_details.append({
                    "route_index": route_index,
                    "vehicle": active_fleet()[vehicle_index]["name"],
                    "order_ids": ";".join(str(order_id) for order_id in route),
                    "city_ids": ";".join(str(city_id) for city_id in city_ids),
                    "cost_rs": metrics[0],
                    "distance_km": metrics[1],
                    "penalty_rs": metrics[2],
                    "ontime_pct": metrics[3],
                })
            split_name = SPLIT_NAMES[si]
            if si == 6 and not CONFIG.get("enable_penalty_risk_split", True):
                split_name = "EDD (penalty-risk removed)"
            if si == 7 and not CONFIG.get("enable_dbscan_split", True):
                split_name = "EDD (DBSCAN removed)"
            rows.append({"split_index": si, "split": split_name, "heuristic": heuristic, "cost_rs": total,
                         "distance_km": flatdist, "penalty_rs": penalty,
                         "ontime_pct": ontime, "route_details": route_details,
                         "vehicles": ";".join(active_fleet()[v]["name"] for v in assigned)})
    return rows


def route_solution_stats(routes, orders, d, seed):
    total, assigned, details = assign_vehicles(routes, orders, d, seed)
    distance = sum(x[1][1] for x in details)
    penalty = sum(x[1][2] for x in details)
    ontime = sum(x[1][3] * len(r) for x, r in zip(details, routes)) / len(orders)
    return total, distance, penalty, ontime, assigned


def order_crossover(a, b, rng):
    if len(a) < 3: return b[:]
    lo, hi = sorted(rng.sample(range(len(a)), 2))
    child = [None] * len(a); child[lo:hi] = a[lo:hi]
    rest = [x for x in b if x not in child]
    it = iter(rest)
    return [next(it) if x is None else x for x in child]


def write_csv(name, rows):
    if rows:
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            fieldnames = list(dict.fromkeys(key for row in rows for key in row))
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader(); w.writerows(rows)


def summarize_stats(rows, key):
    raw = [float(r[key]) for r in rows if r.get(key) is not None]
    vals = [value for value in raw if math.isfinite(value)]
    if not vals:
        return {"mean": None, "sd": None, "min": None, "max": None,
                "n_valid": 0, "n_nonfinite": len(raw)}
    return {
        "mean": statistics.mean(vals),
        "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
        "n_valid": len(vals),
        "n_nonfinite": len(raw) - len(vals),
    }


def contribution_summary(candidate_rows):
    rows = []
    seeds = sorted({int(row["seed"]) for row in candidate_rows})
    winners = {}
    per_seed_best = {}
    for seed in seeds:
        seed_rows = [row for row in candidate_rows if int(row["seed"]) == seed]
        feasible = [row for row in seed_rows if math.isfinite(float(row["cost_rs"]))]
        winner = min(feasible, key=lambda row: (float(row["cost_rs"]),
                                                 int(row["split_index"]),
                                                 HEURISTICS.index(row["heuristic"])))
        winners[seed] = winner
        per_seed_best[seed] = float(winner["cost_rs"])
    for dimension, field in (("split", "split"), ("heuristic", "heuristic")):
        labels = sorted({row[field] for row in candidate_rows})
        for label in labels:
            group = [row for row in candidate_rows if row[field] == label]
            values = [float(row["cost_rs"]) for row in group]
            finite = [value for value in values if math.isfinite(value)]
            regrets = []
            for seed in seeds:
                seed_rows = [row for row in candidate_rows if int(row["seed"]) == seed]
                alternatives = [float(row["cost_rs"]) for row in seed_rows
                                if row[field] != label and math.isfinite(float(row["cost_rs"]))]
                if alternatives:
                    regrets.append(min(alternatives) - per_seed_best[seed])
            rows.append({
                "dimension": dimension,
                "value": label,
                "candidate_rows": len(group),
                "finite_rows": len(finite),
                "nonfinite_rows": len(values) - len(finite),
                "mean_cost_rs": statistics.mean(finite) if finite else math.inf,
                "sd_cost_rs": statistics.stdev(finite) if len(finite) > 1 else 0.0,
                "best_cost_rs": min(finite) if finite else math.inf,
                "best_of_group_win_rate": sum(winners[seed][field] == label for seed in seeds) / len(seeds),
                "mean_leave_one_out_regret_rs": statistics.mean(regrets) if regrets else math.inf,
                "regret_n_seeds": len(regrets),
            })
    return rows


def system_ram_bytes():
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
                        ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
                        ("total_page_file", ctypes.c_ulonglong), ("avail_page_file", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
                        ("avail_extended_virtual", ctypes.c_ulonglong)]

        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.total_phys
    return None


def write_reproducibility_tables(candidate_rows):
    package_versions = {}
    for package in ("ortools", "numpy", "pandas", "scipy", "matplotlib"):
        try:
            package_versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            package_versions[package] = None
    try:
        git_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                                  capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_hash = None
    run_info = {
        "run_command": "python recreate.py",
        "python": platform.python_version(),
        "os": platform.platform(),
        "cpu": platform.processor() or None,
        "logical_cpu_count": os.cpu_count(),
        "ram_bytes": system_ram_bytes(),
        "package_versions": package_versions,
        "git_hash": git_hash,
        "seeds": CONFIG["seeds"],
        "experiment_seeds": {"main": CONFIG["seeds"], "ablation": CONFIG["seeds"],
                     "scalability": [11, 22], "varied_instances": [0, 1, 2],
                     "optimality_gap": [0, 1, 2], "benchmark": [11, 22, 33]},
        "orders": CONFIG["orders"],
        "candidate_count_per_seed": len(SPLIT_NAMES) * len(HEURISTICS),
        "ortools_time_limit_seconds": CONFIG["ortools_seconds"],
        "scalability_ortools_time_limit_seconds": 1,
        "fleet_type_count": len(active_fleet()),
        "available_vehicle_types": [vehicle["name"] for vehicle in active_fleet()],
        "route_group_assumption": CONFIG["assumed_route_groups"],
        "metaheuristic_iterations": CONFIG["metaheuristic_iterations"],
        "ortools_first_solution": "PATH_CHEAPEST_ARC",
        "ortools_local_search": "GUIDED_LOCAL_SEARCH",
        "ortools_seven_factor_traffic_approximation": 1.15,
        "optimality_gap_order_count": 7,
    }
    (OUT / "run_info.json").write_text(json.dumps(run_info, indent=2), encoding="utf-8")

    fleet_table = []
    for vehicle in FLEET:
        vehicle_class = ("two_wheeler" if vehicle["name"].startswith("2W")
                         else "truck" if vehicle["name"].startswith("Truck") else "four_wheeler")
        fleet_table.append({
            "type": vehicle["name"], "weight_capacity_kg": vehicle["weight"],
            "volume_capacity_m3": vehicle["volume"], "speed_km_per_h": vehicle["speed"],
            "bay_dimensions_m": vehicle["bay"], "height_m": vehicle["height"],
            "lane_factor": CONFIG["lane_factor"], "fuel_type": vehicle["kind"],
            "fuel_rs_per_km": CONFIG["fuel_rs_per_km"][vehicle["kind"]],
            "ev_kwh_per_km": CONFIG["electric_consumption_kwh_per_km"] if vehicle["kind"] == "electric" else 0,
            "fixed_route_cost_rs": vehicle["fixed"],
            "wage_rs_per_km": CONFIG["wage_rs_per_km"],
            "maintenance_rs_per_km": CONFIG["maintenance_rs_per_km"],
            "range_km": None,
            "toll_rs_per_route": CONFIG["toll_rs_by_vehicle_class"][vehicle_class],
            "availability": "vehicle type only; not an inventory count",
        })
    tables = {
        "fleet_types": fleet_table,
        "cost_components": [
            {"component": "fuel", "formula": "distance * fuel rate * terrain factor", "unit": "Rs"},
            {"component": "wages", "formula": "distance * wage rate + fixed vehicle route cost", "unit": "Rs"},
            {"component": "late penalty", "formula": "late days * daily rate", "unit": "Rs"},
            {"component": "packaging", "formula": "fragile order count * packaging rate", "unit": "Rs"},
            {"component": "cooling", "formula": "cooling order count * cooling rate", "unit": "Rs"},
            {"component": "maintenance", "formula": "distance * maintenance rate", "unit": "Rs"},
            {"component": "tolls", "formula": "flat class-based charge per active route", "unit": "Rs; synthetic assumption"},
            {"component": "EV charging", "formula": "distance * kWh/km * tariff", "unit": "Rs"},
        ],
        "cost_rates": {key: CONFIG[key] for key in (
            "cost_rate_scale", "late_rate_rs_per_day", "packaging_rs_per_order",
            "cooling_rs_per_order", "wage_rs_per_km", "maintenance_rs_per_km",
            "terrain_gradient_factor", "electric_consumption_kwh_per_km",
            "charging_tariff_rs_per_kwh", "fuel_rs_per_km", "toll_rs_by_vehicle_class")},
        "traffic": {"bands": {"rush_morning": {"hours": "07:00-10:00", "multiplier": CONFIG["traffic"]["rush_morning"]},
                                "rush_evening": {"hours": "16:00-19:00", "multiplier": CONFIG["traffic"]["rush_evening"]},
                                "midday": {"hours": "10:00-16:00 and 19:00-21:00", "multiplier": CONFIG["traffic"]["midday"]},
                                "night": {"hours": "21:00-06:00", "multiplier": CONFIG["traffic"]["night"]}},
                    "other_hours": "midday default, including 06:00-07:00",
                    "weather_multiplier": CONFIG["weather_factor"], "lane_multiplier": CONFIG["lane_factor"],
                    "origin": "synthetic assumptions; not calibrated against observed traffic"},
        "service_time": {"formula": "t_base + alpha*weight + beta*volume + gamma*(fragile+cooling) + delta*skill",
                         "t_base_min": CONFIG["t_base"], "alpha_min_per_kg": CONFIG["service_min_per_kg"],
                         "beta_min_per_m3": CONFIG["service_min_per_m3"], "gamma_min": CONFIG["gamma"],
                         "delta": CONFIG["delta"], "skill_distribution": CONFIG["driver_skill_distribution"],
                         "skill_draw": "one deterministic normal draw per order and seed"},
        "synthetic_generator": {"weight_kg": {"distribution": "uniform", "range": CONFIG["weight_kg"]},
                                "volume_m3": {"distribution": "uniform", "range": CONFIG["volume_m3"]},
                                "city_assignment": "uniform discrete over non-depot configured cities",
                                "coordinate_jitter_degrees": {"distribution": "uniform", "range": [-CONFIG["city_coordinate_jitter_degrees"], CONFIG["city_coordinate_jitter_degrees"]]},
                                "arrival_hour": {"distribution": "uniform", "range": [6, 10]},
                                "due_hour": "min(22, 8 + uniform(due_offset_hours)); offsets are uniform",
                                "fragile_probability": 0.15, "cooling_probability": 0.20,
                                "penalty_risk": {"distribution": "uniform", "range": [0, 1]},
                                "distance_matrix": CONFIG["distance_matrix_formula"],
                                "route_group_count": CONFIG["assumed_route_groups"],
                                "route_groups_source": "synthetic assumption"},
        "infrastructure": {"source": "synthetic rule, not mapped road data",
                           "two_wheeler_forbidden": "(a+b) % 13 == 0",
                           "max_payload_kg_500": "(a*31+b*17) % 29 == 0",
                           "max_height_m_2_4": "(a*11+b*7) % 31 == 0"},
        "packing": {"algorithm": "descending-volume first-fit into residual rectangular spaces; test all six box orientations",
                    "limitations": "heuristic, not an optimal 3D packing solver"},
        "selection": {"objective_candidates": ["minimum cost", "minimum distance", "minimum penalty"],
                      "tie_break": "objective metric, then cost, distance, penalty, split index, heuristic order",
                      "pareto_definition": "non-dominated over cost, distance, and penalty; finite candidates only"},
    }
    (OUT / "reproducibility_tables.json").write_text(json.dumps(tables, indent=2), encoding="utf-8")

    aggregates = []
    for split_index, split in enumerate(SPLIT_NAMES):
        for heuristic in HEURISTICS:
            matches = [row for row in candidate_rows
                       if int(row["split_index"]) == split_index and row["heuristic"] == heuristic]
            aggregate = {"split_index": split_index, "split": split, "heuristic": heuristic}
            for metric in ("cost_rs", "distance_km", "penalty_rs", "ontime_pct"):
                stat = summarize_stats(matches, metric)
                aggregate[f"{metric}_mean"] = stat["mean"]
                aggregate[f"{metric}_sd"] = stat["sd"]
                aggregate[f"{metric}_valid_seeds"] = stat["n_valid"]
                aggregate[f"{metric}_nonfinite_seeds"] = stat["n_nonfinite"]
            aggregates.append(aggregate)
    write_csv("candidate_route_summary.csv", aggregates)

    objective_selections = []
    same_all = 0
    pairwise_coincidences = {"min_cost_min_distance": ["min_cost", "min_distance", 0],
                             "min_cost_min_penalty": ["min_cost", "min_penalty", 0],
                             "min_distance_min_penalty": ["min_distance", "min_penalty", 0]}
    pareto_counts = []
    for seed in CONFIG["seeds"]:
        seed_rows = [row for row in candidate_rows if int(row["seed"]) == seed
                     and math.isfinite(float(row["cost_rs"]))]
        def selector(row, metric):
            return (float(row[metric]), float(row["cost_rs"]), float(row["distance_km"]),
                    float(row["penalty_rs"]), int(row["split_index"]), HEURISTICS.index(row["heuristic"]))
        selected = {metric: min(seed_rows, key=lambda row: selector(row, metric))
                    for metric in ("cost_rs", "distance_km", "penalty_rs")}
        if len({(int(row["split_index"]), row["heuristic"]) for row in selected.values()}) == 1:
            same_all += 1
        selected_keys = {objective: (int(row["split_index"]), row["heuristic"])
                         for objective, row in (("min_cost", selected["cost_rs"]),
                                                ("min_distance", selected["distance_km"]),
                                                ("min_penalty", selected["penalty_rs"]))}
        for pair, (left, right, count) in pairwise_coincidences.items():
            pairwise_coincidences[pair] = [left, right, count + (selected_keys[left] == selected_keys[right])]
        for objective, metric in (("min_cost", "cost_rs"), ("min_distance", "distance_km"),
                                  ("min_penalty", "penalty_rs")):
            row = selected[metric]
            objective_selections.append({"seed": seed, "objective": objective, "split": row["split"],
                                         "heuristic": row["heuristic"], "cost_rs": row["cost_rs"],
                                         "distance_km": row["distance_km"], "penalty_rs": row["penalty_rs"],
                                         "ontime_pct": row["ontime_pct"]})
        pareto = []
        for candidate in seed_rows:
            metrics = [float(candidate[key]) for key in ("cost_rs", "distance_km", "penalty_rs")]
            dominated = any(
                all(float(other[key]) <= value for key, value in zip(("cost_rs", "distance_km", "penalty_rs"), metrics))
                and any(float(other[key]) < value for key, value in zip(("cost_rs", "distance_km", "penalty_rs"), metrics))
                for other in seed_rows if other is not candidate
            )
            if not dominated:
                pareto.append(candidate)
        pareto_counts.append(len(pareto))
    write_csv("objective_selection.csv", objective_selections)
    analysis = {"all_three_objectives_coincide_seeds": same_all,
                "n_seeds": len(CONFIG["seeds"]),
                "pairwise_objective_coincidences": {key: value[2]
                                                     for key, value in pairwise_coincidences.items()},
                "pareto_candidates_per_seed_mean": statistics.mean(pareto_counts),
                "pareto_candidates_per_seed_sd": statistics.stdev(pareto_counts) if len(pareto_counts) > 1 else 0,
                "pareto_candidates_per_seed": pareto_counts,
                "tie_break": tables["selection"]["tie_break"]}
    (OUT / "candidate_analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")


def run_ablation_experiments():
    variants = [
        ("baseline", {}),
        ("no_infrastructure", {"enable_infrastructure": False}),
        ("no_3d_packing", {"enable_pack3d": False}),
        ("no_dbscan_split", {"enable_dbscan_split": False}),
        ("no_penalty_risk_split", {"enable_penalty_risk_split": False}),
        ("no_traffic", {"enable_traffic": False}),
        ("no_stochastic_service", {"enable_stochastic_service": False}),
    ]
    rows = []
    original = copy.deepcopy(CONFIG)
    try:
        for variant_name, overrides in variants:
            CONFIG.clear(); CONFIG.update(copy.deepcopy(original))
            CONFIG.update(copy.deepcopy(overrides))
            for seed in CONFIG["seeds"]:
                t0 = time.perf_counter()
                orders, d = make_instance(seed)
                candidate = candidate_runs(orders, d, seed)
                runtime = time.perf_counter() - t0
                best = min(candidate, key=lambda r: r["cost_rs"])
                variant_config = copy.deepcopy(CONFIG)
                CONFIG.clear(); CONFIG.update(copy.deepcopy(original))
                full_cost = full_distance = full_penalty = weighted_ontime = 0.0
                full_feasible = True
                capacity_violations = pack3d_violations = infrastructure_violations = 0
                for detail in best["route_details"]:
                    route = [int(value) for value in detail["order_ids"].split(";") if value]
                    vehicle = next(v for v in FLEET if v["name"] == detail["vehicle"])
                    route_cost, route_distance, route_penalty, route_ontime = score_route(
                        route, vehicle, orders, d, seed)
                    full_cost += route_cost
                    full_distance += route_distance
                    full_penalty += route_penalty
                    weighted_ontime += route_ontime * len(route) / 100.0
                    load_weight = sum(orders[index].weight for index in route)
                    load_volume = sum(orders[index].volume for index in route)
                    capacity_violations += int(load_weight > vehicle["weight"] or load_volume > vehicle["volume"])
                    pack3d_violations += int(not pack3d(route, vehicle, orders))
                    infrastructure_violations += int(not infrastructure_feasible(route, vehicle, orders))
                    full_feasible &= math.isfinite(route_cost)
                CONFIG.clear(); CONFIG.update(variant_config)
                rows.append({
                    "variant": variant_name,
                    "seed": seed,
                    "selected_split": best["split"],
                    "selected_heuristic": best["heuristic"],
                    "search_cost_rs": best["cost_rs"],
                    "full_cost_rs": full_cost if full_feasible else math.inf,
                    "full_distance_km": full_distance,
                    "full_penalty_rs": full_penalty if full_feasible else math.inf,
                    "full_ontime_pct": 100.0 * weighted_ontime / len(orders),
                    "full_model_feasible": full_feasible,
                    "capacity_violations": capacity_violations,
                    "pack3d_violations": pack3d_violations,
                    "infrastructure_violations": infrastructure_violations,
                    "runtime_s": runtime,
                })
    finally:
        CONFIG.clear(); CONFIG.update(original)
    return rows


def run_scalability_experiments():
    sizes = [20, 30, 50, 80]
    seeds = [11, 22]
    rows = []
    for size in sizes:
        for seed in seeds:
            orders, d = make_instance(seed, order_count=size)
            t0 = time.perf_counter()
            candidates = candidate_runs(orders, d, seed)
            runtime = time.perf_counter() - t0
            best = min(candidates, key=lambda row: float(row["cost_rs"]))
            rows.append({
                "n_orders": size,
                "seed": seed,
                "algorithm": "Trajecta best-of-56",
                "cost_rs": best["cost_rs"],
                "distance_km": best["distance_km"],
                "penalty_rs": best["penalty_rs"],
                "ontime_pct": best["ontime_pct"],
                "full_model_feasible": math.isfinite(best["cost_rs"]),
                "runtime_s": runtime,
            })
            for objective, label in (("simplified", "OR-Tools simplified"),
                                     ("seven_factor", "OR-Tools seven-factor")):
                t0 = time.perf_counter()
                base = ortools_baseline(orders, d, seed, seconds=1, objective=objective)
                runtime = time.perf_counter() - t0
                rows.append({
                    "n_orders": size,
                    "seed": seed,
                    "algorithm": label,
                    "cost_rs": base.get("cost_rs"),
                    "distance_km": base.get("distance_km"),
                    "penalty_rs": base.get("penalty_rs"),
                    "ontime_pct": base.get("ontime_pct"),
                    "full_model_feasible": base.get("full_model_feasible"),
                    "runtime_s": runtime,
                })
            t0 = time.perf_counter()
            meta = metaheuristic_runs(orders, d, seed)
            for algo in meta:
                rows.append({
                    "n_orders": size,
                    "seed": seed,
                    "algorithm": algo["algorithm"],
                    "cost_rs": algo["cost_rs"],
                    "distance_km": algo["distance_km"],
                    "penalty_rs": algo["penalty_rs"],
                    "ontime_pct": algo["ontime_pct"],
                    "full_model_feasible": math.isfinite(algo["cost_rs"]),
                    "runtime_s": algo["runtime_s"],
                })
    return rows


def run_varied_experiments():
    scenarios = [
        ("orders_20", {"order_count": 20}),
        ("orders_50", {"order_count": 50}),
        ("fleet_types_4", {"fleet_type_limit": 4}),
        ("fleet_types_7", {"fleet_type_limit": 7}),
        ("high_demand", {"weight_kg": [20, 100], "volume_m3": [0.08, 0.40]}),
        ("low_traffic", {"traffic": {"rush_morning": 1.0, "rush_evening": 1.0,
                                       "midday": 1.0, "night": 1.0}}),
        ("high_traffic", {"traffic": {"rush_morning": 1.6, "rush_evening": 1.7,
                                        "midday": 1.2, "night": 1.0}}),
    ]
    rows = []
    original = copy.deepcopy(CONFIG)
    try:
        for scenario, overrides in scenarios:
            CONFIG.clear(); CONFIG.update(copy.deepcopy(original))
            CONFIG.update(copy.deepcopy(overrides))
            order_count = overrides.get("order_count", CONFIG["orders"])
            for seed in (0, 1, 2):
                orders, d = make_instance(seed, order_count=order_count)
                started = time.perf_counter()
                candidates = candidate_runs(orders, d, seed)
                candidate_runtime = time.perf_counter() - started
                best = min(candidates, key=lambda row: float(row["cost_rs"]))
                rows.append({"scenario": scenario, "seed": seed, "n_orders": order_count,
                             "fleet_type_count": len(active_fleet()),
                             "route_groups": CONFIG["assumed_route_groups"],
                             "algorithm": "Trajecta best-of-56", "cost_rs": best["cost_rs"],
                             "distance_km": best["distance_km"], "penalty_rs": best["penalty_rs"],
                             "ontime_pct": best["ontime_pct"], "full_model_feasible": math.isfinite(best["cost_rs"]),
                             "runtime_s": candidate_runtime})
                for objective, label in (("simplified", "OR-Tools simplified"),
                                         ("seven_factor", "OR-Tools seven-factor")):
                    started = time.perf_counter()
                    baseline = ortools_baseline(orders, d, seed, seconds=1, objective=objective)
                    rows.append({"scenario": scenario, "seed": seed, "n_orders": order_count,
                                 "fleet_type_count": len(active_fleet()),
                                 "route_groups": CONFIG["assumed_route_groups"],
                                 "algorithm": label, "cost_rs": baseline["cost_rs"],
                                 "distance_km": baseline["distance_km"], "penalty_rs": baseline["penalty_rs"],
                                 "ontime_pct": baseline["ontime_pct"],
                                 "full_model_feasible": baseline["full_model_feasible"],
                                 "full_model_cost_rs": baseline["full_model_cost_rs"],
                                 "runtime_s": time.perf_counter() - started})
    finally:
        CONFIG.clear(); CONFIG.update(original)
    return rows


def exact_small_instance(orders, d, seed):
    order_count = len(orders)
    full_mask = (1 << order_count) - 1
    vehicles = active_fleet()
    route_cost = {}
    for mask in range(1, full_mask + 1):
        route_orders = [index for index in range(order_count) if mask & (1 << index)]
        total_weight = sum(orders[index].weight for index in route_orders)
        total_volume = sum(orders[index].volume for index in route_orders)
        for vehicle_index, vehicle in enumerate(vehicles):
            if (total_weight > vehicle["weight"] or total_volume > vehicle["volume"]
                    or not pack3d(route_orders, vehicle, orders)):
                route_cost[(mask, vehicle_index)] = math.inf
                continue
            best_cost = math.inf
            for route in itertools.permutations(route_orders):
                cost = score_route(route, vehicle, orders, d, seed, prevalidated=True)[0]
                if cost < best_cost:
                    best_cost = cost
            route_cost[(mask, vehicle_index)] = best_cost

    @functools.lru_cache(maxsize=None)
    def solve(mask, used_vehicles, route_count):
        if mask == full_mask:
            return 0.0
        if route_count >= CONFIG["assumed_route_groups"]:
            return math.inf
        remaining = full_mask ^ mask
        first = remaining & -remaining
        best = math.inf
        subset = remaining
        while subset:
            if subset & first:
                for vehicle_index in range(len(vehicles)):
                    vehicle_bit = 1 << vehicle_index
                    if used_vehicles & vehicle_bit:
                        continue
                    this_route = route_cost[(subset, vehicle_index)]
                    if not math.isfinite(this_route):
                        continue
                    best = min(best, this_route + solve(mask | subset,
                                                         used_vehicles | vehicle_bit,
                                                         route_count + 1))
            subset = (subset - 1) & remaining
        return best

    return solve(0, 0, 0)


def run_optimality_gap_experiments():
    rows = []
    for seed in (0, 1, 2):
        orders, d = make_instance(seed, order_count=7)
        exact_cost = exact_small_instance(orders, d, seed)
        candidates = candidate_runs(orders, d, seed)
        best_candidate = min(candidates, key=lambda row: float(row["cost_rs"]))
        meta = {row["algorithm"]: row for row in metaheuristic_runs(orders, d, seed)}
        baseline_full = ortools_baseline(orders, d, seed, seconds=2, objective="seven_factor")
        baseline_simple = ortools_baseline(orders, d, seed, seconds=2, objective="simplified")
        methods = [
            ("Trajecta best-of-56", best_candidate["cost_rs"], math.isfinite(best_candidate["cost_rs"])),
            ("ALNS", meta["ALNS"]["cost_rs"], math.isfinite(meta["ALNS"]["cost_rs"])),
            ("Genetic Algorithm", meta["Genetic Algorithm"]["cost_rs"], math.isfinite(meta["Genetic Algorithm"]["cost_rs"])),
            ("Tabu Search", meta["Tabu Search"]["cost_rs"], math.isfinite(meta["Tabu Search"]["cost_rs"])),
            ("OR-Tools seven-factor", baseline_full["cost_rs"], baseline_full["full_model_feasible"]),
            ("OR-Tools simplified, rescored", baseline_simple["full_model_cost_rs"], baseline_simple["full_model_feasible"]),
        ]
        for method, cost, feasible in methods:
            gap = 100.0 * (float(cost) / exact_cost - 1.0) if feasible and math.isfinite(exact_cost) else math.inf
            rows.append({"n_orders": len(orders), "seed": seed, "method": method,
                         "exact_optimum_cost_rs": exact_cost,
                         "cost_rs": cost if feasible else math.inf,
                         "feasible": bool(feasible), "gap_pct": gap,
                         "gap_valid": bool(feasible and math.isfinite(exact_cost))})
    return rows


def paired_comparison_rows(varied_rows):
    output = []
    keys = sorted({(row["scenario"], int(row["seed"])) for row in varied_rows})
    for baseline_name in ("OR-Tools seven-factor", "OR-Tools simplified"):
        differences = []
        baseline_values = []
        trajecta_values = []
        for scenario, seed in keys:
            matches = [row for row in varied_rows
                       if row["scenario"] == scenario and int(row["seed"]) == seed]
            candidate = next(row for row in matches if row["algorithm"] == "Trajecta best-of-56")
            baseline = next(row for row in matches if row["algorithm"] == baseline_name)
            baseline_cost = (baseline.get("full_model_cost_rs")
                             if baseline_name == "OR-Tools simplified" else baseline.get("cost_rs"))
            if (candidate.get("full_model_feasible") and baseline.get("full_model_feasible")
                    and baseline_cost is not None and math.isfinite(float(baseline_cost))
                    and math.isfinite(float(candidate["cost_rs"]))):
                trajecta_values.append(float(candidate["cost_rs"]))
                baseline_values.append(float(baseline_cost))
                differences.append(float(candidate["cost_rs"]) - float(baseline_cost))
        statistic = p_value = None
        if len(differences) >= 2:
            try:
                from scipy.stats import wilcoxon
                result = wilcoxon(differences, alternative="two-sided", zero_method="zsplit")
                statistic, p_value = float(result.statistic), float(result.pvalue)
            except (ImportError, ValueError):
                pass
        output.append({"baseline": baseline_name, "matched_scenario_seed_pairs": len(differences),
                       "available_scenario_seed_pairs": len(keys),
                       "excluded_due_to_infeasibility_or_failure": len(keys) - len(differences),
                       "mean_trajecta_cost_rs": statistics.mean(trajecta_values) if trajecta_values else None,
                       "mean_baseline_full_model_cost_rs": statistics.mean(baseline_values) if baseline_values else None,
                       "mean_paired_cost_difference_rs": statistics.mean(differences) if differences else None,
                       "wilcoxon_statistic": statistic, "wilcoxon_p_value": p_value,
                       "test_scope": "paired only where both methods produced full-model-feasible plans"})
    return output


def metaheuristic_runs(orders, d, seed):
                                                                       
    rng = random.Random(seed + 80001)
    initial = [make_routes(g, orders, d, "NN", seed) for g in make_splits(orders, d)[0]]
    def fit(routes): return route_solution_stats(routes, orders, d, seed)[0]
    def best_route_cost(route):
        return min(score_route(route, v, orders, d, seed)[0] for v in active_fleet())
    rows = []

                                                                         
    started = time.perf_counter()
    cur = [r[:] for r in initial]; best = [r[:] for r in cur]
    best_cost = cur_cost = fit(cur)
    for _ in range(CONFIG["metaheuristic_iterations"]):
        cand = [r[:] for r in cur]
        ri = rng.randrange(len(cand)); route = cand[ri]
        q = max(1, len(route) // 4)
        removed = rng.sample(route, min(q, len(route)))
        cand[ri] = [x for x in route if x not in removed]
        rng.shuffle(removed)
        for node in removed:
            positions = range(len(cand[ri]) + 1)
            pos = min(positions, key=lambda p: best_route_cost(cand[ri][:p] + [node] + cand[ri][p:]))
            cand[ri].insert(pos, node)
        value = fit(cand)
        if value < cur_cost or rng.random() < .08:
            cur, cur_cost = cand, value
        if value < best_cost: best, best_cost = cand, value
    c, km, pen, ot, _ = route_solution_stats(best, orders, d, seed)
    rows.append({"algorithm":"ALNS", "cost_rs":c, "distance_km":km, "penalty_rs":pen,
                 "ontime_pct":ot, "runtime_s":time.perf_counter() - started})

                                                                      
    started = time.perf_counter()
    population = []
    for _ in range(10):
        ind = [r[:] for r in initial]
        for r in ind: rng.shuffle(r)
        population.append(ind)
    for _ in range(12):
        population.sort(key=fit); nxt = population[:2]
        while len(nxt) < 10:
            p1, p2 = rng.sample(population[:6], 2)
            child = [order_crossover(a, b, rng) for a, b in zip(p1, p2)]
            ri = rng.randrange(len(child))
            if len(child[ri]) > 1:
                i, j = rng.sample(range(len(child[ri])), 2); child[ri][i], child[ri][j] = child[ri][j], child[ri][i]
            nxt.append(child)
        population = nxt
    best = min(population, key=fit)
    c, km, pen, ot, _ = route_solution_stats(best, orders, d, seed)
    rows.append({"algorithm":"Genetic Algorithm", "cost_rs":c, "distance_km":km, "penalty_rs":pen,
                 "ontime_pct":ot, "runtime_s":time.perf_counter() - started})

                                                                                 
    started = time.perf_counter()
    cur = [r[:] for r in initial]; best = [r[:] for r in cur]
    cur_cost = best_cost = fit(cur); tabu = []
    for _ in range(CONFIG["metaheuristic_iterations"]):
        neighbors = []
        for ri, route in enumerate(cur):
            if len(route) < 2: continue
            pairs = list(itertools.combinations(range(len(route)), 2)); rng.shuffle(pairs)
            for i, j in pairs[:12]:
                cand = [r[:] for r in cur]; cand[ri][i], cand[ri][j] = cand[ri][j], cand[ri][i]
                move = tuple(sorted((route[i], route[j])))
                val = fit(cand)
                if move not in tabu or val < best_cost: neighbors.append((val, cand, move))
        if not neighbors: break
        value, cur, move = min(neighbors, key=lambda x: x[0]); cur_cost = value
        tabu.append(move); tabu = tabu[-7:]
        if value < best_cost: best, best_cost = [r[:] for r in cur], value
    c, km, pen, ot, _ = route_solution_stats(best, orders, d, seed)
    rows.append({"algorithm":"Tabu Search", "cost_rs":c, "distance_km":km, "penalty_rs":pen,
                 "ontime_pct":ot, "runtime_s":time.perf_counter() - started})
    return rows


def score_simplified_route(route, vehicle, orders, d, seed):
    if not route:
        return 0.0, 0.0, 0.0, 100.0
    clock = 8.0
    distance = 0.0
    late_days = 0.0
    ontime = 0
    previous_city = 0
    for index in route:
        order = orders[index]
        km = d[previous_city][order.city]
        distance += km
        clock = max(clock + travel_hours(km, vehicle, clock), order.arrival_h)
        clock += service_minutes(order, seed) / 60.0
        ontime += clock <= order.due_h
        late_days += max(0.0, (clock - order.due_h) / 24.0)
        previous_city = order.city
    distance += d[previous_city][0]
    penalty = late_days * CONFIG["late_rate_rs_per_day"]
    cost = distance * CONFIG["baseline_distance_cost_rs_per_km"] + penalty
    return cost, distance, penalty, 100.0 * ontime / len(route)


def ortools_baseline(orders, d, seed, seconds=None, objective="simplified"):
    vehicles = active_fleet()
    n, nv = len(orders), len(vehicles)
    manager = pywrapcp.RoutingIndexManager(n + 1, nv, 0)
    routing = pywrapcp.RoutingModel(manager)

    def city_for_node(node):
        return 0 if node == 0 else orders[node - 1].city

    def transit(from_idx, to_idx, vi):
        a, b = manager.IndexToNode(from_idx), manager.IndexToNode(to_idx)
        km = d[city_for_node(a)][city_for_node(b)]
        if objective == "simplified":
            cost_rs = km * CONFIG["baseline_distance_cost_rs_per_km"]
        else:
            vehicle = vehicles[vi]
            variable_rate = (
                CONFIG["fuel_rs_per_km"][vehicle["kind"]] * CONFIG["terrain_gradient_factor"]
                + CONFIG["wage_rs_per_km"]
                + CONFIG["maintenance_rs_per_km"]
                + (CONFIG["electric_consumption_kwh_per_km"]
                   * CONFIG["charging_tariff_rs_per_kwh"] if vehicle["kind"] == "electric" else 0.0)
            )
            cost_rs = km * variable_rate
            if b:
                order = orders[b - 1]
                cost_rs += (int(order.fragile) * CONFIG["packaging_rs_per_order"]
                            + int(order.cooling) * CONFIG["cooling_rs_per_order"])
            cost_rs *= CONFIG["cost_rate_scale"]
        return int(round(cost_rs * 100))

    for vi in range(nv):
        cb = routing.RegisterTransitCallback(lambda a, b, vi=vi: transit(a, b, vi))
        routing.SetArcCostEvaluatorOfVehicle(cb, vi)
        if objective == "seven_factor":
            vehicle = vehicles[vi]
            vehicle_class = ("two_wheeler" if vehicle["name"].startswith("2W")
                             else "truck" if vehicle["name"].startswith("Truck") else "four_wheeler")
            fixed_rs = vehicle["fixed"] + CONFIG["toll_rs_by_vehicle_class"][vehicle_class]
            routing.SetFixedCostOfVehicle(int(round(fixed_rs * CONFIG["cost_rate_scale"] * 100)), vi)
    def demand_cb(idx):
        node = manager.IndexToNode(idx)
        return 0 if node == 0 else int(round(orders[node - 1].weight * 100))
    demand = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(demand, 0,
        [int(v["weight"] * 100) for v in vehicles], True, "Weight")
    def vol_cb(idx):
        node = manager.IndexToNode(idx)
        return 0 if node == 0 else int(round(orders[node - 1].volume * 1000))
    vol = routing.RegisterUnaryTransitCallback(vol_cb)
    routing.AddDimensionWithVehicleCapacity(vol, 0,
        [int(v["volume"] * 1000) for v in vehicles], True, "Volume")
    time_callbacks = []
    for vehicle in vehicles:
        def time_cb(from_idx, to_idx, vehicle=vehicle):
            a, b = manager.IndexToNode(from_idx), manager.IndexToNode(to_idx)
            km = d[city_for_node(a)][city_for_node(b)]
            service = 0.0
            if b != 0:
                order = orders[b - 1]
                service = service_minutes(order, seed)
            return int(round(km / vehicle["speed"] * 1.15 * 60 + service))
        time_callbacks.append(routing.RegisterTransitCallback(time_cb))
    routing.AddDimensionWithVehicleTransitAndCapacity(
        time_callbacks, 12 * 60, [48 * 60] * nv, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for vi in range(nv):
        time_dim.CumulVar(routing.Start(vi)).SetRange(8 * 60, 8 * 60)
    for oi, o in enumerate(orders):
        idx = manager.NodeToIndex(oi + 1)
        lo = max(8 * 60, int(o.arrival_h * 60)); hi = 48 * 60
        time_dim.CumulVar(idx).SetRange(lo, hi)
        penalty_scale = CONFIG["cost_rate_scale"] if objective == "seven_factor" else 1.0
        time_dim.SetCumulVarSoftUpperBound(
            idx, int(o.due_h * 60),
            max(1, int(CONFIG["late_rate_rs_per_day"] * penalty_scale * 100 / (24 * 60))))
        eligible = {vi for vi, v in enumerate(vehicles)
                if o.weight <= v["weight"] and o.volume <= v["volume"]}
                                                                               
                                                                              
        for vi in range(nv):
            if vi not in eligible:
                routing.solver().Add(routing.VehicleVar(idx) != vi)
    solver = routing.solver()
    solver.Add(solver.Sum([routing.ActiveVehicleVar(vi) for vi in range(nv)]) <= CONFIG["assumed_route_groups"])
    if objective == "seven_factor":
        for vi, vehicle in enumerate(vehicles):
            for from_node in range(n + 1):
                from_index = routing.Start(vi) if from_node == 0 else manager.NodeToIndex(from_node)
                from_city = city_for_node(from_node)
                for to_node in range(n + 1):
                    if from_node == to_node:
                        continue
                    to_index = routing.End(vi) if to_node == 0 else manager.NodeToIndex(to_node)
                    rule = infrastructure_rule(from_city, city_for_node(to_node))
                    if not rule:
                        continue
                    violates = (
                        (rule.get("two_wheeler_allowed") is False and vehicle["name"].startswith("2W"))
                        or vehicle["weight"] > rule.get("max_payload_kg", math.inf)
                        or vehicle["height"] > rule.get("max_vehicle_height_m", math.inf)
                    )
                    if violates:
                        if from_node == 0:
                            solver.Add(routing.NextVar(from_index) != to_index)
                        else:
                            solver.Add(
                                solver.IsDifferentCstVar(routing.VehicleVar(from_index), vi)
                                + solver.IsDifferentCstVar(routing.NextVar(from_index), to_index) >= 1
                            )
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(seconds or CONFIG["ortools_seconds"])
    params.log_search = False
    solution = routing.SolveWithParameters(params)
    if solution is None:
        return {"status": "no_solution", "cost_rs": None, "distance_km": None,
                "penalty_rs": None, "ontime_pct": None, "solver_objective_rs": None,
                "full_model_feasible": False, "full_model_cost_rs": None,
                "objective_model": "seven-factor" if objective == "seven_factor"
                else "distance_km*12 + due_lateness_penalty"}
    distance = 0.0; penalty = 0.0; cost = 0.0; ontime = 0; served = 0
    full_model_cost = 0.0; full_model_feasible = True
    for vi, vehicle in enumerate(vehicles):
        idx = routing.Start(vi); route = []
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            if node:
                route.append(node - 1)
            idx = solution.Value(routing.NextVar(idx))
        if not route:
            continue
        simple_result = score_simplified_route(route, vehicle, orders, d, seed)
        full_result = score_route(route, vehicle, orders, d, seed)
        result = full_result if objective == "seven_factor" else simple_result
        cost += result[0]
        distance += result[1]; penalty += result[2]
        ontime += result[3] * len(route) / 100; served += len(route)
        if math.isfinite(full_result[0]):
            full_model_cost += full_result[0]
        else:
            full_model_feasible = False
    return {"status": "ok", "cost_rs": cost,
            "solver_objective_rs": float(solution.ObjectiveValue()) / 100.0,
            "distance_km": distance,
            "penalty_rs": penalty,
            "ontime_pct": 100 * ontime / max(1, served),
            "full_model_feasible": full_model_feasible,
            "full_model_cost_rs": full_model_cost if full_model_feasible else None,
            "objective_model": "seven-factor" if objective == "seven_factor"
            else "distance_km*12 + due_lateness_penalty"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DATA = HERE / "datasets"
    DATA.mkdir(parents=True, exist_ok=True)
    (HERE / "assumptions.json").write_text(json.dumps(CONFIG | {"fleet": FLEET}, indent=2), encoding="utf-8")
    candidate_rows, route_detail_rows, base_rows, instance_rows, meta_rows = [], [], [], [], []

    for seed in CONFIG["seeds"]:
        orders, d = make_instance(seed)
        for o in orders:
            instance_rows.append(asdict(o) | {"seed": seed})
        cr = candidate_runs(orders, d, seed)
        best = min(cr, key=lambda r: r["cost_rs"])
        for candidate in cr:
            candidate_rows.append({"seed": seed, **{key: value for key, value in candidate.items()
                                                     if key != "route_details"}})
            candidate_id = f"{seed}-{candidate['split_index']}-{candidate['heuristic']}"
            route_detail_rows.extend({
                "seed": seed,
                "candidate_id": candidate_id,
                "split_index": candidate["split_index"],
                "split": candidate["split"],
                "heuristic": candidate["heuristic"],
                **detail,
            } for detail in candidate["route_details"])
        meta_rows.extend({"seed": seed, **r} for r in metaheuristic_runs(orders, d, seed))
        base = ortools_baseline(orders, d, seed, objective="simplified")
        base_rows.append({"seed": seed, "baseline_type": "simplified_cost", **base})
        full_base = ortools_baseline(orders, d, seed, objective="seven_factor")
        base_rows.append({"seed": seed, "baseline_type": "seven_factor", **full_base})
        print(f"seed={seed}: best 56-route candidate Rs {best['cost_rs']:.0f}, "
              f"{best['distance_km']:.1f} km, penalty Rs {best['penalty_rs']:.0f}, "
              f"on-time {best['ontime_pct']:.1f}%; OR-Tools={base['status']} "
              f"Rs {base['cost_rs']}")
    ablation_rows = run_ablation_experiments()
    scalability_rows = run_scalability_experiments()
    varied_rows = run_varied_experiments()
    gap_rows = run_optimality_gap_experiments()
    paired_rows = paired_comparison_rows(varied_rows)
    write_csv("ablation_summary.csv", ablation_rows)
    write_csv("scalability_summary.csv", scalability_rows)
    write_csv("varied_instances.csv", varied_rows)
    write_csv("optimality_gaps.csv", gap_rows)
    write_csv("paired_comparisons.csv", paired_rows)
    write_csv("contribution_summary.csv", contribution_summary(candidate_rows))
    with (DATA / "synthetic_30_orders.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(instance_rows[0]))
        w.writeheader(); w.writerows(instance_rows)
    city_names = [city[0] for city in CONFIG["cities"]]
    with (DATA / "city_distance_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["city_id", "city_name", *city_names])
        for city_id, city in enumerate(CONFIG["cities"]):
            w.writerow([city_id, city[0], *d[city_id]])
                                                                        
    infra_rows = []
    city_count = CONFIG["cities_including_depot"]
    for a in range(city_count):
        for b in range(a + 1, city_count):
            rule = infrastructure_rule(a, b)
            if rule: infra_rows.append({"from_city_id": a, "to_city_id": b, **rule,
                                        "source": "synthetic_assumption"})
    if infra_rows:
        infra_fields = list(dict.fromkeys(k for row in infra_rows for k in row))
        with (DATA / "synthetic_infrastructure_constraints.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=infra_fields); w.writeheader(); w.writerows(infra_rows)
    write_csv("candidate_routes.csv", candidate_rows)
    write_csv("candidate_route_details.csv", route_detail_rows)
    write_csv("ortools_baseline.csv", base_rows)
    write_csv("metaheuristic_results.csv", meta_rows)
    write_reproducibility_tables(candidate_rows)
    minima = [min(candidate_rows[i*56:(i+1)*56], key=lambda r: r["cost_rs"]) for i in range(len(CONFIG["seeds"]))]
    def stats(key):
        return summarize_stats(minima, key)
    def comparator_stats(baseline_type, key, feasible_only=False):
        rows = [r for r in base_rows if r["baseline_type"] == baseline_type and r.get("status") == "ok"]
        if feasible_only:
            rows = [r for r in rows if r.get("full_model_feasible")]
        return summarize_stats(rows, key)

    full_baseline_rows = [r for r in base_rows if r["baseline_type"] == "seven_factor"]

    def algorithm_stats(name, key):
        rows = [r for r in meta_rows if r["algorithm"] == name]
        return summarize_stats(rows, key)
    summary = {"status": "synthetic_scenario_summary",
               "runtime_environment": {"python_version": platform.python_version(),
                                       "platform": platform.platform(),
                                       "ortools_version": ortools.__version__},
               "n_seeds": len(CONFIG["seeds"]), "candidate_best_cost_rs": stats("cost_rs"),
               "candidate_distance_km": stats("distance_km"),
               "candidate_penalty_rs": stats("penalty_rs"), "candidate_ontime_pct": stats("ontime_pct"),
             "ortools_simplified_distance_penalty": {
                   key: comparator_stats("simplified_cost", key)
                   for key in ("cost_rs", "solver_objective_rs", "distance_km", "penalty_rs", "ontime_pct")
               } | {
                   "full_model_cost_rs": comparator_stats("simplified_cost", "full_model_cost_rs"),
                   "feasible_only": {key: comparator_stats("simplified_cost", key, True)
                                     for key in ("cost_rs", "distance_km", "penalty_rs", "ontime_pct",
                                                 "full_model_cost_rs")},
                   "n_solved": sum(r.get("status") == "ok" for r in base_rows
                                    if r["baseline_type"] == "simplified_cost"),
                   "n_full_model_feasible": sum(bool(r.get("full_model_feasible")) for r in base_rows
                                                 if r["baseline_type"] == "simplified_cost"),
                   "objective_model": "distance_km*12 + due_lateness_penalty"},
             "ortools_seven_factor": {
                   key: summarize_stats([r for r in full_baseline_rows if r.get("status") == "ok"], key)
                   for key in ("cost_rs", "distance_km", "penalty_rs", "ontime_pct")
               } | {
                   "feasible_only": {key: comparator_stats("seven_factor", key, True)
                                     for key in ("cost_rs", "distance_km", "penalty_rs", "ontime_pct")},
                   "n_solved": sum(r.get("status") == "ok" for r in full_baseline_rows),
                   "n_full_model_feasible": sum(bool(r.get("full_model_feasible")) for r in full_baseline_rows),
                   "objective_model": "seven-factor; post-solve 3D packing feasibility check; static 1.15 traffic factor",
               },
             "metaheuristics": {name: {key: algorithm_stats(name, key)
                                  for key in ("cost_rs", "distance_km", "penalty_rs", "ontime_pct")}
                                   for name in ("ALNS", "Genetic Algorithm", "Tabu Search")},
               "ablation": {
                   variant: {key: summarize_stats([r for r in ablation_rows if r["variant"] == variant], key)
                             for key in ("full_cost_rs", "full_distance_km", "full_penalty_rs",
                                         "full_ontime_pct", "runtime_s", "capacity_violations",
                                         "pack3d_violations", "infrastructure_violations")}
                           | {"n_feasible": sum(bool(r["full_model_feasible"]) for r in ablation_rows
                                               if r["variant"] == variant),
                              "n_runs": sum(r["variant"] == variant for r in ablation_rows)}
                   for variant in sorted({r["variant"] for r in ablation_rows})
               },
               "scalability": {
                   str(size): {
                       "n_orders": size,
                       "n_runs": sum(r["n_orders"] == size for r in scalability_rows),
                       "n_valid_costs": sum(r["n_orders"] == size and r["cost_rs"] is not None
                                            and math.isfinite(float(r["cost_rs"])) for r in scalability_rows),
                       "avg_runtime_s": summarize_stats([r for r in scalability_rows if r["n_orders"] == size], "runtime_s")["mean"],
                       "avg_cost_rs": summarize_stats([r for r in scalability_rows if r["n_orders"] == size], "cost_rs")["mean"],
                       "avg_distance_km": summarize_stats([r for r in scalability_rows if r["n_orders"] == size], "distance_km")["mean"],
                       "algorithms": {
                           name: {
                               "cost_rs": summarize_stats([r for r in scalability_rows
                                   if r["n_orders"] == size and r["algorithm"] == name], "cost_rs"),
                               "distance_km": summarize_stats([r for r in scalability_rows
                                   if r["n_orders"] == size and r["algorithm"] == name], "distance_km"),
                               "runtime_s": summarize_stats([r for r in scalability_rows
                                   if r["n_orders"] == size and r["algorithm"] == name], "runtime_s"),
                               "feasible_runs": sum(bool(r.get("full_model_feasible")) for r in scalability_rows
                                   if r["n_orders"] == size and r["algorithm"] == name),
                               "total_runs": sum(r["n_orders"] == size and r["algorithm"] == name
                                   for r in scalability_rows),
                           }
                           for name in sorted({r["algorithm"] for r in scalability_rows if r["n_orders"] == size})
                       },
                   } for size in sorted({r["n_orders"] for r in scalability_rows})
               },
               "optimality_gaps": {
                   method: summarize_stats([r for r in gap_rows if r["method"] == method and r["gap_valid"]], "gap_pct")
                   | {"n_infeasible_or_failed": sum(r["method"] == method and not r["feasible"] for r in gap_rows),
                      "n_runs": sum(r["method"] == method for r in gap_rows)}
                   for method in sorted({r["method"] for r in gap_rows})
               },
               "candidate_analysis": json.loads((OUT / "candidate_analysis.json").read_text(encoding="utf-8")),
               "paired_comparisons": paired_rows,
               "varied_scenarios": sorted({r["scenario"] for r in varied_rows})}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Wrote", OUT)
    print(json.dumps(summary, indent=2))


def run_stage(stage):
    if stage == "core_tables":
        with (OUT / "candidate_routes.csv").open(newline="", encoding="utf-8") as stream:
            candidate_rows = list(csv.DictReader(stream))
        (HERE / "assumptions.json").write_text(json.dumps(CONFIG | {"fleet": FLEET}, indent=2), encoding="utf-8")
        write_csv("contribution_summary.csv", contribution_summary(candidate_rows))
        write_reproducibility_tables(candidate_rows)
    elif stage == "ablation":
        write_csv("ablation_summary.csv", run_ablation_experiments())
    elif stage == "scalability":
        write_csv("scalability_summary.csv", run_scalability_experiments())
    elif stage == "varied":
        write_csv("varied_instances.csv", run_varied_experiments())
    elif stage == "optimality_gaps":
        write_csv("optimality_gaps.csv", run_optimality_gap_experiments())
    else:
        raise ValueError(f"Unknown experiment stage: {stage}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_stage(sys.argv[1].lstrip("-"))
    else:
        main()
