import os
import sys
import traci
import pandas as pd
from NU_Project_Traffic_Opt.qubo_builder import build_qubo
from NU_Project_Traffic_Opt.solvers import solve_SA, fixed_cycle_phase

def get_weighted_queue():
    """
    Returns a dictionary of queued vehicles classified by type and direction.
    """
    q = {
        "moto_NS": 0, "car_NS": 0, "tuk_NS": 0,
        "moto_EW": 0, "car_EW": 0, "tuk_EW": 0
    }
    
    # North-South edges
    for edge in ["edge_N", "edge_S"]:
        for veh_id in traci.edge.getLastStepVehicleIDs(edge):
            if traci.vehicle.getSpeed(veh_id) < 0.1: # Stopped/Queued
                vclass = traci.vehicle.getVehicleClass(veh_id)
                if vclass == "motorcycle": q["moto_NS"] += 1
                elif vclass == "passenger": q["car_NS"] += 1
                elif vclass == "taxi": q["tuk_NS"] += 1
                
    # East-West edges
    for edge in ["edge_E", "edge_W"]:
        for veh_id in traci.edge.getLastStepVehicleIDs(edge):
            if traci.vehicle.getSpeed(veh_id) < 0.1: # Stopped/Queued
                vclass = traci.vehicle.getVehicleClass(veh_id)
                if vclass == "motorcycle": q["moto_EW"] += 1
                elif vclass == "passenger": q["car_EW"] += 1
                elif vclass == "taxi": q["tuk_EW"] += 1
                
    return q

def run_simulation(method="SA"):
    # Connect to SUMO
    # Fallback to absolute path if system path is not updated yet
    # Use the visual GUI version so the user can see it!
    sumo_bin = "sumo-gui"
    if os.path.exists("C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe"):
        sumo_bin = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe"
        
    sumo_cmd = [sumo_bin, "-c", "phnom_penh.sumocfg", "--no-step-log", "true", "--time-to-teleport", "-1", "--start"]
    print(f"Starting SUMO for {method} method...")
    traci.start(sumo_cmd)
    
    step = 0
    wait_time_records = []
    
    while step < 3600:
        traci.simulationStep()
        
        # Every 30 seconds, Artificial Quantum Core makes a phase decision
        if step % 30 == 0:
            if method == "SA":
                q = get_weighted_queue()
                bqm, lns, lew = build_qubo(q)
                decision = solve_SA(bqm)
            else:
                decision = fixed_cycle_phase(step)
            
            current_phase = traci.trafficlight.getPhase("J0")
            
            # Simple override logic
            # Note: Phase 0 is NS Green, Phase 2 is EW Green
            if decision == 1: 
                if current_phase == 2 or current_phase == 3:
                    traci.trafficlight.setPhase("J0", 0) 
            else: 
                if current_phase == 0 or current_phase == 1: 
                    traci.trafficlight.setPhase("J0", 2) 
            
        # Log metrics every step (Total halted vehicles across all edges = Total Queue)
        total_halted = sum([traci.edge.getLastStepHaltingNumber(e) for e in ["edge_N", "edge_S", "edge_E", "edge_W"]])
        wait_time_records.append({"step": step, "halted_vehicles": total_halted})
        step += 1
        
    traci.close()
    
    # Save the output to build charts later
    df = pd.DataFrame(wait_time_records)
    df.to_csv(f"results_{method}_SC1.csv", index=False)
    print(f"[{method}] Simulation complete. Average Halted Vehicles: {df['halted_vehicles'].mean():.2f}\n")

if __name__ == "__main__":
    print("=== TRAFFIC SIGNAL OPTIMIZATION SIMULATION ===")
    print("1. Running Baseline Fixed Cycle...")
    run_simulation(method="Fixed")
    print("2. Running Quantum Simulated Annealing...")
    run_simulation(method="SA")
    print("All tasks finished successfully!")
