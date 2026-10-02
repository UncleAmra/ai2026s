import math

x = int(input())
y = int(input())
z = int(input())

total_qty = x + y + z
subtotal  = x * 440 + y * 1200 + z * 130

if total_qty >= 5:
   subtotal = math.floor(subtotal * 0.9)

if subtotal >= 3000:
   subtotal -= 300

print(subtotal)