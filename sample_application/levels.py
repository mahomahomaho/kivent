from kivy.properties import (StringProperty, NumericProperty, BooleanProperty)
import random
import math
from kivent import (GameSystem)
from kivy.atlas import Atlas
from kivy.clock import Clock
from functools import partial

class LevelBoundaries(GameSystem):

    def generate_boundaries(self):
        gameworld = self.gameworld
        map_pos = gameworld.pos
        map_size = gameworld.currentmap.map_size
        pos = (map_pos[0] + .5*map_size[0], map_pos[1] + .5*map_size[1])
        shape_dict = {'width': map_size[0], 'height': map_size[1], 'mass': 0}
        col_shape_dict = {'shape_type': 'box', 
            'elasticity': 0.0, 'collision_type': 10, 
            'shape_info': shape_dict, 'friction': 0.0}
        physics_component_dict = {'main_shape': 'box', 'velocity': (0, 0), 
            'position': pos, 'angle':0, 'angular_velocity': 0,
            'mass': 0, 'vel_limit': 0, 'ang_vel_limit': 0, 
            'col_shapes': [col_shape_dict]}
        boundary_system = {}
        create_component_dict = {
            'position': pos,
            'rotate': 0.,
            'cymunk_physics': physics_component_dict, 
            'boundary_system': boundary_system}
        component_order = ['position', 'rotate', 
            'cymunk_physics', 'boundary_system']
        self.gameworld.init_entity(create_component_dict, component_order)

    def clear(self):
        for entity_id in self.entity_ids:
            Clock.schedule_once(partial(
                self.gameworld.timed_remove_entity, entity_id))

    def collision_separate_func(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        entity_id = arbiter.shapes[0].body.data
        entity = entities[entity_id]
        map_pos = gameworld.pos
        map_size = gameworld.currentmap.map_size
        mapw, maph = map_size
        physics_data = entity.cymunk_physics
        body = physics_data.body
        x_pos, y_pos = body.position
        if x_pos < map_pos[0] or x_pos > mapw:
            new_x = mapw - x_pos
        else:
            new_x = x_pos
        if y_pos < map_pos[1] or y_pos > maph:
            new_y = maph - y_pos
        else:
            new_y = y_pos
        body.position = (new_x, new_y)
        return False

    def collision_begin_func(self, space, arbiter):
        return False



class AsteroidsLevel(GameSystem):
    system_id = StringProperty('asteroids_level')
    current_level_id = NumericProperty(0)
    do_asteroids = BooleanProperty(False)
    do_probes = BooleanProperty(False)
    do_enemies = BooleanProperty(False)
    number_of_enemies_to_spawn = NumericProperty(0)

    def on_current_level_id(self, instance, value):
        if value >= 5:
            self.current_level_id = 0

    def generate_new_level(self, dt):
        level_win_conditions = [(False, True, False), (False, False, True), 
        (False, False, True), (False, True, True), (False, False, True)]
        level_number_of_enemies = [0, 1, 1, 2, 3]
        self.number_of_enemies_to_spawn = level_number_of_enemies[
            self.current_level_id]
        current_level_win_conditions = level_win_conditions[
            self.current_level_id]
        self.do_asteroids = current_level_win_conditions[0]
        self.do_probes = current_level_win_conditions[1]
        self.do_enemies = current_level_win_conditions[2]
        dust_choices_gold = [
        'stardust1bg', 
        'stardust4bg',
        'stardust7bg',
            ] 
        dust_choices_green = [
        'stardust2bg', 
        'stardust5bg',
            ]
        dust_choices_purple = [
        'stardust3bg',
            ]
        dust_choices_blue = [
        'stardust6bg', 
        'stardust8bg',
            ]
        star_choice_gold = ['star3', 'star7']
        star_choice_green = ['star5', 'star8']
        star_choice_blue = ['star1', 'star2']
        star_choice_purple = ['star4', 'star6']
        color_choice = [star_choice_gold, star_choice_green, 
            star_choice_purple, star_choice_blue]
        first_color_choice = random.choice(color_choice)
        second_color_choice = random.choice(color_choice)
        num_star_1 = random.randint(0, 25)
        num_star_2 = random.randint(0, 15)
        num_star_3 = random.randint(0, 10)
        num_star_4 = random.randint(0, 10)
        self.generate_stars(first_color_choice[0], first_color_choice[1], 
            second_color_choice[0], second_color_choice[1], 
            num_star_1, num_star_2, num_star_3, num_star_4)
        #generate background
        chance_of_dust = random.random()
        if chance_of_dust >= 0.35:
            if first_color_choice == star_choice_gold:
                bg_choice = random.choice(dust_choices_gold)
            if first_color_choice == star_choice_green:
                bg_choice = random.choice(dust_choices_green)
            if first_color_choice == star_choice_blue:
                bg_choice = random.choice(dust_choices_blue)
            if first_color_choice == star_choice_purple:
                bg_choice = random.choice(dust_choices_purple)
            print bg_choice
            self.generate_prerendered_background(bg_choice, (512, 512))
        self.choose_damping()
        self.choose_gravity()
        self.spawn_probes()
        

    def begin_spawning_of_ai(self):
        if self.number_of_enemies_to_spawn > 0:
            time_to_ship_spawn = random.random()*15.0
            Clock.schedule_once(self.spawn_ai_ship, time_to_ship_spawn)


    def spawn_ai_ship(self, dt):
        self.number_of_enemies_to_spawn -= 1
        character_system = self.gameworld.systems['ship_system']
        ship_choice = random.choice(['ship_1', 'ship_2', 'ship_3', 
            'ship_4', 'ship_5', 'ship_6'])
        rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
        rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
        character_system.spawn_ship_with_dict(
            character_system.ship_dicts[ship_choice], False, (rand_x, rand_y))
        if self.number_of_enemies_to_spawn > 0:
            time_to_ship_spawn = random.random()*10.0
            Clock.schedule_once(self.spawn_ai_ship, time_to_ship_spawn)

    def spawn_probes(self):
        systems = self.gameworld.systems
        probe_system = systems['probe_system']
        number_of_probes_to_spawn = [5, 0, 0, 10, 0]
        for x in range(number_of_probes_to_spawn[self.current_level_id]):
            rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
            rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
            probe_system.spawn_probe_with_dict(
                probe_system.probe_dict['probe1'], (rand_x, rand_y))

    def choose_gravity(self):
        #'x', 'y', 'xy', '
        choice = random.choice(['none', 'none', 'none', 'none'])
        systems = self.gameworld.systems
        physics_system = systems['cymunk_physics']
        if choice == 'none':
            physics_system.gravity = (0, 0)
        if choice == 'x':
            x_grav = random.randrange(-100, 100)
            physics_system.gravity = (x_grav, 0)
        if choice == 'y':
            y_grav = random.randrange(-100, 100)
            physics_system.gravity = (0, y_grav)
        if choice == 'xy':
            y_grav = random.randrange(-100, 100)
            x_grav = random.randrange(-100, 100)
            physics_system.gravity = (x_grav, y_grav)

    def choose_damping(self):
        systems = self.gameworld.systems
        level_damping = [.75, .75, .80, .9, 1.0]
        physics_system = systems['cymunk_physics']
        #damping_factor = .75 + .25*random.random()
        physics_system.damping = level_damping[self.current_level_id]

    def clear_level(self):
        for entity_id in self.entity_ids:
            Clock.schedule_once(partial(
                self.gameworld.timed_remove_entity, entity_id))

    def generate_stars(self, first_star_choice1, first_star_choice2, 
        second_star_choice1, second_star_choice2, num_star_1, 
        num_star_2, num_star_3, num_star_4):
        for x in range(num_star_1):
            self.generate_star(first_star_choice1, (28, 28))
        for x in range(num_star_2):
            self.generate_star(first_star_choice2, (16, 16))
        for x in range(num_star_3):
            self.generate_star(second_star_choice1, (28, 28))
        for x in range(num_star_4):
            self.generate_star(second_star_choice2, (16, 16))

    def generate_star(self, star_graphic, star_size):
        rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
        rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
        create_component_dict = {'position': (rand_x, rand_y), 
            'static_renderer': {'texture': star_graphic, 'size': star_size}, 
            'asteroids_level': {'level_id': self.current_level_id}}
        component_order = ['position', 'static_renderer', 'asteroids_level']
        self.gameworld.init_entity(create_component_dict, component_order)

    
    def generate_prerendered_background(self, atlas_address, atlas_size):
        gameworld = self.gameworld
        systems = gameworld.systems
        bg_renderer = systems['background_renderer']
        bg_renderer.atlas = atlas_address
        bg_renderer.clear_mesh()
        uv_dict = bg_renderer.uv_dict
        num_tiles = len(uv_dict)-2
        map_to_use = self.gameworld.systems['default_map']
        map_size = map_to_use.map_size
        side_length_x = math.sqrt(num_tiles)
        side_length_y = side_length_x
        scale_x = map_size[0]/atlas_size[0]
        scale_y = map_size[1]/atlas_size[1]
        x_distance = map_size[0]/4.
        y_distance = map_size[1]/4.
        position_dict = {}
        index = 0
        size = (x_distance, y_distance)
        for y in range(4):
            for x in range(4):
                position_dict[index] = (x * x_distance + x_distance *.5, 
                    y * y_distance + y_distance*.5)
                index += 1
        for num in range(num_tiles):
            create_component_dict = {
            'position': position_dict[num], 
            'background_renderer': {'texture': str(num+1), 'size': size,}, 
            'asteroids_level': {'level_id': self.current_level_id}}
            component_order = ['position', 
                'background_renderer', 'asteroids_level']
            self.gameworld.init_entity(create_component_dict, component_order)

class AsteroidSystem(GameSystem):
    system_id = StringProperty('asteroid_system')
    updateable = BooleanProperty(True)
    number_of_asteroids = NumericProperty(0)

    def generate_asteroids(self, dt):
        current_level_id = self.gameworld.systems[
            'asteroids_level'].current_level_id
        level_asteroids = [(5, 15), (0, 5), (5, 20), (10, 0), (5,20)]
        if current_level_id <= 4:
            num_small_asteroids = level_asteroids[current_level_id][1]
            num_big_asteroids = level_asteroids[current_level_id][0]
        if current_level_id > 4:
            num_big_asteroids = (current_level_id - 1) * 5
            num_small_asteroids = (current_level_id + 1) * 5
        #small asteroids
        for x in range(num_small_asteroids):
            rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
            rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
            self.create_asteroid_1((rand_x, rand_y))
        #big asteroids
        for x in range(num_big_asteroids):
            rand_x = random.randint(0, self.gameworld.currentmap.map_size[0])
            rand_y = random.randint(0, self.gameworld.currentmap.map_size[1])
            self.create_asteroid_2((rand_x, rand_y))


    def clear_asteroids(self):
        for entity_id in self.entity_ids:
            Clock.schedule_once(partial(
                self.gameworld.timed_remove_entity, entity_id))

    def create_asteroid_2(self, pos):
        x_vel = random.randint(-75, 75)
        y_vel = random.randint(-75, 75)
        angle = math.radians(random.randint(-360, 360))
        angular_velocity = math.radians(random.randint(-150, -150))
        shape_dict = {'inner_radius': 0, 'outer_radius': 43, 'mass': 150, 
            'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5, 
         'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle', 
            'velocity': (x_vel, y_vel), 
            'position': pos, 'angle': angle, 
            'angular_velocity': angular_velocity,
            'vel_limit': 200, 
            'ang_vel_limit': math.radians(150), 
            'mass': 100, 'col_shapes': col_shapes}
        asteroid_component = {'health': 30, 'damage': 15, 
        'asteroid_size': 2, 'pending_destruction': False}
        create_component_dict = {'position': pos, 
            'rotate': 0,
            'cymunk_physics': physics_component, 
            'physics_renderer': {'texture': 'asteroid2', 'size': (90, 90)}, 
            'asteroid_system': asteroid_component}
        component_order = ['position', 'rotate', 
            'cymunk_physics', 'physics_renderer', 
            'asteroid_system']
        self.gameworld.init_entity(create_component_dict, component_order)

    def create_asteroid_1(self, pos):
        x_vel = random.randint(-100, 100)
        y_vel = random.randint(-100, 100)
        angle = math.radians(random.randint(-360, 360))
        angular_velocity = math.radians(random.randint(-150, -150))
        shape_dict = {'inner_radius': 0, 'outer_radius': 32, 
        'mass': 50, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5, 
        'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle', 
        'velocity': (x_vel, y_vel), 
        'position': pos, 'angle': angle, 
        'angular_velocity': angular_velocity, 
        'vel_limit': 250, 
        'ang_vel_limit': math.radians(200), 
        'mass': 50, 'col_shapes': col_shapes}
        asteroid_component = {'health': 15, 'damage': 5, 
        'asteroid_size': 1, 'pending_destruction': False}
        create_component_dict = {'cymunk_physics': physics_component, 
            'physics_renderer': {'texture': 'asteroid1', 'size': (64 , 64)}, 
            'asteroid_system': asteroid_component, 'position': pos,
            'rotate': 0}
        component_order = ['position', 'rotate', 
            'cymunk_physics', 'physics_renderer', 
            'asteroid_system']
        self.gameworld.init_entity(create_component_dict, component_order)

    def create_component(self, entity_id, entity_component_dict):
        super(AsteroidSystem, self).create_component(entity_id, 
            entity_component_dict)
        self.number_of_asteroids += 1

    def remove_entity(self, entity_id):
        super(AsteroidSystem, self).remove_entity(entity_id)
        self.number_of_asteroids -= 1

    def update(self, dt):
        system_id = self.system_id
        entities = self.gameworld.entities
        for entity_id in self.entity_ids:
            entity = entities[entity_id]
            if not hasattr(entity, system_id):
                continue
            system_data = getattr(entity, system_id)
            if (system_data.health <= 0 and 
                not system_data.pending_destruction):
                system_data.pending_destruction = True
                if system_data.asteroid_size == 2:
                    for x in range(4):
                        position = (entity.position.x, entity.position.y)
                        self.create_asteroid_1(position)
                Clock.schedule_once(partial(
                    self.gameworld.timed_remove_entity, entity_id))
                
    def damage(self, entity_id, damage):
        system_id = self.system_id
        entities = self.gameworld.entities
        entity = entities[entity_id]
        system_data = getattr(entity, system_id)
        system_data.health -= damage

    def collision_begin_asteroid_asteroid(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        asteroid1_id = arbiter.shapes[0].body.data
        asteroid2_id = arbiter.shapes[1].body.data
        asteroid1 = entities[asteroid1_id]
        asteroid2 = entities[asteroid2_id]
        if (asteroid1.physics_renderer.on_screen or 
            asteroid2.physics_renderer.on_screen):
            sound_system = gameworld.systems['sound_system']
            sound_system.play('asteroidhitasteroid')
        return True