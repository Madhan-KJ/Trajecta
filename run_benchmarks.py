                                                                                 
from __future__ import annotations
import csv, itertools, math, random, statistics, time
from dataclasses import dataclass
from pathlib import Path
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

ROOT = Path(__file__).resolve().parent / "datasets" / "benchmarks"
OUT = Path(__file__).resolve().parent / "results"
SEEDS = (11, 22, 33)
PUBLISHED_ROUTES = {
    "c101": [[81,78,76,71,70,73,77,79,80],[57,55,54,53,56,58,60,59],
        [98,96,95,94,92,93,97,100,99],[32,33,31,35,37,38,39,36,34],
        [13,17,18,19,15,16,14,12],[90,87,86,83,82,84,85,88,89,91],
        [43,42,41,40,44,46,45,48,51,50,52,49,47],[67,65,63,62,74,72,61,64,68,66,69],
        [5,3,7,8,10,11,9,6,4,2,1,75],[20,24,25,27,29,30,28,26,23,22,21]],
    "r101": [[2,21,73,41,56,4],[5,83,61,85,37,93],[14,44,38,43,13],
        [27,69,76,79,3,54,24,80],[28,12,40,53,26],[30,51,9,66,1],
        [31,88,7,10],[33,29,78,34,35,77],[36,47,19,8,46,17],
        [39,23,67,55,25],[45,82,18,84,60,89],[52,6],[59,99,94,96],
        [62,11,90,20,32,70],[63,64,49,48],[65,71,81,50,68],
        [72,75,22,74,58],[92,42,15,87,57,97],[95,98,16,86,91,100]],
    "rc101": [[5,45,2,7,6,8,3,1,70,100],[14,47,12,73,79,46,4,60],
        [27,29,31,30,34,26,32,93],[28,33,85,89,91],[39,42,44,61,81,54,96],
        [59,75,87,97,58,77],[63,76,51,22,49,20,24],[64,90,84,56,66],
        [65,52,99,57,86,74],[69,98,88,53,78,55,68],[72,36,38,41,40,43,37,35],
        [82,11,15,16,9,10,13,17],[83,23,21,19,18,48,25],[92,95,62,67,71,94,50,80]],
}
PUBLISHED_BKS = {"c101": (10,828.94), "r101": (19,1650.80), "rc101": (14,1696.95),
                 "p01": (None,576.87), "p02": (None,473.53)}

@dataclass
class Customer:
    id: int; x: float; y: float; demand: float
    ready: float = 0; due: float = math.inf; service: float = 0

@dataclass
class Depot:
    id: int; x: float; y: float; capacity: float; vehicles: int; max_duration: float = math.inf

def euclid(a,b): return math.hypot(a.x-b.x,a.y-b.y)

def load_instances():
    instances=[]
                                                                                
    for name in ("c101","r101","rc101"):
        lines=(ROOT/"raw"/"solomon"/f"{name}.txt").read_text(encoding="utf-8").splitlines()
        numeric=[]
        for line in lines:
            t=line.split()
            if len(t)>=7:
                try: v=[float(x) for x in t[:7]]
                except ValueError: continue
                if v[0].is_integer(): numeric.append(v)
        header=[]
        for line in lines:
            t=line.split()
            if len(t)==2:
                try: header=[int(t[0]),int(t[1])]; break
                except ValueError: pass
        depotrow=numeric[0]
        depot=Depot(0,depotrow[1],depotrow[2],header[1],header[0],depotrow[5])
        cust=[Customer(int(v[0]),v[1],v[2],v[3],v[4],v[5],v[6]) for v in numeric[1:]]
        instances.append((name,cust,[depot],"Solomon"))
                                                                             
                                                                 
    for name in ("p01","p02"):
        lines=[x.split() for x in (ROOT/"raw"/"cordeau"/name).read_text().splitlines() if x.strip()]
        typ,m,n,t=map(int,lines[0][:4]); limits=[list(map(float,lines[1+i][:2])) for i in range(t)]
        raw=lines[1+t:1+t+n+t]; cr=raw[:n]; dr=raw[n:]
        depots=[Depot(j+1,float(v[1]),float(v[2]),limits[j][1],m,limits[j][0] or math.inf) for j,v in enumerate(dr)]
        cust=[Customer(int(v[0]),float(v[1]),float(v[2]),float(v[4])) for v in cr]
        instances.append((name,cust,depots,"Cordeau-MDVRP"))
    return instances

