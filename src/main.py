import pygame
import sys
import math
import cv2
import numpy as np
import threading
import time

# Initialize Pygame
pygame.init()

info = pygame.display.Info()
width_screen = info.current_w
height_screen = info.current_h
res_screen = (width_screen, height_screen)

screen = pygame.display.set_mode(res_screen)

ball_color = (255, 0, 0)
rect_color = (0, 255, 0)
background_color = (255, 255, 255)

ball_radius = 10
gravity = 0.25
bounciness = 0.85
friction = 0.998
sub_steps = 3

balls = []
obstacles = []
obstacles_lock = threading.Lock()


def add_rect(cx, cy, w, h, angle_deg):
    obstacles.append({
        'cx': cx,
        'cy': cy,
        'w': w,
        'h': h,
        'angle': math.radians(angle_deg)
    })


def spawn_balls(n):
    for _ in range(n):
        angle = math.radians(45)
        speed = 5.0
        balls.append({
            'x': width_screen / 2,
            'y': 10,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'color': ball_color
        })


# --- CALIBRATION CONFIG ---
screen_pts = np.array([
    [0, 0],
    [width_screen, 0],
    [width_screen, height_screen],
    [0, height_screen]
], dtype=np.float32)

clicked_pts = []
M_homography = None
calibrated = False


def calibration_click(event, x, y, flags, param):
    global clicked_pts, M_homography, calibrated
    if event == cv2.EVENT_LBUTTONDOWN and not calibrated:
        clicked_pts.append([x, y])
        print(f"Captured Corner {len(clicked_pts)}: [{x}, {y}]")
        if len(clicked_pts) == 4:
            camera_pts = np.array(clicked_pts, dtype=np.float32)
            M_homography = cv2.getPerspectiveTransform(camera_pts, screen_pts)
            calibrated = True
            print("--- CALIBRATION SUCCESSFUL! ---")


# Initialize Camera

cam_index = 0

cam = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow('res')
cv2.setMouseCallback('res', calibration_click)

# --- BACKGROUND CAMERA STREAM THREAD ---
running = True
latest_frame = None
frame_lock = threading.Lock()


def camera_capture_thread():
    global latest_frame, running
    while running:
        ret, frame = cam.read()
        if ret and frame is not None:
            with frame_lock:
                latest_frame = frame
        else:
            time.sleep(0.01)


