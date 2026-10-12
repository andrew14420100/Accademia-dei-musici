"""STEAM FOCUS — ECC: REDLINE demo, shot S3 (vertical 1080x1920).

The gameplay plate (official Steam trailer footage) floats above the real
Steam store page, the camera pulls back, the plate lands inside the page's
media player, then the camera tilts down the page's info column.

Run:
  blender -b --factory-startup --python redline_steam_page.py -- \
      --assets /path/to/assets --plate /path/to/plate --out /path/to/render \
      --anchors /path/to/public/s3_anchors.json [--samples 32] [--scale 100] \
      [--frames 1-292] [--anchors-only]

Units: 1 page pixel (3840 px wide capture) = 1 mm. The page lies in the XY
plane at z=0 facing +Z; screen-up is +Y.
"""
import argparse
import json
import math
import random
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--assets", required=True)
ap.add_argument("--plate", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--anchors", required=True)
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--frames", default="1-292")
ap.add_argument("--anchors-only", action="store_true")
args = ap.parse_args(argv)

FPS = 30
FRAMES = 292
PAGE_W, PAGE_H = 3.84, 4.32           # page_tex.png is 3840 x 4320
SLOT = (722, 580, 2338, 1489)          # media player box in page pixels
PLATE_W, PLATE_H = 1.616, 0.909
PLATE_CROP_X = (900 - 960) / 1920 * PLATE_W   # match S1/S2 reframe centre


def px(x, y):
    return Vector((x / 1000 - PAGE_W / 2, PAGE_H / 2 - y / 1000, 0.0))


SLOT_C = px((SLOT[0] + SLOT[2]) / 2, (SLOT[1] + SLOT[3]) / 2)

# Points the Remotion overlays attach to (page pixels).
ANCHORS = {
    "release": (2648, 1251),      # "In arrivo"
    "developer": (2652, 1314),    # "NetEase Games"
    "tags": (2380, 1581),         # popular tags row
    "crossplay": (2440, 2122),    # "Multigiocatore multipiattaforma"
    "italian": (2372, 2452),      # languages table, "Italiano" row
    "italian_na": (2860, 2452),   # "Non disponibile"
    "steam_logo": (870, 102),     # Steam header logo (Valve's own page)
}

scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

scene.frame_start, scene.frame_end = 1, FRAMES
scene.render.fps = FPS
scene.render.resolution_x, scene.render.resolution_y = 1080, 1920
scene.render.resolution_percentage = args.scale
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.max_bounces = 3
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 0
scene.cycles.volume_bounces = 0
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.45
# Standard keeps the page and the footage at their true colours.
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = args.out.rstrip("/") + "/s3_"
scene.render.use_overwrite = False   # resumable: skip frames already on disk
scene.render.use_placeholder = True

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.006, 0.011, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def image(path, colorspace="sRGB"):
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = colorspace
    return img


def mat_screen(name, img, emit, albedo, seq=False):
    """A lit display surface: part emissive, part diffuse so it takes shadows."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Cubic"
    tex.extension = "CLIP"
    if seq:
        tex.image_user.frame_duration = FRAMES + 8
        tex.image_user.frame_start = 1
        tex.image_user.frame_offset = 0
        tex.image_user.use_auto_refresh = True
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Coat Weight"].default_value = 0.0
    bsdf.inputs["Coat Roughness"].default_value = 0.08
    alb = nt.nodes.new("ShaderNodeMixRGB")
    alb.blend_type = "MULTIPLY"
    alb.inputs[0].default_value = 1.0
    alb.inputs[2].default_value = (albedo, albedo, albedo, 1)
    nt.links.new(tex.outputs[0], alb.inputs[1])
    nt.links.new(alb.outputs[0], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs[0], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = emit
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m


def mat_edge(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.02, 0.025, 0.03, 1)
    b.inputs["Metallic"].default_value = 0.85
    b.inputs["Roughness"].default_value = 0.28
    return m


def slab(name, w, h, depth, face_mat, edge_mat, loc):
    """Thin box: textured top face, metal edges. Origin on the top face."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (w, h, depth)
    bpy.ops.object.transform_apply(scale=True)
    for v in ob.data.vertices:
        v.co.z -= depth / 2
    ob.data.materials.append(edge_mat)
    ob.data.materials.append(face_mat)
    while ob.data.uv_layers:
        ob.data.uv_layers.remove(ob.data.uv_layers[0])
    uv = ob.data.uv_layers.new(name="PageUV")
    for poly in ob.data.polygons:
        top = poly.normal.z > 0.9
        poly.material_index = 1 if top else 0
        for li in poly.loop_indices:
            co = ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv = (co.x / w + 0.5, co.y / h + 0.5)
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = min(depth * 0.35, 0.004)
    bev.segments = 3
    bev.limit_method = "ANGLE"
    ob.location = loc
    return ob


edge = mat_edge("edge_metal")

# --- Steam page (real capture) --------------------------------------------
page_mat = mat_screen("page", image(f"{args.assets}/page_tex.png"), emit=0.62, albedo=0.40)
page = slab("SteamPage", PAGE_W, PAGE_H, 0.03, page_mat, edge, (0, 0, 0))

# --- Background: the game's own store backdrop, far behind -----------------
bg_mat = bpy.data.materials.new("bg")
bg_mat.use_nodes = True
nt = bg_mat.node_tree
nt.nodes.clear()
o = nt.nodes.new("ShaderNodeOutputMaterial")
t = nt.nodes.new("ShaderNodeTexImage")
t.image = image(f"{args.assets}/bg_blur.jpg")
e = nt.nodes.new("ShaderNodeEmission")
e.inputs[1].default_value = 0.55
nt.links.new(t.outputs[0], e.inputs[0])
nt.links.new(e.outputs[0], o.inputs[0])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.2, 1.0, -2.6))
bgp = bpy.context.object
bgp.scale = (12.8, 7.2, 1)
bgp.data.materials.append(bg_mat)
bgp.visible_shadow = False

