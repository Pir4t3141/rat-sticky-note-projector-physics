import pygame
import sys
import math
import cv2
import numpy as np

pygame.init()

info = pygame.display.Info()
width_screen = info.current_w
height_screen = info.current_h

res_screen = (width_screen, height_screen)
screen = pygame.display.set_mode(res_screen)
#screen = pygame.display.set_mode(res_screen, pygame.FULLSCREEN)

ball_color = (255, 0, 0)
rect_color = (0, 255, 0)
background_color = (255, 255, 255)
background_image = pygame.image.load('training_image_1.jpg')

ball_radius = 10
gravity = 0.25
bounciness = 0.85
friction = 0.998
spawn_count = 1
sub_steps = 10

balls = []
obstacles = []


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


#add_rect(width_screen / 2 - 300, height_screen / 2 + 200, 400, 30, 20)
#add_rect(width_screen / 2 + 300, height_screen / 2 + 350, 400, 30, -20)
#add_rect(width_screen / 2, height_screen - 250, 800, 40, 0)

clock = pygame.time.Clock()
ticks_since_last_ball_spawn = 60

cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)

while True:
    ret,frame = cam.read()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            spawn_balls(1)

    if ticks_since_last_ball_spawn >= 60:
        ticks_since_last_ball_spawn = 0
        #spawn_balls(spawn_count)
    else:
        ticks_since_last_ball_spawn += 1

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

            for obs in obstacles:
                dx = ball['x'] - obs['cx']
                dy = ball['y'] - obs['cy']

                cos_a = math.cos(-obs['angle'])
                sin_a = math.sin(-obs['angle'])
                local_x = dx * cos_a - dy * sin_a
                local_y = dx * sin_a + dy * cos_a

                half_w = obs['w'] / 2
                half_h = obs['h'] / 2

                closest_x = max(-half_w, min(local_x, half_w))
                closest_y = max(-half_h, min(local_y, half_h))

                dist_x = local_x - closest_x
                dist_y = local_y - closest_y
                distance = math.hypot(dist_x, dist_y)

                if distance < ball_radius:
                    cos_r = math.cos(obs['angle'])
                    sin_r = math.sin(obs['angle'])

                    if distance == 0:
                        world_normal_x = -sin_r
                        world_normal_y = cos_r
                        overlap = ball_radius
                    else:
                        local_normal_x = dist_x / distance
                        local_normal_y = dist_y / distance
                        world_normal_x = local_normal_x * cos_r - local_normal_y * sin_r
                        world_normal_y = local_normal_x * sin_r + local_normal_y * cos_r
                        overlap = ball_radius - distance

                    ball['x'] += world_normal_x * (overlap + 0.05)
                    ball['y'] += world_normal_y * (overlap + 0.05)

                    dot_product = ball['vx'] * world_normal_x + ball['vy'] * world_normal_y
                    if dot_product < 0:
                        vn_x = dot_product * world_normal_x
                        vn_y = dot_product * world_normal_y

                        vt_x = ball['vx'] - vn_x
                        vt_y = ball['vy'] - vn_y

                        if abs(dot_product) < 0.6:
                            ball['vx'] = vt_x * 0.90
                            ball['vy'] = vt_y * 0.90

                            if abs(ball['vx']) < 0.1 and abs(ball['vy']) < 0.1:
                                ball['vx'] = 0.0
                                ball['vy'] = 0.0
                        else:
                            ball['vx'] = vt_x * 0.98 - vn_x * bounciness
                            ball['vy'] = vt_y * 0.98 - vn_y * bounciness

    img = frame

    img_h, img_w, _ = img.shape
    scale_x = width_screen / img_w
    scale_y = height_screen / img_h

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([95, 100, 100])

    upper_blue = np.array([115, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacles.clear()

    for cnt in contours:
        if cv2.contourArea(cnt) < 400:
            continue

        rect = cv2.minAreaRect(cnt)
        (cx, cy), (w, h), angle = rect

        cx_scaled = cx * scale_x
        cy_scaled = cy * scale_y
        w_scaled = w * scale_x
        h_scaled = h * scale_y

        add_rect(cx_scaled, cy_scaled, w_scaled, h_scaled, angle)

    res = cv2.bitwise_and(img,img, mask= mask)
    #cv2.imshow('frame',img)
    #cv2.imshow('mask',mask)
    cv2.imshow('res',res)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame_transposed = np.transpose(frame_rgb, (1, 0, 2))

    background_image = pygame.surfarray.make_surface(frame_transposed)
    background_image = pygame.transform.scale(background_image, (width_screen, height_screen))

    screen.fill(background_color)
    # screen.blit(background_image, (0, 0))

    for obs in obstacles:
        half_w = obs['w'] / 2
        half_h = obs['h'] / 2
        local_points = [
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h)
        ]

        world_points = []
        cos_a = math.cos(obs['angle'])
        sin_a = math.sin(obs['angle'])
        for px, py in local_points:
            wx = obs['cx'] + (px * cos_a - py * sin_a)
            wy = obs['cy'] + (px * sin_a + py * cos_a)
            world_points.append((wx, wy))

        pygame.draw.polygon(screen, rect_color, world_points)

    for ball in balls:
        pygame.draw.circle(screen, ball['color'], (int(ball['x']), int(ball['y'])), ball_radius)

    pygame.display.flip()
    clock.tick(60)