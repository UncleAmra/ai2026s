import math

def solve_telecom():
    net_voice = int(input())
    out_voice = int(input())
    land_voice = int(input())
    net_sms = int(input())
    out_sms = int(input())
    
    plans = [
        {"name": 199, "base": 199, "net_v": 0.090, "out_v": 0.15, "land_v": 0.14, "net_s": 1.20, "out_s": 1.60},
        {"name": 399, "base": 399, "net_v": 0.075, "out_v": 0.135, "land_v": 0.125, "net_s": 1.15, "out_s": 1.30},
        {"name": 799, "base": 799, "net_v": 0.065, "out_v": 0.11, "land_v": 0.10, "net_s": 0.95, "out_s": 1.10}
    ]
    
    best_cost = float('inf')
    best_plan = None
    
    for p in plans:
        comm_cost = (net_voice * p["net_v"] + 
                     out_voice * p["out_v"] + 
                     land_voice * p["land_v"] + 
                     net_sms * p["net_s"] + 
                     out_sms * p["out_s"])
        
        if comm_cost > p["base"]:
            cost = comm_cost
        else:
            cost = p["base"]
            
        final_cost = math.floor(cost)
        
        if final_cost < best_cost:
            best_cost = final_cost
            best_plan = p["name"]
        elif final_cost == best_cost:
            if p["name"] < best_plan:
                best_plan = p["name"]
                
    print(best_cost)
    print(best_plan)

if __name__ == "__main__":
    solve_telecom()