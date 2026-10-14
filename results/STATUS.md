# Revision Status: P0-P3 Complete

Experiment command: `python recreate.py`  
Paper-input command: `python revision_outputs.py`  
Implementation: `recreate.py`; report generator: `revision_outputs.py`.  
Environment: Python 3.12.9, Windows 11, AMD64 Family 25 Model 80, 12 logical CPUs, 16,539,553,792 RAM bytes, OR-Tools 9.15.6755. See `results/run_info.json` for package versions and git hash.  
Main run: seeds 0-9, 30 orders, all 56 candidates per seed. Each candidate is a full four-route-group plan. The seven fleet records are vehicle types, not vehicle inventory.

## Headline Results

| Method | Cost Rs. mean +/- SD | Distance km mean +/- SD | Penalty Rs. mean +/- SD | On-time % mean +/- SD | Full-check feasibility |
|---|---:|---:|---:|---:|---:|
| Trajecta best-of-56, full-plan totals | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 | 10/10 |
| OR-Tools seven-factor search, rescored | 5,261.99 +/- 186.51 | 1,183.27 +/- 72.35 | 699.82 +/- 153.06 | 42.38 +/- 5.68 | 7/10; 3 failed |
| OR-Tools simplified objective, feasible subset | 12,691.96 +/- 1,894.24 full-model cost | 1,181.69 +/- 84.79 | 547.92 +/- 119.76 | 42.67 +/- 4.35 | 5/10; 5 failed |

The seven-factor OR-Tools comparator has lower mean cost and distance on its feasible runs; current evidence does not show a Trajecta advantage. Its valid-cost mean covers 7 runs, not 10. The simplified comparator's own objective cost is Rs. 14,425.23 +/- 1,043.89 across 10 solved runs; its full-model rescoring is possible on only 5/10 runs. Its all-solved penalty mean is Rs. 596.93 +/- 164.28, while the feasible-only penalty mean is Rs. 547.92 +/- 119.76. The seven-factor comparator penalty is Rs. 699.82 +/- 153.06 on 7 feasible runs.

On-time is the share of orders completed at or before due time after waiting until arrival/release time; the paper metric is the mean and sample SD of seed-level best-cost-plan percentages. The current value is 42.00% +/- 12.49 percentage points, not 95%.

## P1 Experiments

- Six-feature ablation: 10 seeds per variant; each selected plan is rescored with all features enabled. Baseline is 10/10 feasible. Disabling infrastructure yields 6/10 feasible and 6 route-level infrastructure violations across failed plans. In the first three seeds, baseline and no-infrastructure select identical plans with no active restricted edges; the old match was locally inactive, not proof that the check is globally inactive. Other seeds demonstrate violations when the filter is removed.
- Removing 3D packing, penalty-risk splitting, or stochastic service time produced the same best-of-56 metrics as baseline on this synthetic sample; this means no measured effect on selected plans here, not general irrelevance. Removing DBSCAN worsened the best-plan mean cost to Rs. 18,447.40 +/- 2,680.33. Removing traffic changed mean cost only slightly to Rs. 13,500.35 +/- 1,364.79.
- Split/heuristic contribution: generated win rates, mean/best cost, nonfinite candidate counts, and leave-one-out regret are in `results/contribution_summary.csv` and `results/summary.md`.
- Exact gaps: seven-order exhaustive ordered-route evaluation plus subset DP over three seeds. Mean gaps: Trajecta 118.76% +/- 30.94; ALNS, GA, and Tabu each 177.00% +/- 26.70; OR-Tools seven-factor 0% +/- 0%; simplified OR-Tools rescored 125.13% +/- 0.71. This is an exact optimum only for the implemented seven-order model.
- Varied instances cover order counts 20/30/50, type pools of 4/7, high demand, and low/high traffic, three seeds per scenario. Four-type scenarios had 0/3 feasible runs for both Trajecta and seven-factor OR-Tools; failures are retained.
- Scalability covers 20/30/50/80 orders, two seeds, per-algorithm runtimes, quality, and feasibility counts. At 30 orders, Trajecta's 56-candidate constructive run averaged 0.145 s +/- 0.005; the seven-factor OR-Tools run averaged 1.017 s +/- 0.003 with a one-second limit. These are not an exact-solver comparison; traffic treatment and packing enforcement differ.
- Paired Wilcoxon tests on matched full-model-feasible scenario-seed pairs: seven-factor OR-Tools, 13/21 pairs, p=0.0002441; simplified baseline, 7/21 pairs, p=0.03125. Excluded pairs are due to infeasibility/failure; report denominators with p-values.
- Solomon/Cordeau artifacts remain distance-based algorithm tests: Solomon methods use published reference-route warm starts; Cordeau uses nearest-depot assignment. They are not independent full-Trajecta evaluations.

## Reproducibility and Deliverables

Generated: `results/run_info.json`, `results/reproducibility_tables.json`, the 56-row `results/candidate_route_summary.csv`, `results/objective_selection.csv`, `results/candidate_analysis.json`, all experiment CSVs, `results/summary.md`, `results/claims_ledger.md`, and `results/paper_changes.md`. Six figures are under `results/figures/`: main comparison, ablation, scalability, optimality gap, split/heuristic contribution, and distance-penalty scatter.

Distance discrepancy: 2,182.45 km is the full-plan mean across four route groups. Feasible individual route groups in current details average 907.82 km (SD 260.84; range 178.29-1,725.41). The paper's 420-520 km range is not supported as a full-plan total or by current route-detail values; do not reuse it without recovering its original calculation.

All scenario data, infrastructure rules, route-group counts, traffic factors, fuel and toll rates, and service-time parameters are synthetic assumptions. The OR-Tools seven-factor objective uses a static 1.15 traffic factor and validates 3D packing after solve; it is not fully equivalent to Trajecta's dynamic scoring and must not be called Gurobi or exact. Range and real fleet inventory are not modeled. The historical Rs. 4,200 / 31% / 100% penalty reduction / 95% on-time / Gurobi timing claims are retired.

The Word manuscript was intentionally not created, as requested. Industry validation, real-time traffic, dispatcher visualization/authorization, and multi-depot live replanning remain future work.
