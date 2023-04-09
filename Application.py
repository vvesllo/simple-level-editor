import pygame
import tkinter
from tkinter import ttk
from tkinter import filedialog

class Application:
	def __init__(self, tileset_path):
		# class initialization
		self.FPS = 60
		self.filetypes = (
			('All Files', '*.*'),
			('Level Colliders File', '*.lcf'),
			('Level Decoration File', '*.ldf'),
			('Text Document', '*.txt')
		)

		self.is_colliders = False
		self.running = True
		self.filepath = ''
		self.tk_widgets_width = 300
		self.tk_window_width = 300
		self.tk_window_height = 200
		
		# pygame initialization
		pygame.init()
		pygame.display.set_caption("Editor")

		# cells settings
		self.cell_type = 0
		self.cell_size = 32
		self.max_cells_count = 5+2
		# tileset loading
		self.tileset_image = pygame.transform.scale(
			pygame.image.load(tileset_path), 
			(self.cell_size*3, self.cell_size*3)
		)

		# window settings
		self.clock = pygame.time.Clock()

		self.window_size = [self.cell_size*40, self.cell_size*30]
		self.window = pygame.display.set_mode(
			self.window_size,
			pygame.RESIZABLE
		)

		# grid settings
		self.grid_opacity_max_type = 5
		self.grid_opacity = 1
		self.grid = []
		self.grid_size = [
			self.window_size[0]//self.cell_size, 
			self.window_size[1]//self.cell_size
		]

		# cell surface initialization
		self.cell_surface = self.get_outline(
			pygame.Surface((self.cell_size, self.cell_size)), 
			(255,255,255)
		)

		self.cell_surface.set_alpha(
			255 // self.grid_opacity_max_type * self.grid_opacity
		)

		# create empty grid 
		self.empty_grid()


		# init tkinter menu window
		self.root = tkinter.Tk()
		self.menu_window = tkinter.Frame(self.root)
		self.init_tkinter_window()

	def draw(self):
		self.window.fill(pygame.Color(0x1A, 0x1A, 0x20))
		for row in range(self.grid_size[1]):
			for col in range(self.grid_size[0]):
				x, y = col * self.cell_size, row * self.cell_size
				if self.grid[row][col] == '0':
					self.window.blit(self.tileset_image, (x, y), (0, 0, self.cell_size, self.cell_size))
				elif self.grid[row][col] == '1':
					self.window.blit(self.tileset_image, (x, y), (self.cell_size, 0, self.cell_size, self.cell_size))
				elif self.grid[row][col] == '2':
					self.window.blit(self.tileset_image, (x, y), (0, self.cell_size, self.cell_size, self.cell_size))
				elif self.grid[row][col] == '3':
					self.window.blit(self.tileset_image, (x, y), (self.cell_size, self.cell_size, self.cell_size, self.cell_size))
				elif self.grid[row][col] == '4':
					self.window.blit(self.tileset_image, (x, y), (self.cell_size*2, 0, self.cell_size, self.cell_size))
				elif self.grid[row][col] == '5':
					self.window.blit(self.tileset_image, (x, y), (self.cell_size*2, self.cell_size, self.cell_size, self.cell_size))
				elif self.grid[row][col] == 'p':
					pygame.draw.rect(
						self.window,
						pygame.Color('red'),
						(x, y, self.cell_size, self.cell_size)
					)
				elif self.grid[row][col] == 'e':
					pygame.draw.rect(
						self.window,
						pygame.Color('blue'),
						(x, y, self.cell_size, self.cell_size)
					)
				elif self.grid[row][col] == ' ':
					self.window.blit(self.cell_surface, (x, y))

	def update(self):
		self.cell_surface.set_alpha(
			self.grid_opacity.get()
		)
		if self.filepath != '':
			pygame.display.set_caption(self.filepath + " - MapEditor")
		mouse_position = pygame.mouse.get_pos()
		b1, _, b3 = pygame.mouse.get_pressed()

		mouse_row, mouse_col = mouse_position[1] // self.cell_size, mouse_position[0] // self.cell_size
		if mouse_position[0] > 0 and mouse_position[0] < self.window_size[0] and\
			mouse_position[1] > 0 and mouse_position[1] < self.window_size[1]:
			if b1:
				# print(self.cell_type)
				if    self.cell_type == 0: self.grid[mouse_row][mouse_col] = 'p'
				elif  self.cell_type == 1: self.grid[mouse_row][mouse_col] = 'e'
				else: self.grid[mouse_row][mouse_col] = str(self.cell_type-2)
			if b3:
				self.grid[mouse_row][mouse_col] = ' '

	def check_events(self):
		for	event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				running = False

			elif event.type == pygame.VIDEORESIZE:
				self.resize_grid(event.w, event.h)

			elif event.type == pygame.KEYDOWN:
				match event.key:
					case pygame.K_F1:
						if self.cell_type > 0:
							self.cell_type -= 1
					case pygame.K_F2:
						if self.cell_type < self.max_cells_count:
							self.cell_type += 1

				#print(self.cell_type)
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					if event.key == pygame.K_s:
						if self.filepath == "":
							self.filepath = self.ask_filepath_to_save(self.filetypes, ".glf")
							if not self.filepath: continue
						with open(self.filepath, 'w') as file:
							for row in range(self.grid_size[1]):
								for col in range(self.grid_size[0]):
									file.write(self.grid[row][col])
								file.write('\n')
					if event.key ==  pygame.K_o:
						self.filepath = self.ask_filepath_to_open(self.filetypes, ".glf")
						if not self.filepath: continue
						with open(self.filepath, 'r') as file:
							file_lines = file.read().split('\n')
						lines = []
						for i in file_lines:
							if len(i) == 0: continue
							lines.append(i)
							
						self.resize_grid(
							len(lines[0]) * self.cell_size,
							len(lines)    * self.cell_size
						)
						for row in range(len(lines)):
							self.grid[row] = list(lines[row])

	def empty_grid(self):
		self.grid = []
		for row in range(self.grid_size[1]):
			line = []
			for col in range(self.grid_size[0]):
				line.append(' ')
			self.grid.append(line)



	def run(self):
		while self.running:
			self.check_events()
			self.update()
			self.draw()
			pygame.display.update()
			self.menu_window.update()
			self.clock.tick(self.FPS)

	def get_outline(self, image,color=(0,0,0)):
		rect = image.get_rect()
		mask = pygame.mask.from_surface(image)
		outline = mask.outline()
		outline_image = pygame.Surface(rect.size).convert_alpha()
		outline_image.fill((0,0,0,0))
		for point in outline:
			outline_image.set_at(point,color)
		return outline_image

	def resize_grid(self, w, h):

		self.window_size = [
			round(w / self.cell_size) * self.cell_size,
			round(h / self.cell_size) * self.cell_size
		]
		self.window = pygame.display.set_mode(
			self.window_size,
			pygame.RESIZABLE
		)
		new_grid_size = [
			self.window_size[0] // self.cell_size,
			self.window_size[1] // self.cell_size
		]

		# ----------------------------------------------------------------------
		if new_grid_size[1] > self.grid_size[1]:
			for row in range(new_grid_size[1]-self.grid_size[1]):
				self.grid.append([' '] * self.grid_size[0])

			for row in range(new_grid_size[1]):
				if new_grid_size[0] > self.grid_size[0]:
					self.grid[row] += [' '] * (new_grid_size[0] - self.grid_size[0])
				else:
					self.grid[row] = self.grid[row][:new_grid_size[0]]
					

		else:
			self.grid = self.grid[:new_grid_size[1]]
			for row in range(new_grid_size[1]):
				if new_grid_size[0] > self.grid_size[0]:
					self.grid[row] += [' '] * (new_grid_size[0] - self.grid_size[0])
				else:
					self.grid[row] = self.grid[row][:new_grid_size[0]]

		# ----------------------------------------------------------------------

		self.grid_size = new_grid_size


	def set_tileset(self):
		filepath = self.ask_filepath_to_open(self.filetypes, ".glf")
		if not self.filepath: return
		with open(self.filepath, 'r') as file:
			data = file.open()
		self.tileset_image = pygame.image.load(filepath)

		
	def open_file(self):
		self.filepath = self.ask_filepath_to_open(self.filetypes, ".glf")
		if not self.filepath: return
		with open(self.filepath, 'r') as file:
			file_lines = file.read().split('\n')
		lines = []
		for i in file_lines:
			if len(i) == 0: continue
			lines.append(i)
		self.resize_grid(
			len(lines[0]) * self.cell_size,
			len(lines)    * self.cell_size
		)
		for row in range(len(lines)):
			self.grid[row] = list(lines[row])

	def save_file(self):
		if self.filepath == "":
			self.filepath = self.ask_filepath_to_save(self.filetypes, ".glf")
			if not self.filepath: return

		with open(self.filepath, 'w') as file:
			for row in range(self.grid_size[1]):
				for col in range(self.grid_size[0]):
					file.write(self.grid[row][col])
				file.write('\n')

	def save_as_file(self):
		self.filepath = self.ask_filepath_to_save(self.filetypes, ".glf")
		if not self.filepath: return

		with open(self.filepath, 'w') as file:
			for row in range(self.grid_size[1]):
				for col in range(self.grid_size[0]):
					file.write(self.grid[row][col])
				file.write('\n')

	def save_as_image(self):
		filepath = self.ask_filepath_to_save(
			(
				("JPG Image", "*.jpg"),
				("PNG Image", "*.png"),
				("JPEG Image", "*.jpeg")
			),
			".jpg")
		if not filepath: return

		pygame.image.save(self.window, filepath)



	def ask_filepath_to_save(self, filetypes, default_extension):
		return filedialog.asksaveasfilename(
			filetypes=filetypes,
			defaultextension=default_extension
		)

	def ask_filepath_to_open(self, filetypes, default_extension):
		return filedialog.askopenfilename(
			filetypes=filetypes,
			defaultextension=default_extension
		)

	def close_window_callback(self):
		self.running = False

	def init_tkinter_window(self):
		self.root.protocol("WM_DELETE_WINDOW", self.close_window_callback)
		self.root.title("Menu - Editor")
		self.root.geometry(f"{self.tk_window_width}x{self.tk_window_height}")
		self.draw_tkinter_window()


	def draw_tkinter_window(self):
		ttk.Button(
			text="Open (ctrl+O)",
			command=self.open_file,
			width=self.tk_widgets_width
			).pack(anchor=tkinter.NW)
		ttk.Button(
			text="Save (ctrl+S)", 
			command=self.save_file,
			width=self.tk_widgets_width
			).pack(anchor=tkinter.NW)
		ttk.Button(
			text="Save as", 
			command=self.save_as_file,
			width=self.tk_widgets_width
			).pack(anchor=tkinter.NW)
		ttk.Button(
			text="Save as image",
			command=self.save_as_image,
			width=self.tk_widgets_width
			).pack(anchor=tkinter.NW)
		ttk.Button(
			text="Open tileset",
			command=self.set_tileset,
			width=self.tk_widgets_width
			).pack(anchor=tkinter.NW)
		ttk.Button(
			text="Clear canvas",
			command=self.empty_grid,
			width=self.tk_widgets_width
			).pack(anchor=tkinter.NW)
		ttk.Label(text="Grid Opacity").pack()
		self.grid_opacity = ttk.Scale(self.root, from_=0, to=255, orient=tkinter.HORIZONTAL)
		self.grid_opacity.pack()

