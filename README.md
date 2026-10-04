# Smart Parking Analyzer — Advanced Edition

This project adds:

- Live CCTV / RTSP / webcam support
- Automatic parking-slot proposal/calibration
- SQLite database
- Login and role-based admin dashboard
- Parking history and occupancy graphs
- Vehicle tracking
- Number-plate recognition using EasyOCR
- Parking sessions
- CSV export
- Camera management
- Manual slot correction after automatic calibration

## Important design note

Automatic parking-space discovery from a normal CCTV camera is not mathematically guaranteed from one frame, because empty spaces contain no visual object that uniquely identifies their boundaries.

This implementation therefore performs **automatic calibration**:

1. It samples several frames from the camera/video.
2. YOLO detects vehicles.
3. Vehicle-center positions are clustered.
4. Stable parking positions are converted into proposed parking polygons.
5. The administrator can review or edit the generated `slots.json`.

This is a practical approach for a student/project deployment. For a production system, train a parking-slot segmentation/detection model on the target car park.

## Architecture

```text
                  +--------------------+
                  | CCTV / RTSP / File |
                  +----------+---------+
                             |
                             v
                    +----------------+
                    | OpenCV Capture |
                    +-------+--------+
                            |
                            v
                    +---------------+
                    | YOLO Detection|
                    +-------+-------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
        Parking Occupancy          Plate Crop
                |                       |
                v                       v
        Slot State Engine           EasyOCR
                |                       |
                +-----------+-----------+
                            |
                            v
                    +---------------+
                    | SQLite / ORM   |
                    +-------+-------+
                            |
                            v
                    +---------------+
                    | Streamlit UI   |
                    +---------------+
```

## Installation

Use Python 3.10 or 3.11.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Start the application

```bash
streamlit run app.py
```

On first startup, the application creates:

```text
parking.db
```

Default administrator:

```text
username: admin
password: admin123
```

Change this password before real deployment.

## Add a CCTV camera

In the sidebar, use:

```text
0
```

for the first local webcam.

For an IP camera:

```text
rtsp://username:password@192.168.1.50:554/stream1
```

For a video file:

```text
data/videos/parking.mp4
```

For a browser-accessible MJPEG/HLS source, support depends on OpenCV/FFmpeg and the camera's stream format.

## Automatic slot calibration

Run:

```bash
python scripts/auto_calibrate.py --source data/videos/parking.mp4 --output data/slots/slots.json --frames 40
```

For an RTSP camera:

```bash
python scripts/auto_calibrate.py --source "rtsp://user:password@CAMERA_IP:554/stream1" --output data/slots/slots.json --frames 80
```

The script creates a slot proposal file.

Because this is an automatic proposal system, inspect the generated slots before deployment. You can use:

```bash
python scripts/edit_slots.py --image data/snapshots/calibration.jpg --slots data/slots/slots.json
```

Controls in the editor:

- Click 4 points to create a slot
- `n` save current slot
- `r` reset
- `u` undo
- `d` delete the last slot
- `q` save and quit

## Run live monitoring

Log in as admin, go to **Live Monitor**, select a camera/source and start monitoring.

The system:

1. Reads frames.
2. Runs YOLO.
3. Tracks vehicles.
4. Calculates parking occupancy.
5. Extracts possible plate regions.
6. Runs OCR.
7. Saves occupancy snapshots and parking events.
8. Updates the dashboard.

## Number plate recognition

EasyOCR is used because it is straightforward to install and works on many Latin/English-style plates.

For higher accuracy on Indian number plates, production deployment should replace the generic OCR stage with:

```text
vehicle detection
    ->
plate detection model trained for Indian plates
    ->
plate rectification
    ->
EasyOCR / PaddleOCR / specialized OCR
    ->
regex validation
```

A generic OCR model should not be treated as an authoritative registration-number reader.

## Database

SQLite tables:

- users
- cameras
- parking_events
- occupancy_snapshots
- plate_reads

The ORM models are in:

```text
src/database.py
```

## Dashboard

The admin dashboard displays:

- current occupancy
- free spaces
- occupied spaces
- average occupancy
- peak occupancy
- recent plate reads
- parking events
- hourly occupancy history
- daily occupancy history
- camera list

## CSV export

The admin dashboard provides CSV downloads for:

- occupancy history
- parking events
- plate reads

## Security before deployment

The supplied project is a learning/demo implementation.

Before production:

- Change the default password.
- Store passwords with a managed identity provider or stronger password policy.
- Use HTTPS.
- Put credentials in environment variables/secrets.
- Restrict RTSP credentials.
- Do not expose SQLite over the network.
- Add retention policies for plate data.
- Follow applicable privacy/data-protection rules.
- Restrict admin access.
- Encrypt sensitive data at rest where appropriate.

## Useful tuning

`src/config.py`:

```python
YOLO_MODEL = "yolo26n.pt"
CONFIDENCE = 0.30
OCCUPANCY_THRESHOLD = 0.20
PROCESS_EVERY_N_FRAMES = 2
PLATE_OCR_INTERVAL_SECONDS = 2.0
```

For more accuracy, change to a larger YOLO model, but inference will be slower.

## Running the included test

```bash
python -m compileall .
```

## Suggested final-year-project modules

1. Authentication
2. Camera management
3. Automatic calibration
4. Vehicle detection
5. Vehicle tracking
6. Parking occupancy
7. Number-plate OCR
8. Database
9. Historical analytics
10. Admin dashboard

## Future upgrades

- PostgreSQL
- Redis task queue
- FastAPI backend
- React frontend
- Multi-camera processing
- WebSocket live updates
- Indian plate detector
- Parking reservation
- QR payment
- Mobile application
- Edge deployment on Jetson/Raspberry Pi
