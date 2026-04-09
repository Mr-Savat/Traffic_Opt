import os
import pandas as pd
import matplotlib.pyplot as plt

def analyze_results():
    if not (os.path.exists("results_Fixed_SC1.csv") and os.path.exists("results_SA_SC1.csv")):
        print("Error: CSV result files not found.")
        return

    # Load data
    df_fixed = pd.read_csv("results_Fixed_SC1.csv")
    df_sa = pd.read_csv("results_SA_SC1.csv")

    avg_fixed = df_fixed['halted_vehicles'].mean()
    avg_sa = df_sa['halted_vehicles'].mean()
    
    # Calculate percentage reduction in queue length
    improvement = ((avg_fixed - avg_sa) / avg_fixed) * 100

    print("=== TRAFFIC SIMULATION RESULTS ===")
    print(f"Fixed Cycle Average Queue: {avg_fixed:>.2f} vehicles")
    print(f"Quantum SA Average Queue:  {avg_sa:>.2f} vehicles")
    print(f"Total Improvement:         {improvement:.2f}% reduction in traffic congestion!")

    # Plot 1: Average Comparison
    plt.figure(figsize=(8, 5))
    bars = plt.bar(['Traditional Fixed Cycle', 'Quantum-Enhanced (QUBO)'], [avg_fixed, avg_sa], color=['#FF6B6B', '#4ECDC4'])
    plt.title('Average Traffic Queue in Phnom Penh (Motorcycle-Dominant)')
    plt.ylabel('Average Halted Vehicles')
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (yval * 0.02), f"{yval:.1f}", ha='center', va='bottom', fontweight='bold', fontsize=12)
        
    plt.tight_layout()
    plt.savefig('average_queue_comparison.png', dpi=300)
    plt.show()

    # Plot 2: Queue Over Time
    plt.figure(figsize=(10, 6))
    
    # To make the graph cleaner, we'll plot a rolling average so it's not too spiky
    plt.plot(df_fixed['step'], df_fixed['halted_vehicles'].rolling(10).mean(), label='Traditional Fixed Cycle', alpha=0.8, color='#FF6B6B', linewidth=1.5)
    plt.plot(df_sa['step'], df_sa['halted_vehicles'].rolling(10).mean(), label='Quantum-Enhanced (QUBO)', alpha=0.8, color='#4ECDC4', linewidth=1.5)
    
    plt.title('Traffic Queue Over 1 Hour Simulation (SC-1)', fontsize=14)
    plt.xlabel('Simulation Step (Seconds)', fontsize=12)
    plt.ylabel('Total Halted Vehicles (Network-wide)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('queue_over_time.png', dpi=300)
    plt.show()
    
    print("\nGraphs successfully generated and saved:")
    print(" - average_queue_comparison.png")
    print(" - queue_over_time.png")

if __name__ == "__main__":
    analyze_results()
