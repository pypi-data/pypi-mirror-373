try:
    from ...IO.structure_handling_tools.AtomPosition import AtomPosition
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys
    
try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import subprocess
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing subprocess: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class Blender_builder(BasePartition):
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """
        super().__init__(name=name, file_location=file_location, *args, **kwargs)

    def get_blender_str(self, atomPositions, atomLabelsList, uniqueAtomLabels, latticeVectors,
                        atomCount, colors, radii, conection, fog, path,
                        scale, camera, samples, resolution_x, resolution_y,
                        hdri_path, depth_of_field, emission_strength):
        
        atomPositions = np.array(atomPositions)
        atomLabelsList = np.array(atomLabelsList)
        uniqueAtomLabels = np.array(uniqueAtomLabels)
        latticeVectors = np.array(latticeVectors)

        camera_X, camera_Y, camera_Z = 'x' in camera, 'y' in camera, 'z' in camera

        self.blender_script = f"""
import bpy
import numpy as np
from mathutils import Vector

def create_object_instance(original, location=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
    instance = bpy.data.objects.new(name=original.name + "_instance", object_data=original.data)
    instance.location = location
    instance.rotation_euler = rotation
    instance.scale = scale
    bpy.context.collection.objects.link(instance)
    return instance

def align_object_between_points(obj, start_point, end_point):
    direction = end_point - start_point
    midpoint = start_point + direction / 2
    obj.location = midpoint
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    obj.scale[2] = direction.length / 2

def setup_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    sphere_original = {{}}
    cylinder_original = {{}}
    for label in uniqueAtomLabels:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radii[label]*0.88)
        sphere_original[label] = bpy.context.object
        sphere_original[label].name = f'sphere_label_{{label}}'
        bpy.ops.object.shade_smooth()

        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=2)
        cylinder_original[label] = bpy.context.object
        cylinder_original[label].name = f'cylinder_label_{{label}}'
        bpy.ops.object.shade_smooth()

    for i, n in enumerate(atomPositions):
        loc = (n[0], n[1], n[2])
        sphere_instance = create_object_instance(sphere_original[atomLabelsList[i]], location=loc)

    for [A, B] in conection:
        cylinder_instance_A = create_object_instance(cylinder_original[atomLabelsList[A]])
        cylinder_instance_B = create_object_instance(cylinder_original[atomLabelsList[B]])
        
        midpoint = Vector((np.array(atomPositions[A]) + np.array(atomPositions[B]))/2)
        
        align_object_between_points(cylinder_instance_A, Vector(atomPositions[A]), midpoint)
        align_object_between_points(cylinder_instance_B, midpoint, Vector(atomPositions[B]))

    return sphere_original, cylinder_original

def create_material(name, base_color, metallic=0.7, specular=0.9, roughness=0.5, emission_strength=0):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Limpiar nodos existentes
    for node in nodes:
        nodes.remove(node)
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_mix = nodes.new(type='ShaderNodeMixShader')
    
    node_principled.inputs['Base Color'].default_value = base_color + (1,) if len(base_color) == 3 else base_color
    node_principled.inputs['Metallic'].default_value = metallic
    #node_principled.inputs['Specular'].default_value = specular
    node_principled.inputs['Roughness'].default_value = roughness
    
    node_emission.inputs['Color'].default_value = base_color + (1,) if len(base_color) == 3 else base_color
    node_emission.inputs['Strength'].default_value = emission_strength
    
    node_mix.inputs[0].default_value = min(emission_strength, 1)
    
    links.new(node_principled.outputs['BSDF'], node_mix.inputs[1])
    links.new(node_emission.outputs['Emission'], node_mix.inputs[2])
    links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])
    
    return material

def setup_lighting():
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()
    
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
    sun = bpy.context.object
    sun.data.energy = 5
    sun.data.angle = np.radians(30)

    bpy.ops.object.light_add(type='AREA', location=(-5, 5, 5))
    area = bpy.context.object
    area.data.energy = 100
    area.data.size = 5

def setup_background(color=(0.377116, 0.377116, 0.377116, 1)):
    world = bpy.context.scene.world
    world.use_nodes = True
    node_tree = world.node_tree

    # Eliminar todos los nodos existentes
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)
    
    # Crear un nodo de fondo simple
    node_background = node_tree.nodes.new(type='ShaderNodeBackground')
    node_output = node_tree.nodes.new(type='ShaderNodeOutputWorld')
    
    # Configurar el color y la intensidad del fondo
    node_background.inputs['Color'].default_value = color
    node_background.inputs['Strength'].default_value = 4.0  # Intensidad de 2
    
    # Conectar el nodo de fondo a la salida
    node_tree.links.new(node_background.outputs['Background'], node_output.inputs['Surface'])
    
    bpy.context.scene.render.film_transparent = True

