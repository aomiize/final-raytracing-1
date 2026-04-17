# object class
import RT_utility as rtu
import math

class Object:
    def __init__(self) -> None:
        pass

    def intersect(self, rRay, cInterval):
        pass

class Sphere(Object):
    def __init__(self, vCenter, fRadius, mMat=None) -> None:
        super().__init__()
        self.center = vCenter
        self.radius = fRadius
        self.material = mMat
        # additional parameters for motion blur
        self.moving_center = None       # where to the sphere moves to
        self.is_moving = False          # is it moving ?
        self.moving_dir = None          # moving direction

    def add_material(self, mMat):
        self.material = mMat

    def add_moving(self, vCenter):      # set an ability to move to the sphere
        self.moving_center = vCenter
        self.is_moving = True
        self.moving_dir = self.moving_center - self.center

    def move_sphere(self, fTime):       # move the sphere by time parameter
        return self.center + self.moving_dir*fTime

    def printInfo(self):
        self.center.printout()        
    
    def intersect(self, rRay, cInterval):        

        # check if the sphere is moving then move center of the sphere.
        sphere_center = self.center
        if self.is_moving:
            sphere_center = self.move_sphere(rRay.getTime())

        oc = rRay.getOrigin() - sphere_center
        a = rRay.getDirection().len_squared()
        half_b = rtu.Vec3.dot_product(oc, rRay.getDirection())
        c = oc.len_squared() - self.radius*self.radius
        discriminant = half_b*half_b - a*c 

        if discriminant < 0:
            return None
        sqrt_disc = math.sqrt(discriminant)

        root = (-half_b - sqrt_disc) / a 
        if not cInterval.surrounds(root):
            root = (-half_b + sqrt_disc) / a 
            if not cInterval.surrounds(root):
                return None
            
        hit_t = root
        hit_point = rRay.at(root)
        hit_normal = (hit_point - sphere_center) / self.radius
        hinfo = rtu.Hitinfo(hit_point, hit_normal, hit_t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # set uv coordinates for texture mapping
        fuv = self.get_uv(hit_normal)
        hinfo.set_uv(fuv[0], fuv[1])

        return hinfo

    # return uv coordinates of the sphere at the hit point.
    def get_uv(self, vNormal):
        theta = math.acos(-vNormal.y())
        phi = math.atan2(-vNormal.z(), vNormal.x()) + math.pi

        u = phi / (2*math.pi)
        v = theta / math.pi
        return (u,v)

# Ax + By + Cz = D
class Quad(Object):
    def __init__(self, vQ, vU, vV, mMat=None) -> None:
        super().__init__()
        self.Qpoint = vQ
        self.Uvec = vU
        self.Vvec = vV
        self.material = mMat
        self.uxv = rtu.Vec3.cross_product(self.Uvec, self.Vvec)
        self.normal = rtu.Vec3.unit_vector(self.uxv)
        self.D = rtu.Vec3.dot_product(self.normal, self.Qpoint)
        self.Wvec = self.uxv / rtu.Vec3.dot_product(self.uxv, self.uxv)

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        denom = rtu.Vec3.dot_product(self.normal, rRay.getDirection())
        # if parallel
        if rtu.Interval.near_zero(denom):
            return None

        # if it is hit.
        t = (self.D - rtu.Vec3.dot_product(self.normal, rRay.getOrigin())) / denom
        if not cInterval.contains(t):
            return None
        
        hit_t = t
        hit_point = rRay.at(t)
        hit_normal = self.normal

        # determine if the intersection point lies on the quad's plane.
        planar_hit = hit_point - self.Qpoint
        alpha = rtu.Vec3.dot_product(self.Wvec, rtu.Vec3.cross_product(planar_hit, self.Vvec))
        beta = rtu.Vec3.dot_product(self.Wvec, rtu.Vec3.cross_product(self.Uvec, planar_hit))
        if self.is_interior(alpha, beta) is None:
            return None

        hinfo = rtu.Hitinfo(hit_point, hit_normal, hit_t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # set uv coordinates for texture mapping
        hinfo.set_uv(alpha, beta)

        return hinfo
    
    def is_interior(self, fa, fb):
        delta = 0   
        if (fa<delta) or (1.0<fa) or (fb<delta) or (1.0<fb):
            return None

        return True


class Triangle(Object):
    def __init__(self, v0, v1, v2, mMat=None) -> None:
        super().__init__()
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = mMat

        self.edge1 = self.v1 - self.v0
        self.edge2 = self.v2 - self.v0
        self.normal = rtu.Vec3.unit_vector(
            rtu.Vec3.cross_product(self.edge1, self.edge2)
        )

    def intersect(self, rRay, cInterval):

        h = rtu.Vec3.cross_product(rRay.getDirection(), self.edge2)
        a = rtu.Vec3.dot_product(self.edge1, h)

        if abs(a) < 1e-8:
            return None

        f = 1.0 / a
        s = rRay.getOrigin() - self.v0
        u = f * rtu.Vec3.dot_product(s, h)

        if u < 0.0 or u > 1.0:
            return None

        q = rtu.Vec3.cross_product(s, self.edge1)
        v = f * rtu.Vec3.dot_product(rRay.getDirection(), q)

        if v < 0.0 or u + v > 1.0:
            return None

        t = f * rtu.Vec3.dot_product(self.edge2, q)

        if not cInterval.contains(t):
            return None

        hit_point = rRay.at(t)

        hinfo = rtu.Hitinfo(hit_point, self.normal, t, self.material)
        hinfo.set_face_normal(rRay, self.normal)

        hinfo.set_uv(u, v)

        return hinfo
    
def bounding_sphere(self):
    return self.center, self.radius

class Cylinder(Object):
    def __init__(self, vCenter, fRadius, fHeight=None, mMat=None):
        super().__init__()
        self.center = vCenter
        self.radius = fRadius
        self.material = mMat

        if fHeight is not None:
            self.y_min = vCenter.y() - fHeight / 2
            self.y_max = vCenter.y() + fHeight / 2
            self.finite = True
        else:
            self.finite = False

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        ro = rRay.getOrigin()
        rd = rRay.getDirection()
        oc = ro - self.center

        a = rd.x()*rd.x() + rd.z()*rd.z()
        b = 2.0 * (oc.x()*rd.x() + oc.z()*rd.z())
        c = oc.x()*oc.x() + oc.z()*oc.z() - self.radius*self.radius

        discriminant = b*b - 4*a*c

        if discriminant < 0:
            return None

        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        t = None
        if cInterval.contains(t1):
            hit_y = ro.y() + t1 * rd.y()
            if not self.finite or (self.y_min <= hit_y <= self.y_max):
                t = t1

        if t is None and cInterval.contains(t2):
            hit_y = ro.y() + t2 * rd.y()
            if not self.finite or (self.y_min <= hit_y <= self.y_max):
                t = t2

        if t is None:
            return None

        hit_point = rRay.at(t)
        normal_x = hit_point.x() - self.center.x()
        normal_z = hit_point.z() - self.center.z()
        hit_normal = rtu.Vec3(normal_x, 0, normal_z) / self.radius

        hinfo = rtu.Hitinfo(hit_point, hit_normal, t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        theta = math.atan2(normal_z, normal_x)
        u = (theta + math.pi) / (2 * math.pi)

        if self.finite:
            v = (hit_point.y() - self.y_min) / (self.y_max - self.y_min)
        else:
            v = hit_point.y() * 0.1

        hinfo.set_uv(u, v)
        return hinfo

class Cone(Object):
    def __init__(self, vCenter, fRadius, fHeight, mMat=None):
        super().__init__()
        self.center = vCenter
        self.base_radius = fRadius
        self.height = fHeight
        self.material = mMat
        self.apex = vCenter + rtu.Vec3(0, fHeight, 0)

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        ro = rRay.getOrigin()
        rd = rRay.getDirection()
        oc = ro - self.center

        k = self.base_radius / self.height
        k2 = k * k

        a = rd.x()*rd.x() + rd.z()*rd.z() - k2*rd.y()*rd.y()
        b = 2*(oc.x()*rd.x() + oc.z()*rd.z() - k2*oc.y()*rd.y())
        c = oc.x()*oc.x() + oc.z()*oc.z() - k2*oc.y()*oc.y()

        discriminant = b*b - 4*a*c

        if discriminant < 0:
            return None

        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        t = None
        for t_test in [t1, t2]:
            if cInterval.contains(t_test):
                hit_y = ro.y() + t_test * rd.y()
                if self.center.y() <= hit_y <= self.apex.y():
                    t = t_test
                    break

        if t is None:
            return None

        hit_point = rRay.at(t)
        y_from_base = hit_point.y() - self.center.y()
        r_at_y = y_from_base * k

        normal_x = hit_point.x() - self.center.x()
        normal_z = hit_point.z() - self.center.z()
        normal_y = -r_at_y * k

        hit_normal = rtu.Vec3.unit_vector(rtu.Vec3(normal_x, normal_y, normal_z))

        hinfo = rtu.Hitinfo(hit_point, hit_normal, t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        theta = math.atan2(normal_z, normal_x)
        u = (theta + math.pi) / (2 * math.pi)
        v = y_from_base / self.height
        hinfo.set_uv(u, v)

        return hinfo