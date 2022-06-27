import cosmos
import math
import random
import statistics

def speed(v):
    return math.sqrt(v[0]**2 + v[1]**2)

m1 = random.randint(1, 10)
m2 = random.randint(1, 10)

# m1 = 10
# m2 = 2 

r1 = [1, 0]
r2 = [0, -1]

v1 = [random.randint(1, 10), 0]
v2 = [0, random.randint(1, 10)]
# v1 = [1, 0]
# v2 = [0, 10]
speed1 = speed(v1)
speed2 = speed(v2)

print(f"\nMass #1:  {m1}")
print(f"Mass #2:  {m2}")

print(f"\nInitial Velocity #1:  {v1}")
print(f"Initial Speed #1:  {speed1}")
print(f"Initial Velocity #2:  {v2}")
print(f"Initial Speed #2:  {speed2}")

Ei = 0.5*(m1*(speed1**2) + m2*(speed2**2))

print(f"Initial Energy:  {Ei}")

# oldv1 = v1

# v1 = cosmos.bounce_v(m1, m2, r1, r2, v1, v2)
# v2 = cosmos.bounce_v(m2, m1, r2, r1, v2, oldv1)
[v1, v2] = cosmos.bounce_v2(m1, m2, r1, r2, v1, v2)
speed1 = speed(v1)
speed2 = speed(v2)

print(f"\nFinal Velocity #1:  {v1}")
print(f"Final Speed #1:  {speed1}")
print(f"Final Velocity #2:  {v2}")
print(f"Final Speed #2:  {speed2}")

Ef = 0.5*(m1*(speed1**2) + m2*(speed2**2))

print(f"Final Energy:  {Ef}")

err_tolerance = 0.01

if ( abs(Ei - Ef)/statistics.mean([Ei, Ef]) ) > err_tolerance:
    print("\nEnergies are not equal")
