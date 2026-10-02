name        = input().strip()
student_id  = int(input())
chinese     = int(input())
cs          = int(input())
prog        = int(input())

total   = chinese + cs + prog
average = total // 3

print(f"Name:{name}")
print(f"Id:{student_id}")
print(f"Total:{total}")
print(f"Average:{average}")