import tkinter as tk
from tkinter import messagebox

class MazeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("лабиринт")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg='gray')

        self.player_radius = 10
        self.step = 10
        self.obstacle_message_shown = False

        self.canvas = tk.Canvas(root, bg='white', highlightthickness=2, highlightbackground='black')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.focus_set()

        self.walls = [
            (50,50,200,70), (250,50,400,70), (450,50,600,70), (650,50,800,70),
            (50,100,70,400), (800,100,820,400), (150,150,170,350), (300,150,320,450),
            (500,200,520,500), (700,250,720,550), (100,450,120,650), (400,500,420,650),
            (200,300,400,320), (500,350,700,370), (200,400,400,420), (600,450,800,470),
            (50,600,200,620), (300,600,500,620), (650,600,800,620),
            (150,200,350,220), (450,250,650,270), (100,300,250,320), (400,100,600,120),
            (550,400,570,600), (250,500,270,700)
        ]

        self.start = (100,100,120,120)
        self.finish = (850,600,900,650)

        self.obstacles = [
            (200,200,250,250), (400,300,450,350), (600,150,650,200),
            (300,500,350,550), (700,400,750,450)
        ]

        self.portals = [
            (150,400,180,430), (500,150,530,180),
            (300,200,330,230), (700,500,730,530),
            (450,450,480,480), (250,600,280,630)
        ]
        self.portal_pairs = [(0,1),(2,3),(4,5)]

        self.enemies = []
        self.enemy_positions = [
            {'x':300,'y':100,'dx':5,'dy':0,'radius':12},
            {'x':600,'y':400,'dx':-4,'dy':0,'radius':12},
            {'x':150,'y':550,'dx':6,'dy':0,'radius':12}
        ]

        self.draw_walls()
        self.draw_start_finish()
        self.draw_obstacles()
        self.draw_portals()
        self.create_enemies()

        self.player = self.canvas.create_oval(
            self.start[0], self.start[1], self.start[2], self.start[3],
            fill='blue', outline='black'
        )
        self.player_pos = (self.start[0]+self.player_radius, self.start[1]+self.player_radius)

        self.root.bind('<Key>', self.key_press)
        self.move_enemies()

    def draw_walls(self):
        for wall in self.walls:
            self.canvas.create_rectangle(wall, fill='gray', outline='black')

    def draw_start_finish(self):
        self.canvas.create_rectangle(self.start, fill='green', outline='black')
        self.canvas.create_rectangle(self.finish, fill='red', outline='black')
        self.canvas.create_text(self.start[0]+10, self.start[1]-15, text="СТАРТ")
        self.canvas.create_text(self.finish[0]+25, self.finish[1]-15, text="ФИНИШ")

    def draw_obstacles(self):
        for obs in self.obstacles:
            self.canvas.create_rectangle(obs, fill='yellow', outline='black')

    def draw_portals(self):
        colors = ['cyan', 'lightblue', 'deepskyblue']
        for i, portal in enumerate(self.portals):
            self.canvas.create_rectangle(portal, fill=colors[i//2], outline='black')
            self.canvas.create_text(portal[0]+15, portal[1]-10, text=f"P{i+1}")

    def create_enemies(self):
        for e in self.enemy_positions:
            obj = self.canvas.create_oval(
                e['x']-e['radius'], e['y']-e['radius'],
                e['x']+e['radius'], e['y']+e['radius'],
                fill='red', outline='darkred'
            )
            self.enemies.append(obj)

    def key_press(self, event):
        dx = dy = 0
        if event.keysym == 'Up':
            dy = -self.step
        elif event.keysym == 'Down':
            dy = self.step
        elif event.keysym == 'Left':
            dx = -self.step
        elif event.keysym == 'Right':
            dx = self.step
        else:
            return
        x1,y1,x2,y2 = self.canvas.coords(self.player)
        cx = (x1+x2)//2
        cy = (y1+y2)//2
        self.move_player_to(cx+dx, cy+dy)

    def move_player_to(self, x, y):
        x = max(self.player_radius, min(x, self.canvas.winfo_width()-self.player_radius))
        y = max(self.player_radius, min(y, self.canvas.winfo_height()-self.player_radius))
        self.canvas.coords(self.player,
                           x-self.player_radius, y-self.player_radius,
                           x+self.player_radius, y+self.player_radius)
        self.check_collisions(x, y)

    def check_collisions(self, x, y):
        player_bbox = (x-self.player_radius, y-self.player_radius,
                       x+self.player_radius, y+self.player_radius)

        for wall in self.walls:
            if self.rect_overlap(player_bbox, wall):
                self.reset_to_start()
                return

        if self.rect_overlap(player_bbox, self.finish):
            self.show_victory()
            return

        for obs in self.obstacles:
            if self.rect_overlap(player_bbox, obs):
                if not self.obstacle_message_shown:
                    self.obstacle_message_shown = True
                    messagebox.showwarning("Препятствие", "Error!")
                    self.root.after(500, self.reset_obstacle_flag)
                break

        for idx, portal in enumerate(self.portals):
            if self.rect_overlap(player_bbox, portal):
                for pair in self.portal_pairs:
                    if idx in pair:
                        dest_idx = pair[0] if pair[1]==idx else pair[1]
                        dest = self.portals[dest_idx]
                        dest_x = (dest[0]+dest[2])//2
                        dest_y = (dest[1]+dest[3])//2
                        self.move_player_to(dest_x, dest_y)
                        return

        for enemy_obj, e_data in zip(self.enemies, self.enemy_positions):
            ex,ey = e_data['x'], e_data['y']
            er = e_data['radius']
            if (x-ex)**2 + (y-ey)**2 < (self.player_radius+er)**2:
                self.reset_to_start()
                return

    def rect_overlap(self, r1, r2):
        return not (r1[2] < r2[0] or r1[0] > r2[2] or
                    r1[3] < r2[1] or r1[1] > r2[3])

    def reset_to_start(self):
        cx = (self.start[0]+self.start[2])//2
        cy = (self.start[1]+self.start[3])//2
        self.move_player_to(cx, cy)

    def show_victory(self):
        if messagebox.askyesno("Победа!", "Вы достигли финиша! Начать заново?"):
            self.reset_to_start()

    def reset_obstacle_flag(self):
        self.obstacle_message_shown = False

    def move_enemies(self):
        for i, e in enumerate(self.enemy_positions):
            e['x'] += e['dx']
            if e['x'] < 50 or e['x'] > 950:
                e['dx'] = -e['dx']
            self.canvas.coords(self.enemies[i],
                               e['x']-e['radius'], e['y']-e['radius'],
                               e['x']+e['radius'], e['y']+e['radius'])

            px1,py1,px2,py2 = self.canvas.coords(self.player)
            pcx = (px1+px2)//2
            pcy = (py1+py2)//2
            if (pcx-e['x'])**2 + (pcy-e['y'])**2 < (self.player_radius+e['radius'])**2:
                self.reset_to_start()

        self.root.after(50, self.move_enemies)

if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()