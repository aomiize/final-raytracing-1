import RT_utility as rtu
import RT_camera as rtc
import RT_renderer as rtren
import RT_material as rtm
import RT_scene as rts
import RT_object as rto
import RT_integrator as rti
import RT_light as rtl
import math
import numpy as np
from PIL import Image as im

# Denoiser
try:
    import cv2
    HAS_CV2 = True
except:
    HAS_CV2 = False
    try:
        print("WARNING: opencv-python not found")
        print("Denoising will be disabled")
        print("Install: pip install opencv-python")
        print()
    except:
        pass

def denoise_bilateral(img_array, strength=1.0):
    """Bilateral filter - ลด noise โดยเก็บขอบคม"""
    if not HAS_CV2:
        return img_array
    
    d = int(9 * strength)
    sigma_color = 75 * strength
    sigma_space = 75 * strength
    
    return cv2.bilateralFilter(img_array, d, sigma_color, sigma_space)

# ========================================
# ⚙️ SETTINGS - แก้ตรงนี้ได้
# ========================================
IMG_WIDTH = 960          # 320, 640, 960, 1280, 1920
SAMPLES = 64             # 16, 64, 256, 512, 1024
MAX_DEPTH = 12           # 8, 12, 16

DENOISE_STRENGTH = 1.0   # 0.5 (อ่อน), 1.0 (กลาง), 1.5 (แรง)

# ========================================
# CHESS PIECE BUILDERS
# ========================================

def build_pawn_standing(world, material, pos):
    """Pawn ตั้งตรง"""
    x, z = pos.x(), pos.z()
    y = pos.y()
    
    # Bottom
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.02, z),
        fRadius=0.15,
        fHeight=0.04,
        mMat=material
    ))
    y += 0.04
    
    # Base (cone with spheres)
    for i in range(15):
        t = i / 14
        yy = y + t * 0.15
        r = 0.14 - t * 0.06
        world.add_object(rto.Sphere(rtu.Vec3(x, yy, z), r, material))
    y += 0.15
    
    # Body
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.15, z),
        fRadius=0.08,
        fHeight=0.30,
        mMat=material
    ))
    y += 0.30
    
    # Collar
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.015, z),
        fRadius=0.12,
        fHeight=0.03,
        mMat=material
    ))
    y += 0.03
    
    # Head
    head_y = y + 0.09
    for i in range(30):
        t = i / 29
        angle = t * math.pi
        yy = head_y - 0.10 * math.cos(angle)
        r = 0.10 * math.sin(angle)
        if r > 0.002:
            world.add_object(rto.Sphere(rtu.Vec3(x, yy, z), r, material))

def build_rook_standing(world, material, pos):
    """Rook ตั้งตรง - แบบ cylinder top"""
    x, z = pos.x(), pos.z()
    y = pos.y()
    
    # Bottom
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.02, z),
        fRadius=0.15,
        fHeight=0.04,
        mMat=material
    ))
    y += 0.04
    
    # Base
    for i in range(8):
        t = i / 7
        yy = y + t * 0.08
        r = 0.15 - t * 0.01
        world.add_object(rto.Sphere(rtu.Vec3(x, yy, z), r, material))
    y += 0.08
    
    # Lower body
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.08, z),
        fRadius=0.14,
        fHeight=0.16,
        mMat=material
    ))
    y += 0.16
    
    # Lower ring
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.015, z),
        fRadius=0.15,
        fHeight=0.03,
        mMat=material
    ))
    y += 0.03
    
    # Middle body
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.08, z),
        fRadius=0.13,
        fHeight=0.16,
        mMat=material
    ))
    y += 0.16
    
    # Upper ring
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.015, z),
        fRadius=0.14,
        fHeight=0.03,
        mMat=material
    ))
    y += 0.03
    
    # Upper body
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.075, z),
        fRadius=0.13,
        fHeight=0.15,
        mMat=material
    ))
    y += 0.15
    
    # Top Ring
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(x, y + 0.05, z),
        fRadius=0.13,
        fHeight=0.10,
        mMat=material
    ))
    y += 0.10
    
    # 4 Top Cylinders
    top_cyl_height = 0.03
    top_cyl_radius = 0.035
    offset = 0.095
    
    top_positions = [
        (x + offset, z),
        (x - offset, z),
        (x, z + offset),
        (x, z - offset),
    ]
    
    for tx, tz in top_positions:
        world.add_object(rto.Cylinder(
            vCenter=rtu.Vec3(tx, y + top_cyl_height/2, tz),
            fRadius=top_cyl_radius,
            fHeight=top_cyl_height,
            mMat=material
        ))

# ========================================
# MAIN FUNCTION
# ========================================

