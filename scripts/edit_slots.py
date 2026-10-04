import argparse
import json
import cv2
import numpy as np

from src.slots import load_slots, save_slots

parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
parser.add_argument("--slots", required=True)
args = parser.parse_args()

image = cv2.imread(args.image)
if image is None:
    raise RuntimeError("Could not open image.")

slots = load_slots(args.slots)
current = []

def redraw():
    canvas = image.copy()

    for s in slots:
        pts = np.array(s["points"], np.int32)
        cv2.polylines(canvas, [pts], True, (0,255,0), 2)
        center = tuple(np.mean(pts, axis=0).astype(int))
        cv2.putText(canvas, f"#{s['id']}", center,
                    cv2.FONT_HERSHEY_SIMPLEX, .6, (0,255,0), 2)

    if current:
        pts = np.array(current, np.int32)
        cv2.polylines(canvas, [pts], False, (0,255,255), 2)
        for p in current:
            cv2.circle(canvas, tuple(p), 5, (0,255,255), -1)

    cv2.rectangle(canvas, (0,0), (900,70), (20,20,20), -1)
    cv2.putText(canvas,
                "Click 4 points | n=add | r=reset | u=undo | d=delete last | q=save",
                (10,28), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,255,255), 2)
    cv2.putText(canvas,
                f"Slots: {len(slots)} | Current: {len(current)}",
                (10,55), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,255,255), 2)

    cv2.imshow("Slot Editor", canvas)

def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(current) < 4:
        current.append([x,y])
        redraw()

cv2.namedWindow("Slot Editor", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Slot Editor", mouse)
redraw()

while True:
    k = cv2.waitKey(50) & 0xff
    if k == ord("r"):
        current.clear()
        redraw()
    elif k == ord("u"):
        if current:
            current.pop()
        redraw()
    elif k == ord("n"):
        if len(current) >= 3:
            next_id = max([s["id"] for s in slots], default=0) + 1
            slots.append({"id": next_id, "points": current.copy(), "source": "manual"})
            current.clear()
            redraw()
    elif k == ord("d"):
        if slots:
            slots.pop()
            redraw()
    elif k == ord("q"):
        break

cv2.destroyAllWindows()
save_slots(args.slots, slots)
print(f"Saved {len(slots)} slots to {args.slots}")
