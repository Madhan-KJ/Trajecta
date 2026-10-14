# Trajecta Revision Results

Generated from experiment artifacts by `revision_outputs.py`; do not edit reported values by hand.

## Run Record

Command: `python recreate.py`; Python 3.12.9; Windows-11-10.0.26300-SP0; CPU `AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD`; logical CPUs 12; RAM bytes 16539553792.
Packages: {"matplotlib": "3.11.2", "numpy": "2.3.5", "ortools": "9.15.6755", "pandas": "3.0.1", "scipy": "1.18.1"}. Git hash: `46c40c24599a11b3128a94c6d5b7524ec983e615`.
Main seeds: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9; main orders per seed: 30; candidates per seed: 56; OR-Tools time limit: 2 s.
All generated data, infrastructure restrictions, traffic parameters, tolls, and route-group counts are synthetic assumptions; none are measured operational data.

## Main Results

| Method / selection | Cost Rs. mean +/- SD | Distance km mean +/- SD | Penalty Rs. mean +/- SD | On-time % mean +/- SD | Feasible / runs |
|---|---|---|---|---|---|
| Trajecta best-of-56 full-plan | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 | 10/10 |
| OR-Tools seven-factor search; full-model rescoring | 5,261.99 +/- 186.51 | 1,183.27 +/- 72.35 | 699.82 +/- 153.06 | 42.38 +/- 5.68 | 7/10 |
| OR-Tools simplified objective; full-model feasible subset | 12,691.96 +/- 1,894.24 | 1,181.69 +/- 84.79 | 547.92 +/- 119.76 | 42.67 +/- 4.35 | 5/10 |

On-time percentage is the share of orders completed at or before due time after waiting until arrival/release time; the table reports mean and sample SD over seed-level plans. Candidate cost, distance, and penalty are totals across the complete four-group plan. OR-Tools seven-factor traffic is approximated with a static factor and 3D packing is checked after solve; its infeasible outputs remain counted above.

## Corrected Objective Table

| Objective | Selected split / heuristic by seed | Cost Rs. mean +/- SD | Distance km mean +/- SD | Penalty Rs. mean +/- SD | On-time % mean +/- SD |
|---|---|---|---|---|---|
| min_cost | 0:DensityGeo/FI; 1:DensityGeo/FI; 2:DensityGeo/RNN; 3:DensityGeo/FI; 4:DensityGeo/FI; 5:DensityGeo/CFRS; 6:DensityGeo/FI; 7:DensityGeo/RNN; 8:DensityGeo/FI; 9:DensityGeo/FI | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 |
| min_distance | 0:DensityGeo/FI; 1:DensityGeo/FI; 2:DensityGeo/RNN; 3:DensityGeo/FI; 4:DensityGeo/FI; 5:DensityGeo/CFRS; 6:DensityGeo/FI; 7:DensityGeo/FI; 8:DensityGeo/FI; 9:DensityGeo/FI | 13,504.36 +/- 1,368.58 | 2,178.90 +/- 210.34 | 469.68 +/- 154.46 | 40.67 +/- 12.25 |
| min_penalty | 0:DensityGeo/RNN; 1:DensityGeo/RNN; 2:DensityGeo/RNN; 3:DensityGeo/RNN; 4:DensityGeo/FI; 5:DensityGeo/CFRS; 6:DensityGeo/NN; 7:DensityGeo/RNN; 8:DensityGeo/NN; 9:DensityGeo/RNN | 14,203.38 +/- 2,106.03 | 2,243.66 +/- 200.54 | 347.71 +/- 136.35 | 48.33 +/- 13.54 |

All three objectives selected the same candidate in 3 of 10 seeds. Pairwise coincidences: {"min_cost_min_distance": 9, "min_cost_min_penalty": 4, "min_distance_min_penalty": 3}. Pareto-optimal candidates per seed: mean 1.90, SD 0.74; finite candidates only. Tie-breaking: objective metric, then cost, distance, penalty, split index, heuristic order.
Unit clarification: candidate distances are totals over four route groups. Individual route-group distances from candidate_route_details.csv have mean 907.82 km (SD 260.84; min 178.29, max 1,725.41). The paper's 420-520 km range is not supported as a full-plan distance; any route-level comparison must state its aggregation and seed set.

### All 56 Candidates

