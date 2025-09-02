import pyvista as pv

def plotDeflection(xMargin=1, yMargin=1, zMargin=0.5, elevation=30, rotation=210, scaleFactor=1):
    """
    Interactive 3D plot of the deflected shape using PyVista.
    """
    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Plot original and deflected members
    for mbr in members:
        node_i = mbr[0]  # Node i
        node_j = mbr[1]  # Node j
        
        # Original coordinates
        ix, iy, iz = nodes[node_i - 1]
        jx, jy, jz = nodes[node_j - 1]
        
        # Indices for the degrees of freedom
        ia = 6 * node_i - 6
        ib = 6 * node_i - 4
        ja = 6 * node_j - 6
        jb = 6 * node_j - 4
        
        # Deflected coordinates
        ix_def = ix + UG[ia, 0] * scaleFactor
        iy_def = iy + UG[ia + 1, 0] * scaleFactor
        iz_def = iz + UG[ib, 0] * scaleFactor
        jx_def = jx + UG[ja, 0] * scaleFactor
        jy_def = jy + UG[ja + 1, 0] * scaleFactor
        jz_def = jz + UG[jb, 0] * scaleFactor
        
        # Plot the original member in grey
        line_original = pv.Line([ix, iy, iz], [jx, jy, jz])
        plotter.add_mesh(line_original, color="grey", line_width=1)
        
        # Plot the deflected member in red
        line_deflected = pv.Line([ix_def, iy_def, iz_def], [jx_def, jy_def, jz_def])
        plotter.add_mesh(line_deflected, color="red", line_width=2)

    # Compute axis limits
    maxX, maxY, maxZ = nodes.max(axis=0)
    minX, minY, minZ = nodes.min(axis=0)

    # Center the camera on the structure
    center = [(minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2]
    plotter.camera_position = [
        [maxX + xMargin, maxY + yMargin, maxZ + zMargin],  # Camera location
        center,                                           # Focal point
        [0, 0, 1]                                         # Up direction
    ]
    
    # Add interactive axes and labels
    plotter.set_background("white")
    plotter.add_axes(interactive=True)
    plotter.add_text("Deflected Shape", position="upper_left", font_size=12, color="black")
    
    # Show the plot
    plotter.show()



def calculateKg3DBeam(memberNo):
    
    #Extract individual member properties
    A = Areas[memberNo-1]
    E = YoungMod[memberNo-1]
    L = lengths[memberNo-1]
    Iz = Izz[memberNo-1]
    Iy = Iyy[memberNo-1]
    G =  ShearMod[memberNo-1]
    J =  Ip[memberNo-1]
    
    Kl = np.zeros((12,12))
    #Row #1
    Kl[0,0] = E*A/L
    Kl[0,6] = -E*A/L
    #Row #2
    Kl[1,1] = 12*E*Iz/L**3
    Kl[1,5] = -6*E*Iz/L**2 
    Kl[1,7] = -12*E*Iz/L**3
    Kl[1,11] = -6*E*Iz/L**2
    #Row 3
    Kl[2,2] = 12*E*Iy/L**3 
    Kl[2,4] = 6*E*Iy/L**2 
    Kl[2,8] = -12*E*Iy/L**3 
    Kl[2,10] = 6*E*Iy/L**2
    #Row 4
    Kl[3,3] = G*J/L
    Kl[3,9] = -G*J/L
    #Row 5
    Kl[4,2] = 6*E*Iy/L**2
    Kl[4,4] = 4*E*Iy/L
    Kl[4,8] = -6*E*Iy/L**2
    Kl[4,10] = 2*E*Iy/L
    #Row 6
    Kl[5,1] = -6*E*Iz/L**2 
    Kl[5,5] = 4*E*Iz/L
    Kl[5,7] = 6*E*Iz/L**2
    Kl[5,11] = 2*E*Iz/L
    #Row 7
    Kl[6,0] = -E*A/L
    Kl[6,6] = E*A/L
    #Row 8
    Kl[7,1] = -12*E*Iz/L**3
    Kl[7,5] = 6*E*Iz/L**2
    Kl[7,7] = 12*E*Iz/L**3
    Kl[7,11] = 6*E*Iz/L**2
    #Row 9
    Kl[8,2] = -12*E*Iy/L**3
    Kl[8,4] = -6*E*Iy/L**2
    Kl[8,8] = 12*E*Iy/L**3
    Kl[8,10] = -6*E*Iy/L**2
    #Row 10
    Kl[9,3] = -G*J/L
    Kl[9,9] = G*J/L
    #Row 11
    Kl[10,2] = 6*E*Iy/L**2 
    Kl[10,4] = 2*E*Iy/L
    Kl[10,8] = -6*E*Iy/L**2
    Kl[10,10] = 4*E*Iy/L
    #Row 12
    Kl[11,1] = -6*E*Iz/L**2
    Kl[11,5] = 2*E*Iz/L
    Kl[11,7] = 6*E*Iz/L**2
    Kl[11,11] = 4*E*Iz/L
    
    #Build the full transformation matrix for this element
    TM = np.zeros((12,12))
    T_repeat = TransformationMatrices[memberNo-1,:,:]
    TM[0:3,0:3] = T_repeat
    TM[3:6,3:6] = T_repeat
    TM[6:9,6:9] = T_repeat
    TM[9:12,9:12] = T_repeat
    
    #Calculate the global element stiffness matrix
    Kg = TM.T.dot(Kl).dot(TM)
    
    K11g = Kg[0:6,0:6]
    K12g = Kg[0:6,6:12]
    K21g = Kg[6:12,0:6]
    K22g = Kg[6:12,6:12]
    
    return [K11g, K12g, K21g, K22g]


def buildLocalRF(memberNo):
    """
    For non-vertical members, the local x-y plane is determined by offsetting 
    the mid-point of the member vertically by +1m in the positive global z-direction.  
    
    For vertical members, the local x-y plan is determined by offsetting 
    the mid-point of the member by -1m in the negative global x-direction.
    
    Note that for all members: 
    - the local z-axis will be assumed to be the major principle axis
    - the local y-axis will be assumed to be the minor principle axis
    """
    
    memberIndex = memberNo -1 #Index identifying the member in the array of members
    node_i = members[memberIndex][0] #Node number for node i of this member    
    node_j = members[memberIndex][1] #Node number for node j of this member
    
    #Nodal coordinates
    ix = nodes[node_i-1][0]
    iy = nodes[node_i-1][1]
    iz = nodes[node_i-1][2]
    jx = nodes[node_j-1][0]
    jy = nodes[node_j-1][1]
    jz = nodes[node_j-1][2]
    
    #Member length
    dx = jx-ix #x-component of vector along member
    dy = jy-iy #y-component of vector along member
    dz = jz-iz #z-component of vector along member
    length = math.sqrt(dx**2 + dy**2 + dz**2) #Length if member
    
    if(abs(dx)<0.001 and abs(dy)<0.001):
        #Member is vertical - offset in negative global x to define local x-y plane
        i_offset = np.array([ix-1, iy, iz]) #Offset node i by 1m in negative global x-direction
        j_offset = np.array([jx-1, jy, jz]) #Offset node j by 1m in negative global x-direction
    else:
        #Member is not vertical - offset in positive global z to define local x-y plane
        i_offset = np.array([ix, iy, iz+1]) #Offset node i by 1m in positive global z-direction
        j_offset = np.array([jx, jy, jz+1]) #Offset node j by 1m in positive global z-direction
    node_k = i_offset + 0.5*(j_offset-i_offset) #Point in the local x-y plane
    
    #Local x-vector in the global reference frame running along the member
    local_x_vector = nodes[node_j-1] - nodes[node_i-1] #Vector along local x-axis
    local_x_unit = local_x_vector/length #Local unit vector defining local x-axis
    
    #Local y-vector in the global reference frame using Gram-Schmidt process
    vector_in_plane = node_k-nodes[node_i-1] #Vector in local x-y plane
    local_y_vector = vector_in_plane - np.dot(vector_in_plane,local_x_unit)*local_x_unit #local y-vector in global RF (Gram-Schmidt)
    magY = math.sqrt(local_y_vector[0]**2 + local_y_vector[1]**2+local_y_vector[2]**2) #Length of local y-vector
    local_y_unit = local_y_vector/magY #Local unit vector defining the local y-axis
    
    #Local z-vector in global RF using matrix cross product
    local_z_unit = np.cross(local_x_unit, local_y_unit) #Local unit vector defining the local z-axis
    
    #Combine reference frame into a standard rotation matrix for the element x,y,z => columns 1,2,3
    rotationMatrix = np.array([local_x_unit, local_y_unit, local_z_unit,]).T
    
    return [length, rotationMatrix]    


def plotStructure(label_offset=0.01, xMargin=1, yMargin=1, zMargin=1, elevation=30, rotation=210):
    """
    Interactive 3D structure visualization using PyVista.
    """
    # Create a PyVista plotter
    plotter = pv.Plotter()
    
    # Plot members (edges)
    for mbr in members:
        node_i = mbr[0]  # Node i
        node_j = mbr[1]  # Node j
        
        # Coordinates for the nodes
        ix, iy, iz = nodes[node_i-1]
        jx, jy, jz = nodes[node_j-1]
        
        # Create a line between the two nodes
        line = pv.Line([ix, iy, iz], [jx, jy, jz])
        plotter.add_mesh(line, color="blue", line_width=2)
    
    # Plot nodes
    for n, node in enumerate(nodes):
        x, y, z = node
        # Add points for nodes
        plotter.add_mesh(pv.Sphere(center=(x, y, z), radius=0.02), color="red")
        # Add labels near each node
        label_position = (x + label_offset, y + label_offset, z + label_offset)
        plotter.add_point_labels(np.array([label_position]), [str(n+1)], font_size=14, point_color="black")
    
    # Adjust camera view
    maxX, maxY, maxZ = nodes.max(axis=0)
    minX, minY, minZ = nodes.min(axis=0)
    
    # Center the camera on the structure
    center = [(minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2]
    plotter.camera_position = [
        [maxX + xMargin, maxY + yMargin, maxZ + zMargin],  # Camera location
        center,                                           # Focal point
        [0, 0, 1]                                         # Up direction
    ]
    
    # Add labels and axes
    plotter.set_background("white")
    plotter.add_axes(interactive=True)
    plotter.add_text("Interactive 3D Structure", position="upper_left", font_size=12, color="black")
    
    # Show the plot in an interactive window
    plotter.show()



import math
import copy
import csv
import numpy as np
from glob import glob
import matplotlib.colors
from numpy import genfromtxt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

nodes = genfromtxt('data/Vertices.csv', delimiter=',') 

members = genfromtxt('data/Edges.csv', delimiter=',')
members = np.int_(members) 

restraintNodes = genfromtxt('data/Restraint-Nodes.csv', delimiter=',')

restraintData = genfromtxt('data/Restraint-DoF.csv', delimiter=',')
restraintData = np.int_(restraintData) #Convert members definitions from float to int
flatData = restraintData.flatten() #Flatten DoF data
restrainedDoF = flatData[np.nonzero(flatData)[0]].tolist() #Remove zeros from DoF data


forceLocationData = genfromtxt('data/Force-Data.csv', delimiter=',')
forceLocationData = np.int_(forceLocationData) #Convert from float to int

A_beam = 0.027385 #(m^2)
A_bar = 0.01 #(m^2)
YoungMod = 200*10**9 * np.ones([len(members)]) #(N/m^2)
ShearMod = 200*10**9 * np.ones([len(members)]) #(N/m^2)
Izz = 250*10**-6 * np.ones([len(members)]) #(m^4)
Iyy = 100*10**-6 * np.ones([len(members)]) #(m^4)
Ip = (Izz+Iyy) * np.ones([len(members)]) #(m^4)
P = -1000 #(N) Point load magnitude (and direction via sign)
pointLoadAxis = 'z' #The GLOBAL axis along which point loads are applied

# =============================================================================
# Making member areas 
# =============================================================================

Areas = A_beam*np.ones([len(members)]) #Initialise all member areas to beam area


rotationMatrices = np.empty((len(members),3,3)) #Initialise data holder
lengths = np.zeros(len(members))

for n, mbr in enumerate(members):
    
    #Calculate the rotation matrix that defines the member orientation
    [length, rotationMatrix] = buildLocalRF(n+1)
    
    #Store rotation matrix and length
    rotationMatrices[n,:,:] = rotationMatrix
    lengths[n] = length        

#Calculate the transformation matrix for each member
TransformationMatrices = np.empty((len(members),3,3)) #Initialise data holder

for n, mbr in enumerate(members):
    rMatrix = rotationMatrices[n,:,:] #Default orientation rotation matrix for this members
    TransformationMatrices[n,:,:] = rMatrix.T #For convenience, store transformation matrix directly
    
    #Initialise an empty force (& moment) vector
forceVector = np.array([np.zeros(len(nodes)*6)]).T 

#Add point loads to force vector
if(len(forceLocationData)>0):      
    #Split force location data (index starting at 0)
    forcedNodes = forceLocationData[:,0]
    xForceIndices = forceLocationData[:,1]
    yForceIndices = forceLocationData[:,2]
    zForceIndices = forceLocationData[:,3]
    xMomentIndices = forceLocationData[:,4]
    yMomentIndices = forceLocationData[:,5]
    zMomentIndices = forceLocationData[:,6]

    #Assign forces to degrees of freedom
    if(pointLoadAxis=='x'):
        forceVector[xForceIndices] = P 
    elif(pointLoadAxis=='y'):
        forceVector[yForceIndices] = P 
    else:
        forceVector[zForceIndices] = P 
        
nDoF = np.amax(members)*6 #The total number of degrees of freedom in the problem
Kp = np.zeros([nDoF,nDoF]) #Initialise the primary stiffness matrix

for n, mbr in enumerate(members):
    node_i = mbr[0] #Node number for node i of this member    
    node_j = mbr[1] #Node number for node j of this member
    
    [K11, K12, K21, K22] = calculateKg3DBeam(n+1)
    #Primary stiffness matrix indices associated with each node
    ia = 6*node_i-6 #index 0 (e.g. node 1)
    ib = 6*node_i-1 #index 5 (e.g. node 1)
    ja = 6*node_j-6 #index 6 (e.g. node 2)
    jb = 6*node_j-1 #index 11 (e.g. node 2)
    
    Kp[ia:ib+1, ia:ib+1] = Kp[ia:ib+1, ia:ib+1] + K11
    Kp[ia:ib+1, ja:jb+1] = Kp[ia:ib+1, ja:jb+1] + K12
    Kp[ja:jb+1, ia:ib+1] = Kp[ja:jb+1, ia:ib+1] + K21
    Kp[ja:jb+1, ja:jb+1] = Kp[ja:jb+1, ja:jb+1] + K22   

#Remove restrained degrees of freedom
removedDoF = restrainedDoF #(later we'll add in pinned DoF here)
removedIndex = [x-1 for x in removedDoF] #Index for each removed DoF

#Reduce to structure stiffness matrix by deleting rows and columns for removed DoF
Ks = np.delete(Kp,removedIndex,0) #Delete rows
Ks = np.delete(Ks,removedIndex,1) #Delete columns
Ks = np.matrix(Ks)

forceVectorRed = copy.copy(forceVector)
forceVectorRed = np.delete(forceVectorRed,removedIndex,0) #Delete rows corresponding to restrained DoF
U = Ks.I*forceVectorRed

#Construct global displacement vector
UG = np.zeros(nDoF) #Initialise an array to hold the global displacement vector
c=0 #Initialise a counter to track how many restraints have been imposed

for i in np.arange(nDoF):
    if i in removedIndex:
        #Impose zero displacement
        UG[i] = 0
    else:
        #Assign actual displacement
        UG[i] = U[c]
        c=c+1
        
UG = np.array([UG]).T
FG = np.matmul(Kp,UG)

mbrForceX = np.array([]) #Initialise an array to hold member axial forces
mbrForceY = np.zeros(members.shape) #Initialise an array to hold member shear forces
mbrForceZ = np.zeros(members.shape) #Initialise an array to hold member transverse forces
mbrMomentX = np.zeros(members.shape) #Initialise an array to hold member torsional moments
mbrMomentY = np.zeros(members.shape) #Initialise an array to hold member minor axis moments
mbrMomentZ = np.zeros(members.shape) #Initialise an array to hold member major axis moments

for n,mbr in enumerate(members):  

    #Extract individual member properties
    A = Areas[n]
    E = YoungMod[n]
    L = lengths[n]
    Iz = Izz[n]
    Iy = Iyy[n]
    G =  ShearMod[n]
    J =  Ip[n]
    
    node_i = mbr[0] #Node number for node i of this member    
    node_j = mbr[1] #Node number for node j of this member

    #Primary stiffness matrix indices associated with each node
    ia = 6*node_i-6 #index 0 (e.g. node 1)
    ib = 6*node_i-1 #index 5 (e.g. node 1)
    ja = 6*node_j-6 #index 6 (e.g. node 2)
    jb = 6*node_j-1 #index 11 (e.g. node 2)
    
    #Build the full transformation matrix for this element
    TM = np.zeros((12,12))
    T_repeat = TransformationMatrices[n,:,:]
    TM[0:3,0:3] = T_repeat
    TM[3:6,3:6] = T_repeat
    TM[6:9,6:9] = T_repeat
    TM[9:12,9:12] = T_repeat
    
    disp = np.array([[ UG[ia,0],
                       UG[ia+1,0],
                       UG[ia+2,0],
                       UG[ia+3,0],
                       UG[ia+4,0],
                       UG[ib,0],
                       UG[ja,0],
                       UG[ja+1,0],
                       UG[ja+2,0],
                       UG[ja+3,0],
                       UG[ja+4,0],
                       UG[jb,0]]]).T
    
    disp_local = np.matmul(TM,disp)
    
    F_axial = (A*E/L)*(disp_local[6] - disp_local[0])[0]
    
    #Caclulate the quadrants of the global stiffness matrix for the member
    [K11, K12, K21, K22] = calculateKg3DBeam(n+1)
    top = np.concatenate((K11,K12),axis=1) #Top 6 rows
    btm = np.concatenate((K21,K22),axis=1) #Bottom 6 rows
    Kg = np.concatenate((top,btm), axis=0) #Full global stiffness matrix
    
    #Convert back to local stiffness matrix
    Kl = TM.dot(Kg).dot(TM.T)
    
    #Compute moments at each end of the member
    Mix = Kl[3,:].dot(disp_local)[0]
    Mjx = Kl[9,:].dot(disp_local)[0]
    
    Miy = Kl[4,:].dot(disp_local)[0]
    Mjy = Kl[10,:].dot(disp_local)[0]
    
    Miz = Kl[5,:].dot(disp_local)[0]
    Mjz = Kl[11,:].dot(disp_local)[0]
    
    #Compute shear forces at each end of the member
    Fy_i = Kl[1,:].dot(disp_local)[0]
    Fy_j = Kl[7,:].dot(disp_local)[0]
    
    Fz_i = Kl[2,:].dot(disp_local)[0]
    Fz_j = Kl[8,:].dot(disp_local)[0]
    
    #Store member actions
    mbrForceX = np.append(mbrForceX,F_axial)
    mbrForceY[n,0] = Fy_i
    mbrForceY[n,1] = Fy_j    
    mbrForceZ[n,0] = Fz_i
    mbrForceZ[n,1] = Fz_j     
    mbrMomentX[n,0] = Mix
    mbrMomentX[n,1] = Mjx
    mbrMomentY[n,0] = Miy
    mbrMomentY[n,1] = Mjy
    mbrMomentZ[n,0] = Miz
    mbrMomentZ[n,1] = Mjz  

plotDeflection(
    xMargin=1,
    yMargin=1,
    zMargin=0.5,
    elevation=30,
    rotation=210,
    scaleFactor=500
)
