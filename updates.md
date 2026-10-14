## Planned code changes for Group C
We would add three focused experimental layers:

1. Ablation runner

- New script or function to toggle one design choice at a time.
- Example variants:
    - no infrastructure filter
    - no late-penalty term
    - no traffic/weather multipliers
    - no warm-start routes
    - no route-splitting heuristic
- Output: per-variant metrics on cost, distance, feasibility, runtime.

2. Scaling runner

- Generate or reuse instances with increasing sizes, e.g. 20, 40, 60, 80, 100.
- Run each algorithm and record:
    - runtime
    - cost
    - gap to benchmark / best known
    - feasibility rate
- Output: a scaling CSV/JSON summary.

3. Benchmark summary upgrades

- Standardize gap reporting:
    - average gap %
    - best/median/worst gap
    - feasible runs
    - runtime
- Include both synthetic and benchmark datasets in one summary table.

## File-level change list

1. recreate.py

- add an ablation runner that toggles one component at a time
- add a scaling experiment over increasing instance sizes
- add a consistent reporting function for cost, gap, runtime, feasibility
- keep the OR-Tools + heuristic comparison in the same pipeline

2. run_benchmarks.py

- add benchmark gap summaries by family and instance
- add scaling loops over Solomon/Cordeau sizes if available
- report mean/median/worst gap and feasible-run counts
- keep published benchmark references for comparison

3. summary.json

- expand output to include:
    - ablation results
    - scalability results
    - benchmark gap statistics
- keep the current algorithm summary but add the missing experiment sections

4. README.md

- add a short “Experimental setup” section
- describe ablation design and scalability protocol
- note fair baseline and benchmark methodology
