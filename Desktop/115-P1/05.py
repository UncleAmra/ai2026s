def solve_triangle():
    a = int(input())
    b = int(input())
    c = int(input())
    
    sides = sorted([a, b, c])
    x, y, z = sides[0], sides[1], sides[2]
    
    if x <= 0 or x + y <= z:
        print("Not Triangle")
        return
        
    results = []
    
    if x == y == z:
        results.append("Equilateral Triangle")
        
    if x == y or y == z or x == z:
        results.append("Isosceles Triangle")
        
    z_sq = z * z
    xy_sq = x * x + y * y
    
    if z_sq > xy_sq:
        results.append("Obtuse Triangle")
    elif z_sq < xy_sq:
        results.append("Acute Triangle")
    else:
        results.append("Right Triangle")
        
    for r in results:
        print(r)
        
    print(a + b + c)

if __name__ == "__main__":
    solve_triangle()