def setup_orthographic_cameras(lattice_vectors, look_at_point):
    corners = [np.dot(np.array([x, y, z]), lattice_vectors) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    center = look_at_point
    distance = np.max(np.ptp(corners, axis=0)) * 2.5
    
    ortho_scales = {{
        'x': np.max([np.ptp(corners, axis=0)[1], np.ptp(corners, axis=0)[2]]) * 1.05 * {scale},
        'y': np.max([np.ptp(corners, axis=0)[0], np.ptp(corners, axis=0)[2]]) * 1.05 * {scale},
        'z': np.max([np.ptp(corners, axis=0)[0], np.ptp(corners, axis=0)[1]]) * 1.05 * {scale},
    }}

    camera_positions = {{}}

    if {camera_X}:
        camera_positions['Camera_X'] = (center[0] + distance, center[1], center[2])
    if {camera_Y}:
        camera_positions['Camera_Y'] = (center[0], center[1] + distance, center[2])
    if {camera_Z}:
        camera_positions['Camera_Z'] = (center[0], center[1], center[2] + distance)

    for camera, pos in camera_positions.items():
        axis = camera[-1].lower()
        ortho_scale = ortho_scales[axis]
        add_camera(camera, pos, center, ortho_scale, scale='orthographic')

def add_camera(name, location, look_at_point, ortho_scale, scale='orthographic', depth_of_field:bool=False):
    bpy.ops.object.camera_add(location=Vector(location))
    camera = bpy.context.object
    camera.name = name
    
    if scale == 'orthographic':
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = ortho_scale
    
    direction = Vector(look_at_point) - Vector(location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Añadir profundidad de campo
    if depth_of_field:
        camera.data.dof.use_dof = True
        empty = bpy.data.objects.new("DofEmpty", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = look_at_point
        camera.data.dof.focus_object = empty
        camera.data.dof.aperture_fstop = {depth_of_field}

def setup_compositing_nodes():
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)
    
    render_layers = tree.nodes.new('CompositorNodeRLayers')
    viewer = tree.nodes.new('CompositorNodeViewer')
    comp = tree.nodes.new('CompositorNodeComposite')

    glare = tree.nodes.new('CompositorNodeGlare')
    glare.glare_type = 'FOG_GLOW'
    glare.mix = 0.5
    glare.threshold = 0.8
    
    #color_correction = tree.nodes.new('CompositorNodeColorCorrection')
    #color_correction.master_saturation = 1.2
    #color_correction.master_contrast = 1.1
    
    #tree.links.new(render_layers.outputs[0], glare.inputs[0])
    #tree.links.new(glare.outputs[0], color_correction.inputs[0])
    #tree.links.new(color_correction.outputs[0], viewer.inputs[0])
    #tree.links.new(color_correction.outputs[0], comp.inputs[0])

def high_quality_render_settings():
    bpy.context.scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons['cycles'].preferences
    
    try:
        cycles_prefs.compute_device_type = 'CUDA'
    except:
        pass

    for device in cycles_prefs.devices:
        if device.type == 'CUDA':
            device.use = True
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = {samples}
    bpy.context.scene.render.resolution_x = {resolution_x}
    bpy.context.scene.render.resolution_y = {resolution_y}
    bpy.context.scene.cycles.use_denoising = True
    try:
        bpy.context.scene.cycles.denoiser = 'OPTIX'
    except:
        try:
            bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        except: pass

def add_fog():
    bpy.ops.mesh.primitive_cube_add(size=20, location=(0, 0, 0))
    cube = bpy.context.object
    cube.name = 'FogVolume'

    mat_fog = bpy.data.materials.new(name="FogMaterial")
    cube.data.materials.append(mat_fog)
    mat_fog.use_nodes = True
    nodes = mat_fog.node_tree.nodes

    for node in nodes:
        nodes.remove(node)

    volume_shader = nodes.new(type='ShaderNodeVolumePrincipled')
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    
    noise_tex.inputs['Scale'].default_value = 5.0
    volume_shader.inputs['Density'].default_value = 0.01
    
    mat_fog.node_tree.links.new(noise_tex.outputs['Fac'], volume_shader.inputs['Density'])
    mat_fog.node_tree.links.new(volume_shader.outputs['Volume'], output_node.inputs['Volume'])

def draw_lattice_edges(lattice_vectors, edge_radius=0.01, edge_color=(0.5, 0.5, 0.5, 1)):
    edge_material = create_material("EdgeMaterial", edge_color, metallic=0.8, roughness=0.2)

    corners = [np.dot(np.array([x, y, z]), lattice_vectors) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    edges = [(0, 1), (1, 3), (3, 2), (2, 0), 
             (4, 5), (5, 7), (7, 6), (6, 4),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    
    for start, end in edges:
        start_point = corners[start]
        end_point = corners[end]
        midpoint = (np.array(start_point) + np.array(end_point)) / 2
        length = np.linalg.norm(np.array(start_point) - np.array(end_point))
        
        bpy.ops.mesh.primitive_cylinder_add(radius=edge_radius, depth=length, location=midpoint)
        cylinder = bpy.context.object

        direction = np.array(end_point) - np.array(start_point)
        rot_axis = np.cross([0, 0, 1], direction)
        if np.linalg.norm(rot_axis) != 0:
            rot_angle = np.arccos(np.dot([0, 0, 1], direction) / np.linalg.norm(direction))
            cylinder.rotation_mode = 'AXIS_ANGLE'
            cylinder.rotation_axis_angle = [rot_angle] + list(rot_axis)
        else:
            if np.allclose(direction, [0, 0, -1]):
                cylinder.rotation_euler = [np.pi, 0, 0]

        if cylinder.data.materials:
            cylinder.data.materials[0] = edge_material
        else:
            cylinder.data.materials.append(edge_material)

atomPositions = {np.array(atomPositions).tolist()}
atomLabelsList = {np.array(atomLabelsList).tolist()}
uniqueAtomLabels = {np.array(uniqueAtomLabels).tolist()}
lattice_vectors = {np.array(latticeVectors).tolist()}
atomCount = {atomCount}
colors = {colors}
radii = {radii}
conection = {conection}

sphere_original, cylinder_original = setup_scene()

material_sphere = {{label: create_material(f'SphereMaterial_{{label}}', colors[label], emission_strength={emission_strength}) for label in uniqueAtomLabels}}
material_cylinder = {{label: create_material(f'CylinderMaterial_{{label}}', colors[label]) for label in uniqueAtomLabels}}

for obj in bpy.context.scene.objects:
    for label in uniqueAtomLabels:
        if "sphere" in obj.name.lower() and f'label_{{label.lower()}}' in obj.name.lower():
            if obj.data.materials:
                obj.data.materials[0] = material_sphere[label]
            else:
                obj.data.materials.append(material_sphere[label])
            break
        
        elif "cylinder" in obj.name.lower() and f'label_{{label.lower()}}' in obj.name.lower():
            if obj.data.materials:
                obj.data.materials[0] = material_cylinder[label]
            else:
                obj.data.materials.append(material_cylinder[label])
            break

for label in uniqueAtomLabels:
    sphere_original[label].hide_render = True
    sphere_original[label].hide_viewport = True
    cylinder_original[label].hide_render = True
    cylinder_original[label].hide_viewport = True

draw_lattice_edges(lattice_vectors)

setup_lighting()
setup_background()
setup_orthographic_cameras(lattice_vectors, np.mean(atomPositions, axis=0))
setup_compositing_nodes()
high_quality_render_settings()

if {fog}:
    add_fog()

def render_scene(camera_name, output_path):
    bpy.context.scene.camera = bpy.data.objects[camera_name]
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

cameras = [camera for camera, flag in zip(['Camera_X', 'Camera_Y', 'Camera_Z'], [{camera_X}, {camera_Y}, {camera_Z}]) if flag]
for camera in cameras:
    output_path = f"{path}_{{camera}}.png"
    render_scene(camera, output_path)
"""
        return self.blender_script

    def handleBLENDER(self, values: list):
        """
        Handle BLENDER rendering tasks for each container based on the 'values' dictionary.

        This function processes each 'plot' in 'values'. If the plot is 'RENDER', it creates
        a supercell of the atomic positions (if requested) and then generates a Blender script
        to render the resulting structure.

        Default values are assigned to any parameters that are missing or None in 'values[plot]'.
        """

        import numpy as np
        import subprocess

        def _generate_supercell(APM, repeat: np.array = np.array([1, 1, 1], dtype=np.int64)):
            """
            Create a supercell by repeating the base cell in ±repeat directions.
            Modifies APM in place and returns it.
            """
            a, b, c = APM.latticeVectors
            nx, ny, nz = repeat
            displacement_vectors = [
                a * i + b * j + c * k
                for i in range(-nx, nx + 1)
                for j in range(-ny, ny + 1)
                for k in range(-nz, nz + 1)
            ]
            atom_positions = np.array(APM.atomPositions)
            supercell_positions = np.vstack([atom_positions + dv for dv in displacement_vectors])

            supercell_atomLabelsList = np.tile(
                APM.atomLabelsList, (nx * 2 + 1) * (ny * 2 + 1) * (nz * 2 + 1)
            )
            supercell_atomicConstraints = np.tile(
                APM.atomicConstraints, ((nx * 2 + 1) * (ny * 2 + 1) * (nz * 2 + 1), 1)
            )

            APM._atomLabelsList = supercell_atomLabelsList
            APM._atomicConstraints = supercell_atomicConstraints
            APM._atomPositions = supercell_positions
            APM._latticeVectors *= np.array(repeat * 2 + 1)[:, np.newaxis]

            # Invalidate any cached derived data
            APM._atomPositions_fractional = None
            APM._atomCount = None
            APM._atomCountByType = None
            APM._fullAtomLabelString = None
            return APM

        # Process the plots given
        for plot in values:
            # Only handle 'RENDER' plots
            if plot.upper() == "RENDER":
                # Ensure values[plot] is a dictionary
                render_data = values[plot] if isinstance(values[plot], dict) else {}

                # Set default parameters if missing or None
                # You can adjust these defaults as appropriate
                render_data.setdefault("repeat", [1, 1, 1])
                render_data.setdefault("sigma", 0.1)
                render_data.setdefault("fog", True)
                render_data.setdefault("resolution_x", 1920)
                render_data.setdefault("resolution_y", 1080)
                render_data.setdefault("samples", 128)
                render_data.setdefault("camera", "default_cam")
                render_data.setdefault("scale", 1.0)
                render_data.setdefault("hdri_path", "")
                render_data.setdefault("depth_of_field", 0.1)
                render_data.setdefault("emission_strength", 0.5)
                render_data.setdefault("render", True)
                render_data.setdefault("verbose", True)

                # Apply to each container
                for container_index, container in enumerate(self.containers):
                    # Optionally build a supercell if desired
                    repeat_array = np.array(render_data["repeat"], dtype=np.int64)
                    container.AtomPositionManager = _generate_supercell(
                        container.AtomPositionManager, repeat=repeat_array
                    )

                    # Generate the Blender script
                    blender_str = self.get_blender_str(
                        atomPositions=container.AtomPositionManager.atomPositions,
                        atomLabelsList=container.AtomPositionManager.atomLabelsList,
                        uniqueAtomLabels=container.AtomPositionManager.uniqueAtomLabels,
                        latticeVectors=container.AtomPositionManager.latticeVectors,
                        atomCount=container.AtomPositionManager.atomCount,
                        colors=container.AtomPositionManager.element_colors,
                        radii=container.AtomPositionManager.atomic_radii_empirical,
                        conection=container.AtomPositionManager.get_connection_list(
                            sigma=render_data["sigma"], periodic=False
                        ),
                        fog=render_data["fog"],
                        path=f'blender_plot_{container_index}_',
                        resolution_x=render_data["resolution_x"],
                        resolution_y=render_data["resolution_y"],
                        samples=render_data["samples"],
                        camera=render_data["camera"],
                        scale=render_data["scale"],
                        hdri_path=render_data["hdri_path"],
                        depth_of_field=render_data["depth_of_field"],
                        emission_strength=render_data["emission_strength"],
                    )

                    # Write the script to file
                    blender_script_name = f"blender_script_{container_index}.py"
                    with open(blender_script_name, "w") as file:
                        file.write(blender_str)

                    # Print info if verbose
                    if render_data["verbose"]:
                        print(f">> Blender script saved to {blender_script_name}")

                    # If 'render' is True, run Blender
                    if render_data["render"]:
                        command = f"blender -b -P {blender_script_name}"
                        process = subprocess.run(command, shell=True, check=True)

                        if render_data["verbose"]:
                            print(f">> DONE :: Render container {container_index} finished")

