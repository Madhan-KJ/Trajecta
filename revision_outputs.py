from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"


def read_json(name):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def read_csv(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def number(value, digits=2):
    if value is None:
        return "NA"
    value = float(value)
    if math.isnan(value):
        return "NA"
    if math.isinf(value):
        return "infeasible"
    if abs(value) < 0.5 * (10 ** -digits):
        value = 0.0
    return f"{value:,.{digits}f}"


def p_value(value):
    return "NA" if value in (None, "") else f"{float(value):.4g}"


def stats(values):
    numeric = [float(value) for value in values if value not in (None, "") and math.isfinite(float(value))]
    invalid = sum(value not in (None, "") and not math.isfinite(float(value)) for value in values)
    return (statistics.mean(numeric) if numeric else None,
            statistics.stdev(numeric) if len(numeric) > 1 else (0.0 if numeric else None),
            len(numeric), invalid)


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def write_summary_md():
    summary = read_json("summary.json")
    info = read_json("run_info.json")
    tables = read_json("reproducibility_tables.json")
    candidate = read_csv("candidate_route_summary.csv")
    route_details = read_csv("candidate_route_details.csv")
    selection = read_csv("objective_selection.csv")
    contributions = read_csv("contribution_summary.csv")
    ablations = read_csv("ablation_summary.csv")
    scale = read_csv("scalability_summary.csv")
    varied = read_csv("varied_instances.csv")
    gaps = read_csv("optimality_gaps.csv")
    benchmarks = read_csv("benchmark_algorithm_summary.csv") if (RESULTS / "benchmark_algorithm_summary.csv").exists() else []
    analysis = read_json("candidate_analysis.json")

    lines = ["# Trajecta Revision Results", "",
             "Generated from experiment artifacts by `revision_outputs.py`; do not edit reported values by hand.", "",
             "## Run Record", "",
             f"Command: `{info['run_command']}`; Python {info['python']}; {info['os']}; CPU `{info['cpu']}`; logical CPUs {info['logical_cpu_count']}; RAM bytes {info['ram_bytes']}.",
             f"Packages: {json.dumps(info['package_versions'], sort_keys=True)}. Git hash: `{info['git_hash']}`.",
             f"Main seeds: {', '.join(map(str, info['seeds']))}; main orders per seed: {info['orders']}; candidates per seed: {info['candidate_count_per_seed']}; OR-Tools time limit: {info['ortools_time_limit_seconds']} s.",
             "All generated data, infrastructure restrictions, traffic parameters, tolls, and route-group counts are synthetic assumptions; none are measured operational data.", "",
             "## Main Results", "",
             md_table(["Method / selection", "Cost Rs. mean +/- SD", "Distance km mean +/- SD", "Penalty Rs. mean +/- SD", "On-time % mean +/- SD", "Feasible / runs"], [
                 ["Trajecta best-of-56 full-plan", f"{number(summary['candidate_best_cost_rs']['mean'])} +/- {number(summary['candidate_best_cost_rs']['sd'])}",
                  f"{number(summary['candidate_distance_km']['mean'])} +/- {number(summary['candidate_distance_km']['sd'])}",
                  f"{number(summary['candidate_penalty_rs']['mean'])} +/- {number(summary['candidate_penalty_rs']['sd'])}",
                  f"{number(summary['candidate_ontime_pct']['mean'])} +/- {number(summary['candidate_ontime_pct']['sd'])}",
                  f"{summary['candidate_best_cost_rs']['n_valid']}/{summary['n_seeds']}"],
                 ["OR-Tools seven-factor search; full-model rescoring", f"{number(summary['ortools_seven_factor']['cost_rs']['mean'])} +/- {number(summary['ortools_seven_factor']['cost_rs']['sd'])}",
                  f"{number(summary['ortools_seven_factor']['feasible_only']['distance_km']['mean'])} +/- {number(summary['ortools_seven_factor']['feasible_only']['distance_km']['sd'])}",
                  f"{number(summary['ortools_seven_factor']['penalty_rs']['mean'])} +/- {number(summary['ortools_seven_factor']['penalty_rs']['sd'])}",
                  f"{number(summary['ortools_seven_factor']['feasible_only']['ontime_pct']['mean'])} +/- {number(summary['ortools_seven_factor']['feasible_only']['ontime_pct']['sd'])}",
                  f"{summary['ortools_seven_factor']['n_full_model_feasible']}/{summary['ortools_seven_factor']['n_solved']}"],
                 ["OR-Tools simplified objective; full-model feasible subset", f"{number(summary['ortools_simplified_distance_penalty']['full_model_cost_rs']['mean'])} +/- {number(summary['ortools_simplified_distance_penalty']['full_model_cost_rs']['sd'])}",
                  f"{number(summary['ortools_simplified_distance_penalty']['feasible_only']['distance_km']['mean'])} +/- {number(summary['ortools_simplified_distance_penalty']['feasible_only']['distance_km']['sd'])}",
                  f"{number(summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']['mean'])} +/- {number(summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']['sd'])}",
                  f"{number(summary['ortools_simplified_distance_penalty']['feasible_only']['ontime_pct']['mean'])} +/- {number(summary['ortools_simplified_distance_penalty']['feasible_only']['ontime_pct']['sd'])}",
                  f"{summary['ortools_simplified_distance_penalty']['n_full_model_feasible']}/{summary['ortools_simplified_distance_penalty']['n_solved']}"]])]
    lines += ["", "On-time percentage is the share of orders completed at or before due time after waiting until arrival/release time; the table reports mean and sample SD over seed-level plans. Candidate cost, distance, and penalty are totals across the complete four-group plan. OR-Tools seven-factor traffic is approximated with a static factor and 3D packing is checked after solve; its infeasible outputs remain counted above.", "",
              "## Corrected Objective Table", ""]
    by_objective = defaultdict(list)
    for row in selection:
        by_objective[row["objective"]].append(row)
    lines.append(md_table(["Objective", "Selected split / heuristic by seed", "Cost Rs. mean +/- SD", "Distance km mean +/- SD", "Penalty Rs. mean +/- SD", "On-time % mean +/- SD"], [
        [objective,
         "; ".join(f"{row['seed']}:{row['split']}/{row['heuristic']}" for row in rows),
         f"{number(stats([row['cost_rs'] for row in rows])[0])} +/- {number(stats([row['cost_rs'] for row in rows])[1])}",
         f"{number(stats([row['distance_km'] for row in rows])[0])} +/- {number(stats([row['distance_km'] for row in rows])[1])}",
         f"{number(stats([row['penalty_rs'] for row in rows])[0])} +/- {number(stats([row['penalty_rs'] for row in rows])[1])}",
         f"{number(stats([row['ontime_pct'] for row in rows])[0])} +/- {number(stats([row['ontime_pct'] for row in rows])[1])}"]
        for objective, rows in by_objective.items()]))
    feasible_route_details = [row for row in route_details if math.isfinite(float(row["cost_rs"]))]
    route_distance_stats = stats([row["distance_km"] for row in feasible_route_details])
    route_distances = [float(row["distance_km"]) for row in feasible_route_details]
    lines += ["", f"All three objectives selected the same candidate in {analysis['all_three_objectives_coincide_seeds']} of {analysis['n_seeds']} seeds. Pairwise coincidences: {json.dumps(analysis['pairwise_objective_coincidences'], sort_keys=True)}. Pareto-optimal candidates per seed: mean {number(analysis['pareto_candidates_per_seed_mean'])}, SD {number(analysis['pareto_candidates_per_seed_sd'])}; finite candidates only. Tie-breaking: {analysis['tie_break']}.",
              f"Unit clarification: candidate distances are totals over four route groups. Individual route-group distances from candidate_route_details.csv have mean {number(route_distance_stats[0])} km (SD {number(route_distance_stats[1])}; min {number(min(route_distances))}, max {number(max(route_distances))}). The paper's 420-520 km range is not supported as a full-plan distance; any route-level comparison must state its aggregation and seed set.", "",
              "### All 56 Candidates", "",
              md_table(["Split", "Heuristic", "Cost mean +/- SD", "Distance mean +/- SD", "Penalty mean +/- SD", "On-time mean +/- SD", "Valid seeds / nonfinite"], [
                  [row["split"], row["heuristic"],
                   f"{number(row['cost_rs_mean'])} +/- {number(row['cost_rs_sd'])}",
                   f"{number(row['distance_km_mean'])} +/- {number(row['distance_km_sd'])}",
                   f"{number(row['penalty_rs_mean'])} +/- {number(row['penalty_rs_sd'])}",
                   f"{number(row['ontime_pct_mean'])} +/- {number(row['ontime_pct_sd'])}",
                   f"{row['cost_rs_valid_seeds']} / {row['cost_rs_nonfinite_seeds']}"] for row in candidate]), "",
              "### Split and Heuristic Contribution", "",
              md_table(["Dimension", "Value", "Mean cost Rs.", "SD", "Best cost Rs.", "Best-of-group win rate", "Leave-one-out regret Rs.", "Nonfinite candidates"], [
                  [row["dimension"], row["value"], number(row["mean_cost_rs"]), number(row["sd_cost_rs"]),
                   number(row["best_cost_rs"]), number(float(row["best_of_group_win_rate"]) * 100, 1) + "%",
                   number(row["mean_leave_one_out_regret_rs"]), row["nonfinite_rows"]] for row in contributions]), "",
              "## Ablation", "",
              md_table(["Variant", "Full cost mean +/- SD", "Full distance mean +/- SD", "Full penalty mean +/- SD", "Full on-time mean +/- SD", "Feasible / runs", "Packing violations", "Infrastructure violations"], [
                  [variant, f"{number(stats([r['full_cost_rs'] for r in rows])[0])} +/- {number(stats([r['full_cost_rs'] for r in rows])[1])}",
                   f"{number(stats([r['full_distance_km'] for r in rows])[0])} +/- {number(stats([r['full_distance_km'] for r in rows])[1])}",
                   f"{number(stats([r['full_penalty_rs'] for r in rows])[0])} +/- {number(stats([r['full_penalty_rs'] for r in rows])[1])}",
                   f"{number(stats([r['full_ontime_pct'] for r in rows])[0])} +/- {number(stats([r['full_ontime_pct'] for r in rows])[1])}",
                   f"{sum(r['full_model_feasible'].lower() == 'true' for r in rows)}/{len(rows)}",
                   sum(int(r['pack3d_violations']) for r in rows), sum(int(r['infrastructure_violations']) for r in rows)]
                  for variant in sorted({r['variant'] for r in ablations})
                  for rows in [[row for row in ablations if row['variant'] == variant]]]), "",
              "Each ablation disables one feature during candidate generation/scoring, selects its best plan, then rescoring is performed with all baseline features enabled. Nonfinite full-model results and violation counts remain in the CSV. An identical no-infrastructure outcome is evidence of no active prohibited edge in that selected plan only; inspect per-seed `infrastructure_violations` before making a broader claim.", "",
              "## Small-Instance Optimality Gaps", ""]
    by_method = defaultdict(list)
    for row in gaps:
        by_method[row["method"]].append(row)
    lines.append(md_table(["Method", "Mean gap % +/- SD", "Valid / runs", "Infeasible / failed"], [
        [method, f"{number(stats([r['gap_pct'] for r in rows])[0])} +/- {number(stats([r['gap_pct'] for r in rows])[1])}",
         f"{sum(r['gap_valid'].lower() == 'true' for r in rows)}/{len(rows)}",
         sum(r['feasible'].lower() != 'true' for r in rows)] for method, rows in by_method.items()]))
    lines += ["", "The reference optimum is exhaustive ordered-route enumeration plus subset DP for the full seven-factor scoring/feasibility model on seven orders, at most four routes, and distinct vehicle types. This is exact only for that finite implemented model and seed; it is not a Gurobi result.", "",
              "## Varied Instances and Paired Tests", ""]
    varied_groups = defaultdict(list)
    for row in varied:
        varied_groups[(row['scenario'], row['algorithm'])].append(row)
    lines.append(md_table(["Scenario", "Method", "Cost mean +/- SD", "Valid / rows", "Feasible / rows", "Runtime mean +/- SD s"], [
        [scenario, method,
         f"{number(stats([r['cost_rs'] for r in rows])[0])} +/- {number(stats([r['cost_rs'] for r in rows])[1])}",
         f"{stats([r['cost_rs'] for r in rows])[2]}/{len(rows)}",
         f"{sum(r['full_model_feasible'].lower() == 'true' for r in rows)}/{len(rows)}",
         f"{number(stats([r['runtime_s'] for r in rows])[0], 3)} +/- {number(stats([r['runtime_s'] for r in rows])[1], 3)}"]
        for (scenario, method), rows in sorted(varied_groups.items())]))
    lines.append("")
    paired = read_csv("paired_comparisons.csv")
    lines.append(md_table(["Baseline", "Matched feasible pairs / available", "Mean paired cost difference Rs.", "Wilcoxon p", "Excluded pairs"], [
        [row['baseline'], f"{row['matched_scenario_seed_pairs']}/{row['available_scenario_seed_pairs']}",
         number(row['mean_paired_cost_difference_rs']), p_value(row['wilcoxon_p_value']),
         row['excluded_due_to_infeasibility_or_failure']] for row in paired]))
    lines += ["", "Paired tests use only scenario-seed pairs where both methods have full-model-feasible plans; exclusions and denominator are shown and must accompany any p-value.", "",
              "### Scalability", ""]
    scale_groups = defaultdict(list)
    for row in scale:
        scale_groups[(int(row['n_orders']), row['algorithm'])].append(row)
    lines.append(md_table(["Orders", "Method", "Cost mean +/- SD", "Distance mean +/- SD", "Runtime mean +/- SD s", "Feasible / runs"], [
        [size, method,
         f"{number(stats([r['cost_rs'] for r in rows])[0])} +/- {number(stats([r['cost_rs'] for r in rows])[1])}",
         f"{number(stats([r['distance_km'] for r in rows])[0])} +/- {number(stats([r['distance_km'] for r in rows])[1])}",
         f"{number(stats([r['runtime_s'] for r in rows])[0], 3)} +/- {number(stats([r['runtime_s'] for r in rows])[1], 3)}",
         f"{sum(r['full_model_feasible'].lower() == 'true' for r in rows)}/{len(rows)}"]
        for (size, method), rows in sorted(scale_groups.items())]))
    lines += ["", "## Standard Benchmarks", ""]
    if benchmarks:
        lines.append(md_table(["Family", "Instance", "Algorithm", "Runs", "Feasible", "Mean vehicles", "Mean distance", "SD distance", "Mean gap %", "SD gap %"], [
            [row['family'], row['instance'], row['algorithm'], row['n_runs'], row['feasible_runs'],
             number(row['mean_vehicles']), number(row['mean_distance']), number(row['sd_distance']),
             number(row['mean_gap_pct']), number(row['sd_gap_pct'])] for row in benchmarks]))
    lines += ["", "Solomon results start from published reference routes (warm start); Cordeau results use nearest-depot assignment and do not represent independent full-Trajecta evaluation. Benchmark figures are distance-based and should not be conflated with the synthetic seven-factor experiment.", "",
              "## Reproducibility Tables", "",
              "### Fleet Types", "",
              md_table(["Type", "Weight kg", "Volume m3", "Speed km/h", "Bay m", "Height m", "Fuel", "Fuel Rs/km", "EV kWh/km", "Fixed Rs/route", "Toll Rs/route", "Range km"], [
                  [v['type'], v['weight_capacity_kg'], v['volume_capacity_m3'], v['speed_km_per_h'],
                   " x ".join(map(str, v['bay_dimensions_m'])), v['height_m'], v['fuel_type'], v['fuel_rs_per_km'],
                   v['ev_kwh_per_km'], v['fixed_route_cost_rs'], v['toll_rs_per_route'], "not modeled"]
                  for v in tables['fleet_types']]), "",
              "### Cost Components", "",
              md_table(["Component", "Formula in implementation", "Unit"], [[c['component'], c['formula'], c['unit']] for c in tables['cost_components']]), "",
              "Rates (Rs/km or Rs/order as named): `" + json.dumps(tables['cost_rates'], sort_keys=True) + "`.", "",
              "### Traffic, Service, Generator, Infrastructure, Packing", "",
              "```json\n" + json.dumps({key: tables[key] for key in ('traffic', 'service_time', 'synthetic_generator', 'infrastructure', 'packing')}, indent=2) + "\n```", "",
              "## Copy-Ready Statements", "",
              f"On-time delivery is the percentage of orders completed no later than the due time, after waiting until each order's arrival time; across {summary['n_seeds']} seeds the mean is {number(summary['candidate_ontime_pct']['mean'],1)}% (SD {number(summary['candidate_ontime_pct']['sd'],1)} percentage points).",
              f"The simplified-cost comparator's mean penalty is Rs. {number(summary['ortools_simplified_distance_penalty']['penalty_rs']['mean'])} (SD Rs. {number(summary['ortools_simplified_distance_penalty']['penalty_rs']['sd'])}) across {summary['ortools_simplified_distance_penalty']['n_solved']} solved plans; only {summary['ortools_simplified_distance_penalty']['n_full_model_feasible']} pass the full-model checks. On the feasible subset, mean penalty is Rs. {number(summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']['mean'])} (SD Rs. {number(summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']['sd'])}). The historical Rs. 680 baseline and 100% reduction are not supported by current runs.",
              f"At 30 orders, the 56-candidate constructive search averaged {number(stats([r['runtime_s'] for r in scale if int(r['n_orders']) == 30 and r['algorithm'] == 'Trajecta best-of-56'])[0],3)} s (SD {number(stats([r['runtime_s'] for r in scale if int(r['n_orders']) == 30 and r['algorithm'] == 'Trajecta best-of-56'])[1],3)}); the time-limited OR-Tools seven-factor Guided Local Search averaged {number(stats([r['runtime_s'] for r in scale if int(r['n_orders']) == 30 and r['algorithm'] == 'OR-Tools seven-factor'])[0],3)} s (SD {number(stats([r['runtime_s'] for r in scale if int(r['n_orders']) == 30 and r['algorithm'] == 'OR-Tools seven-factor'])[1],3)}), with a one-second solver limit. This compares a constructive heuristic with a time-limited solver, not an exact solver; traffic treatment and packing enforcement differ.", "",
              "## Interpretation", "",
              "The current evidence does not establish that Trajecta beats the fair-cost comparator. The reported numbers are reproducibility outputs from synthetic assumptions, and infeasibility must remain visible in the accompanying tables.", ""]
    (RESULTS / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_claims_ledger():
    summary = read_json("summary.json")
    analysis = read_json("candidate_analysis.json")
    selected = read_csv("objective_selection.csv")
    min_penalty_rows = [row for row in selected if row["objective"] == "min_penalty"]
    feasible = summary['ortools_seven_factor']['n_full_model_feasible']
    runs = summary['ortools_seven_factor']['n_solved']
    candidate_cost = summary['candidate_best_cost_rs']['mean']
    candidate_sd = summary['candidate_best_cost_rs']['sd']
    candidate_ontime = summary['candidate_ontime_pct']['mean']
    candidate_ontime_sd = summary['candidate_ontime_pct']['sd']
    rows = [
        ("Old Rs. 4,200 minimum cost / 31% gain", "summary.json: candidate_best_cost_rs; ortools_seven_factor", "unsupported", f"Retired. Current best-of-56 mean cost is Rs. {number(candidate_cost)} +/- {number(candidate_sd)}; fair comparator mean on {feasible}/{runs} feasible runs is Rs. {number(summary['ortools_seven_factor']['cost_rs']['mean'])} +/- {number(summary['ortools_seven_factor']['cost_rs']['sd'])}. No Trajecta advantage is demonstrated."),
        ("Old 100% penalty reduction / Rs. 680 comparator penalty", "summary.json: ortools_simplified_distance_penalty and ortools_seven_factor", "unsupported", f"Retired. Report current objective-specific penalty mean and feasibility denominator; simplified baseline full-model feasible subset penalty is Rs. {number(summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']['mean'])} +/- {number(summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']['sd'])} over {summary['ortools_simplified_distance_penalty']['n_full_model_feasible']}/{summary['ortools_simplified_distance_penalty']['n_solved']} runs."),
        ("Old Table 1 minimum-penalty alternative (EDD/MU/2W-EV)", "objective_selection.csv: min_penalty rows", "unsupported", f"Replace with generated selections; current min-penalty full-plan cost mean is Rs. {number(stats([r['cost_rs'] for r in min_penalty_rows])[0])} +/- {number(stats([r['cost_rs'] for r in min_penalty_rows])[1])}, penalty mean Rs. {number(stats([r['penalty_rs'] for r in min_penalty_rows])[0])} +/- {number(stats([r['penalty_rs'] for r in min_penalty_rows])[1])}. Do not reuse the old single-row alternative."),
        ("Old Route 7 EDD/CFRS/4W-EV minimum-cost claim", "objective_selection.csv; candidate_route_details.csv", "unsupported", "Use the current objective-selection rows; plans assign four groups and do not map to that single-route label."),
        ("Old 95% on-time delivery", "summary.json: candidate_ontime_pct", "unsupported", f"Retired. On-time is percent of orders completed by due time after release-time waiting; current mean is {number(candidate_ontime,1)} +/- {number(candidate_ontime_sd,1)} percentage points over {summary['n_seeds']} seeds."),
        ("Old Gurobi exact comparator", "recreate.py: ortools_baseline; run_info.json", "unsupported", "Call it OR-Tools Guided Local Search with the recorded time limit, first-solution strategy, and local-search setting; never call it Gurobi or exact."),
        ("Old 1,250 ms vs 12,500 ms runtime comparison", "run_info.json; scalability_summary.csv", "unsupported", "Retire the old timing. Report per-algorithm runtime from the regenerated experiment and state the different objectives/constraints."),
        ("Eight splits x seven heuristics yield 56 candidates per seed", "candidate_routes.csv; candidate_route_summary.csv", "supported", "Supported for the current generator; call each candidate a complete four-group plan."),
        ("Plan distances of 420-520 km", "summary.json: candidate_distance_km", "unsupported", f"Retired. Current best-of-56 plan distance mean is {number(summary['candidate_distance_km']['mean'])} +/- {number(summary['candidate_distance_km']['sd'])} km across four route groups."),
        ("Old 467 km mean / CFRS 438 km distance claim", "candidate_route_details.csv; candidate_route_summary.csv", "unsupported", "The current paper-facing metric is full-plan distance; route-group distances have a different distribution. Recompute only with a stated route-level aggregation."),
        ("Seven-factor OR-Tools comparator beats Trajecta on cost", "summary.json: ortools_seven_factor and candidate_best_cost_rs", "supported", f"Current result: OR-Tools mean Rs. {number(summary['ortools_seven_factor']['cost_rs']['mean'])} +/- {number(summary['ortools_seven_factor']['cost_rs']['sd'])} on {feasible}/{runs} feasible runs; Trajecta best-of-56 mean Rs. {number(candidate_cost)} +/- {number(candidate_sd)}. State post-solve packing check and traffic approximation."),
        ("Seven fleet vehicle specifications", "reproducibility_tables.json: fleet_types", "partly", "Seven vehicle types are specified; they are not inventory counts. Range is not modeled, four route groups are an explicit synthetic assumption."),
        ("3D capacity validation", "recreate.py: pack3d; ablation_summary.csv", "partly", "A descending-volume first-fit residual-space heuristic with box rotations is implemented; not an exact 3D packing solver."),
        ("Infrastructure feasibility checking", "recreate.py: infrastructure_rule; synthetic_infrastructure_constraints.csv", "partly", "Implemented using generated synthetic index-modulo restrictions only; no real road/infrastructure source."),
        ("Seven-factor cost model", "recreate.py: seven_cost; reproducibility_tables.json: cost_components", "partly", "Components are coded, but tolls and rates are synthetic assumptions; toll is flat class-based per active route."),
        ("Traffic-aware travel time", "recreate.py: travel_hours; reproducibility_tables.json: traffic", "partly", "Four static synthetic time bands are implemented; weather/lane factors are assumptions, and OR-Tools uses a static 1.15 approximation."),
        ("All three objective minima are distinct / Pareto selection", "objective_selection.csv; candidate_analysis.json", "supported", f"Report the generated objective selections; all-three coincidence occurred in {analysis['all_three_objectives_coincide_seeds']}/{analysis['n_seeds']} seeds. Pareto counts are emitted in candidate_analysis.json."),
        ("95% was average across ten stochastic seeds", "summary.json: candidate_ontime_pct", "unsupported", "Do not claim this. Cite the current on-time mean/SD and the exact seed-level selection definition."),
        ("Geospatial visualization and dispatcher authorization are implemented", "workspace source inventory", "unsupported", "Describe as future work unless a separate implementation is supplied and independently evaluated."),
        ("Solomon/Cordeau are independent full-Trajecta evaluations", "run_benchmarks.py; benchmark_algorithm_runs.csv", "unsupported", "State Solomon reference-route warm starts and Cordeau nearest-depot assignment; results are distance-based benchmark experiments."),
        ("No real transaction, traffic, or infrastructure data was used", "recreate.py; reproducibility_tables.json", "supported", "All synthetic input ranges and assumptions must be named; do not describe them as calibrated operational data."),
        ("Old O(SH(N^2 + E + N)) complexity claim", "recreate.py: assign_vehicles; contribution_summary.csv", "unsupported", "Do not claim the old bound without accounting for the explicit distinct-fleet permutation assignment and route feasibility checks."),
    ]
    content = ["# Claims Ledger", "", "Generated from current experiment outputs by `revision_outputs.py`. `Supported` means directly evidenced by this workspace; `partly` requires the allowed qualification; `unsupported` claims must not appear as results.", "",
               md_table(["Claim", "Evidence", "Verdict", "Allowed wording"], rows), ""]
    (RESULTS / "claims_ledger.md").write_text("\n".join(content), encoding="utf-8")


def write_paper_changes():
    summary = read_json("summary.json")
    selection = read_csv("objective_selection.csv")
    grouped = defaultdict(list)
    for row in selection:
        grouped[row['objective']].append(row)
    table_rows = []
    for objective, rows in grouped.items():
        table_rows.append([objective,
                           "; ".join(f"{r['seed']}:{r['split']}/{r['heuristic']}" for r in rows),
                           f"{number(stats([r['cost_rs'] for r in rows])[0])} +/- {number(stats([r['cost_rs'] for r in rows])[1])}",
                           f"{number(stats([r['distance_km'] for r in rows])[0])} +/- {number(stats([r['distance_km'] for r in rows])[1])}",
                           f"{number(stats([r['penalty_rs'] for r in rows])[0])} +/- {number(stats([r['penalty_rs'] for r in rows])[1])}"])
    old_rows = "\n".join([
        "- Retire Rs. 4,200 and the claimed 31% cost gain; unsupported by current runs.",
        "- Retire Rs. 0 penalty and 100% penalty reduction; the simplified comparator's current all-solved penalty mean is generated in results/summary.md and only its feasible subset supports full-model comparison.",
        "- Retire the claimed 95% on-time delivery; use the generated seed mean and standard deviation.",
        "- Retire the 1,250 ms versus 12,500 ms claim; use the measured scalability runtimes and state that a constructive heuristic is compared with a time-limited solver on different traffic/constraint implementations.",
    ])
    content = ["# Paper Changes for the Author", "", "## Abstract", "",
               f"Replace the old cost, penalty, on-time, and runtime claims. The current best-of-56 mean cost is Rs. {number(summary['candidate_best_cost_rs']['mean'])} +/- {number(summary['candidate_best_cost_rs']['sd'])}; on-time is {number(summary['candidate_ontime_pct']['mean'],1)} +/- {number(summary['candidate_ontime_pct']['sd'],1)}%. The OR-Tools seven-factor comparator has a lower feasible-run mean cost and succeeds the full checks in {summary['ortools_seven_factor']['n_full_model_feasible']}/{summary['ortools_seven_factor']['n_solved']} runs; do not claim Trajecta outperforms it.", "",
               "## Introduction and Related Work", "",
               "Add an explicit comparison table. The inherited/new distinction below follows the current paper's Profecta description and must be verified against the cited Profecta publication before submission.", "",
               md_table(["Component", "Profecta status in current paper", "Trajecta status / evidence"], [
                   ["EDD, arrival, latitude, longitude, latitude-longitude, depot-distance splits", "Inherited six split families (paper claim)", "Current code implements these; current paper must call depot distance truthfully."],
                   ["Penalty-risk and DBSCAN splits", "New relative to Profecta (paper claim)", "Implemented as synthetic heuristic splits; ablated in generated results."],
                   ["Seven route heuristics", "Inherited/extended status not established in repo", "Current candidates are fully enumerated in candidate_route_summary.csv."],
                   ["Heterogeneous vehicle types / 3D pack heuristic", "Verify against Profecta source", "Seven synthetic vehicle types; first-fit 3D check."],
                   ["Traffic, infrastructure, stochastic service, seven-factor costs", "Verify against Profecta source", "Current code additions are synthetic assumptions; OR-Tools comparator has documented approximation."],
               ]), "",
               "Contrast against heterogeneous-VRP and traffic-aware literature without claiming the combination is globally novel; novelty claims require a scoped literature review and component-level evidence.", "",
               "## Methodology", "",
               f"State that each plan comprises four route groups, assigned distinct available vehicle types from a seven-type pool. Report full-plan totals. The current mean best-plan total is {number(summary['candidate_distance_km']['mean'])} km; report the route-group distribution from summary.md separately. The paper's 420-520 km range is not supported as a full-plan total and must not be mixed with full-plan distance.", "",
               "Formal formulation matching the implementation:", "",
               "Let I be orders, C cities including depot 0, V the available vehicle types, and K the four route-group slots. Each order i has city c_i, weight w_i, volume q_i, arrival a_i, due d_i, handling flags, and a box (l_i,w_i,h_i). Each type v has weight/volume limits, bay dimensions, speed, cost rates, and height.", "",
               "Decision variables: x_ik = 1 if order i belongs to route group k; y_ijk = 1 if route k traverses arc i->j; z_kv = 1 if type v serves group k; T_ik is service completion time. The implemented heuristic constructs these variables by splitting and ordering rather than solving this formulation directly.", "",
               "Constraints represented by code: each order appears exactly once; each of four route groups has one assigned vehicle type and selected types are distinct; total weight and volume per group do not exceed type capacities; the first-fit 3D packing check must pass; every traversed city pair must satisfy the generated synthetic infrastructure limits; service starts no earlier than arrival; completion times include time-dependent travel, service, and waiting; lateness incurs the configured daily penalty. Route groups begin/end at depot. Note: the OR-Tools search approximates traffic and validates 3D packing post-solve, so do not say those two are fully enforced inside its search model.", "",
               "## Experimental Setup and Results", "",
               "Replace Table 1 with generated objective selections:", "",
               md_table(["Objective", "Seed-level split/heuristic", "Total cost Rs. mean +/- SD", "Full-plan distance km mean +/- SD", "Penalty Rs. mean +/- SD"], table_rows), "",
               "The prior minimum-penalty alternative row is not reliable as printed. Use objective_selection.csv and state that objectives are selected independently with the generated tie-break. Include all 56 candidate means/SDs from candidate_route_summary.csv in an appendix or supplemental table.", "",
               "Describe the OR-Tools Guided Local Search settings and limit from run_info.json. It is not Gurobi and not exact. Explain that the simplified objective is distance*12 plus due-lateness penalty; compare on the shared full-model rescoring subset and report infeasible denominators. The fairer seven-factor search still uses a static traffic approximation and post-solve packing validation.", "",
               "Add ablation, varied-instance, paired Wilcoxon, scalability, exact seven-order gap, and standard benchmark tables from results/summary.md. Benchmark scope must state Solomon published-reference warm starts and Cordeau nearest-depot assignment.", "",
               "## Limitations and Conclusion", "",
               "Demonstrated: synthetic offline route construction, heuristic 3D feasibility checks, generated infrastructure rules, static traffic-band estimates, and coded cost components. Future/unimplemented in this workspace: real traffic feeds, real infrastructure data, industry validation, geospatial dispatcher UI/authorization, and multi-depot live replanning.", "",
               "## Retired Numbers", "", old_rows, ""]
    (RESULTS / "paper_changes.md").write_text("\n".join(content), encoding="utf-8")


def write_figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    summary = read_json("summary.json")
    candidate = read_csv("candidate_route_summary.csv")
    ablations = read_csv("ablation_summary.csv")
    scale = read_csv("scalability_summary.csv")
    gaps = read_csv("optimality_gaps.csv")
    contributions = read_csv("contribution_summary.csv")
    FIGURES.mkdir(parents=True, exist_ok=True)

    methods = ["Trajecta best-of-56", "OR-Tools seven-factor", "OR-Tools simplified feasible subset"]
    cost_stats = [summary['candidate_best_cost_rs'], summary['ortools_seven_factor']['cost_rs'],
                  summary['ortools_simplified_distance_penalty']['full_model_cost_rs']]
    distance_stats = [summary['candidate_distance_km'], summary['ortools_seven_factor']['feasible_only']['distance_km'],
                      summary['ortools_simplified_distance_penalty']['feasible_only']['distance_km']]
    penalty_stats = [summary['candidate_penalty_rs'], summary['ortools_seven_factor']['penalty_rs'],
                     summary['ortools_simplified_distance_penalty']['feasible_only']['penalty_rs']]
    ontime_stats = [summary['candidate_ontime_pct'], summary['ortools_seven_factor']['feasible_only']['ontime_pct'],
                    summary['ortools_simplified_distance_penalty']['feasible_only']['ontime_pct']]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for axis, title, records in zip(axes.flat, ("Full-plan cost (Rs.)", "Full-plan distance (km)", "Penalty (Rs.)", "On-time orders (%)"),
                                   (cost_stats, distance_stats, penalty_stats, ontime_stats)):
        means = [item['mean'] for item in records]
        sds = [item['sd'] for item in records]
        axis.bar(methods, means, yerr=sds, capsize=3, color=["#167D8D", "#D06B46", "#70844A"])
        axis.set_title(title)
        axis.tick_params(axis="x", rotation=18)
        axis.grid(axis="y", alpha=.25)
    fig.suptitle("Synthetic case study: feasible results and seed variation")
    fig.tight_layout()
    fig.savefig(FIGURES / "main_comparison.png", dpi=180)
    plt.close(fig)

    variants = sorted({row['variant'] for row in ablations})
    means, errors, infeasible = [], [], []
    for variant in variants:
        rows = [row for row in ablations if row['variant'] == variant]
        mean, sd, _, _ = stats([row['full_cost_rs'] for row in rows])
        means.append(mean if mean is not None else np.nan)
        errors.append(sd if sd is not None else 0)
        infeasible.append(sum(row['full_model_feasible'].lower() != 'true' for row in rows))
    fig, axis = plt.subplots(figsize=(10, 5))
    bars = axis.bar(variants, means, yerr=errors, capsize=3, color="#167D8D")
    for bar, failed in zip(bars, infeasible):
        axis.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"infeasible={failed}", ha="center", va="bottom", fontsize=8)
    axis.set_ylabel("Full-model cost (Rs.)")
    axis.tick_params(axis="x", rotation=25)
    axis.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "ablation.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    algorithms = sorted({row['algorithm'] for row in scale})
    for algorithm in algorithms:
        rows = [row for row in scale if row['algorithm'] == algorithm]
        by_size = defaultdict(list)
        for row in rows:
            by_size[int(row['n_orders'])].append(row)
        sizes = sorted(by_size)
        runtime_means = [stats([r['runtime_s'] for r in by_size[size]])[0] for size in sizes]
        quality_means = [stats([r['cost_rs'] for r in by_size[size]])[0] for size in sizes]
        axes[0].plot(sizes, runtime_means, marker="o", label=algorithm)
        axes[1].plot(sizes, quality_means, marker="o", label=algorithm)
    axes[0].set_ylabel("Runtime (s), per algorithm")
    axes[1].set_ylabel("Cost (Rs.; nonfinite runs counted separately in table)")
    for axis in axes:
        axis.set_xlabel("Orders")
        axis.grid(alpha=.25)
        axis.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "scalability.png", dpi=180)
    plt.close(fig)

    methods = sorted({row['method'] for row in gaps})
    gap_means = [stats([row['gap_pct'] for row in gaps if row['method'] == method and row['gap_valid'].lower() == 'true'])[0] for method in methods]
    gap_sds = [stats([row['gap_pct'] for row in gaps if row['method'] == method and row['gap_valid'].lower() == 'true'])[1] for method in methods]
    fig, axis = plt.subplots(figsize=(10, 5))
    axis.bar(methods, gap_means, yerr=gap_sds, capsize=3, color="#D06B46")
    axis.set_ylabel("Gap to exact 8-order optimum (%)")
    axis.tick_params(axis="x", rotation=20)
    axis.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "optimality_gap.png", dpi=180)
    plt.close(fig)

    split_rows = [row for row in contributions if row['dimension'] == 'split']
    heuristic_rows = [row for row in contributions if row['dimension'] == 'heuristic']
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for axis, rows, title in ((axes[0], split_rows, "Split win rate"), (axes[1], heuristic_rows, "Heuristic win rate")):
        labels = [row['value'] for row in rows]
        values = [float(row['best_of_group_win_rate']) * 100 for row in rows]
        axis.bar(labels, values, color="#70844A")
        axis.set_title(title)
        axis.set_ylabel("Best-of-56 wins (% seeds)")
        axis.tick_params(axis="x", rotation=35)
        axis.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "split_heuristic_contribution.png", dpi=180)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 6))
    distances = [float(row['distance_km_mean']) for row in candidate]
    penalties = [float(row['penalty_rs_mean']) for row in candidate]
    costs = [float(row['cost_rs_mean']) for row in candidate]
    scatter = axis.scatter(distances, penalties, c=costs, cmap="viridis", edgecolors="black", linewidths=.25)
    axis.set_xlabel("Full-plan distance (km), mean across seeds")
    axis.set_ylabel("Penalty (Rs.), mean across seeds")
    axis.set_title("56 split/heuristic candidates: distance vs penalty")
    fig.colorbar(scatter, ax=axis, label="Total cost (Rs.)")
    axis.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "distance_penalty_scatter.png", dpi=180)
    plt.close(fig)


def main():
    write_summary_md()
    write_claims_ledger()
    write_paper_changes()
    write_figures()
    print(f"Wrote summary, claims ledger, paper changes, and figures under {RESULTS}")


if __name__ == "__main__":
    main()
