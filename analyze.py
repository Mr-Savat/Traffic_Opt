import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_full_results():
    scenarios = ["SC1", "SC2", "SC3", "SC4"]
    methods = ["Fixed", "Webster", "SA", "QA"]
    
    data = {}
    for s in scenarios:
        data[s] = {}
        for m in methods:
            file = f"results/results_{m}_{s}.csv"
            if os.path.exists(file):
                df = pd.read_csv(file)
                data[s][m] = df
            else:
                print(f"File missing: {file}")
                
    # --- Print Summary Table ---
    print("\n" + "="*70)
    print("   TABLE 1: AVERAGE HALTED VEHICLES BY METHOD & SCENARIO   ")
    print("="*70)
    print(f"{'Method':<10} | {'SC-1 (AM)':<12} | {'SC-2 (PM)':<12} | {'SC-3 (Off)':<12} | {'SC-4 (Extreme)':<14}")
    print("-" * 70)
    
    avg_matrix = {m: [] for m in methods}
    for m in methods:
        row = [m]
        res_text = f"{m:<10} | "
        for s in scenarios:
            if m in data[s]:
                avg = data[s][m]['halted_vehicles'].mean()
                avg_matrix[m].append(avg)
                res_text += f"{avg:<12.2f} | "
            else:
                avg_matrix[m].append(0)
                res_text += f"{'N/A':<12} | "
        print(res_text)
        
    print("="*70)
    
    # Calculate key improvement for SC-4
    if "Fixed" in avg_matrix and "SA" in avg_matrix:
        f_sc4 = avg_matrix["Fixed"][3]
        sa_sc4 = avg_matrix["SA"][3]
        imp = ((f_sc4 - sa_sc4) / f_sc4) * 100
        print(f"\n[KEY FINDING] In SC-4 (Extreme Moto Wave), QUBO SA reduces traffic wait by {imp:.2f}% compared to Fixed!")
    
    # --- Figure 1: Grouped Bar Chart ---
    x = np.arange(len(scenarios))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"Fixed": "#e74c3c", "Webster": "#f39c12", "SA": "#2ecc71", "QA": "#3498db"}
    
    for i, m in enumerate(methods):
        if len(avg_matrix[m]) == len(scenarios):
            ax.bar(x + (i - 1.5) * width, avg_matrix[m], width, label=m, color=colors[m])
        
    ax.set_ylabel('Average Halted Vehicles (Queue Depth)', fontsize=12)
    ax.set_title('Performance Comparison Across Scenarios\nPhnom Penh Intersection Analysis', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(['SC-1 (Rush AM)', 'SC-2 (Rush PM)', 'SC-3 (Off-Peak)', 'SC-4 (Extreme Moto)'])
    ax.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('results/fig1_4x4_comparison.png', dpi=300)
    plt.show()
    plt.close()
    
    # --- Figure 2: Line chart for SC-4 specifically ---
    plt.figure(figsize=(10, 6))
    for m in methods:
        if m in data["SC4"]:
            df = data["SC4"][m]
            # Smoothing line using rolling average to deal with sub-lane noise
            plt.plot(df['step'], df['halted_vehicles'].rolling(15).mean(), label=m, color=colors[m], linewidth=1.5)
        
    plt.title('Traffic Queue Evolution (SC-4: Extreme Motorcycle Wave)', fontsize=14)
    plt.xlabel('Simulation Step (Seconds)', fontsize=12)
    plt.ylabel('Halted Vehicles in Network', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('results/fig2_SC4_timeline.png', dpi=300)
    plt.show()
    plt.close()
    
    print("\n✅ New IEEE Charts successfully saved (fig1_4x4_comparison.png, fig2_SC4_timeline.png)!")

if __name__ == "__main__":
    analyze_full_results()