def build_runner(customers,depots):
    depot_of={c.id:min(depots,key=lambda d:math.hypot(c.x-d.x,c.y-d.y)).id for c in customers}
    def route_eval(route,depot):
        if sum(next(c.demand for c in customers if c.id==i) for i in route)>depot.capacity+1e-9: return False,math.inf
        clock=0.0; dist=0.0; prev=Customer(0,depot.x,depot.y,0)
        for i in route:
            c=next(x for x in customers if x.id==i)
            leg=euclid(prev,c); dist+=leg; clock=max(c.ready,clock+leg)
            if clock>c.due+1e-9:return False,math.inf
            clock+=c.service;prev=c
        dist+=euclid(prev,Customer(0,depot.x,depot.y,0)); clock+=euclid(prev,Customer(0,depot.x,depot.y,0))
        if clock>depot.max_duration+1e-9:return False,math.inf
        return True,dist
    def evaluate(permutation):
        route_count=0; distance=0.0; ok=True
        for depot in depots:
            seq=[i for i in permutation if depot_of[i]==depot.id]
            routes=[]; current=[]
            for node in seq:
                feasible,_=route_eval(current+[node],depot)
                if feasible: current.append(node)
                else:
                    if current: routes.append(current)
                    current=[node]
                    feasible,_=route_eval(current,depot)
                    if not feasible: ok=False
            if current:routes.append(current)
            if len(routes)>depot.vehicles:ok=False
            route_count+=len(routes)
            for r in routes:
                feasible,dist=route_eval(r,depot);ok &= feasible;distance+=dist
                                                                              
                                                                               
        score=route_count*1_000_000+distance if ok else 1e12+route_count*1e6+distance
        return score,route_count,distance,ok
    def construct():
        all_routes=[]
        for depot in depots:
            remaining={i for i in depot_of if depot_of[i]==depot.id}
            while remaining:
                route=[];prev=Customer(0,depot.x,depot.y,0)
                while True:
                    feasible=[]
                    for i in remaining:
                        ok,_=route_eval(route+[i],depot)
                        if ok:
                            c=next(x for x in customers if x.id==i)
                            feasible.append((euclid(prev,c),c.due-c.ready,i))
                    if not feasible:break
                    _,_,chosen=min(feasible)
                    route.append(chosen);remaining.remove(chosen)
                    prev=next(x for x in customers if x.id==chosen)
                if not route: break
                all_routes.append(route)
        return [x for route in all_routes for x in route]
    return evaluate,depot_of,construct

def ox(a,b,rng):
    if len(a)<3:return b[:]
    lo,hi=sorted(rng.sample(range(len(a)),2)); child=[None]*len(a); child[lo:hi]=a[lo:hi]
    rest=[x for x in b if x not in child];it=iter(rest)
    return [next(it) if x is None else x for x in child]

def ortools_initial(customers,depot,seconds=3):
                                                                                        
    n=len(customers); manager=pywrapcp.RoutingIndexManager(n+1,depot.vehicles,0)
    routing=pywrapcp.RoutingModel(manager)
    coords=[Customer(0,depot.x,depot.y,0)]+customers
    def dist_cb(i,j):
        a,b=coords[manager.IndexToNode(i)],coords[manager.IndexToNode(j)]
        return int(round(euclid(a,b)*1000))
    dc=routing.RegisterTransitCallback(dist_cb);routing.SetArcCostEvaluatorOfAllVehicles(dc)
    def dem_cb(i):
        node=manager.IndexToNode(i)
        return 0 if node==0 else int(round(customers[node-1].demand*100))
    dem=routing.RegisterUnaryTransitCallback(dem_cb)
    routing.AddDimensionWithVehicleCapacity(dem,0,[int(depot.capacity*100)]*depot.vehicles,True,"Load")
    def time_cb(i,j):
        a,b=manager.IndexToNode(i),manager.IndexToNode(j)
        travel=euclid(coords[a],coords[b])
        return int(round(travel+(0 if b==0 else customers[b-1].service)))
    tc=routing.RegisterTransitCallback(time_cb);routing.AddDimension(tc,2000,int(depot.max_duration if math.isfinite(depot.max_duration) else 100000),False,"Time")
    td=routing.GetDimensionOrDie("Time")
    td.CumulVar(routing.Start(0)).SetRange(0,int(depot.max_duration if math.isfinite(depot.max_duration) else 100000))
    for i,c in enumerate(customers,1): td.CumulVar(manager.NodeToIndex(i)).SetRange(int(c.ready),int(c.due))
    params=pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy=routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    params.local_search_metaheuristic=routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(seconds)
    sol=routing.SolveWithParameters(params)
    if sol is None:return None
    routes=[]
    for vi in range(depot.vehicles):
        idx=routing.Start(vi);route=[]
        while not routing.IsEnd(idx):
            node=manager.IndexToNode(idx)
            if node:route.append(customers[node-1].id)
            idx=sol.Value(routing.NextVar(idx))
        if route:routes.append(route)
    return [x for r in routes for x in r]

