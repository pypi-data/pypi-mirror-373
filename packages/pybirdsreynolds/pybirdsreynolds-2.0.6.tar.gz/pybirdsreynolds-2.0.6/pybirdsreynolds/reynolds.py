import math
import random
import pybirdsreynolds.const as const
import pybirdsreynolds.params as params
import pybirdsreynolds.variables as variables
from scipy.spatial import cKDTree

birds = []
velocities = []


def limit_speed(vx, vy):
    speed = math.sqrt(vx * vx + vy * vy)
    if speed > params.MAX_SPEED:
        vx = (vx / speed) * params.MAX_SPEED
        vy = (vy / speed) * params.MAX_SPEED
    return vx, vy


def move_birds(with_move, translate):
    if not birds or birds == []:
        for _ in range(params.NUM_BIRDS):
            px = random.randint(
                const.MARGIN + variables.WIDTH_CONTROLS,
                params.WIDTH - const.MARGIN + variables.WIDTH_CONTROLS,
            )
            py = random.randint(const.MARGIN, params.HEIGHT - const.MARGIN)
            birds.append((px, py))
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0, params.MAX_SPEED)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            velocities.append((vx, vy))
    else:
        if translate:
            for i in range(len(birds)):
                x, y = birds[i]
                if variables.HIDDEN:
                    birds[i] = (x - const.WIDTH_CONTROLS_DEFAULT, y)
                else:
                    birds[i] = (x + const.WIDTH_CONTROLS_DEFAULT, y)
        # Keep birds only if inside
        inside_points = []
        inside_velocities = []
        for (x, y), (vx, vy) in zip(birds, velocities):
            if (
                variables.WIDTH_CONTROLS + const.MARGIN
                <= x
                <= variables.WIDTH_CONTROLS + params.WIDTH - const.MARGIN
                and 0 + const.MARGIN <= y <= params.HEIGHT - const.MARGIN
            ):
                inside_points.append((x, y))
                inside_velocities.append((vx, vy))
        birds[:] = inside_points
        velocities[:] = inside_velocities
        variables.COUNT = len(birds)

        # Add birds if not enough
        if params.NUM_BIRDS > variables.COUNT:
            for _ in range(params.NUM_BIRDS - variables.COUNT):
                px = random.randint(
                    const.MARGIN + variables.WIDTH_CONTROLS,
                    params.WIDTH - const.MARGIN + variables.WIDTH_CONTROLS,
                )
                py = random.randint(const.MARGIN, params.HEIGHT - const.MARGIN)
                birds.append((px, py))

                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, params.MAX_SPEED)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        # Delete birds if not enough
        elif params.NUM_BIRDS < variables.COUNT:
            for _ in range(variables.COUNT - params.NUM_BIRDS):
                idx = random.randint(0, len(birds) - 1)
                birds.pop(idx)
                velocities.pop(idx)

        if with_move:
            tree = cKDTree(birds)
            new_velocities = []
            for i, (x, y) in enumerate(birds):
                move_sep_x, move_sep_y = 0, 0
                move_align_x, move_align_y, move_align_x_tmp, move_align_y_tmp = (
                    0,
                    0,
                    0,
                    0,
                )
                move_coh_x, move_coh_y, move_coh_x_tmp, move_coh_y_tmp = 0, 0, 0, 0
                neighbors = 0
                vx, vy = velocities[i]
                if params.NEIGHBOR_RADIUS > 0 and not (
                    params.SEP_WEIGHT == 0
                    and params.ALIGN_WEIGHT == 0
                    and params.COH_WEIGHT == 0
                ):
                    neighbors_idx = tree.query_ball_point(
                        [x, y], params.NEIGHBOR_RADIUS
                    )
                    for j in neighbors_idx:
                        if i == j:
                            continue

                        x2, y2 = birds[j]
                        vx2, vy2 = velocities[j]
                        dx, dy = x - x2, y - y2
                        radius2 = params.NEIGHBOR_RADIUS**2
                        dist2 = dx * dx + dy * dy
                        if 0 < dist2 < radius2:
                            dist = math.sqrt(dist2)
                            # SEPARATION
                            # If a neighbor is too close, add a vector to move away from it (opposite direction of the neighbor).
                            move_sep_x += (x - x2) / dist
                            move_sep_y += (y - y2) / dist
                            # ALIGNMENT
                            # Add the neighbor's velocity so the bird tends to align with it.
                            # Division is done later
                            vx2, vy2 = velocities[j]
                            move_align_x_tmp += vx2
                            move_align_y_tmp += vy2
                            # COHESION
                            # Add the neighbor's position to later calculate an average point,
                            # so the bird moves toward the group's center.
                            # Division is done later
                            move_coh_x_tmp += x2
                            move_coh_y_tmp += y2
                            neighbors += 1

                    if neighbors > 0:
                        move_align_x = move_align_x_tmp / neighbors
                        move_align_y = move_align_y_tmp / neighbors
                        move_coh_x = move_coh_x_tmp / neighbors
                        move_coh_y = move_coh_y_tmp / neighbors
                        move_coh_x = move_coh_x - x
                        move_coh_y = move_coh_y - y

                    vx += (
                        params.SEP_WEIGHT * move_sep_x
                        + params.ALIGN_WEIGHT * move_align_x
                        + params.COH_WEIGHT * move_coh_x
                    )
                    vy += (
                        params.SEP_WEIGHT * move_sep_y
                        + params.ALIGN_WEIGHT * move_align_y
                        + params.COH_WEIGHT * move_coh_y
                    )

                # RANDOM
                speed = math.sqrt(vx**2 + vy**2)
                if params.RANDOM_SPEED != 0:
                    target_speed = params.MAX_SPEED / 2
                    sigma_percent = params.RANDOM_SPEED
                    adjust_strength = 0.05
                    sigma_base = (sigma_percent / 100) * params.MAX_SPEED
                    weight = (
                        4 * speed * (params.MAX_SPEED - speed) / (params.MAX_SPEED**2)
                    )
                    sigma = sigma_base * weight
                    delta_speed = random.gauss(0, sigma)
                    new_speed = speed + delta_speed
                    new_speed += (target_speed - new_speed) * adjust_strength
                    new_speed = max(0.1, min(params.MAX_SPEED, new_speed))
                    factor = new_speed / speed
                    vx *= factor
                    vy *= factor
                if params.RANDOM_ANGLE != 0:
                    angle = math.atan2(vy, vx)
                    angle += math.radians(
                        random.uniform(-1 * params.RANDOM_ANGLE, params.RANDOM_ANGLE)
                    )
                    speed = math.sqrt(vx**2 + vy**2)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                vx, vy = limit_speed(vx, vy)

                new_velocities.append((vx, vy))

            # Update positions
            new_points = []
            for (x, y), (vx, vy) in zip(birds, new_velocities):
                nx = x + vx
                ny = y + vy
                # Bounces
                while (
                    nx < const.MARGIN + variables.WIDTH_CONTROLS
                    or nx > params.WIDTH - const.MARGIN + variables.WIDTH_CONTROLS
                ):
                    if nx < const.MARGIN + variables.WIDTH_CONTROLS:
                        overshoot = (const.MARGIN + variables.WIDTH_CONTROLS) - nx
                        nx = (const.MARGIN + variables.WIDTH_CONTROLS) + overshoot
                        vx = abs(vx)
                    elif nx > params.WIDTH - const.MARGIN + variables.WIDTH_CONTROLS:
                        overshoot = nx - (
                            params.WIDTH - const.MARGIN + variables.WIDTH_CONTROLS
                        )
                        nx = (
                            params.WIDTH - const.MARGIN + variables.WIDTH_CONTROLS
                        ) - overshoot
                        vx = -abs(vx)
                while ny < const.MARGIN or ny > params.HEIGHT - const.MARGIN:
                    if ny < const.MARGIN:
                        overshoot = const.MARGIN - ny
                        ny = const.MARGIN + overshoot
                        vy = abs(vy)
                    elif ny > params.HEIGHT - const.MARGIN:
                        overshoot = ny - (params.HEIGHT - const.MARGIN)
                        ny = (params.HEIGHT - const.MARGIN) - overshoot
                        vy = -abs(vy)
                idx = birds.index((x, y))
                velocities[idx] = (vx, vy)
                new_points.append((nx, ny))
            birds[:] = new_points
    if birds:
        variables.AVG_X = sum(x for x, _ in birds) / len(birds)
        variables.AVG_Y = sum(y for _, y in birds) / len(birds)
        variables.AVG_SPEED_ABS = sum(
            math.sqrt(vx**2 + vy**2) for vx, vy in velocities
        ) / len(velocities)
        variables.AVG_VX = sum(vx for vx, _ in velocities) / len(velocities)
        variables.AVG_VY = sum(vy for _, vy in velocities) / len(velocities)
