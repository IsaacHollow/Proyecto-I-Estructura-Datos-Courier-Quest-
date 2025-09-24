import arcade

WIDTH = 800
HEIGHT = 600

class Juego(arcade.View):
    def on_draw(self):
        self.clear()
        arcade.draw_text("Aqui inicia el juego", WIDTH // 2, HEIGHT // 2,
                         arcade.color.YELLOW, 30, anchor_x="center")
