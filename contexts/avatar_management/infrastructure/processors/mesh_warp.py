# contexts/avatar_management/infrastructure/processors/mesh_warp.py
import cv2
import numpy as np
from typing import Tuple, List

_EPS_AREA = 1.0  # área mínima de triángulo (px^2) para evitar degenerados


def _tri_area(pts: np.ndarray) -> float:
    x1, y1 = pts[0]; x2, y2 = pts[1]; x3, y3 = pts[2]
    return abs(0.5 * ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)))


class MeshWarpProcessor:
    """
    Warping por malla usando Delaunay sobre la plantilla (neutral).
    Warpea por-triángulo con ROIs (sin artefactos de “cara pequeña”).
    """

    def __init__(self, image_shape: Tuple[int, int, int], template_landmarks: np.ndarray):
        self.h, self.w = image_shape[:2]
        self.template_landmarks = np.asarray(template_landmarks, dtype=np.float32)
        if self.template_landmarks.ndim != 2 or self.template_landmarks.shape[1] != 2:
            raise ValueError("template_landmarks debe ser (N,2)")

        # Tolerancia dinámica (px^2) para asociar vértices de Subdiv2D a tus landmarks
        max_side = float(max(self.w, self.h))
        self._tol_sq = (0.05 * max_side) ** 2  # 5% del lado mayor

        rect = (0, 0, self.w, self.h)
        subdiv = cv2.Subdiv2D(rect)
        for (x, y) in self.template_landmarks:
            if np.isfinite(x) and np.isfinite(y):
                subdiv.insert((float(x), float(y)))

        tri_list = subdiv.getTriangleList()
        tri_list = np.asarray(tri_list, dtype=np.float32).reshape(-1, 3, 2)

        self.tri_indices: List[Tuple[int, int, int]] = []
        for tri in tri_list:
            idxs = []
            ok = True
            for p in tri:
                px = np.clip(p[0], 0, self.w - 1)
                py = np.clip(p[1], 0, self.h - 1)
                d = np.sum((self.template_landmarks - np.array([px, py], np.float32)) ** 2, axis=1)
                j = int(np.argmin(d))
                if d[j] > self._tol_sq:  # tolerancia dinámica
                    ok = False
                    break
                idxs.append(j)
            if not ok or len(set(idxs)) != 3:
                continue
            pts = self.template_landmarks[idxs].astype(np.float32)
            if _tri_area(pts) < _EPS_AREA:
                continue
            self.tri_indices.append(tuple(idxs))

        if not self.tri_indices:
            raise RuntimeError("No se pudo construir triangulación válida para warping.")

    def warp(self, src_bgr: np.ndarray, dst_landmarks: np.ndarray) -> np.ndarray:
        """
        Warpea por-triángulo desde la plantilla a dst_landmarks.
        - src_bgr se reescala a (w,h) si hace falta.
        - dst_landmarks: (N,2) float32 en coordenadas de la imagen destino (w,h).
        """
        if src_bgr is None or src_bgr.size == 0:
            raise ValueError("src_bgr vacío.")

        base = src_bgr
        if base.shape[1] != self.w or base.shape[0] != self.h:
            base = cv2.resize(base, (self.w, self.h), interpolation=cv2.INTER_LINEAR)

        dst_landmarks = np.asarray(dst_landmarks, dtype=np.float32)
        if dst_landmarks.ndim != 2 or dst_landmarks.shape[1] != 2:
            raise ValueError("dst_landmarks debe ser (N,2).")

        if dst_landmarks.shape[0] != self.template_landmarks.shape[0]:
            # Re-triangula si difiere el conteo de puntos
            n = min(dst_landmarks.shape[0], self.template_landmarks.shape[0])
            tmpl = self.template_landmarks[:n]
            dst = dst_landmarks[:n]
            return self._warp_retriangulate(base, tmpl, dst)

        out = np.zeros_like(base)
        mask_total = np.zeros((self.h, self.w), dtype=np.uint8)

        for (i0, i1, i2) in self.tri_indices:
            src_tri = self.template_landmarks[[i0, i1, i2]].astype(np.float32)
            dst_tri = dst_landmarks[[i0, i1, i2]].astype(np.float32)
            if _tri_area(src_tri) < _EPS_AREA or _tri_area(dst_tri) < _EPS_AREA:
                continue

            # ROIs fuente y destino
            xS, yS, wS, hS = cv2.boundingRect(src_tri)
            xD, yD, wD, hD = cv2.boundingRect(dst_tri)
            if wS <= 1 or hS <= 1 or wD <= 1 or hD <= 1:
                continue

            # Triángulos relativos a sus ROIs
            src_tri_r = src_tri - np.array([xS, yS], np.float32)
            dst_tri_r = dst_tri - np.array([xD, yD], np.float32)

            # Parches fuente/destino
            src_patch = base[yS:yS + hS, xS:xS + wS]
            M = cv2.getAffineTransform(src_tri_r, dst_tri_r)
            warped = cv2.warpAffine(
                src_patch, M, (wD, hD),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT_101
            )

            # Máscara triangular en ROI destino
            mask = np.zeros((hD, wD), dtype=np.uint8)
            cv2.fillConvexPoly(mask, np.int32(dst_tri_r), 255)

            # Componer en canvas
            y0, y1 = yD, min(self.h, yD + hD)
            x0, x1 = xD, min(self.w, xD + wD)
            roi_canvas = out[y0:y1, x0:x1]
            roi_warped = warped[:(y1 - y0), :(x1 - x0)]
            roi_mask = mask[:(y1 - y0), :(x1 - x0)]

            np.copyto(roi_canvas, roi_warped, where=roi_mask[..., None].astype(bool))
            mask_total[y0:y1, x0:x1] = np.maximum(mask_total[y0:y1, x0:x1], roi_mask)

        # Relleno de agujeros con la imagen base
        out[mask_total == 0] = base[mask_total == 0]
        return out

    def _warp_retriangulate(self, base: np.ndarray, tmpl: np.ndarray, dst: np.ndarray) -> np.ndarray:
        h, w = self.h, self.w
        if base.shape[:2] != (h, w):
            base = cv2.resize(base, (w, h), interpolation=cv2.INTER_LINEAR)

        rect = (0, 0, w, h)
        subdiv = cv2.Subdiv2D(rect)
        for (x, y) in tmpl:
            if np.isfinite(x) and np.isfinite(y):
                subdiv.insert((float(x), float(y)))

        tri_list = np.asarray(subdiv.getTriangleList(), np.float32).reshape(-1, 3, 2)

        out = np.zeros_like(base)
        mask_total = np.zeros((h, w), dtype=np.uint8)
        tol_sq = self._tol_sq  # misma tolerancia

        for tri in tri_list:
            idxs = []
            ok = True
            for p in tri:
                px = np.clip(p[0], 0, w - 1)
                py = np.clip(p[1], 0, h - 1)
                d = np.sum((tmpl - np.array([px, py], np.float32)) ** 2, axis=1)
                j = int(np.argmin(d))
                if d[j] > tol_sq:
                    ok = False
                    break
                idxs.append(j)
            if not ok or len(set(idxs)) != 3:
                continue

            src_tri = tmpl[idxs].astype(np.float32)
            dst_tri = dst[idxs].astype(np.float32)
            if _tri_area(src_tri) < _EPS_AREA or _tri_area(dst_tri) < _EPS_AREA:
                continue

            xS, yS, wS, hS = cv2.boundingRect(src_tri)
            xD, yD, wD, hD = cv2.boundingRect(dst_tri)
            if wS <= 1 or hS <= 1 or wD <= 1 or hD <= 1:
                continue

            src_tri_r = src_tri - np.array([xS, yS], np.float32)
            dst_tri_r = dst_tri - np.array([xD, yD], np.float32)

            src_patch = base[yS:yS + hS, xS:xS + wS]
            M = cv2.getAffineTransform(src_tri_r, dst_tri_r)
            warped = cv2.warpAffine(
                src_patch, M, (wD, hD),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT_101
            )

            mask = np.zeros((hD, wD), dtype=np.uint8)
            cv2.fillConvexPoly(mask, np.int32(dst_tri_r), 255)

            y0, y1 = yD, min(h, yD + hD)
            x0, x1 = xD, min(w, xD + wD)
            roi_canvas = out[y0:y1, x0:x1]
            roi_warped = warped[:(y1 - y0), :(x1 - x0)]
            roi_mask = mask[:(y1 - y0), :(x1 - x0)]

            np.copyto(roi_canvas, roi_warped, where=roi_mask[..., None].astype(bool))
            mask_total[y0:y1, x0:x1] = np.maximum(mask_total[y0:y1, x0:x1], roi_mask)

        out[mask_total == 0] = base[mask_total == 0]
        return out
