from random import randint, randrange

class Colors(object):
    red = [250, 0, 0, 0]
    green = [0, 255, 0, 0]
    blue = [0, 0, 255, 0]

    bright_white = [100, 100, 100, 200]
    soft_white = [20, 20, 20, 100]

    mid_green = [150, 250, 0, 50]
    light_green = [0, 250, 0, 100]

    mixed_blue = [0, 50, 255, 100]

    def get_random_color_weighted(self):
        all_colors = self.get_all_colors()
        index = randrange(len(all_colors))
        return all_colors[index]

    def get_all_colors(self):
        return [self.light_green, self.mid_green, self.green, self.mixed_blue, self.blue, self.red]




