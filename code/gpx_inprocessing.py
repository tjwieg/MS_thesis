#!/usr/bin/python3
# 2024-07-01 TJ Wiegman
# Uses `gopro2gpx` (from https://github.com/juanmcasillas/gopro2gpx)
# to get GPS time for each frame of gopro video

import cv2, json, os, subprocess, sys
import xml.etree.ElementTree as ET

def main(infile: str):
    # Scrub input file names
    if len(infile.split(".")) >= 2:
        name,_ = "".join(infile.split(".")[:-1]), infile.split(".")[-1]
    else: name = infile

    # Get video frame count
    cap = cv2.VideoCapture(infile)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Generate gpx file
    proc = subprocess.run(["gopro2gpx", infile, os.path.join("/tmp", name)], capture_output=True)
    if proc.returncode != 0: # if it fails, bail
        print(f"Failed to extract GPS from {infile}. Output stderr:")
        print(proc.stderr.decode("UTF-8"))
        sys.exit()
    else:
        for line in proc.stdout.decode("UTF-8").splitlines()[-7:]:
            print(line) # ^^ [-7:] = only print the summary stats at the end
    os.remove(os.path.join("/tmp", name + ".kml"))

    # Get list of points from gpx
    tree = ET.parse(os.path.join("/tmp", name + ".gpx"))
    os.remove(os.path.join("/tmp", name + ".gpx"))
    root = tree.getroot()
    track, segment = False, False
    for child in root:
        if child.tag[-3:] == "trk":
            track = child
    if not track:
        print(f"Couldn't find track in GPX for {infile}")
        sys.exit()
    for child in track:
        if child.tag[-6:] == "trkseg":
            segment = child
    if not segment:
        print(f"Couldn't find track segment in GPX for {infile}")
        sys.exit()
    
    # Serialize GPS points neatly
    tracklist = []
    oldtime = ""
    skip = 0
    for i in range(len(segment)):
        point = segment[i]
        gpstime = None
        for child in point:
            if child.tag[-4:] == "time": gpstime = child.text
        if oldtime == gpstime:
            print(f"Frame {i} is a duplicate of {i-1}: skipping...")
            skip += 1
        else:
            tracklist.append({
                "frame": i - skip,
                "cam_gps": point.attrib,
                "gps_time": gpstime
            })
        oldtime = gpstime
    
    # Get timestamp of first GPS point
    startTime = tracklist[0]["gps_time"] # ex: 2024-05-05T20:43:28.764000Z
    date, time = startTime.split("T")
    time, utc = time.split(".")
    if utc[-1] == "Z": utc = -4 # need to subtract 4 from zulu time for EDT
    else: utc = 0 # unless it's already localized
    hh, mm, ss = time.split(":")
    ext = infile.split(".")[-1]
    newName = f"{date}_{((utc + int(hh)) % 24):02}{int(mm):02}{int(ss):02}"

    # Error Checking
    if skip > 1:
        print(f"WARNING: Found {skip} duplicate points, data may be corrupted!")
        newName = "ERR_" + newName # Flag the filename for bad GPS
    if len(tracklist) != n_frames:
        print(f"WARNING: {infile} has {n_frames} frames, but found only {len(tracklist)} GPS points!")
        if abs(len(tracklist) - n_frames) > 2: # In non-negligible cases, flag the filename
            newName = "WRN_" + newName
    
    # Export JSON with GPS information
    with open(newName + ".json", "w") as file:
        json.dump(tracklist, file)
    
    # Rename the input video file with timestamp
    newName = ".".join([newName, ext])
    if newName != infile:
        if os.path.exists(newName):
            print(f"ERROR: Wanted to rename `{infile}` to `{newName}`, but `{newName}` already exists!")
        else:
            os.rename(infile, newName)
            print(f"Renamed `{infile}` to `{newName}` successfully!")
    else:
        print(f"Input file `{infile}` already has the right name. No changes needed :)")


if __name__ == "__main__":
    # get input filename
    if len(sys.argv) > 1: infile = sys.argv[1]
    else:
        print("ERROR: Must provide input video!")
        raise ValueError

    # help script
    if infile in ["-h", "--help"]:
        print("usage: gps_time.py [file]")
        print("options:")
        print("\t-h, --help \tshow this message and exit")
        sys.exit()
    
    # check if input file exists
    if not os.path.exists(infile):
        print(f"ERROR: Video {infile} does not exist!")
        raise ValueError
    
    main(infile)