| Split | Heuristic | Cost mean +/- SD | Distance mean +/- SD | Penalty mean +/- SD | On-time mean +/- SD | Valid seeds / nonfinite |
|---|---|---|---|---|---|---|
| EDD | NN | 20,545.27 +/- 2,468.64 | 2,909.08 +/- 842.93 | 636.21 +/- 132.90 | 39.00 +/- 10.66 | 9 / 1 |
| EDD | BiDir | 27,008.97 +/- 3,341.02 | 3,199.54 +/- 1,384.70 | 1,336.44 +/- 174.27 | 24.00 +/- 8.43 | 7 / 3 |
| EDD | MU | 27,711.01 +/- 3,583.25 | 3,928.89 +/- 693.05 | 1,919.88 +/- 279.77 | 5.33 +/- 5.26 | 9 / 1 |
| EDD | FI | 18,768.82 +/- 2,617.13 | 2,626.83 +/- 719.93 | 890.30 +/- 167.89 | 27.00 +/- 10.12 | 9 / 1 |
| EDD | RNN | 20,656.47 +/- 2,867.53 | 2,444.84 +/- 1,250.02 | 627.60 +/- 167.11 | 33.33 +/- 18.66 | 7 / 3 |
| EDD | G TW | 23,711.68 +/- 3,372.50 | 3,648.94 +/- 438.25 | 830.36 +/- 217.29 | 35.33 +/- 5.71 | 10 / 0 |
| EDD | CFRS | 24,928.67 +/- 2,848.46 | 3,899.48 +/- 368.01 | 1,119.44 +/- 221.87 | 22.67 +/- 7.34 | 10 / 0 |
| Arrival | NN | 21,494.65 +/- 2,226.98 | 2,953.16 +/- 894.80 | 637.12 +/- 158.90 | 40.00 +/- 12.37 | 9 / 1 |
| Arrival | BiDir | 26,673.29 +/- 3,526.95 | 3,341.34 +/- 1,438.59 | 1,373.18 +/- 212.63 | 24.00 +/- 9.14 | 8 / 2 |
| Arrival | MU | 28,879.07 +/- 3,619.53 | 4,277.72 +/- 510.24 | 2,024.81 +/- 320.17 | 3.33 +/- 2.22 | 10 / 0 |
| Arrival | FI | 19,502.61 +/- 1,941.92 | 2,658.22 +/- 775.48 | 933.02 +/- 121.19 | 24.67 +/- 9.84 | 9 / 1 |
| Arrival | RNN | 20,726.36 +/- 2,458.24 | 2,892.73 +/- 860.59 | 693.57 +/- 144.75 | 38.67 +/- 11.46 | 9 / 1 |
| Arrival | G TW | 24,818.30 +/- 2,487.10 | 3,786.23 +/- 371.62 | 889.60 +/- 194.39 | 37.00 +/- 5.54 | 10 / 0 |
| Arrival | CFRS | 26,360.65 +/- 2,888.83 | 4,042.28 +/- 426.91 | 1,129.32 +/- 263.70 | 24.33 +/- 7.71 | 10 / 0 |
| Latitude | NN | 24,143.99 +/- 3,498.61 | 3,144.22 +/- 1,089.09 | 731.70 +/- 153.65 | 32.67 +/- 11.20 | 8 / 2 |
| Latitude | BiDir | 28,427.06 +/- 3,709.36 | 2,937.46 +/- 1,678.40 | 1,434.79 +/- 233.01 | 21.67 +/- 10.69 | 6 / 4 |
| Latitude | MU | 31,325.37 +/- 4,849.35 | 4,575.28 +/- 624.31 | 2,199.16 +/- 349.84 | 3.00 +/- 3.67 | 10 / 0 |
| Latitude | FI | 21,856.20 +/- 2,865.62 | 3,190.75 +/- 354.83 | 1,042.93 +/- 171.76 | 26.00 +/- 6.81 | 10 / 0 |
| Latitude | RNN | 23,195.20 +/- 3,473.72 | 3,067.18 +/- 1,052.73 | 729.16 +/- 155.76 | 32.00 +/- 11.13 | 8 / 2 |
| Latitude | G TW | 29,511.21 +/- 3,560.15 | 3,705.38 +/- 1,514.38 | 1,095.88 +/- 220.03 | 27.00 +/- 11.27 | 8 / 2 |
| Latitude | CFRS | 30,363.45 +/- 5,227.78 | 4,613.92 +/- 679.58 | 1,333.02 +/- 343.99 | 20.00 +/- 6.67 | 10 / 0 |
| Depot Distance | NN | 24,139.38 +/- 1,963.00 | 2,803.61 +/- 1,216.31 | 675.42 +/- 81.70 | 33.33 +/- 14.66 | 7 / 3 |
| Depot Distance | BiDir | 26,932.68 +/- 4,021.22 | 3,024.98 +/- 1,537.68 | 1,370.51 +/- 292.14 | 21.67 +/- 8.50 | 7 / 3 |
| Depot Distance | MU | 31,624.81 +/- 4,495.27 | 4,219.05 +/- 1,294.31 | 2,252.58 +/- 314.56 | 2.33 +/- 2.25 | 9 / 1 |
| Depot Distance | FI | 21,716.08 +/- 1,963.18 | 2,432.45 +/- 1,181.20 | 1,018.60 +/- 115.65 | 19.33 +/- 9.00 | 7 / 3 |
| Depot Distance | RNN | 23,673.39 +/- 1,979.71 | 2,822.45 +/- 1,249.39 | 747.54 +/- 194.36 | 32.67 +/- 15.46 | 7 / 3 |
| Depot Distance | G TW | 28,453.40 +/- 2,641.15 | 3,926.28 +/- 1,118.94 | 1,062.67 +/- 190.73 | 29.67 +/- 9.49 | 9 / 1 |
| Depot Distance | CFRS | 31,015.51 +/- 3,835.62 | 4,714.96 +/- 489.66 | 1,319.81 +/- 313.61 | 20.67 +/- 6.25 | 10 / 0 |
| Longitude | NN | 22,960.29 +/- 1,875.68 | 3,289.95 +/- 551.06 | 737.62 +/- 141.33 | 38.00 +/- 9.05 | 9 / 1 |
| Longitude | BiDir | 26,505.12 +/- 3,332.43 | 3,736.55 +/- 1,171.12 | 1,444.59 +/- 239.12 | 25.67 +/- 6.68 | 9 / 1 |
| Longitude | MU | 30,891.67 +/- 3,730.60 | 4,561.10 +/- 569.03 | 2,227.90 +/- 262.55 | 3.00 +/- 1.89 | 10 / 0 |
| Longitude | FI | 21,083.88 +/- 1,903.99 | 2,477.67 +/- 1,140.76 | 1,057.17 +/- 164.49 | 21.00 +/- 8.90 | 7 / 3 |
| Longitude | RNN | 23,371.25 +/- 2,399.51 | 3,213.07 +/- 946.56 | 769.27 +/- 176.24 | 35.33 +/- 11.24 | 9 / 1 |
| Longitude | G TW | 28,130.08 +/- 1,952.01 | 3,935.58 +/- 1,110.47 | 1,115.38 +/- 206.86 | 29.00 +/- 11.01 | 9 / 1 |
| Longitude | CFRS | 29,925.54 +/- 3,056.36 | 4,165.09 +/- 1,177.52 | 1,345.17 +/- 307.27 | 17.00 +/- 7.11 | 9 / 1 |
| Lat-Lon | NN | 23,951.40 +/- 3,186.76 | 2,741.51 +/- 1,441.59 | 789.06 +/- 193.46 | 29.00 +/- 13.97 | 7 / 3 |
| Lat-Lon | BiDir | 27,695.50 +/- 4,008.11 | 2,632.13 +/- 1,675.92 | 1,438.36 +/- 141.14 | 18.00 +/- 11.13 | 5 / 5 |
| Lat-Lon | MU | 31,410.14 +/- 4,524.89 | 3,937.85 +/- 1,655.71 | 2,238.83 +/- 236.74 | 1.67 +/- 1.76 | 8 / 2 |
| Lat-Lon | FI | 21,838.02 +/- 2,401.26 | 2,945.35 +/- 880.82 | 1,077.15 +/- 182.39 | 23.33 +/- 7.20 | 9 / 1 |
| Lat-Lon | RNN | 24,049.75 +/- 3,284.72 | 2,757.87 +/- 1,455.44 | 782.79 +/- 181.19 | 27.33 +/- 12.94 | 7 / 3 |
| Lat-Lon | G TW | 27,421.36 +/- 2,811.48 | 4,167.34 +/- 451.80 | 1,028.97 +/- 239.84 | 33.67 +/- 5.54 | 10 / 0 |
| Lat-Lon | CFRS | 30,081.87 +/- 4,221.36 | 4,591.20 +/- 563.37 | 1,339.30 +/- 311.66 | 20.33 +/- 7.45 | 10 / 0 |
| Penalty-Risk | NN | 21,045.05 +/- 2,202.39 | 3,182.85 +/- 291.39 | 662.28 +/- 121.00 | 41.33 +/- 4.22 | 10 / 0 |
| Penalty-Risk | BiDir | 26,584.25 +/- 2,967.96 | 3,063.94 +/- 1,525.55 | 1,360.39 +/- 205.77 | 21.33 +/- 11.02 | 7 / 3 |
| Penalty-Risk | MU | 29,018.96 +/- 2,166.29 | 3,963.39 +/- 971.31 | 1,980.06 +/- 227.24 | 2.33 +/- 2.25 | 9 / 1 |
| Penalty-Risk | FI | 19,765.40 +/- 2,186.71 | 2,922.39 +/- 307.58 | 936.61 +/- 229.64 | 26.00 +/- 7.34 | 10 / 0 |
| Penalty-Risk | RNN | 21,407.29 +/- 2,085.25 | 3,240.77 +/- 273.24 | 640.09 +/- 115.08 | 41.00 +/- 4.17 | 10 / 0 |
| Penalty-Risk | G TW | 24,869.34 +/- 3,434.44 | 3,730.11 +/- 506.62 | 855.45 +/- 178.92 | 35.67 +/- 7.21 | 10 / 0 |
| Penalty-Risk | CFRS | 26,204.56 +/- 2,815.19 | 4,007.86 +/- 312.17 | 1,068.99 +/- 195.86 | 24.33 +/- 6.49 | 10 / 0 |
| DensityGeo | NN | 14,024.80 +/- 2,053.22 | 2,031.79 +/- 565.70 | 324.33 +/- 82.79 | 47.00 +/- 15.27 | 9 / 1 |
| DensityGeo | BiDir | 17,937.01 +/- 2,838.77 | 2,588.05 +/- 734.97 | 857.97 +/- 134.91 | 31.00 +/- 11.01 | 9 / 1 |
| DensityGeo | MU | 19,990.40 +/- 2,615.28 | 2,905.54 +/- 780.08 | 1,306.33 +/- 202.63 | 12.00 +/- 8.34 | 9 / 1 |
| DensityGeo | FI | 13,138.01 +/- 738.88 | 1,957.45 +/- 535.85 | 456.26 +/- 139.02 | 39.00 +/- 14.83 | 9 / 1 |
| DensityGeo | RNN | 14,004.36 +/- 2,020.80 | 2,031.22 +/- 564.22 | 314.96 +/- 91.82 | 47.67 +/- 17.00 | 9 / 1 |
| DensityGeo | G TW | 14,694.60 +/- 1,372.34 | 2,198.09 +/- 646.84 | 392.88 +/- 106.22 | 44.67 +/- 15.57 | 9 / 1 |
| DensityGeo | CFRS | 15,132.67 +/- 1,056.94 | 2,522.79 +/- 229.76 | 606.26 +/- 219.53 | 35.00 +/- 12.40 | 10 / 0 |