def main():
    """Main rendering function"""
    
    # ========================================
    # CAMERA
    # ========================================
    print("\n" + "="*70)
    print("  Creating Camera...")
    print("="*70)
    
    main_camera = rtc.Camera()
    
    main_camera.aspect_ratio = 16.0 / 9.0
    main_camera.img_width = IMG_WIDTH
    main_camera.samples_per_pixel = SAMPLES
    main_camera.max_depth = MAX_DEPTH
    
    # Camera - dramatic close-up
    main_camera.vertical_fov = 40
    main_camera.look_from = rtu.Vec3(0, 0.4, 2.2)
    main_camera.look_at = rtu.Vec3(0, 0.45, 0)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)
    
    main_camera.init_camera(0.04, 2.2)
    
    print(f"  Resolution: {main_camera.img_width}x{main_camera.img_height}")
    print(f"  Samples: {SAMPLES} SPP")
    print(f"  Max Depth: {MAX_DEPTH}")
    
    # ========================================
    # SCENE
    # ========================================
    print("\n" + "="*70)
    print("  Creating Scene...")
    print("="*70)
    
    world = rts.Scene(cBgcolor=rtu.Color(0.02, 0.02, 0.03))
    
    # Materials
    white_mat = rtm.Lambertian(rtu.Color(0.95, 0.93, 0.91))
    black_mat = rtm.Lambertian(rtu.Color(0.12, 0.10, 0.08))
    table_mat = rtm.Lambertian(rtu.Color(0.15, 0.12, 0.10))
    floor = rtm.Lambertian(rtu.Color(0.05, 0.04, 0.03))
    wall_mat = rtm.Lambertian(rtu.Color(0.08, 0.07, 0.06))
    
    # Floor
    world.add_object(rto.Sphere(rtu.Vec3(0, -1000, 0), 1000, floor))
    
    # Walls
    world.add_object(rto.Quad(
        rtu.Vec3(-5, 0, -3),
        rtu.Vec3(10, 0, 0),
        rtu.Vec3(0, 5, 0),
        wall_mat
    ))
    
    world.add_object(rto.Quad(
        rtu.Vec3(-3, 0, -3),
        rtu.Vec3(0, 0, 6),
        rtu.Vec3(0, 5, 0),
        wall_mat
    ))
    
    world.add_object(rto.Quad(
        rtu.Vec3(3, 0, -3),
        rtu.Vec3(0, 0, 6),
        rtu.Vec3(0, 5, 0),
        wall_mat
    ))
    
    # Table
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(0, 0.15, 0),
        fRadius=0.80,
        fHeight=0.30,
        mMat=table_mat
    ))
    
    print("  Building chess pieces...")
    
    # Chess pieces
    build_pawn_standing(world, white_mat, rtu.Vec3(-0.5, 0.30, 0))
    build_rook_standing(world, black_mat, rtu.Vec3(0.5, 0.30, 0))
    
    print("  Adding person silhouette...")
    
    # Person silhouette
    person_mat = rtm.Lambertian(rtu.Color(0.08, 0.07, 0.06))
    
    world.add_object(rto.Cylinder(
        vCenter=rtu.Vec3(2.5, 0.6, -1.5),
        fRadius=0.25,
        fHeight=1.2,
        mMat=person_mat
    ))
    
    world.add_object(rto.Sphere(
        rtu.Vec3(2.5, 1.4, -1.5),
        0.2,
        person_mat
    ))
    
    # ========================================
    # LIGHTING
    # ========================================
    print("  Setting up lighting...")
    
    # Single dim light (outside frame)
    dim_light = rtl.Diffuse_light(rtu.Color(3.5, 3.2, 3.0))
    world.add_object(rto.Sphere(rtu.Vec3(3.5, 2.0, -1.0), 2.0, dim_light))
    
    print(f"  Scene created (Chess pieces + Person + Lighting)")
    
    # ========================================
    # RENDER
    # ========================================
    print("\n" + "="*70)
    print("  RENDERING")
    print("="*70)
    print(f"  Resolution: {main_camera.img_width}x{main_camera.img_height}")
    print(f"  Samples: {SAMPLES} SPP")
    print(f"  Estimated time: ~5-8 minutes")
    print("="*70 + "\n")
    
    integrator = rti.Integrator(bDlight=True, bSkyBG=False)
    renderer = rtren.Renderer(main_camera, integrator, world)
    
    # Render
    print("Rendering...\n")
    renderer.render_jittered()
    
    # Save RAW
    raw_output = "chess_raw.png"
    renderer.write_img2png(raw_output)
    print(f"\nSaved RAW: {raw_output}")
    
    # ========================================
    # DENOISE
    # ========================================
    if HAS_CV2:
        print("\n" + "="*70)
        print("  DENOISING...")
        print("="*70)
        print(f"  Method: Bilateral Filter")
        print(f"  Strength: {DENOISE_STRENGTH}")
        
        # Load image
        img = im.open(raw_output)
        img_array = np.array(img)
        
        # Denoise
        denoised = denoise_bilateral(img_array, DENOISE_STRENGTH)
        
        # Save
        final_output = "chess_final.png"
        final_img = im.fromarray(denoised.astype(np.uint8))
        final_img.save(final_output)
        
        print(f"  Saved FINAL: {final_output}")
        print("="*70)
        
        print("\n" + "="*70)
        print("  COMPLETE!")
        print("="*70)
        print(f"  RAW:   {raw_output} (with noise)")
        print(f"  FINAL: {final_output} (clean)")
        print("="*70 + "\n")
        
    else:
        print("\nDenoising skipped (opencv not installed)")
        print(f"Output: {raw_output}\n")

# ========================================
# RUN
# ========================================

if __name__ == "__main__":
    print("\n")
    print("="*70)
    print("  CHESS SCENE RENDERER")
    print("="*70)
    print(f"  Resolution: {IMG_WIDTH}x{int(IMG_WIDTH/16*9)}")
    print(f"  Samples: {SAMPLES} SPP")
    print(f"  Denoise: {'Enabled' if HAS_CV2 else 'Disabled'}")
    print("="*70)
    
    main()