# --- Gameplay plate (image sequence of the official footage) ---------------
seq = image(f"{args.plate}/p_0001.jpg")
seq.source = "SEQUENCE"
plate_mat = mat_screen("plate", seq, emit=0.66, albedo=0.36, seq=True)
plate = slab("Plate", PLATE_W, PLATE_H, 0.012, plate_mat, edge, (SLOT_C.x, SLOT_C.y, 1.0))
plate.rotation_mode = "XYZ"


def key(ob, frame, loc=None, rot=None):
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=frame)
    if rot is not None:
        ob.rotation_euler = [math.radians(r) for r in rot]
        ob.keyframe_insert("rotation_euler", frame=frame)


Z0 = 1.0
key(plate, 1, (SLOT_C.x, SLOT_C.y, Z0), (0, 0, 0))
key(plate, 42, (SLOT_C.x, SLOT_C.y, Z0), (0, 0, 0))
key(plate, 96, (SLOT_C.x + 0.03, SLOT_C.y + 0.02, Z0 * 0.82), (5, -9, 0.6))
key(plate, 150, (SLOT_C.x, SLOT_C.y, 0.0015), (0, 0, 0))

# --- Camera ----------------------------------------------------------------
cam_data = bpy.data.cameras.new("Cam")
cam_data.sensor_fit = "VERTICAL"
cam_data.sensor_height = 36
cam_data.lens = 40
cam_data.clip_start = 0.02
cam_data.dof.use_dof = True
cam_data.dof.aperture_blades = 7
cam_data.dof.aperture_rotation = math.radians(12)
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
tgt = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(tgt)

PX = SLOT_C.x + PLATE_CROP_X
D0 = PLATE_H * 0.965 / 0.9   # frame height = 0.9 * distance; slight overscan
cam_keys = [
    # frame, camera xyz, target xyz
    (1,   (PX, SLOT_C.y, Z0 + D0), (PX, SLOT_C.y + 0.0001, Z0)),
    (42,  (PX, SLOT_C.y, Z0 + D0 * 0.95), (PX, SLOT_C.y + 0.0001, Z0)),
    (108, (SLOT_C.x + 0.34, SLOT_C.y + 0.42, 3.55), (SLOT_C.x - 0.02, SLOT_C.y + 0.16, 0.35)),
    (152, (SLOT_C.x + 0.78, SLOT_C.y + 0.02, 2.75), (SLOT_C.x + 0.42, SLOT_C.y - 0.02, 0.0)),
    (196, (0.80, 0.93, 2.16), (0.80, 0.96, 0.0)),
    (262, (0.80, 0.16, 2.06), (0.80, 0.18, 0.0)),
    (FRAMES, (0.80, 0.08, 2.02), (0.80, 0.10, 0.0)),
]
for f, c, t_ in cam_keys:
    cam.location = c
    cam.keyframe_insert("location", frame=f)
    tgt.location = t_
    tgt.keyframe_insert("location", frame=f)