### Split and Heuristic Contribution

| Dimension | Value | Mean cost Rs. | SD | Best cost Rs. | Best-of-group win rate | Leave-one-out regret Rs. | Nonfinite candidates |
|---|---|---|---|---|---|---|---|
| split | Arrival | 24,145.83 | 4,230.10 | 17,108.23 | 0.0% | 0.00 | 5 |
| split | DensityGeo | 15,553.58 | 2,946.42 | 12,206.64 | 100.0% | 4,951.25 | 6 |
| split | Depot Distance | 27,251.60 | 4,702.19 | 20,024.10 | 0.0% | 0.00 | 14 |
| split | EDD | 23,332.58 | 4,280.82 | 13,558.16 | 0.0% | 0.00 | 9 |
| split | Lat-Lon | 26,738.23 | 4,724.46 | 17,184.20 | 0.0% | 0.00 | 14 |
| split | Latitude | 27,013.60 | 5,316.61 | 17,812.80 | 0.0% | 0.00 | 10 |
| split | Longitude | 26,363.46 | 4,328.16 | 18,633.32 | 0.0% | 0.00 | 8 |
| split | Penalty-Risk | 23,942.07 | 4,032.48 | 16,438.78 | 0.0% | 0.00 | 4 |
| heuristic | BiDir | 25,622.18 | 4,661.08 | 15,625.79 | 0.0% | 0.00 | 22 |
| heuristic | CFRS | 26,711.44 | 5,931.72 | 13,526.95 | 10.0% | 515.73 | 1 |
| heuristic | FI | 19,643.47 | 3,452.11 | 12,206.64 | 70.0% | 427.83 | 10 |
| heuristic | G TW | 25,143.99 | 5,085.37 | 12,834.20 | 0.0% | 0.00 | 5 |
| heuristic | MU | 28,883.09 | 5,098.69 | 16,452.51 | 0.0% | 0.00 | 6 |
| heuristic | NN | 21,345.04 | 3,942.09 | 12,375.11 | 0.0% | 0.00 | 12 |
| heuristic | RNN | 21,230.45 | 3,985.86 | 12,377.43 | 20.0% | 6.42 | 14 |

