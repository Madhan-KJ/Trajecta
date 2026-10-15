# Trajecta

Routing optimization code, scenario datasets, benchmark inputs, and result artifacts.

The synthetic scenario uses structured parameter settings. Standard benchmark runs execute Trajecta's 8 split rules x 7 route heuristics and compare its best candidate with OR-Tools, ALNS, a genetic algorithm, and tabu search. Methods use a shared vehicle-count-first, distance-second objective and feasibility evaluator; published Solomon values are references only, not warm starts. Cordeau instances use a nearest-depot decomposition. See `results/benchmark_algorithm_runs.csv` and `results/benchmark_algorithm_summary.csv` for per-run and aggregated results.

The synthetic OR-Tools baseline uses CP-SAT with the same seven-factor objective, per-order/per-seed service-time samples, traffic bands, vehicle capacities, and infrastructure arc restrictions as the candidate evaluator. The existing 3D packing checker is enforced with no-good route cuts. Results report solver status, objective bound, and optimality gap; time-limited runs without a feasible solution are retained as failures, not scored.

## Setup

```powershell
python -m pip install -r requirements.txt
python recreate.py
python download_benchmarks.py
python run_benchmarks.py
```

Datasets are in `datasets/`; generated results are in `results/`.
