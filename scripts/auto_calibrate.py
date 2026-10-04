import argparse
from src.calibration import automatic_calibration

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--frames", type=int, default=40)
args = parser.parse_args()

slots, _ = automatic_calibration(
    args.source, args.output, args.frames
)
print(f"Generated {len(slots)} slot proposals.")
print(f"Saved to: {args.output}")
