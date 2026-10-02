def solve_conflict():
    parsed = []
    for _ in range(3):
        cid = int(input())
        t1 = int(input())
        t2 = int(input())
        parsed.append((cid, [t1, t2]))
        
    all_conflicts = []
    for i in range(3):
        for j in range(i + 1, 3):
            id1, times1 = parsed[i]
            id2, times2 = parsed[j]
            
            common = set(times1).intersection(set(times2))
            if common:
                sorted_common = sorted(list(common))
                for t in sorted_common:
                    c_min = min(id1, id2)
                    c_max = max(id1, id2)
                    all_conflicts.append((c_min, c_max, t))
                    
    all_conflicts.sort(key=lambda x: (x[0], x[1], x[2]))
    
    if not all_conflicts:
        print("correct")
    else:
        for c in all_conflicts:
            print(f"{c[0]} and {c[1]} conflict on {c[2]}")

if __name__ == "__main__":
    solve_conflict()