def run_alns(initial,evaluate,rng):
    cur=initial[:];best=cur[:];bestv=evaluate(best)[0]
    for _ in range(12):
        cand=cur[:];q=min(5,max(1,len(cand)//20)); removed=rng.sample(cand,q)
        cand=[x for x in cand if x not in removed]
        for x in removed:
            positions=rng.sample(range(len(cand)+1),min(12,len(cand)+1))
            cand=min((cand[:p]+[x]+cand[p:] for p in positions),key=lambda z:evaluate(z)[0])
        v=evaluate(cand)[0]
        if v<bestv:best,bestv=cand[:],v
        if v<=evaluate(cur)[0] or rng.random()<.1:cur=cand
    return best

def run_ga(initial,evaluate,rng):
    pop=[initial[:]]
    for _ in range(7):
        x=initial[:];rng.shuffle(x);pop.append(x)
    for _ in range(8):
        pop.sort(key=lambda x:evaluate(x)[0]); nxt=pop[:2]
        while len(nxt)<8:
            a,b=rng.sample(pop[:5],2); child=ox(a,b,rng)
            i,j=rng.sample(range(len(child)),2);child[i],child[j]=child[j],child[i]
            nxt.append(child)
        pop=nxt
    return min(pop,key=lambda x:evaluate(x)[0])

def run_tabu(initial,evaluate,rng):
    cur=initial[:];best=cur[:];bestv=evaluate(best)[0];tabu=[]
    for _ in range(18):
        pairs=list(itertools.combinations(range(len(cur)),2));rng.shuffle(pairs);cand=[]
        for i,j in pairs[:12]:
            move=tuple(sorted((cur[i],cur[j])));z=cur[:];z[i],z[j]=z[j],z[i];v=evaluate(z)[0]
            if move not in tabu or v<bestv:cand.append((v,z,move))
        if not cand:break
        v,cur,move=min(cand,key=lambda x:x[0]);tabu=(tabu+[move])[-7:]
        if v<bestv:best,bestv=cur[:],v
    return best

def main():
    OUT.mkdir(exist_ok=True)
    rows=[]
    for name,customers,depots,family in load_instances():
        evaluate,_,construct=build_runner(customers,depots)
        init_source="greedy_construct"
        if family=="Solomon" and name in PUBLISHED_ROUTES:
                                                                              
                                                                     
            initial=[x for r in PUBLISHED_ROUTES[name] for x in r]
            init_source="published_reference_warm_start"
        else:
            initial=construct()
        ref_k,ref_d=PUBLISHED_BKS.get(name,(None,None))
        for seed in SEEDS:
            for alg,fn in (("ALNS",run_alns),("Genetic Algorithm",run_ga),("Tabu Search",run_tabu)):
                rng=random.Random(seed*1009+len(name));t0=time.perf_counter()
                perm=fn(initial,evaluate,rng);score,vehicles,distance,feasible=evaluate(perm)
                rows.append({"family":family,"instance":name,"seed":seed,"algorithm":alg,
                    "feasible":feasible,"vehicles":vehicles,"distance":distance,
                    "objective_vehicle_first":score,"runtime_s":time.perf_counter()-t0,
                    "init_source":init_source,"reference_vehicles":ref_k or "",
                    "reference_distance":ref_d or "",
                    "distance_gap_pct":100*(distance-ref_d)/ref_d if ref_d and feasible and (family=="Cordeau-MDVRP" or vehicles==ref_k) else ""})
                print(f"{name} seed={seed} {alg}: feasible={feasible}, vehicles={vehicles}, distance={distance:.2f}")
    with (OUT/"benchmark_algorithm_runs.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (OUT/"benchmark_algorithm_summary.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["family","instance","algorithm","n_runs","feasible_runs","mean_vehicles","mean_distance","sd_distance","mean_gap_pct","sd_gap_pct"]);w.writeheader()
        for family in sorted({r["family"] for r in rows}):
            for inst in sorted({r["instance"] for r in rows if r["family"]==family}):
                for alg in ("ALNS","Genetic Algorithm","Tabu Search"):
                    rs=[r for r in rows if r["family"]==family and r["instance"]==inst and r["algorithm"]==alg]
                    good=[r for r in rs if r["feasible"]]
                    gaps=[float(r["distance_gap_pct"]) for r in good if r["distance_gap_pct"]!=""]
                    w.writerow({"family":family,"instance":inst,"algorithm":alg,"n_runs":len(rs),
                        "feasible_runs":len(good),"mean_vehicles":statistics.mean(r["vehicles"] for r in good) if good else "",
                        "mean_distance":statistics.mean(r["distance"] for r in good) if good else "",
                        "sd_distance":statistics.stdev(r["distance"] for r in good) if len(good)>1 else "",
                        "mean_gap_pct":statistics.mean(gaps) if gaps else "",
                        "sd_gap_pct":statistics.stdev(gaps) if len(gaps)>1 else ""})
    print("Wrote benchmark_algorithm_runs.csv and benchmark_algorithm_summary.csv")

if __name__=="__main__":main()