## Ablation

| Variant | Full cost mean +/- SD | Full distance mean +/- SD | Full penalty mean +/- SD | Full on-time mean +/- SD | Feasible / runs | Packing violations | Infrastructure violations |
|---|---|---|---|---|---|---|---|
| baseline | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 | 10/10 | 0 | 0 |
| no_3d_packing | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 | 10/10 | 0 | 0 |
| no_dbscan_split | 18,447.40 +/- 2,680.33 | 2,806.50 +/- 343.51 | 815.40 +/- 179.78 | 30.67 +/- 8.29 | 10/10 | 0 | 0 |
| no_infrastructure | 13,234.01 +/- 719.32 | 1,758.52 +/- 515.55 | 451.11 +/- 164.40 | 37.33 +/- 14.38 | 6/10 | 0 | 6 |
| no_penalty_risk_split | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 | 10/10 | 0 | 0 |
| no_stochastic_service | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 | 42.00 +/- 12.49 | 10/10 | 0 | 0 |
| no_traffic | 13,500.35 +/- 1,364.79 | 2,182.45 +/- 209.37 | 450.95 +/- 156.34 | 41.67 +/- 11.14 | 10/10 | 0 | 0 |

Each ablation disables one feature during candidate generation/scoring, selects its best plan, then rescoring is performed with all baseline features enabled. Nonfinite full-model results and violation counts remain in the CSV. An identical no-infrastructure outcome is evidence of no active prohibited edge in that selected plan only; inspect per-seed `infrastructure_violations` before making a broader claim.

