import nextcord as discord
from nextcord.ext import commands
import cv2
import numpy as np
import dotenv
import os

dotenv.load_dotenv()

bot = commands.Bot()
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print("Do you want to build a snowman?")
    await bot.change_presence(activity = discord.Game("Do you wanna build a snowman?"))

class BuildStructure(discord.ui.Modal):
    def __init__(self, button_view: discord.ui.View, bottom_radius: int = 50, middle_radius: int = 37, top_radius: int = 28, arm_length: int = 50, num_buttons: int = 3, rgb: tuple = (0, 0, 0), scarf: tuple = (0, 0, 0), bg: tuple = (55, 100, 255)):
        super().__init__("Build a snowman!", timeout = None)
        self.button_view = button_view
        self.bottom_radius_value = bottom_radius
        self.middle_radius_value = middle_radius
        self.top_radius_value = top_radius
        self.arm_length_value = arm_length
        self.num_buttons_value = num_buttons
        self.rgb = rgb
        self.scarf = scarf
        self.bg = bg

        self.bottom_radius = discord.ui.TextInput(
            label = "Radius of the bottom snowball",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the radius of the bottom snowball",
            required = False
        )
        self.add_item(self.bottom_radius)

        self.middle_radius = discord.ui.TextInput(
            label = "Radius of the middle snowball",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the radius of the middle snowball",
            required = False
        )
        self.add_item(self.middle_radius)

        self.top_radius = discord.ui.TextInput(
            label = "Radius of the top snowball",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the radius of the top snowball",
            required = False
        )
        self.add_item(self.top_radius)

        self.arm_length = discord.ui.TextInput(
            label = "Length of the arm",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the length of the arm",
            required = False
        )
        self.add_item(self.arm_length)

        self.num_buttons = discord.ui.TextInput(
            label = "Number of buttons",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the number of buttons",
            required = False
        )
        self.add_item(self.num_buttons)

    async def callback(self, interaction: discord.Interaction):
        try:
            self.bottom_radius_value = abs(int(float(self.bottom_radius.value)))
        except:
            if not self.bottom_radius.value and not self.bottom_radius_value:
                self.bottom_radius_value = 50
            elif not self.bottom_radius_value:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        try:
            self.middle_radius_value = abs(int(float(self.middle_radius.value)))
        except:
            if not self.middle_radius.value and not self.middle_radius_value:
                self.middle_radius_value = int(0.75*self.bottom_radius_value)
            elif not self.middle_radius_value:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        try:
            self.top_radius_value = abs(int(float(self.top_radius.value)))
        except:
            if not self.top_radius.value and not self.top_radius_value:
                self.top_radius_value = int(0.75*self.middle_radius_value)
            elif not self.top_radius_value:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        
        try:
            self.arm_length_value = abs(int(float(self.arm_length.value)))
        except:
            if not self.arm_length.value and not self.arm_length_value:
                self.arm_length_value = 50
            elif not self.arm_length_value:
                await interaction.send("The value of the arm length has to be a number", ephemeral = True)
                return
        
        try:
            self.num_buttons_value = abs(int(self.num_buttons.value))
        except:
            if not self.num_buttons.value and not self.num_buttons_value:
                self.num_buttons_value = 3
            elif not self.num_buttons_value:
                await interaction.send("The number of buttons has to be an integer", ephemeral = True)
                return

        if not (self.bottom_radius_value >= self.middle_radius_value >= self.top_radius_value):
            await interaction.send("The radii of your snowballs have to be lesser than or equal to the radius of the snowball beneath them!", ephemeral = True)
            return
        
        if 2*sum([self.bottom_radius_value, self.middle_radius_value, self.top_radius_value]) >= 512:
            await interaction.send("The sum of the diameters of your snowballs cannot exceed 512", ephemeral = True)
            return
        
        else:
            snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
            snowman_embed.add_field(name = "Bottom snowball radius", value = self.bottom_radius_value)
            snowman_embed.add_field(name = "Middle snowball radius", value = self.middle_radius_value)
            snowman_embed.add_field(name = "Top snowball radius", value = self.top_radius_value)
            snowman_embed.add_field(name = "Arm length", value = self.arm_length_value)
            snowman_embed.add_field(name = "Number of buttons", value = self.num_buttons_value)
            snowman_embed.add_field(name = "Hat colour", value = str(self.rgb))
            snowman_embed.add_field(name = "Scarf colour", value = str(self.scarf))
            snowman_embed.add_field(name = "Background colour", value = str(self.bg))
            self.button_view.modal_design.setValues(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value)
            createImage(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, self.rgb[::-1], self.scarf[::-1], self.bg[::-1], interaction.guild_id, interaction.user)
            return await interaction.response.edit_message(embed = snowman_embed, view = self.button_view, file = discord.File(f"./build-a-snowman/snowmen/{interaction.guild_id}_{interaction.user}.png"))
    
    def setValues(self, hat_colour, scarf_colour, bg_colour):
        self.rgb = hat_colour
        self.scarf = scarf_colour
        self.bg = bg_colour

