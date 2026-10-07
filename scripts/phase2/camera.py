"""Pinhole camera in the project frame (origin on the ground below the front axle, +X right, +Y forward,
+Z up, metres). Image coordinates: u to the right, v down, pixels.

x_cam = R (P - C); u = f * x/z + cx (+ radial distortion k1), v = f * y/z + cy.
Rotation is parametrised by a Rodrigues vector. One radial distortion term k1 (normalised radius)
is supported for the distortion sensitivity study; fits use k1 = 0 unless stated.
"""
import math

import numpy as np


def rodrigues(r):
    r = np.asarray(r, float)
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def rot_to_rodrigues(R):
    th = math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2)))
    if th < 1e-12:
        return np.zeros(3)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * math.sin(th))
    return v * th


def look_at(C, target, up=(0, 0, 1)):
    """Rotation whose camera z points from C to target, image v down (along -up)."""
    C, target, up = (np.asarray(a, float) for a in (C, target, up))
    z = target - C
    z /= np.linalg.norm(z)
    x = np.cross(z, up)          # image right
    x /= np.linalg.norm(x)
    y = np.cross(z, x)           # image down
    return np.vstack([x, y, z])


class Camera:
    def __init__(self, R, C, f, cx, cy, k1=0.0):
        self.R, self.C = np.asarray(R, float), np.asarray(C, float)
        self.f, self.cx, self.cy, self.k1 = float(f), float(cx), float(cy), float(k1)

    @classmethod
    def from_params(cls, p, f, cx, cy, k1=0.0):
        """p = [rx, ry, rz, Cx, Cy, Cz] (+ optional f as p[6])."""
        f = p[6] if len(p) > 6 else f
        return cls(rodrigues(p[:3]), p[3:6], f, cx, cy, k1)

    def params(self):
        return np.r_[rot_to_rodrigues(self.R), self.C]

    def to_cam(self, P):
        P = np.atleast_2d(np.asarray(P, float))
        return (self.R @ (P - self.C).T).T

    def project(self, P):
        Xc = self.to_cam(P)
        xn, yn = Xc[:, 0] / Xc[:, 2], Xc[:, 1] / Xc[:, 2]
        if self.k1:
            r2 = xn ** 2 + yn ** 2
            d = 1 + self.k1 * r2
            xn, yn = xn * d, yn * d
        return np.c_[self.f * xn + self.cx, self.f * yn + self.cy]

    def ray(self, uv):
        """World-frame ray (origin C, unit direction) through pixel uv (distortion inverted iteratively)."""
        u, v = uv
        xn, yn = (u - self.cx) / self.f, (v - self.cy) / self.f
        if self.k1:
            x0, y0 = xn, yn
            for _ in range(10):
                r2 = xn ** 2 + yn ** 2
                xn, yn = x0 / (1 + self.k1 * r2), y0 / (1 + self.k1 * r2)
        d = self.R.T @ np.array([xn, yn, 1.0])
        return self.C, d / np.linalg.norm(d)

    def backproject_to_plane(self, uv, n, d0):
        """Intersect the pixel ray with the plane n . P = d0 (world frame)."""
        C, d = self.ray(uv)
        n = np.asarray(n, float)
        t = (d0 - n @ C) / (n @ d)
        return C + t * d

    def depth(self, P):
        return self.to_cam(P)[:, 2]

    def mm_per_px(self, P):
        """Object-space size of one pixel at point P (approximate, metres)."""
        return float(self.depth(P)[0] / self.f)
