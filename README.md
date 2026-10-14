# Trajecta

Routing optimization code, scenario datasets, benchmark inputs, and result artifacts.

The synthetic scenario data uses structured parameter settings. Solomon benchmark runs use published reference route warm starts; Cordeau runs use a nearest-depot decomposition. See `results/summary.json`, `results/benchmark_algorithm_summary.csv`, `results/ablation_summary.csv`, and `results/scalability_summary.csv` for run outputs.

The synthetic OR-Tools baseline uses CP-SAT with the same seven-factor objective, per-order/per-seed service-time samples, traffic bands, vehicle capacities, and infrastructure arc restrictions as the candidate evaluator. The existing 3D packing checker is enforced with no-good route cuts. Results report solver status, objective bound, and optimality gap; time-limited runs without a feasible solution are retained as failures, not scored.

## Setup

```powershell
python -m pip install -r requirements.txt
python recreate.py
python download_benchmarks.py
python run_benchmarks.py
```

Datasets are in `datasets/`; generated results are in `results/`.
