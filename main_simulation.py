import os
import sys
import traci
import pandas as pd
from NU_Project_Traffic_Opt.qubo_builder import build_qubo
from NU_Project_Traffic_Opt.solvers import solve_SA, solve_QA, fixed_cycle_phase, webster_phase

def get_weighted_queue():
    q = {
        "moto_NS": 0, "car_NS": 0, "tuk_NS": 0,
        "moto_EW": 0, "car_EW": 0, "tuk_EW": 0
    }
    for edge in ["edge_N", "edge_S"]:
        for veh_id in traci.edge.getLastStepVehicleIDs(edge):
            if traci.vehicle.getSpeed(veh_id) < 0.1:
                vclass = traci.vehicle.getVehicleClass(veh_id)
                if vclass == "motorcycle": q["moto_NS"] += 1
                elif vclass == "passenger": q["car_NS"] += 1
                elif vclass == "taxi": q["tuk_NS"] += 1
                
    for edge in ["edge_E", "edge_W"]:
        for veh_id in traci.edge.getLastStepVehicleIDs(edge):
            if traci.vehicle.getSpeed(veh_id) < 0.1:
                vclass = traci.vehicle.getVehicleClass(veh_id)
                if vclass == "motorcycle": q["moto_EW"] += 1
                elif vclass == "passenger": q["car_EW"] += 1
                elif vclass == "taxi": q["tuk_EW"] += 1
    return q

def run_simulation(method="SA", scenario="SC1", use_gui=False):
    # Determine the SUMO binary to use
    sumo_bin = "sumo-gui" if use_gui else "sumo"
    
    path_sumo_x86 = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo.exe"
    path_gui_x86 = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe"
    path_sumo_64 = "C:\\Program Files\\Eclipse\\Sumo\\bin\\sumo.exe"
    path_gui_64 = "C:\\Program Files\\Eclipse\\Sumo\\bin\\sumo-gui.exe"
    
    if not use_gui:
        if os.path.exists(path_sumo_x86): sumo_bin = path_sumo_x86
        elif os.path.exists(path_sumo_64): sumo_bin = path_sumo_64
    else:
        if os.path.exists(path_gui_x86): sumo_bin = path_gui_x86
        elif os.path.exists(path_gui_64): sumo_bin = path_gui_64
        
    print(f"-> Simulating {method} on {scenario} (GUI: {use_gui})...", end=" ", flush=True)
    
    # Pass --route-files to dynamically load SC1, SC2, etc.
    routes = f"vehicles.rou.xml,flows_{scenario}.rou.xml"
    sumo_cmd = [sumo_bin, "-c", "phnom_penh.sumocfg", "--route-files", routes, "--time-to-teleport", "-1"]
    if not use_gui:
        sumo_cmd.extend(["--no-step-log", "true"])
    else:
        sumo_cmd.append("--start") # Auto start in GUI
    
    traci.start(sumo_cmd)
    
    step = 0
    wait_time_records = []
    
    while step < 3600:
        traci.simulationStep()
        
        if step % 30 == 0:
            q = get_weighted_queue()
            
            if method == "SA":
                bqm, lns, lew = build_qubo(q)
                decision = solve_SA(bqm)
            elif method == "QA":
                bqm, lns, lew = build_qubo(q)
                decision = solve_QA(bqm) 
            elif method == "Fixed":
                decision = fixed_cycle_phase(step)
            elif method == "Webster":
                decision = webster_phase(step, q)
            
            # Simple apply logic
            current_phase = traci.trafficlight.getPhase("J0")
            if decision == 1: 
                if current_phase == 2 or current_phase == 3: traci.trafficlight.setPhase("J0", 0) 
            else: 
                if current_phase == 0 or current_phase == 1: traci.trafficlight.setPhase("J0", 2) 
            
        # Log metrics every step
        total_halted = sum([traci.edge.getLastStepHaltingNumber(e) for e in ["edge_N", "edge_S", "edge_E", "edge_W"]])
        wait_time_records.append({"step": step, "halted_vehicles": total_halted})
        step += 1
        
    traci.close()
    
    df = pd.DataFrame(wait_time_records)
    df.to_csv(f"results_{method}_{scenario}.csv", index=False)
    print(f"DONE. (Avg Queue: {df['halted_vehicles'].mean():.2f})")

if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        print("=== LAUNCHING THESIS PRESENTATION DEMO ===")
        print("Note: Fast-forward the wait time or adjust delay inside the GUI.")
        run_simulation(method="SA", scenario="SC4", use_gui=True)
    else:
        print("=== STARTING FULL EXPERIMENTAL MATRIX (16 SIMULATIONS) ===")
        scenarios = ["SC1", "SC2", "SC3", "SC4"]
        methods = ["Fixed", "Webster", "SA", "QA"]
        
        for scenario in scenarios:
            print(f"\n--- Scenario: {scenario} ---")
            for method in methods:
                run_simulation(method=method, scenario=scenario)
                
        print("\nAll 16 experimental datasets have been successfully generated!")
