from PIL import Image
import numpy as np
import trimesh


def attach_texture_to_mesh(mesh, texture_image):
    # Use x and z coordinates for UV mapping (since terrain is in the x-z plane)
    # This matches how 3D terrain is typically oriented in 3D space
    uv_coordinates = mesh.vertices[:, [0, 2]]  # FIXED: Use x,y for UV mapping

    uv_min = uv_coordinates.min(axis=0)
    uv_max = uv_coordinates.max(axis=0)
    uv = (uv_coordinates - uv_min) / (uv_max - uv_min)

    # Create material with better defaults for visibility
    material = trimesh.visual.texture.SimpleMaterial(
        image=Image.fromarray(texture_image.astype(np.uint8)),
        diffuse=[255, 255, 255, 255],  # Full white diffuse for better visibility
        ambient=[200, 200, 200, 255],  # High ambient for visibility in low light
        specular=[0, 0, 0, 255],  # No specular to avoid dark spots
        glossiness=0.0,  # No glossiness to avoid dark spots
    )

    mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=material)

    return mesh