## Small-Instance Optimality Gaps

| Method | Mean gap % +/- SD | Valid / runs | Infeasible / failed |
|---|---|---|---|
| Trajecta best-of-56 | 118.76 +/- 30.94 | 3/3 | 0 |
| ALNS | 177.00 +/- 26.70 | 3/3 | 0 |
| Genetic Algorithm | 177.00 +/- 26.70 | 3/3 | 0 |
| Tabu Search | 177.00 +/- 26.70 | 3/3 | 0 |
| OR-Tools seven-factor | 0.00 +/- 0.00 | 3/3 | 0 |
| OR-Tools simplified, rescored | 125.13 +/- 0.71 | 3/3 | 0 |

The reference optimum is exhaustive ordered-route enumeration plus subset DP for the full seven-factor scoring/feasibility model on seven orders, at most four routes, and distinct vehicle types. This is exact only for that finite implemented model and seed; it is not a Gurobi result.

## Varied Instances and Paired Tests

| Scenario | Method | Cost mean +/- SD | Valid / rows | Feasible / rows | Runtime mean +/- SD s |
|---|---|---|---|---|---|
| fleet_types_4 | OR-Tools seven-factor | NA +/- NA | 0/3 | 0/3 | 1.008 +/- 0.002 |
| fleet_types_4 | OR-Tools simplified | 14,667.91 +/- 1,080.37 | 3/3 | 0/3 | 1.004 +/- 0.002 |
| fleet_types_4 | Trajecta best-of-56 | NA +/- NA | 0/3 | 0/3 | 0.048 +/- 0.003 |
| fleet_types_7 | OR-Tools seven-factor | 5,075.79 +/- 218.97 | 2/3 | 2/3 | 1.013 +/- 0.001 |
| fleet_types_7 | OR-Tools simplified | 14,106.07 +/- 1,083.89 | 3/3 | 1/3 | 1.003 +/- 0.001 |
| fleet_types_7 | Trajecta best-of-56 | 13,242.92 +/- 1,052.55 | 3/3 | 3/3 | 0.149 +/- 0.006 |
| high_demand | OR-Tools seven-factor | 6,343.70 +/- 180.11 | 2/3 | 2/3 | 1.011 +/- 0.001 |
| high_demand | OR-Tools simplified | 14,221.44 +/- 995.87 | 3/3 | 1/3 | 1.003 +/- 0.001 |
| high_demand | Trajecta best-of-56 | 23,268.51 +/- 10,154.65 | 3/3 | 3/3 | 0.112 +/- 0.002 |
| high_traffic | OR-Tools seven-factor | 5,203.30 +/- 227.46 | 2/3 | 2/3 | 1.012 +/- 0.003 |
| high_traffic | OR-Tools simplified | 14,264.06 +/- 1,045.57 | 3/3 | 1/3 | 1.004 +/- 0.002 |
| high_traffic | Trajecta best-of-56 | 13,388.35 +/- 1,067.48 | 3/3 | 3/3 | 0.160 +/- 0.013 |
| low_traffic | OR-Tools seven-factor | 5,014.72 +/- 216.29 | 2/3 | 2/3 | 1.012 +/- 0.003 |
| low_traffic | OR-Tools simplified | 14,055.33 +/- 1,090.53 | 3/3 | 1/3 | 1.003 +/- 0.000 |
| low_traffic | Trajecta best-of-56 | 13,152.92 +/- 1,050.84 | 3/3 | 3/3 | 0.147 +/- 0.004 |
| orders_20 | OR-Tools seven-factor | 4,296.44 +/- 664.56 | 3/3 | 3/3 | 1.008 +/- 0.002 |
| orders_20 | OR-Tools simplified | 12,148.27 +/- 2,859.14 | 3/3 | 1/3 | 1.003 +/- 0.000 |
| orders_20 | Trajecta best-of-56 | 11,416.74 +/- 2,276.10 | 3/3 | 3/3 | 0.120 +/- 0.002 |
| orders_50 | OR-Tools seven-factor | 8,533.79 +/- 945.36 | 2/3 | 2/3 | 1.028 +/- 0.003 |
| orders_50 | OR-Tools simplified | 17,199.99 +/- 1,938.47 | 3/3 | 2/3 | 1.007 +/- 0.001 |
| orders_50 | Trajecta best-of-56 | 19,445.15 +/- 4,745.42 | 3/3 | 3/3 | 0.187 +/- 0.019 |

