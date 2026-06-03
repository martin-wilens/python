import fresnel
import numpy as np
import PIL.Image

# 1. Initialize the Device and Scene
device = fresnel.Device()
scene = fresnel.Scene(device)

# ---------------------------------------------------------
# 2. Geometry: 7 Spheres with distinct material tracking
# ---------------------------------------------------------
sphere_positions = [
    # Top Row (on the back step)
    [-2.4,  0.5, -1.0],  # 1. Clear Glass / Refractive
    [-1.0,  1.5, -1.0],  # 2. Rough Frosted Glass
    [ 1.0,  1.5, -1.0],  # 3. Smooth Orange Plastic
    [ 3.0,  1.5, -1.0],  # 4. Perfect Chrome Mirror
    # Bottom Row (on the front floor)
    [-2.0, -0.5,  1.0],  # 5. Velvet / Deep Cyan Absorptive
    [ 0.0, -0.5,  1.0],  # 6. Thin Soap Bubble
    [ 2.0, -0.5,  1.0]   # 7. Rough Red Wood
]

materials = [
    fresnel.material.Material(color=fresnel.color.linear([0.9, 0.9, 0.9]), roughness=0.0, specular=0.9, metal=0.0),
    fresnel.material.Material(color=fresnel.color.linear([0.8, 0.8, 0.8]), roughness=0.6, specular=0.7, metal=0.0),
    fresnel.material.Material(color=fresnel.color.linear([0.8, 0.3, 0.0]), roughness=0.1, specular=0.5, metal=0.0),
    fresnel.material.Material(color=fresnel.color.linear([0.9, 0.9, 0.9]), roughness=0.0, specular=1.0, metal=1.0),
    fresnel.material.Material(color=fresnel.color.linear([0.0, 0.1, 0.1]), roughness=0.9, specular=0.1, metal=0.0),
    fresnel.material.Material(color=fresnel.color.linear([1.0, 1.0, 1.0]), roughness=0.0, specular=1.0, metal=0.0),
    fresnel.material.Material(color=fresnel.color.linear([0.4, 0.15, 0.15]), roughness=0.5, specular=0.3, metal=0.0)
]

# Generate each sphere independently with its unique material properties
for pos, mat in zip(sphere_positions, materials):
    single_sphere = fresnel.geometry.Sphere(scene, N=1, radius=0.9)
    single_sphere.position[:] = [pos]
    single_sphere.material = mat

# ---------------------------------------------------------
# 3. Geometry: Solid Step Benches (Using ConvexPolyhedron properly)
# ---------------------------------------------------------
# Step A: Front Lower Platform (Scaling dimensions: width=10.0, height=0.1, depth=6.0)
front_cube_vertices = np.array([
    [-5.0, -0.05, -3.0], [-5.0, -0.05,  3.0], [-5.0,  0.05, -3.0], [-5.0,  0.05,  3.0],
    [ 5.0, -0.05, -3.0], [ 5.0, -0.05,  3.0], [ 5.0,  0.05, -3.0], [ 5.0,  0.05,  3.0]
])
# Process the vertex bounds into the required dictionary layout
front_info = fresnel.util.convex_polyhedron_from_vertices(front_cube_vertices)

# Step B: Back Raised Step (Scaling dimensions: width=10.0, height=1.2, depth=4.0)
back_cube_vertices = np.array([
    [-5.0, -0.6, -2.0], [-5.0, -0.6,  2.0], [-5.0,  0.6, -2.0], [-5.0,  0.6,  2.0],
    [ 5.0, -0.6, -2.0], [ 5.0, -0.6,  2.0], [ 5.0,  0.6, -2.0], [ 5.0,  0.6,  2.0]
])
back_info = fresnel.util.convex_polyhedron_from_vertices(back_cube_vertices)

# Step wood material configuration
wood_mat = fresnel.material.Material(
    color=fresnel.color.linear([0.45, 0.25, 0.1]), 
    roughness=0.4, 
    specular=0.2
)

# Instantiate the objects using the structured dictionary parameters
front_floor = fresnel.geometry.ConvexPolyhedron(scene, polyhedron_info=front_info, N=1)
front_floor.position[:] = [[0.0, -1.4, 1.0]]
front_floor.material = wood_mat

back_step = fresnel.geometry.ConvexPolyhedron(scene, polyhedron_info=back_info, N=1)
back_step.position[:] = [[0.0, -0.8, -3.0]]
back_step.material = wood_mat

# ---------------------------------------------------------
# 4. Environment & Camera Settings
# ---------------------------------------------------------
scene.lights = fresnel.light.cloudy()
for light in scene.lights:
    light.direction = light.direction  # Keep directions
    # Multiply the light brightness to illuminate the dark faces
    light.color = (light.color[0] * 2.5, light.color[1] * 2.5, light.color[2] * 2.5)

scene.camera = fresnel.camera.Perspective(
    position=[0.0, 3.5, 9.0],
    look_at=[0.0, 0.4, 0.5],
    up=[0.0, 1.0, 0.0],
    height=2.3
)

scene.background_color = fresnel.color.linear([0.4, 0.55, 0.7]) # Soft sky blue
scene.background_alpha = 1.0  # Make it fully opaque instead of transparent white

# ---------------------------------------------------------
# 5. Render and Save
# ---------------------------------------------------------
out = fresnel.pathtrace(scene, samples=2560,light_samples=64, w=1680, h=1050)
image = PIL.Image.fromarray(out[:], mode='RGBA')
image.save('fresnel_materials_render.png')
print("Render saved successfully as 'fresnel_materials_render.png'!")

