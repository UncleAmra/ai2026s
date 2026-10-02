import math

a = int(input())
b = int(input())
c = int(input())

delta = b * b - 4 * a * c

if delta > 0:
  x1 = (-b + math.sqrt(delta)) / (2 * a)
  x2 = (-b - math.sqrt(delta)) / (2 * a)
  print(f"{x1:.1f}")
  print(f"{x2:.1f}")
elif delta == 0:
  x = -b / (2 * a)
  print(f"{x:.1f}")
else:
  real_part = -b / (2 * a)
  imag_part = math.sqrt(-delta) / abs(2 * a)
  print(f"{real_part:.1f}+{imag_part:.1f}i")
  print(f"{real_part:.1f}-{imag_part:.1f}i")