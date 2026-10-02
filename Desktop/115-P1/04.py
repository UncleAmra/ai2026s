def solve_bmi():
    h = float(input())
    w = int(input())
    h_m = h / 100.0
    w_kg = w * 0.454
    bmi = w_kg / (h_m * h_m)
    
    if bmi < 18:
        print("Underweight")
    elif 18 <= bmi < 24:
        print("Normal")
    elif 24 <= bmi < 27:
        print("Overweight")
    elif 27 <= bmi < 30:
        print("Mild obesity")
    elif 30 <= bmi < 35:
        print("Moderate obesity")
    else:
        print("Severe obesity")

if __name__ == "__main__":
    solve_bmi()