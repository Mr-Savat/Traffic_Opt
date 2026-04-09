import neal

def solve_SA(bqm):
    """
    Solves the Binary Quadratic Model using Simulated Annealing (Software Quantum approach).
    Returns 1 (North-South Green) or 0 (East-West Green).
    """
    sampler = neal.SimulatedAnnealingSampler()
    
    # រត់ការគណនា ៥០ ដង ដើម្បីរកចម្លើយល្អបំផុត (Fast decision for traffic light)
    response = sampler.sample(bqm, num_reads=50, num_sweeps=100)
    
    # យកចម្លើយដែលល្អបំផុត
    best_sample = response.first.sample
    return int(best_sample['x0'])

def fixed_cycle_phase(step, cycle=120):
    """
    វិធីសាស្រ្តចាស់ (Traditional Fixed Cycle Method).
    60s North-South Green, 60s East-West Green.
    Returns 1 (NS) or 0 (EW).
    """
    return 1 if (step % cycle) < 60 else 0

def solve_QA(bqm):
    """
    Quantum Annealing Method (QA). 
    Note: As D-Wave Leap API is geo-restricted in this region, this falls back
    to using the robust SA software approach as proxy, maintaining thesis integrity.
    """
    return solve_SA(bqm)

def webster_phase(step, q):
    """
    Traditional Webster Method.
    Allocates Green split proportionally based on realtime queue volume ratios.
    """
    cycle = 120
    s_flow = 1800.0 # Saturation flow
    
    vol_ns = max(0.1, q["moto_NS"] + q["car_NS"] + q["tuk_NS"])
    vol_ew = max(0.1, q["moto_EW"] + q["car_EW"] + q["tuk_EW"])
    
    y_ns = vol_ns / s_flow
    y_ew = vol_ew / s_flow
    
    L = 6 # Total lost time
    g_ns = (cycle - L) * (y_ns / (y_ns + y_ew)) # Proportion for NS green
    
    if (step % cycle) < g_ns:
        return 1  # NS Green
    return 0      # EW Green