class BuildDesign(discord.ui.Modal):
    def __init__(self, button_view: discord.ui.View, bottom_radius: int = 50, middle_radius: int = 37, top_radius: int = 28, arm_length: int = 50, num_buttons: int = 3, rgb: tuple = (0, 0, 0), scarf: tuple = (0, 0, 0), bg: tuple = (55, 100, 255)):
        super().__init__("Build a snowman!", timeout = None)
        self.button_view = button_view
        self.bottom_radius_value = bottom_radius
        self.middle_radius_value = middle_radius
        self.top_radius_value = top_radius
        self.arm_length_value = arm_length
        self.num_buttons_value = num_buttons
        self.rgb = rgb
        self.scarf = scarf
        self.bg = bg

        self.hat_colour = discord.ui.TextInput(
            label = "Colour of the hat",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the colour of the hat (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.hat_colour)

        self.scarf_colour = discord.ui.TextInput(
            label = "Colour of the scarf",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the colour of the scarf (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.scarf_colour)

        self.bg_colour = discord.ui.TextInput(
            label = "Colour of the background",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the colour of the background (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.bg_colour)

    async def callback(self, interaction: discord.Interaction):
        
        if self.hat_colour.value:
            self.rgb = ConvertToRGB(self.hat_colour.value)
            if self.rgb == 0:
                await interaction.send("The hex code has to have 6 symbols!", ephemeral = True)
                return
            elif self.rgb == 1:
                await interaction.send("Invalid hex code", ephemeral = True)
                return
        
        if self.scarf_colour.value:
            self.scarf = ConvertToRGB(self.scarf_colour.value)
            if self.scarf == 0:
                await interaction.send("The hex code has to have 6 symbols!", ephemeral = True)
                return
            elif self.scarf == 1:
                await interaction.send("Invalid hex code", ephemeral = True)
                return
        
        if self.bg_colour.value:
            self.bg = ConvertToRGB(self.bg_colour.value)
            if self.bg == 0:
                await interaction.send("The hex code has to have 6 symbols!", ephemeral = True)
                return
            elif self.bg == 1:
                await interaction.send("Invalid hex code", ephemeral = True)
                return

        snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
        snowman_embed.add_field(name = "Bottom snowball radius", value = self.bottom_radius_value)
        snowman_embed.add_field(name = "Middle snowball radius", value = self.middle_radius_value)
        snowman_embed.add_field(name = "Top snowball radius", value = self.top_radius_value)
        snowman_embed.add_field(name = "Arm length", value = self.arm_length_value)
        snowman_embed.add_field(name = "Number of buttons", value = self.num_buttons_value)
        snowman_embed.add_field(name = "Hat colour", value = str(self.rgb))
        snowman_embed.add_field(name = "Scarf colour", value = str(self.scarf))
        snowman_embed.add_field(name = "Background colour", value = str(self.bg))
        self.button_view.modal_structure.setValues(self.rgb, self.scarf, self.bg)
        createImage(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, self.rgb[::-1], self.scarf[::-1], self.bg[::-1], interaction.guild_id, interaction.user)
        return await interaction.response.edit_message(embed = snowman_embed, view = self.button_view, file = discord.File(f"./build-a-snowman/snowmen/{interaction.guild_id}_{interaction.user}.png"))
    
    def setValues(self, bottom_radius, middle_radius, top_radius, arm_length, num_buttons):
        self.bottom_radius_value = bottom_radius
        self.middle_radius_value = middle_radius
        self.top_radius_value = top_radius
        self.arm_length_value = arm_length
        self.num_buttons_value = num_buttons

class BuildView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.modal_structure = BuildStructure(self)
        self.modal_design = BuildDesign(self)
    
    @discord.ui.button(label = "🔨 Structure", style = discord.ButtonStyle.blurple)
    async def structure(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_structure)
    
    @discord.ui.button(label = "🎨 Design", style = discord.ButtonStyle.blurple)
    async def design(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_design)
    
    @discord.ui.button(label = "✅ Done", style = discord.ButtonStyle.blurple)
    async def done(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view = None)

def createImage(bottom_radius: int, middle_radius: int, top_radius: int, arm_length: int, num_buttons: int, hat_colour: tuple, scarf_colour: tuple, bg_colour: tuple, guild_id: int, user: str):
    img = np.zeros((512, 512, 3), np.uint8)
    img[:,:] = bg_colour
    cv2.circle(img, (256, 512-bottom_radius), bottom_radius, (255, 255, 255), -1)
    cv2.circle(img, (256, 512-(2*bottom_radius+middle_radius)), middle_radius, (255, 255, 255), -1)
    cv2.circle(img, (256, 512-(2*bottom_radius+2*middle_radius+top_radius)), top_radius, (255, 255, 255), -1)
    arm_right_start = ((256+middle_radius), (512-(2*bottom_radius+middle_radius)))
    arm_right_end = (int(256+middle_radius+(arm_length)//1.4), int(512-(2*bottom_radius+middle_radius)-(arm_length)//1.4))
    arm_left_start = ((256-middle_radius), (512-(2*bottom_radius+middle_radius)))
    arm_left_end = (int(256-middle_radius-(arm_length)//1.4), int(512-(2*bottom_radius+middle_radius)-(arm_length)//1.4))
    cv2.line(img, arm_right_start, arm_right_end, (0, 75, 150), 3)
    cv2.line(img, arm_left_start, arm_left_end, (0, 75, 150), 3)
    cv2.imwrite(f"./build-a-snowman/snowmen/{guild_id}_{user}.png", img)

def ConvertToRGB(colour: str = "000000"):
    if colour == None:
        colour = "000000"

    if len(colour) != 6:
        return 0
    for x in colour:
        if not(x.isnumeric() or x in "abcdef"):
            return 1
    
    rgb_old = [colour[:2], colour[2:4], colour[4:]]
    rgb = []
    for x in rgb_old:
        rgb.append(int(x, 16))
    
    rgb = tuple(rgb)

    return rgb

@bot.slash_command(name = "build", description = "Build a snowman")
async def build(interaction: discord.Interaction):
    button_view = BuildView()
    await interaction.send(view = button_view, file = discord.File("./build-a-snowman/snowmen/basic_snowman.png"), ephemeral = True)

bot.run(token)