| Baseline | Matched feasible pairs / available | Mean paired cost difference Rs. | Wilcoxon p | Excluded pairs |
|---|---|---|---|---|
| OR-Tools seven-factor | 13/21 | 10,405.09 | 0.0002441 | 8 |
| OR-Tools simplified | 7/21 | 5,587.51 | 0.03125 | 14 |

Paired tests use only scenario-seed pairs where both methods have full-model-feasible plans; exclusions and denominator are shown and must accompany any p-value.

### Scalability

| Orders | Method | Cost mean +/- SD | Distance mean +/- SD | Runtime mean +/- SD s | Feasible / runs |
|---|---|---|---|---|---|
| 20 | ALNS | 14,396.47 +/- 1,400.27 | 2,355.02 +/- 198.82 | 0.061 +/- 0.009 | 2/2 |
| 20 | Genetic Algorithm | 15,158.45 +/- 1,700.48 | 2,500.97 +/- 200.31 | 0.388 +/- 0.004 | 2/2 |
| 20 | OR-Tools seven-factor | 4,330.20 +/- 0.00 | 685.10 +/- 406.77 | 1.010 +/- 0.000 | 1/2 |
| 20 | OR-Tools simplified | 11,565.73 +/- 289.63 | 906.15 +/- 28.02 | 1.011 +/- 0.011 | 1/2 |
| 20 | Tabu Search | 14,316.63 +/- 1,309.64 | 2,327.73 +/- 162.95 | 1.053 +/- 0.119 | 2/2 |
| 20 | Trajecta best-of-56 | 10,970.73 +/- 249.63 | 1,807.74 +/- 76.38 | 0.174 +/- 0.010 | 2/2 |
| 30 | ALNS | 21,904.97 +/- 4,324.45 | 3,363.70 +/- 905.02 | 0.062 +/- 0.009 | 2/2 |
| 30 | Genetic Algorithm | 23,438.65 +/- 3,256.30 | 3,604.19 +/- 584.89 | 0.335 +/- 0.009 | 2/2 |
| 30 | OR-Tools seven-factor | 4,895.62 +/- 0.00 | 946.13 +/- 246.06 | 1.017 +/- 0.003 | 1/2 |
| 30 | OR-Tools simplified | 14,048.28 +/- 1,637.25 | 1,118.06 +/- 134.56 | 1.003 +/- 0.000 | 0/2 |
| 30 | Tabu Search | 20,454.81 +/- 2,890.17 | 3,160.77 +/- 539.89 | 1.216 +/- 0.058 | 2/2 |
| 30 | Trajecta best-of-56 | 13,220.75 +/- 131.44 | 2,048.91 +/- 169.38 | 0.145 +/- 0.005 | 2/2 |
| 50 | ALNS | 25,562.19 +/- 0.00 | 1,887.54 +/- 2,669.39 | 0.231 +/- 0.030 | 1/2 |
| 50 | Genetic Algorithm | 47,878.93 +/- 8,085.53 | 6,716.89 +/- 531.47 | 0.467 +/- 0.046 | 2/2 |
| 50 | OR-Tools seven-factor | NA +/- NA | 931.44 +/- 0.00 | 1.029 +/- 0.003 | 0/2 |
| 50 | OR-Tools simplified | 16,758.68 +/- 480.46 | 1,291.51 +/- 80.57 | 1.008 +/- 0.004 | 1/2 |
| 50 | Tabu Search | 30,862.42 +/- 5,141.10 | 4,424.30 +/- 619.49 | 1.680 +/- 0.197 | 2/2 |
| 50 | Trajecta best-of-56 | 15,260.20 +/- 2,871.17 | 2,236.12 +/- 313.45 | 0.206 +/- 0.010 | 2/2 |
| 80 | ALNS | NA +/- NA | 0.00 +/- 0.00 | 0.731 +/- 0.052 | 0/2 |
| 80 | Genetic Algorithm | NA +/- NA | 3,076.61 +/- 459.20 | 0.552 +/- 0.045 | 0/2 |
| 80 | OR-Tools seven-factor | 17,185.40 +/- 1,211.26 | 1,712.49 +/- 73.90 | 1.068 +/- 0.002 | 2/2 |
| 80 | OR-Tools simplified | 22,410.08 +/- 383.65 | 1,621.82 +/- 7.52 | 1.009 +/- 0.002 | 0/2 |
| 80 | Tabu Search | NA +/- NA | 0.00 +/- 0.00 | 1.755 +/- 0.097 | 0/2 |
| 80 | Trajecta best-of-56 | NA +/- NA | 0.00 +/- 0.00 | 0.276 +/- 0.010 | 0/2 |