# Depth of field: shallow while the plate floats, deepening once it lands.
for f, fs in [(1, 2.0), (96, 1.6), (150, 2.4), (200, 5.6), (FRAMES, 5.6)]:
    cam_data.dof.aperture_fstop = fs
    cam_data.dof.keyframe_insert("aperture_fstop", frame=f)

# Smooth ease on every curve.
for ob in (plate, cam, tgt, cam_data):
    ad = ob.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"

# Orient the camera every frame from its look-at target with a fixed
# screen-up of +Y (a Track To constraint flips when looking straight down).
from mathutils import Matrix
prev = None
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    fwd = (tgt.matrix_world.translation - cam.matrix_world.translation).normalized()
    right = fwd.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(fwd).normalized()
    m = Matrix((right, up, -fwd)).transposed()
    cam.rotation_mode = "XYZ"
    cam.rotation_euler = m.to_euler("XYZ", prev) if prev else m.to_euler("XYZ")
    prev = cam.rotation_euler.copy()
    cam.keyframe_insert("rotation_euler", frame=f)
for fc in cam.animation_data.action.fcurves:
    if fc.data_path == "rotation_euler":
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

# Focus follows the plate centre (it lands on the page plane).
focus = bpy.data.objects.new("Focus", None)
scene.collection.objects.link(focus)
focus.parent = plate
cam_data.dof.focus_object = focus

# --- Lights ----------------------------------------------------------------
sun_d = bpy.data.lights.new("Key", "SUN")
sun_d.energy = 1.0
sun_d.angle = math.radians(9)
sun = bpy.data.objects.new("Key", sun_d)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(-14), math.radians(-12), 0)
sun.visible_glossy = False

# Cool Steam-blue rim from behind/above, warm REDLINE kicker low right.
for name, col, loc, energy, size in [
    ("RimBlue", (0.35, 0.62, 1.0), (-2.2, 3.6, 2.4), 260, 2.5),
    ("KickRed", (1.0, 0.18, 0.12), (2.8, -1.6, 1.4), 120, 1.8),
]:
    ld = bpy.data.lights.new(name, "AREA")
    ld.color = col
    ld.energy = energy
    ld.size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    lo.visible_glossy = False   # light the scene, never show as a blob
    scene.collection.objects.link(lo)
    tc2 = lo.constraints.new("TRACK_TO")
    tc2.target = plate
    tc2.track_axis = "TRACK_NEGATIVE_Z"
    tc2.up_axis = "UP_Y"
    # The coloured lights only shape the floating phase; the landed page
    # must read in its true colours.
    for f, k in [(1, 0.0), (40, 1.0), (140, 1.0), (196, 0.0)]:
        ld.energy = energy * k
        ld.keyframe_insert("energy", frame=f)

# --- Anchor export for Remotion --------------------------------------------
W, H = 1080, 1920
track = {"fps": FPS, "frames": FRAMES, "width": W, "height": H, "points": {}}
pts = {k: px(*v) for k, v in ANCHORS.items()}
corners = {"plate_tl": (-1, 1), "plate_tr": (1, 1), "plate_br": (1, -1), "plate_bl": (-1, -1)}
for k in list(pts) + list(corners):
    track["points"][k] = []
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    for k, p in pts.items():
        v = world_to_camera_view(scene, cam, p)
        track["points"][k].append([round(v.x * W, 2), round((1 - v.y) * H, 2), round(v.z, 4)])
    mw = plate.evaluated_get(dg).matrix_world
    for k, (sx, sy) in corners.items():
        v = world_to_camera_view(scene, cam, mw @ Vector((sx * PLATE_W / 2, sy * PLATE_H / 2, 0)))
        track["points"][k].append([round(v.x * W, 2), round((1 - v.y) * H, 2), round(v.z, 4)])
with open(args.anchors, "w") as fh:
    json.dump(track, fh)
print("ANCHORS_WRITTEN", args.anchors)

if not args.anchors_only:
    a, b = (int(x) for x in args.frames.split("-"))
    scene.frame_start, scene.frame_end = a, b
    bpy.ops.render.render(animation=True)
