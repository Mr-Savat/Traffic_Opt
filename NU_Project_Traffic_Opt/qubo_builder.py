import dimod

# ទម្ងន់ចរាចរណ៍នៅភ្នំពេញ (Phnom Penh JASIC 2023 modal share)
# ម៉ូតូដើរតួនាទីធំជាងគេបំផុត!
W_MOTO = 0.60
W_CAR  = 0.30
W_TUK  = 0.10

def build_qubo(q):
    """
    Builds the QUBO for the traffic intersection.
    Variable x0: 
      1 = North-South Green (អនុញ្ញាតឲ្យរថយន្តទិសជើង-ត្បូងទៅ)
      0 = East-West Green (អនុញ្ញាតឲ្យរថយន្តទិសកើត-លិចទៅ)
    
    The objective is to minimize the unserved weighted queue.
    """
    
    # គណនាផលបូកទម្ងន់ចរាចរណ៍ទិសជើង-ត្បូង (North-South)
    L_NS = (W_MOTO * q.get("moto_NS", 0) + 
            W_CAR  * q.get("car_NS", 0) + 
            W_TUK  * q.get("tuk_NS", 0))
            
    # គណនាផលបូកទម្ងន់ចរាចរណ៍ទិសកើត-លិច (East-West)
    L_EW = (W_MOTO * q.get("moto_EW", 0) + 
            W_CAR  * q.get("car_EW", 0) + 
            W_TUK  * q.get("tuk_EW", 0))
            
    # រូបមន្ត: H(x) = -(L_NS - L_EW) * x0
    # បើ L_NS ធំជាង (ស្ទះជើងត្បូងខ្លាំង) -> h អវិជ្ជមាន -> Machine នឹងរើស x0=1
    h = -(L_NS - L_EW)
    
    Q = {('x0', 'x0'): h}
    
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
    return bqm, L_NS, L_EW
