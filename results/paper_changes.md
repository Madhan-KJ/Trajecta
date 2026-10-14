# Paper Changes for the Author

## Abstract

Replace the old cost, penalty, on-time, and runtime claims. The current best-of-56 mean cost is Rs. 13,496.15 +/- 1,366.96; on-time is 42.0 +/- 12.5%. The OR-Tools seven-factor comparator has a lower feasible-run mean cost and succeeds the full checks in 7/10 runs; do not claim Trajecta outperforms it.

## Introduction and Related Work

Add an explicit comparison table. The inherited/new distinction below follows the current paper's Profecta description and must be verified against the cited Profecta publication before submission.

| Component | Profecta status in current paper | Trajecta status / evidence |
|---|---|---|
| EDD, arrival, latitude, longitude, latitude-longitude, depot-distance splits | Inherited six split families (paper claim) | Current code implements these; current paper must call depot distance truthfully. |
| Penalty-risk and DBSCAN splits | New relative to Profecta (paper claim) | Implemented as synthetic heuristic splits; ablated in generated results. |
| Seven route heuristics | Inherited/extended status not established in repo | Current candidates are fully enumerated in candidate_route_summary.csv. |
| Heterogeneous vehicle types / 3D pack heuristic | Verify against Profecta source | Seven synthetic vehicle types; first-fit 3D check. |
| Traffic, infrastructure, stochastic service, seven-factor costs | Verify against Profecta source | Current code additions are synthetic assumptions; OR-Tools comparator has documented approximation. |

Contrast against heterogeneous-VRP and traffic-aware literature without claiming the combination is globally novel; novelty claims require a scoped literature review and component-level evidence.

## Methodology

State that each plan comprises four route groups, assigned distinct available vehicle types from a seven-type pool. Report full-plan totals. The current mean best-plan total is 2,182.45 km; report the route-group distribution from summary.md separately. The paper's 420-520 km range is not supported as a full-plan total and must not be mixed with full-plan distance.

Formal formulation matching the implementation:

Let I be orders, C cities including depot 0, V the available vehicle types, and K the four route-group slots. Each order i has city c_i, weight w_i, volume q_i, arrival a_i, due d_i, handling flags, and a box (l_i,w_i,h_i). Each type v has weight/volume limits, bay dimensions, speed, cost rates, and height.

Decision variables: x_ik = 1 if order i belongs to route group k; y_ijk = 1 if route k traverses arc i->j; z_kv = 1 if type v serves group k; T_ik is service completion time. The implemented heuristic constructs these variables by splitting and ordering rather than solving this formulation directly.

Constraints represented by code: each order appears exactly once; each of four route groups has one assigned vehicle type and selected types are distinct; total weight and volume per group do not exceed type capacities; the first-fit 3D packing check must pass; every traversed city pair must satisfy the generated synthetic infrastructure limits; service starts no earlier than arrival; completion times include time-dependent travel, service, and waiting; lateness incurs the configured daily penalty. Route groups begin/end at depot. Note: the OR-Tools search approximates traffic and validates 3D packing post-solve, so do not say those two are fully enforced inside its search model.

## Experimental Setup and Results

Replace Table 1 with generated objective selections:

| Objective | Seed-level split/heuristic | Total cost Rs. mean +/- SD | Full-plan distance km mean +/- SD | Penalty Rs. mean +/- SD |
|---|---|---|---|---|
| min_cost | 0:DensityGeo/FI; 1:DensityGeo/FI; 2:DensityGeo/RNN; 3:DensityGeo/FI; 4:DensityGeo/FI; 5:DensityGeo/CFRS; 6:DensityGeo/FI; 7:DensityGeo/RNN; 8:DensityGeo/FI; 9:DensityGeo/FI | 13,496.15 +/- 1,366.96 | 2,182.45 +/- 209.37 | 446.74 +/- 155.22 |
| min_distance | 0:DensityGeo/FI; 1:DensityGeo/FI; 2:DensityGeo/RNN; 3:DensityGeo/FI; 4:DensityGeo/FI; 5:DensityGeo/CFRS; 6:DensityGeo/FI; 7:DensityGeo/FI; 8:DensityGeo/FI; 9:DensityGeo/FI | 13,504.36 +/- 1,368.58 | 2,178.90 +/- 210.34 | 469.68 +/- 154.46 |
| min_penalty | 0:DensityGeo/RNN; 1:DensityGeo/RNN; 2:DensityGeo/RNN; 3:DensityGeo/RNN; 4:DensityGeo/FI; 5:DensityGeo/CFRS; 6:DensityGeo/NN; 7:DensityGeo/RNN; 8:DensityGeo/NN; 9:DensityGeo/RNN | 14,203.38 +/- 2,106.03 | 2,243.66 +/- 200.54 | 347.71 +/- 136.35 |

The prior minimum-penalty alternative row is not reliable as printed. Use objective_selection.csv and state that objectives are selected independently with the generated tie-break. Include all 56 candidate means/SDs from candidate_route_summary.csv in an appendix or supplemental table.

Describe the OR-Tools Guided Local Search settings and limit from run_info.json. It is not Gurobi and not exact. Explain that the simplified objective is distance*12 plus due-lateness penalty; compare on the shared full-model rescoring subset and report infeasible denominators. The fairer seven-factor search still uses a static traffic approximation and post-solve packing validation.

Add ablation, varied-instance, paired Wilcoxon, scalability, exact seven-order gap, and standard benchmark tables from results/summary.md. Benchmark scope must state Solomon published-reference warm starts and Cordeau nearest-depot assignment.

## Limitations and Conclusion

Demonstrated: synthetic offline route construction, heuristic 3D feasibility checks, generated infrastructure rules, static traffic-band estimates, and coded cost components. Future/unimplemented in this workspace: real traffic feeds, real infrastructure data, industry validation, geospatial dispatcher UI/authorization, and multi-depot live replanning.

## Retired Numbers

- Retire Rs. 4,200 and the claimed 31% cost gain; unsupported by current runs.
- Retire Rs. 0 penalty and 100% penalty reduction; the simplified comparator's current all-solved penalty mean is generated in results/summary.md and only its feasible subset supports full-model comparison.
- Retire the claimed 95% on-time delivery; use the generated seed mean and standard deviation.
- Retire the 1,250 ms versus 12,500 ms claim; use the measured scalability runtimes and state that a constructive heuristic is compared with a time-limited solver on different traffic/constraint implementations.