## Standard Benchmarks

| Family | Instance | Algorithm | Runs | Feasible | Mean vehicles | Mean distance | SD distance | Mean gap % | SD gap % |
|---|---|---|---|---|---|---|---|---|---|
| Cordeau-MDVRP | p01 | ALNS | 3 | 3 | 12.00 | 752.93 | 13.39 | 30.52 | 2.32 |
| Cordeau-MDVRP | p01 | Genetic Algorithm | 3 | 3 | 12.00 | 773.69 | 9.51 | 34.12 | 1.65 |
| Cordeau-MDVRP | p01 | Tabu Search | 3 | 3 | 12.00 | 760.63 | 16.18 | 31.85 | 2.80 |
| Cordeau-MDVRP | p02 | ALNS | 3 | 3 | 7.00 | 635.12 | 26.04 | 34.12 | 5.50 |
| Cordeau-MDVRP | p02 | Genetic Algorithm | 3 | 3 | 7.00 | 682.65 | 6.37 | 44.16 | 1.34 |
| Cordeau-MDVRP | p02 | Tabu Search | 3 | 3 | 7.00 | 649.48 | 12.08 | 37.16 | 2.55 |
| Solomon | c101 | ALNS | 3 | 3 | 10.00 | 828.94 | 0.00 | 0.00 | 0.00 |
| Solomon | c101 | Genetic Algorithm | 3 | 3 | 10.00 | 828.94 | 0.00 | 0.00 | 0.00 |
| Solomon | c101 | Tabu Search | 3 | 3 | 10.00 | 828.94 | 0.00 | 0.00 | 0.00 |
| Solomon | r101 | ALNS | 3 | 3 | 19.00 | 1,650.80 | 0.00 | 0.00 | 0.00 |
| Solomon | r101 | Genetic Algorithm | 3 | 3 | 19.00 | 1,650.80 | 0.00 | 0.00 | 0.00 |
| Solomon | r101 | Tabu Search | 3 | 3 | 19.00 | 1,650.80 | 0.00 | 0.00 | 0.00 |
| Solomon | rc101 | ALNS | 3 | 3 | 14.00 | 1,696.95 | 0.00 | 0.00 | 0.00 |
| Solomon | rc101 | Genetic Algorithm | 3 | 3 | 14.00 | 1,696.95 | 0.00 | 0.00 | 0.00 |
| Solomon | rc101 | Tabu Search | 3 | 3 | 14.00 | 1,696.95 | 0.00 | 0.00 | 0.00 |

Solomon results start from published reference routes (warm start); Cordeau results use nearest-depot assignment and do not represent independent full-Trajecta evaluation. Benchmark figures are distance-based and should not be conflated with the synthetic seven-factor experiment.

## Reproducibility Tables

### Fleet Types

| Type | Weight kg | Volume m3 | Speed km/h | Bay m | Height m | Fuel | Fuel Rs/km | EV kWh/km | Fixed Rs/route | Toll Rs/route | Range km |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2W-Petrol | 35 | 0.18 | 34 | 0.55 x 0.45 x 0.4 | 1.5 | petrol | 4.5 | 0 | 0 | 10.0 | not modeled |
| 2W-EV | 30 | 0.16 | 32 | 0.55 x 0.45 x 0.4 | 1.6 | electric | 0.0 | 0.1 | 0 | 10.0 | not modeled |
| 4W-Petrol | 350 | 2.5 | 42 | 2.0 x 1.35 x 0.95 | 2.0 | petrol | 4.5 | 0 | 70 | 30.0 | not modeled |
| 4W-Diesel | 700 | 5.5 | 40 | 2.5 x 1.55 x 1.35 | 2.3 | diesel | 7.0 | 0 | 100 | 30.0 | not modeled |
| 4W-EV | 400 | 3.0 | 38 | 2.1 x 1.4 x 1.05 | 2.1 | electric | 0.0 | 0.1 | 65 | 30.0 | not modeled |
| Truck-Diesel | 4000 | 25 | 35 | 6.0 x 2.2 x 2.0 | 3.6 | diesel | 7.0 | 0 | 180 | 60.0 | not modeled |
| Truck-EV | 2500 | 18 | 33 | 5.0 x 2.0 x 1.8 | 3.2 | electric | 0.0 | 0.1 | 160 | 60.0 | not modeled |

### Cost Components

