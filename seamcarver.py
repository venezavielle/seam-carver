#!/usr/bin/env python3
import math
from PIL import Image
from picture import Picture # Importing the Picture class from the picture module

class SeamCarver(Picture):
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''
        if not (0 <= i < self.width() and 0 <= j < self.height()):
            raise IndexError("Invalid pixel indices")

        if i == 0 or i == self.width() - 1 or j == 0 or j == self.height() - 1:
            left_pixel = self[(i - 1 + self.width()) % self.width(), j]
            right_pixel = self[(i + 1) % self.width(), j]
            top_pixel = self[i, (j - 1 + self.height()) % self.height()]
            bottom_pixel = self[i, (j + 1) % self.height()]
        else:
            left_pixel = self[i - 1, j]
            right_pixel = self[i + 1, j]
            top_pixel = self[i, j - 1]
            bottom_pixel = self[i, j + 1]

        delta_x_squared = sum([abs(right_pixel[k] - left_pixel[k]) ** 2 for k in range(3)])
        delta_y_squared = sum([abs(bottom_pixel[k] - top_pixel[k]) ** 2 for k in range(3)])

        energy = math.sqrt(delta_x_squared + delta_y_squared)
        return energy

    def find_vertical_seam(self) -> list[int]:  # Defining the find_vertical_seam method
        '''
        Return a sequence of indices representing the lowest-energy
        vertical seam
        '''
        width, height = self.width(), self.height()

        dp = [[0 for _ in range(width)] for _ in range(height)]

        for i in range(width):
            dp[0][i] = self.energy(i, 0)

        for j in range(0, height):
            for i in range(width):
                top_left = dp[j - 1][i - 1] if i > 0 else float('inf')
                top_middle = dp[j - 1][i]
                top_right = dp[j - 1][i + 1] if i < width - 1 else float('inf')
                dp[j][i] = self.energy(i, j) + min(top_left, top_middle, top_right)


        min_energy_index = dp[height - 1].index(min(dp[height - 1]))

        seam_list = [min_energy_index]
        for j in range(height - 1, 0, -1):
            current_index = seam_list[-1]
            neighbors = [(dp[j - 1][current_index], current_index)]

            if current_index > 0:
                neighbors.append((dp[j - 1][current_index - 1], current_index - 1))
            if current_index < width - 1:
                neighbors.append((dp[j - 1][current_index + 1], current_index + 1))

            min_neighbor, next_index = min(neighbors)
            seam_list.append(next_index)

        return seam_list[::-1]

    def transpose(self):
        transposed_image = SeamCarver(Image.new('RGB', (self.height(), self.width())))
        for i in range(self.width()):
            for j in range(self.height()):
                transposed_image[j, i] = self[i, j]
        return transposed_image

    def find_horizontal_seam(self) -> list[int]:
        transposed_image = self.transpose()

        seam_list = transposed_image.find_vertical_seam()

        return seam_list

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        width, height = self.width(), self.height()

        if width <= 1:
            raise SeamError("Width of the picture is already 1. Cannot remove vertical seam.")

        if len(seam) != height or not all(0 <= x < width for x in seam):
            raise SeamError("Invalid seam provided.")

        for j in range(height):
            if j > 0 and abs(seam[j] - seam[j - 1]) > 1:
                raise SeamError("Invalid seam provided.")

            for i in range(seam[j], width - 1):
                self[i, j] = self[i + 1, j]
            del self[width - 1, j]

        self._width -= 1

    def _update_data(self, new_image):
        self.clear()
        for i in range(new_image.width()):
            for j in range(new_image.height()):
                self[i, j] = new_image[i, j]

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        width, height = self.width(), self.height()

        if height <= 1:
            raise SeamError("Height of the picture is already 1. Cannot remove horizontal seam.")

        if len(seam) != width or not all(0 <= y < height for y in seam):
            raise SeamError("Invalid seam provided.")

        transposed_image = self.transpose()

        transposed_image.remove_vertical_seam(seam)

        self._update_data(transposed_image.transpose())

        self._height -= 1

class SeamError(Exception): 
    pass