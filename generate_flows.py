import xml.etree.ElementTree as ET

scenarios = {
    "SC1": {"motorcycle": 700, "car": 150, "tuktuk": 60},
    "SC2": {"motorcycle": 600, "car": 200, "tuktuk": 80},
    "SC3": {"motorcycle": 200, "car": 50, "tuktuk": 20},
    "SC4": {"motorcycle": 900, "car": 100, "tuktuk": 30}
}
for name, data in scenarios.items():
    root = ET.Element("routes")
    # For each approach direction
    for d_from, d_to in [("edge_N", "edge_S"), ("edge_S", "edge_N"), ("edge_E", "edge_W"), ("edge_W", "edge_E")]:
        for vtype, rate in data.items():
            # Add slight variation per direction for realism
            rate_var = rate
            if d_from == "edge_W": rate_var = int(rate * 0.8)
            if d_from == "edge_N": rate_var = int(rate * 1.1)
            
            ET.SubElement(root, "flow", id=f"{vtype}_{d_from}_{name}", type=vtype, 
                          **{"from": d_from, "to": d_to, "begin": "0", "end": "3600", 
                             "vehsPerHour": str(rate_var), "departLane": "random"})
    
    with open(f"flows_{name}.rou.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        # Format the XML
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(ET.tostring(root))
        f.write(dom.toprettyxml(indent="  ")[22:])
        
print("Successfully generated all 4 traffic scenario files!")