# --- BACKGROUND COMPUTER VISION WORKER ---
def vision_processing_thread():
    global obstacles, running
    local_obstacles = []

    while running:
        # Don't do any background calculations until calibration is completely finished
        if not calibrated or latest_frame is None:
            time.sleep(0.05)
            continue

        with frame_lock:
            img_copy = latest_frame.copy()

        # Downsample frame natively for speed processing
        small_frame = cv2.resize(img_copy, (426, 240), interpolation=cv2.INTER_NEAREST)
        hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([100, 150, 60])
        upper_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        local_obstacles.clear()

        scale_mat = np.array([[3.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
        M_homography_scaled = M_homography @ scale_mat

        for cnt in contours:
            if cv2.contourArea(cnt) < 30:
                continue

            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.array([box], dtype=np.float32)

            warped_box = cv2.perspectiveTransform(box, M_homography_scaled)[0]
            rect_scaled = cv2.minAreaRect(warped_box)
            (cx_scaled, cy_scaled), (w_scaled, h_scaled), angle = rect_scaled

            local_obstacles.append({
                'cx': cx_scaled, 'cy': cy_scaled,
                'w': w_scaled, 'h': h_scaled,
                'angle': math.radians(angle)
            })

        with obstacles_lock:
            obstacles = list(local_obstacles)

        time.sleep(0.015)  # Caps background processing loop rate safely


# Fire up background threads
cap_t = threading.Thread(target=camera_capture_thread, daemon=True)
vis_t = threading.Thread(target=vision_processing_thread, daemon=True)
cap_t.start()
vis_t.start()

clock = pygame.time.Clock()

while True:
    with frame_lock:
        frame = latest_frame.copy() if latest_frame is not None else np.zeros((720, 1280, 3), dtype=np.uint8)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            cam.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            spawn_balls(1)
    # spawn_balls(1)

    # --- OpenCV MAIN WINDOW HANDLING ---
    # FIXED: The main loop now handles all window draws and waitKeys to prevent UI deadlocks
    if not calibrated:
        debug_frame = frame.copy()
        msg = "Click 4 corners of PROJECTED SCREEN boundary"
        cv2.putText(debug_frame, msg, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        for pt in clicked_pts:
            cv2.circle(debug_frame, tuple(pt), 6, (0, 0, 255), -1)
        cv2.imshow('res', debug_frame)
    else:
        # After calibration, display the optimized low-res camera feed window
        small_display = cv2.resize(frame, (426, 240), interpolation=cv2.INTER_NEAREST)
        cv2.imshow('res', small_display)

    cv2.waitKey(1)

    if not calibrated:
        screen.fill((200, 200, 200))
        pygame.display.flip()
        clock.tick(60)
        continue

    # --- LIVE PHYSICS RUNTIME ---
    with obstacles_lock:
        active_obstacles = list(obstacles)

    obs_trig = [(obs, math.cos(obs['angle']), math.sin(obs['angle']), math.cos(-obs['angle']), math.sin(-obs['angle']))
                for obs in active_obstacles]

    for ball in balls[:]:
        ball['vy'] += gravity
        ball['vx'] *= friction
        dt = 1.0 / sub_steps
        alive = True

        for _ in range(sub_steps):
            if not alive:
                break
            ball['x'] += ball['vx'] * dt
            ball['y'] += ball['vy'] * dt

            if ball['x'] - ball_radius <= 0:
                ball['x'] = ball_radius
                ball['vx'] = -ball['vx'] * bounciness
            elif ball['x'] + ball_radius >= width_screen:
                ball['x'] = width_screen - ball_radius
                ball['vx'] = -ball['vx'] * bounciness

            if ball['y'] + ball_radius >= height_screen:
                if ball in balls:
                    balls.remove(ball)
                alive = False
                break

            if ball['y'] - ball_radius <= 0:
                ball['y'] = ball_radius
                ball['vy'] = -ball['vy'] * bounciness

            for obs, cos_r, sin_r, cos_a, sin_a in obs_trig:
                dx = ball['x'] - obs['cx']
                dy = ball['y'] - obs['cy']
                local_x = dx * cos_a - dy * sin_a
                local_y = dx * sin_a + dy * cos_a
                half_w, half_h = obs['w'] / 2, obs['h'] / 2

                if abs(local_x) > half_w + ball_radius or abs(local_y) > half_h + ball_radius:
                    continue

                closest_x = max(-half_w, min(local_x, half_w))
                closest_y = max(-half_h, min(local_y, half_h))
                dist_x = local_x - closest_x
                dist_y = local_y - closest_y
                distance = math.hypot(dist_x, dist_y)

                if distance < ball_radius:
                    if distance == 0:
                        world_normal_x, world_normal_y = -sin_r, cos_r
                        overlap = ball_radius
                    else:
                        world_normal_x = (dist_x / distance) * cos_r - (dist_y / distance) * sin_r
                        world_normal_y = (dist_x / distance) * sin_r + (dist_y / distance) * cos_r
                        overlap = ball_radius - distance

                    ball['x'] += world_normal_x * (overlap + 0.05)
                    ball['y'] += world_normal_y * (overlap + 0.05)
                    dot_product = ball['vx'] * world_normal_x + ball['vy'] * world_normal_y
                    if dot_product < 0:
                        vn_x, vn_y = dot_product * world_normal_x, dot_product * world_normal_y
                        vt_x, vt_y = ball['vx'] - vn_x, ball['vy'] - vn_y
                        if abs(dot_product) < 0.6:
                            ball['vx'], ball['vy'] = vt_x * 0.90, vt_y * 0.90
                        else:
                            ball['vx'] = vt_x * 0.98 - vn_x * bounciness
                            ball['vy'] = vt_y * 0.98 - vn_y * bounciness

    # --- PYGAME WINDOW RENDERING ---
    screen.fill(background_color)

    transparent_surface = pygame.Surface(res_screen, pygame.SRCALPHA)
    for obs in active_obstacles:
        half_w = obs['w'] / 2
        half_h = obs['h'] / 2
        local_points = [(-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)]
        world_points = []
        cos_a, sin_a = math.cos(obs['angle']), math.sin(obs['angle'])
        for px, py in local_points:
            wx = obs['cx'] + (px * cos_a - py * sin_a)
            wy = obs['cy'] + (px * sin_a + py * cos_a)
            world_points.append((int(wx), int(wy)))

        pygame.draw.polygon(transparent_surface, (rect_color[0], rect_color[1], rect_color[2], 100), world_points)

    screen.blit(transparent_surface, (0, 0))

    for ball in balls:
        pygame.draw.circle(screen, ball['color'], (int(ball['x']), int(ball['y'])), ball_radius)

    pygame.display.flip()
    clock.tick(60)