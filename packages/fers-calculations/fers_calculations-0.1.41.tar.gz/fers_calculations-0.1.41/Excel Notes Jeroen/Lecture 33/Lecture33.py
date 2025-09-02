# DEPENDENCIES
import copy
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
from numpy import genfromtxt
import csv

# =================================START OF DATA ENTRY================================
# Constants
E = 200 * 10**9  # (N/m^2)
A = 0.005  # (m^2)
xFac = 50  # Scale factor for plotted displacements

# Import structure data
nodes = genfromtxt('Vertices.csv', delimiter=',')
members = genfromtxt('Edges.csv', delimiter=',')
members = np.int_(members)  # Convert members definitions from float to int

# Supports [index starting at 1]
restrainedDoF = [1, 2, 3, 10, 11, 12, 151, 152, 153, 154, 155, 156]  # Restrained degrees of freedom

# Loading [index starting at 0]
forceVector = np.zeros(len(nodes) * 3)
forceVector[176] = -25000
forceVector[179] = -25000
forceVector[146] = -25000
forceVector[191] = -25000
forceVector[212] = -25000
forceVector[215] = -25000
# =================================END OF DATA ENTRY================================

# Calculate member orientation and length
def memberOrientation3D(memberNo):
    memberIndex = memberNo - 1
    node_i, node_j = members[memberIndex]
    ix, iy, iz = nodes[node_i - 1]
    jx, jy, jz = nodes[node_j - 1]
    dx, dy, dz = jx - ix, jy - iy, jz - iz
    mag = math.sqrt(dx**2 + dy**2 + dz**2)
    cos_theta_x, cos_theta_y, cos_theta_z = dx / mag, dy / mag, dz / mag
    return [cos_theta_x, cos_theta_y, cos_theta_z, mag]

# Calculate member global stiffness matrix
def calculateKg3D(memberNo):
    x, y, z, mag = memberOrientation3D(memberNo)
    K11 = (E * A / mag) * np.array([[x**2, x*y, x*z], [x*y, y**2, y*z], [x*z, y*z, z**2]])
    K12 = -K11
    return [K11, K12, K12.T, K11]

# Build the primary stiffness matrix, Kp
nDoF = np.amax(members) * 3
Kp = np.zeros((nDoF, nDoF))
for n, mbr in enumerate(members):
    K11, K12, K21, K22 = calculateKg3D(n + 1)
    node_i, node_j = mbr
    ia, ib = 3 * node_i - 3, 3 * node_i
    ja, jb = 3 * node_j - 3, 3 * node_j
    Kp[ia:ib, ia:ib] += K11
    Kp[ia:ib, ja:jb] += K12
    Kp[ja:jb, ia:ib] += K21
    Kp[ja:jb, ja:jb] += K22

# Extract structure stiffness matrix, Ks
restrainedIndex = [x - 1 for x in restrainedDoF]
Ks = np.delete(np.delete(Kp, restrainedIndex, axis=0), restrainedIndex, axis=1)

# Solve for displacements
forceVectorRed = np.delete(forceVector, restrainedIndex, axis=0)
U = np.linalg.inv(Ks) @ forceVectorRed

# Solve for reactions
UG = np.zeros(nDoF)
c = 0
for i in range(nDoF):
    if i in restrainedIndex:
        UG[i] = 0
    else:
        UG[i] = U[c]
        c += 1
FG = Kp @ UG

# Solve for member forces
mbrForces = []
for n, mbr in enumerate(members):
    node_i, node_j = mbr
    ia, ib = 3 * node_i - 3, 3 * node_i
    ja, jb = 3 * node_j - 3, 3 * node_j
    disp = UG[[ia, ia+1, ib-1, ja, ja+1, jb-1]]
    x, y, z, mag = memberOrientation3D(n + 1)
    T = np.array([[x, y, z, 0, 0, 0], [0, 0, 0, x, y, z]])
    F_axial = (E * A / mag) * (T @ disp)[1] - (T @ disp)[0]
    mbrForces.append(F_axial)

# Export deflected coordinates
exportDeflectionFactor = 100
newCoords = []
for n, node in enumerate(nodes):
    ix, iy, iz = 3 * n, 3 * n + 1, 3 * n + 2
    deflection = UG[[ix, iy, iz]] * exportDeflectionFactor
    newCoords.append(node + deflection)
with open("Deflected-Vertices.csv", "w") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(newCoords)

# Print results
print("REACTIONS")
for i in restrainedIndex:
    print(f"Reaction at DoF {i + 1}: {round(FG[i] / 1000, 2)} kN")

print("\nMEMBER FORCES")
for n, force in enumerate(mbrForces):
    node_i, node_j = members[n]
    print(f"Force in member {n + 1} (nodes {node_i} to {node_j}): {round(force / 1000, 2)} kN")
