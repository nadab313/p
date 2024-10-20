# simulation.py
import pygame
import numpy as np
from constants import BLACK, WHITE

class Particle:
    def __init__(self, position, velocity, mass, radius):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.mass = mass
        self.radius = radius

    def move(self, dt):
        self.position += self.velocity * dt

    def wall_collision(self, box_size):
        impulse = 0.0
        for i in range(2):
            if self.position[i] - self.radius < 0:
                self.position[i] = self.radius
                self.velocity[i] = -self.velocity[i]
                impulse += 2 * abs(self.mass * self.velocity[i])
            elif self.position[i] + self.radius > box_size:
                self.position[i] = box_size - self.radius
                self.velocity[i] = -self.velocity[i]
                impulse += 2 * abs(self.mass * self.velocity[i])
        return impulse

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self.position.astype(int), self.radius)


class Simulation:
    def __init__(self, num_particles, box_size, particle_radius, temperature, dt, total_steps):
        self.num_particles = num_particles
        self.box_size = box_size
        self.particle_radius = particle_radius
        self.temperature = temperature
        self.dt = dt
        self.total_steps = total_steps

        self.mass = 1.0       # Mass of particles
        self.kb = 1.0         # Boltzmann constant
        self.display_stats = True

        self.particles = []
        self.initialize_particles()

        self.times = []
        self.temperatures = []
        self.pressures = []

        # Screen setup
        self.screen = pygame.display.set_mode((box_size, box_size))
        pygame.display.set_caption('Ideal Gas Simulation')

    def initialize_particles(self):
        positions = self.initialize_positions()
        velocities = self.initialize_velocities()
        for pos, vel in zip(positions, velocities):
            particle = Particle(pos, vel, self.mass, self.particle_radius)
            self.particles.append(particle)

    def initialize_positions(self):
        positions = []
        attempts = 0
        max_attempts = self.num_particles * 100
        while len(positions) < self.num_particles and attempts < max_attempts:
            new_pos = np.random.uniform(self.particle_radius, self.box_size - self.particle_radius, 2)
            if all(np.linalg.norm(new_pos - pos) >= 2 * self.particle_radius for pos in positions):
                positions.append(new_pos)
            attempts += 1
        if attempts == max_attempts:
            print("Warning: Could not place all particles without overlap.")
        return positions

    def initialize_velocities(self):
        std_dev = np.sqrt(self.kb * self.temperature / self.mass)
        velocities = np.random.normal(0, std_dev, (self.num_particles, 2))
        return velocities

    def run(self):
        clock = pygame.time.Clock()
        step = 0

        while step < self.total_steps:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Clear screen
            self.screen.fill(BLACK)

            # Update positions
            for particle in self.particles:
                particle.move(self.dt)

            # Reset wall collision impulse
            wall_collision_impulse = 0.0

            # Collision detection with walls
            for particle in self.particles:
                impulse = particle.wall_collision(self.box_size)
                wall_collision_impulse += impulse

            # Collision detection between particles
            self.handle_particle_collisions()

            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)

            # Calculate statistics
            current_time = step * self.dt
            kinetic_energy = 0.5 * sum(p.mass * np.linalg.norm(p.velocity) ** 2 for p in self.particles)
            current_temperature = kinetic_energy / (self.num_particles * self.kb)
            self.temperatures.append(current_temperature)
            self.times.append(current_time)

            pressure = wall_collision_impulse / (self.dt * 4 * self.box_size)
            self.pressures.append(pressure)

            if self.display_stats:
                # Display temperature and pressure
                font = pygame.font.SysFont('Arial', 18)
                temp_text = font.render(f'Temperature: {current_temperature:.2f}', True, WHITE)
                pres_text = font.render(f'Pressure: {pressure:.2f}', True, WHITE)
                particle_text = font.render(f'Particles: {self.num_particles}', True, WHITE)
                self.screen.blit(temp_text, (10, 10))
                self.screen.blit(pres_text, (10, 30))
                self.screen.blit(particle_text, (10, 50))

            pygame.display.flip()
            clock.tick(60)  # Limit to 60 FPS
            step += 1

        pygame.quit()
        self.plot_results()

    def handle_particle_collisions(self):
        # Spatial partitioning grid
        grid_size = 20  # Adjust grid size for performance
        cell_size = self.box_size / grid_size
        grid_cells = [[[] for _ in range(grid_size)] for _ in range(grid_size)]

        # Assign particles to grid cells
        for idx, particle in enumerate(self.particles):
            x_cell = int(particle.position[0] / cell_size)
            y_cell = int(particle.position[1] / cell_size)
            grid_cells[x_cell % grid_size][y_cell % grid_size].append(idx)

        # Collision detection between particles using spatial partitioning
        for x in range(grid_size):
            for y in range(grid_size):
                # Get particles in the current cell and neighboring cells
                nearby_cells = [(x + dx) % grid_size for dx in (-1, 0, 1)]
                nearby_cells = [(xc, (y + dy) % grid_size) for xc in nearby_cells for dy in (-1, 0, 1)]
                cell_particles = []
                for xc, yc in nearby_cells:
                    cell_particles.extend(grid_cells[xc][yc])
                # Check collisions among particles in cell_particles
                for i_idx in grid_cells[x][y]:
                    for j_idx in cell_particles:
                        if i_idx < j_idx:
                            p1 = self.particles[i_idx]
                            p2 = self.particles[j_idx]
                            delta_pos = p1.position - p2.position
                            dist_sq = np.dot(delta_pos, delta_pos)
                            min_dist = p1.radius + p2.radius
                            if dist_sq <= min_dist ** 2:
                                distance = np.sqrt(dist_sq)
                                if distance == 0:
                                    # Prevent division by zero
                                    distance = min_dist
                                    delta_pos = min_dist * np.random.uniform(-1, 1, size=2)
                                overlap = 0.5 * (min_dist - distance)
                                correction = (overlap / distance) * delta_pos
                                p1.position += correction
                                p2.position -= correction

                                # Update velocities
                                delta_vel = p1.velocity - p2.velocity
                                norm_delta_pos = delta_pos / distance
                                rel_vel = np.dot(delta_vel, norm_delta_pos)
                                if rel_vel < 0:
                                    m1 = p1.mass
                                    m2 = p2.mass
                                    impulse = (2 * rel_vel) / (1 / m1 + 1 / m2)
                                    p1.velocity -= (impulse / m1) * norm_delta_pos
                                    p2.velocity += (impulse / m2) * norm_delta_pos

    def plot_results(self):
        # Plot final statistics using Matplotlib
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(2, 1, figsize=(8, 8))

        # Temperature plot
        axs[0].plot(self.times, self.temperatures, 'r-')
        axs[0].set_title('Temperature Over Time')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Temperature')

        # Pressure plot
        axs[1].plot(self.times, self.pressures, 'g-')
        axs[1].set_title('Pressure Over Time')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Pressure')

        plt.tight_layout()
        plt.show()
