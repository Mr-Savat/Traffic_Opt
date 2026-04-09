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
