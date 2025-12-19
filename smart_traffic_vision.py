import cv2
import numpy as np
import torch
import time
from ultralytics import YOLO

class SmartTrafficVision:

    class Lane:
        def __init__(self, lane_id, polygon, color):
            self.lane_id = lane_id
            self.polygon = np.array(polygon, np.int32)
            self.current_ids = set()
            self.color = color

        def contains(self, point):
            return cv2.pointPolygonTest(self.polygon, point, False) >= 0

    class Vehicle:
        def __init__(self, track_id, bbox):
            self.id = track_id
            self.bbox = bbox

        def center(self):
            x1, y1, x2, y2 = self.bbox
            return int((x1 + x2) / 2), int((y1 + y2) / 2)

    def __init__(self, lanes):
        colors = [
            (255, 100, 100),
            (100, 255, 100),
            (100, 100, 255),
            (255, 255, 100),
            (255, 100, 255),
            (100, 255, 255),
            (200, 150, 100),
            (150, 200, 150),
        ]

        self.lanes = []
        for i, (lane_id, polygon) in enumerate(lanes):
            self.lanes.append(self.Lane(lane_id, polygon, colors[i % len(colors)]))

    def _get_lane(self, point):
        for lane in self.lanes:
            if lane.contains(point):
                return lane
        return None

    def process_frame(self, frame, vehicles):
        for lane in self.lanes:
            lane.current_ids.clear()

        for v in vehicles:
            cx, cy = v.center()
            lane = self._get_lane((cx, cy))
            if lane:
                lane.current_ids.add(v.id)

        self.draw(frame, vehicles)
        return frame

    def get_lane_counts(self):
        return {f"Lane {lane.lane_id}": len(lane.current_ids) for lane in self.lanes}

    def draw(self, frame, vehicles):
        overlay = frame.copy()

        for lane in self.lanes:
            cv2.fillPoly(overlay, [lane.polygon], lane.color)
            cv2.polylines(frame, [lane.polygon], True, lane.color, 3)

            M = cv2.moments(lane.polygon)
            cx = int(M["m10"] / M["m00"]) if M["m00"] else lane.polygon[0][0]
            cy = int(M["m01"] / M["m00"]) if M["m00"] else lane.polygon[0][1]

            cv2.putText(frame, f"{lane.lane_id}", (cx - 15, cy + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

            cv2.putText(frame, f"{len(lane.current_ids)}", (cx - 25, cy - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 4)

        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        for v in vehicles:
            x1, y1, x2, y2 = v.bbox
            cx, cy = v.center()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)