| Component | Formula in implementation | Unit |
|---|---|---|
| fuel | distance * fuel rate * terrain factor | Rs |
| wages | distance * wage rate + fixed vehicle route cost | Rs |
| late penalty | late days * daily rate | Rs |
| packaging | fragile order count * packaging rate | Rs |
| cooling | cooling order count * cooling rate | Rs |
| maintenance | distance * maintenance rate | Rs |
| tolls | flat class-based charge per active route | Rs; synthetic assumption |
| EV charging | distance * kWh/km * tariff | Rs |

Rates (Rs/km or Rs/order as named): `{"charging_tariff_rs_per_kwh": 3.5, "cooling_rs_per_order": 10.0, "cost_rate_scale": 1.16, "electric_consumption_kwh_per_km": 0.1, "fuel_rs_per_km": {"diesel": 7.0, "electric": 0.0, "petrol": 4.5}, "late_rate_rs_per_day": 100.0, "maintenance_rs_per_km": 0.55, "packaging_rs_per_order": 25.0, "terrain_gradient_factor": 1.0, "toll_rs_by_vehicle_class": {"four_wheeler": 30.0, "truck": 60.0, "two_wheeler": 10.0}, "wage_rs_per_km": 2.0}`.

### Traffic, Service, Generator, Infrastructure, Packing

```json
{
  "traffic": {
    "bands": {
      "rush_morning": {
        "hours": "07:00-10:00",
        "multiplier": 1.3
      },
      "rush_evening": {
        "hours": "16:00-19:00",
        "multiplier": 1.25
      },
      "midday": {
        "hours": "10:00-16:00 and 19:00-21:00",
        "multiplier": 1.05
      },
      "night": {
        "hours": "21:00-06:00",
        "multiplier": 0.9
      }
    },
    "other_hours": "midday default, including 06:00-07:00",
    "weather_multiplier": 1.0,
    "lane_multiplier": 1.0,
    "origin": "synthetic assumptions; not calibrated against observed traffic"
  },
  "service_time": {
    "formula": "t_base + alpha*weight + beta*volume + gamma*(fragile+cooling) + delta*skill",
    "t_base_min": 8.0,
    "alpha_min_per_kg": 0.05,
    "beta_min_per_m3": 5.0,
    "gamma_min": 5.0,
    "delta": 1.0,
    "skill_distribution": {
      "mean_min": 0.0,
      "sd_min": 2.0
    },
    "skill_draw": "one deterministic normal draw per order and seed"
  },
  "synthetic_generator": {
    "weight_kg": {
      "distribution": "uniform",
      "range": [
        4,
        55
      ]
    },
    "volume_m3": {
      "distribution": "uniform",
      "range": [
        0.015,
        0.24
      ]
    },
    "city_assignment": "uniform discrete over non-depot configured cities",
    "coordinate_jitter_degrees": {
      "distribution": "uniform",
      "range": [
        -0.003,
        0.003
      ]
    },
    "arrival_hour": {
      "distribution": "uniform",
      "range": [
        6,
        10
      ]
    },
    "due_hour": "min(22, 8 + uniform(due_offset_hours)); offsets are uniform",
    "fragile_probability": 0.15,
    "cooling_probability": 0.2,
    "penalty_risk": {
      "distribution": "uniform",
      "range": [
        0,
        1
      ]
    },
    "distance_matrix": "Haversine, Earth radius 6371 km, multiplied by road_distance_factor",
    "route_group_count": 4,
    "route_groups_source": "synthetic assumption"
  },
  "infrastructure": {
    "source": "synthetic rule, not mapped road data",
    "two_wheeler_forbidden": "(a+b) % 13 == 0",
    "max_payload_kg_500": "(a*31+b*17) % 29 == 0",
    "max_height_m_2_4": "(a*11+b*7) % 31 == 0"
  },
  "packing": {
    "algorithm": "descending-volume first-fit into residual rectangular spaces; test all six box orientations",
    "limitations": "heuristic, not an optimal 3D packing solver"
  }
}
```

## Copy-Ready Statements

On-time delivery is the percentage of orders completed no later than the due time, after waiting until each order's arrival time; across 10 seeds the mean is 42.0% (SD 12.5 percentage points).
The simplified-cost comparator's mean penalty is Rs. 596.93 (SD Rs. 164.28) across 10 solved plans; only 5 pass the full-model checks. On the feasible subset, mean penalty is Rs. 547.92 (SD Rs. 119.76). The historical Rs. 680 baseline and 100% reduction are not supported by current runs.
At 30 orders, the 56-candidate constructive search averaged 0.145 s (SD 0.005); the time-limited OR-Tools seven-factor Guided Local Search averaged 1.017 s (SD 0.003), with a one-second solver limit. This compares a constructive heuristic with a time-limited solver, not an exact solver; traffic treatment and packing enforcement differ.

## Interpretation

The current evidence does not establish that Trajecta beats the fair-cost comparator. The reported numbers are reproducibility outputs from synthetic assumptions, and infeasibility must remain visible in the accompanying tables.
