import RT_utility as rtu
import RT_camera as rtc
import RT_renderer as rtren
import RT_material as rtm
import RT_scene as rts
import RT_object as rto
import RT_integrator as rti
import RT_light as rtl


def renderDreamyMarbles():

    main_camera = rtc.Camera()

    # ---------- render quality ----------
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 1920
    main_camera.samples_per_pixel = 1024
    main_camera.max_depth = 12  

    main_camera.vertical_fov = 40

    # Camera position - ใกล้กว่าเดิมเพื่อ bokeh ชัด
    main_camera.look_from = rtu.Vec3(0, 2.5, 8)
    main_camera.look_at = rtu.Vec3(0, 0.8, 0)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)

    # Depth of Field แรง สำหรับ dreamy bokeh
    aperture = 0.25  # เพิ่ม aperture = bokeh นุ่มมาก
    focus_distance = 8.0

    main_camera.init_camera(aperture, focus_distance)

    world = rts.Scene(cBgcolor=rtu.Color(0.02, 0.02, 0.03))  # พื้นหลังมืดนิดหน่อย

    # ---------- Ground - Soft reflective surface ----------
    ground_mat = rtm.Metal(
        rtu.Color(0.9, 0.9, 0.95),
        fRoughness=0.4  # นุ่มๆ ไม่ต้องแวววับมาก
    )

    world.add_object(
        rto.Sphere(
            rtu.Vec3(0, -1000, 0),
            1000,
            ground_mat
        )
    )

    # ---------- Glass Marbles - Colorful & Transparent ----------
    # Material = Dielectric (glass) with different colors

    # ลูกแก้วสีฟ้า (น้ำเงินพาสเทล)
    blue_glass = rtm.Dielectric(
        rtu.Color(0.7, 0.85, 1.0),
        fIor=1.5
    )

    # ลูกแก้วสีชมพู
    pink_glass = rtm.Dielectric(
        rtu.Color(1.0, 0.75, 0.85),
        fIor=1.5
    )

    # ลูกแก้วสีเขียว
    green_glass = rtm.Dielectric(
        rtu.Color(0.7, 1.0, 0.8),
        fIor=1.5
    )

    # ลูกแก้วสีเหลือง
    yellow_glass = rtm.Dielectric(
        rtu.Color(1.0, 0.95, 0.6),
        fIor=1.5
    )

    # ลูกแก้วสีม่วง
    purple_glass = rtm.Dielectric(
        rtu.Color(0.9, 0.7, 1.0),
        fIor=1.5
    )

    # ลูกแก้วสีส้ม
    orange_glass = rtm.Dielectric(
        rtu.Color(1.0, 0.8, 0.6),
        fIor=1.5
    )

    # ลูกแก้วใส (clear glass)
    clear_glass = rtm.Dielectric(
        rtu.Color(0.98, 0.98, 0.98),
        fIor=1.5
    )

    # ---------- Arrange marbles in clusters ----------
    
    # Hero marble (focus point) - ตรงกลางด้านหน้า
    world.add_object(
        rto.Sphere(rtu.Vec3(0, 0.8, 0), 0.8, blue_glass)
    )

    # Foreground marbles (out of focus - bokeh)
    world.add_object(
        rto.Sphere(rtu.Vec3(-1.5, 0.5, 2.5), 0.5, pink_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(1.8, 0.4, 2.0), 0.4, yellow_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(-0.5, 0.3, 3.0), 0.3, green_glass)
    )

    # Mid-ground marbles (near focus)
    world.add_object(
        rto.Sphere(rtu.Vec3(1.2, 0.6, -0.5), 0.6, purple_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(-1.5, 0.5, 0.2), 0.5, orange_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(0.8, 0.35, 1.0), 0.35, clear_glass)
    )

    # Background marbles (out of focus)
    world.add_object(
        rto.Sphere(rtu.Vec3(-2.5, 0.7, -2.5), 0.7, green_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(2.0, 0.5, -2.0), 0.5, pink_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(0.5, 0.4, -3.0), 0.4, blue_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(-1.0, 0.3, -2.5), 0.3, yellow_glass)
    )

    # Small scattered marbles
    world.add_object(
        rto.Sphere(rtu.Vec3(2.5, 0.25, 0.5), 0.25, purple_glass)
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(-2.8, 0.3, -1.0), 0.3, orange_glass)
    )

    # ---------- Rainbow Soft Lighting (Glow + Bloom effect) ----------
    
    # Main soft pink glow (top-left)
    pink_glow = rtl.Diffuse_light(
        rtu.Color(15, 8, 12)  # Soft pink-purple glow
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(-3, 4, 2), 1.2, pink_glow)
    )

    # Blue-cyan accent light (top-right)
    cyan_glow = rtl.Diffuse_light(
        rtu.Color(6, 10, 15)  # Cool blue glow
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(4, 3.5, -1), 1.0, cyan_glow)
    )

    # Warm amber/orange fill light (low, behind)
    amber_glow = rtl.Diffuse_light(
        rtu.Color(12, 8, 4)  # Warm orange glow
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(0, 1.5, -5), 1.5, amber_glow)
    )

    # Soft yellow-green accent (side)
    green_glow = rtl.Diffuse_light(
        rtu.Color(8, 12, 6)  # Soft green-yellow
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(-4, 2, -3), 0.8, green_glow)
    )

    # Subtle purple highlight (creates dreamy atmosphere)
    purple_glow = rtl.Diffuse_light(
        rtu.Color(10, 6, 14)  # Dreamy purple
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(3, 2.5, 1), 0.9, purple_glow)
    )

    # Top fill light (soft white-yellow)
    top_fill = rtl.Diffuse_light(
        rtu.Color(8, 8, 7)  # Neutral soft fill
    )
    world.add_object(
        rto.Sphere(rtu.Vec3(0, 6, 0), 2.0, top_fill)
    )

    # ---------- integrator ----------
    integrator = rti.Integrator(bDlight=True, bSkyBG=False)

    renderer = rtren.Renderer(
        main_camera,
        integrator,
        world
    )

    renderer.render_jittered()

    renderer.write_img2png("dreamy_glass_marbles.png")


if __name__ == "__main__":
    renderDreamyMarbles()