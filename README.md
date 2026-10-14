# Trajecta

Routing optimization code, scenario datasets, benchmark inputs, and result artifacts.

The synthetic scenario data uses structured parameter settings. Solomon benchmark runs use published reference route warm starts; Cordeau runs use a nearest-depot decomposition. See `results/summary.json`, `results/benchmark_algorithm_summary.csv`, `results/ablation_summary.csv`, and `results/scalability_summary.csv` for run outputs.

## Synthetic experiment

The synthetic instance uses 30 orders and the 18 configured city coordinates. The distance matrix is city-to-city Haversine distance (Earth radius 6,371 km) multiplied by `road_distance_factor`; order coordinates receive uniform jitter around their assigned city. The generated 18x18 matrix is saved to `datasets/city_distance_matrix.csv`.

Each seed evaluates eight splits (EDD, arrival, latitude, travel distance, longitude, latitude-longitude, penalty risk, and DBSCAN) with seven route heuristics, producing 56 candidates. DBSCAN uses the configured kilometre radius and minimum sample count; noise points remain separate before clusters are balanced into route groups. `results/candidate_routes.csv` contains candidate aggregates, while `results/candidate_route_details.csv` contains each candidate's route groups, vehicle, order sequence, city sequence, and route metrics.

Service completion at or before an order's due time counts as on-time. Service time uses `t_base + alpha*weight + beta*volume + gamma*(fragile + cooling) + delta*skill`, with skill sampled from the configured normal distribution. Cost assumptions, including fuel, packaging, cooling, class-based toll, and EV energy consumption and tariff, are in `assumptions.json`; these are synthetic assumptions, not measured tariffs.

The OR-Tools comparator minimizes `distance_km*12 + due_lateness_penalty`, not the full seven-component objective. Its reported `cost_rs` is therefore not directly comparable with the full-model candidate cost. The baseline CSV also reports whether its routes pass the full 3D-packing and infrastructure checks. Ablations reset to the same baseline configuration for each variant and record measured runtimes.

## Setup

```powershell
python -m pip install -r requirements.txt
python recreate.py
python download_benchmarks.py
python run_benchmarks.py
```

Datasets are in `datasets/`; generated results are in `results/`.
