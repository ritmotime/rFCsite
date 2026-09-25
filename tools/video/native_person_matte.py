"""Protect navy cap and enclosed head interiors in native-frame person mattes.

Apply to RGB native camera footage BEFORE any optical-flow interpolation.
No convex hull or broad silhouette expansion is used; all added pixels are
observed navy cap components touching the existing head or enclosed head holes.
"""
import cv2
import numpy as np


def improve_native_alpha(film, alpha, j, bank, motion=None):
    if motion is None:
        import motion_v6 as motion
    j = int(j)
    x, y, w, h = np.asarray(bank.rows[j]['red_shirt_bbox'], dtype=float)
    M = motion.camera_matrix(j, 'follow')
    corners = np.array([[x-42, y-125, 1], [x+w*.68, y-125, 1],
                        [x-42, y+75, 1], [x+w*.68, y+75, 1]]) @ M.T
    x0, y0 = np.maximum(np.floor(corners.min(axis=0)).astype(int), [0, 0])
    x1, y1 = np.minimum(np.ceil(corners.max(axis=0)).astype(int),
                       [film.shape[1], film.shape[0]])
    out = np.asarray(alpha, dtype=np.float32).copy()
    if x1 <= x0 or y1 <= y0:
        return out
    old = out[y0:y1, x0:x1]
    mask = (old >= .5).astype(np.uint8)
    rgb = film[y0:y1, x0:x1].astype(np.int16)
    # The navy panel is distinctly blue, unlike the green/neutral reed bank.
    navy = ((rgb[...,2]-rgb[...,0] > 7) &
            (rgb[...,2]-rgb[...,1] > 3) & (rgb[...,0] < 130)).astype(np.uint8)
    navy = cv2.morphologyEx(navy, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))
    near = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(navy, 8)
    for k in range(1, n):
        # Reject tiny colour flecks and require an observed head connection.
        if stats[k, cv2.CC_STAT_AREA] >= 12:
            component = labels == k
            if np.any(near[component]):
                mask[component] = 1
    # Fill only enclosed holes in this head crop. Background connected to any
    # crop border stays background, preserving hair, cap rim and neck contours.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(1-mask, 8)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:,0], labels[:,-1]]))
    for k in range(1, n):
        if k not in border:
            mask[labels == k] = 1
    additions = ((mask > 0) & (old < .5)).astype(np.uint8)
    if not np.any(additions):
        return out
    # Leave every unmodified native edge exactly intact. Blend only within
    # three pixels of newly repaired head pixels.
    neighborhood = cv2.dilate(additions, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    soft = cv2.GaussianBlur(mask.astype(np.float32), (0,0), .65)
    out[y0:y1, x0:x1] = np.maximum(old, soft * neighborhood)
    return out
