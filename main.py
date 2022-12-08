import nextcord as discord
from nextcord.ext import commands
import cv2
import numpy as np
import time
import random as rd
import dotenv
import os

dotenv.load_dotenv()

bot = commands.Bot()
token = os.getenv("DISCORD_TOKEN")

snowball_data = {}

@bot.event
async def on_ready():
    print("Do you want to build a snowman?")
    await bot.change_presence(activity = discord.Game("Do you wanna build a snowman?"))

class BuildStructure(discord.ui.Modal):
    def __init__(self, button_view: discord.ui.View, bottom_radius: int = 150, middle_radius: int = 112, top_radius: int = 84, arm_length: int = 125, num_buttons: int = 3, rgb: tuple = (0, 0, 0), rgb_sec: tuple = (255, 0, 0), scarf: tuple = (255, 0, 0), scarf_sec: tuple = (0, 0, 255), bg: tuple = (55, 100, 255)):
        super().__init__("Build a snowman!", timeout = None)
        self.button_view = button_view
        self.bottom_radius_value = bottom_radius
        self.middle_radius_value = middle_radius
        self.top_radius_value = top_radius
        self.arm_length_value = arm_length
        self.num_buttons_value = num_buttons
        self.rgb = rgb
        self.rgb_sec = rgb_sec
        self.scarf = scarf
        self.scarf_sec = scarf_sec
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
            if self.bottom_radius_value < 50:
                await interaction.send("The bottom snowball radius is too small!", ephemeral = True)
                return
            elif self.bottom_radius_value > 256:
                await interaction.send("The bottom snowball radius is too big!", ephemeral = True)
                return
        except:
            if not self.bottom_radius.value and not self.bottom_radius_value:
                self.bottom_radius_value = 150
            elif not self.bottom_radius_value:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        try:
            self.middle_radius_value = abs(int(float(self.middle_radius.value)))
            if self.middle_radius_value < 50:
                await interaction.send("The middle snowball radius is too small!", ephemeral = True)
                return
        except:
            if not self.middle_radius.value and not self.middle_radius_value:
                self.middle_radius_value = int(0.75*self.bottom_radius_value)
            elif not self.middle_radius_value:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        try:
            self.top_radius_value = abs(int(float(self.top_radius.value)))
            if self.top_radius_value < 50:
                await interaction.send("The top snowball radius is too small!", ephemeral = True)
                return
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
                self.arm_length_value = 125
            elif not self.arm_length_value:
                await interaction.send("The value of the arm length has to be a number", ephemeral = True)
                return
        
        try:
            self.num_buttons_value = abs(int(self.num_buttons.value))
            if self.num_buttons > 5:
                await interaction.send("You can only have a maximum of 5 buttons", ephemeral = True)
        except:
            if not self.num_buttons.value and not self.num_buttons_value:
                self.num_buttons_value = 3
            elif not self.num_buttons_value:
                await interaction.send("The number of buttons has to be an integer", ephemeral = True)
                return

        if not (self.bottom_radius_value >= self.middle_radius_value >= self.top_radius_value):
            await interaction.send("The radii of your snowballs have to be lesser than or equal to the radius of the snowball beneath them!", ephemeral = True)
            return
        
        if 2*sum([self.bottom_radius_value, self.middle_radius_value, self.top_radius_value]) >= 950:
            await interaction.send("The sum of the diameters of your snowballs cannot exceed 950", ephemeral = True)
            return
        
        else:
            snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
            snowman_embed.add_field(name = "Bottom snowball radius", value = self.bottom_radius_value)
            snowman_embed.add_field(name = "Middle snowball radius", value = self.middle_radius_value)
            snowman_embed.add_field(name = "Top snowball radius", value = self.top_radius_value)
            snowman_embed.add_field(name = "Arm length", value = self.arm_length_value)
            snowman_embed.add_field(name = "Number of buttons", value = self.num_buttons_value)
            snowman_embed.add_field(name = "Primary hat colour", value = str(self.rgb))
            snowman_embed.add_field(name = "Secondary hat colour", value = str(self.rgb_sec))
            snowman_embed.add_field(name = "Primary scarf colour", value = str(self.scarf))
            snowman_embed.add_field(name = "Secondary scarf colour", value = str(self.scarf_sec))
            snowman_embed.add_field(name = "Background colour", value = str(self.bg))
            snowman_embed.set_footer(text = "Image dimensions: 1024 x 1024")
            self.button_view.modal_design.setValues(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value)
            createImage(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, self.rgb[::-1], self.rgb_sec[::-1], self.scarf[::-1], self.scarf_sec[::-1], self.bg[::-1], interaction.guild_id, interaction.user.id)
            return await interaction.response.edit_message(embed = snowman_embed, view = self.button_view, file = discord.File(f"./build-a-snowman/snowmen/{interaction.guild_id}_{interaction.user.id}.png"))
    
    def setValues(self, hat_colour, hat_colour_secondary, scarf_colour, scarf_colour_secondary, bg_colour):
        self.rgb = hat_colour
        self.rgb_sec = hat_colour_secondary
        self.scarf = scarf_colour
        self.scarf_sec = scarf_colour_secondary
        self.bg = bg_colour

class BuildDesign(discord.ui.Modal):
    def __init__(self, button_view: discord.ui.View, bottom_radius: int = 150, middle_radius: int = 112, top_radius: int = 84, arm_length: int = 125, num_buttons: int = 3, rgb: tuple = (0, 0, 0), rgb_sec: tuple = (255, 0, 0), scarf: tuple = (255, 0, 0), scarf_sec: tuple = (0, 0, 255), bg: tuple = (55, 100, 255)):
        super().__init__("Build a snowman!", timeout = None)
        self.button_view = button_view
        self.bottom_radius_value = bottom_radius
        self.middle_radius_value = middle_radius
        self.top_radius_value = top_radius
        self.arm_length_value = arm_length
        self.num_buttons_value = num_buttons
        self.rgb = rgb
        self.rgb_sec = rgb_sec
        self.scarf = scarf
        self.scarf_sec = scarf_sec
        self.bg = bg

        self.hat_colour = discord.ui.TextInput(
            label = "Primary colour of the hat",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the primary colour of the hat (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.hat_colour)

        self.hat_colour_secondary = discord.ui.TextInput(
            label = "Secondary colour of the hat",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the secondary colour of the hat (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.hat_colour_secondary)

        self.scarf_colour = discord.ui.TextInput(
            label = "Primary colour of the scarf",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the primary colour of the scarf (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.scarf_colour)

        self.scarf_colour_secondary = discord.ui.TextInput(
            label = "Secondary colour of the scarf",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the secondary colour of the scarf (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.scarf_colour_secondary)

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
        
        if self.hat_colour_secondary.value:
            self.rgb_sec = ConvertToRGB(self.hat_colour_secondary.value)
            if self.rgb_sec == 0:
                await interaction.send("The hex code has to have 6 symbols!", ephemeral = True)
                return
            elif self.rgb_sec == 1:
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
        
        if self.scarf_colour_secondary.value:
            self.scarf_sec = ConvertToRGB(self.scarf_colour_secondary.value)
            if self.scarf_sec == 0:
                await interaction.send("The hex code has to have 6 symbols!", ephemeral = True)
                return
            elif self.scarf_sec == 1:
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
        snowman_embed.add_field(name = "Primary hat colour", value = str(self.rgb))
        snowman_embed.add_field(name = "Secondary hat colour", value = str(self.rgb_sec))
        snowman_embed.add_field(name = "Primary scarf colour", value = str(self.scarf))
        snowman_embed.add_field(name = "Secondary scarf colour", value = str(self.scarf_sec))
        snowman_embed.add_field(name = "Background colour", value = str(self.bg))
        snowman_embed.set_footer(text = "Image dimensions: 1024 x 1024")
        self.button_view.modal_structure.setValues(self.rgb, self.rgb_sec, self.scarf, self.scarf_sec, self.bg)
        createImage(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, self.rgb[::-1], self.rgb_sec[::-1], self.scarf[::-1], self.scarf_sec[::-1], self.bg[::-1], interaction.guild_id, interaction.user.id)
        return await interaction.response.edit_message(embed = snowman_embed, view = self.button_view, file = discord.File(f"./build-a-snowman/snowmen/{interaction.guild_id}_{interaction.user.id}.png"))
    
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
    
    @discord.ui.button(label = "🔨 Build", style = discord.ButtonStyle.blurple)
    async def structure(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_structure)
    
    @discord.ui.button(label = "🎨 Design", style = discord.ButtonStyle.blurple)
    async def design(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_design)
    
    @discord.ui.button(label = "✅ Done", style = discord.ButtonStyle.blurple)
    async def done(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view = None)

def createImage(bottom_radius: int, middle_radius: int, top_radius: int, arm_length: int, num_buttons: int, hat_colour: tuple, hat_colour_secondary: tuple, scarf_colour: tuple, scarf_colour_secondary: tuple, bg_colour: tuple, guild_id: int, user: str):
    side = 1024
    img = np.zeros((side, side, 3), np.uint8)
    img[:,:] = bg_colour
    cv2.circle(img, (side//2, side-bottom_radius), bottom_radius, (255, 255, 255), -1)
    cv2.circle(img, (side//2, side-(2*bottom_radius+middle_radius)), middle_radius, (255, 255, 255), -1)
    cv2.circle(img, (side//2, side-(2*bottom_radius+2*middle_radius+top_radius)), top_radius, (255, 255, 255), -1)
    arm_right_start = ((side//2+middle_radius), (side-(2*bottom_radius+middle_radius)))
    arm_right_end = (int(side//2+middle_radius+(arm_length)//1.4), int(side-(2*bottom_radius+middle_radius)-(arm_length)//1.4))
    arm_left_start = ((side//2-middle_radius), (side-(2*bottom_radius+middle_radius)))
    arm_left_end = (int(side//2-middle_radius-(arm_length)//1.4), int(side-(2*bottom_radius+middle_radius)-(arm_length)//1.4))
    cv2.line(img, arm_right_start, arm_right_end, (0, 75, 150), 3)
    cv2.line(img, arm_left_start, arm_left_end, (0, 75, 150), 3)
    hat_bottom_start = (side//2-middle_radius, side-int(2*bottom_radius+2*middle_radius+2.5*top_radius)+top_radius//6)
    hat_bottom_end = (side//2+middle_radius, side-(2*bottom_radius+2*middle_radius+2*top_radius)+top_radius//6)
    hat_top_start = (side//2-middle_radius//2, side-(2*bottom_radius+2*middle_radius+4*top_radius)+top_radius//6)
    hat_top_end = (side//2+middle_radius//2, side-int(2*bottom_radius+2*middle_radius+2.5*top_radius)+top_radius//6)
    cv2.rectangle(img, hat_bottom_start, hat_bottom_end, hat_colour, -1)
    cv2.rectangle(img, hat_top_start, hat_top_end, hat_colour, -1)
    cv2.line(img, (side//2-middle_radius//2, side-int(2*bottom_radius+2*middle_radius+2.5*top_radius)), (side//2+middle_radius//2, side-int(2*bottom_radius+2*middle_radius+2.5*top_radius)), hat_colour_secondary, 3)
    for x in range(-top_radius//2, (top_radius//2) + 1, top_radius//7):
        y_coord = int((top_radius**2 - x**2)**(0.5))
        point = (side//2 + x, (side-(2*bottom_radius+2*middle_radius+top_radius))+y_coord)
        cv2.circle(img, point, top_radius//5, scarf_colour, -1)
        cv2.circle(img, point, top_radius//10, scarf_colour_secondary, -1)
    cv2.circle(img, (side//2, side-(2*bottom_radius+2*middle_radius+top_radius)), top_radius//10, (0, 165, 255), -1)
    cv2.circle(img, (side//2+top_radius//4, side-(2*bottom_radius+2*middle_radius+top_radius)-top_radius//3), top_radius//10, (0, 0, 0), -1)
    cv2.circle(img, (side//2-top_radius//4, side-(2*bottom_radius+2*middle_radius+top_radius)-top_radius//3), top_radius//10, (0, 0, 0), -1)
    for x in range(-top_radius//3, (top_radius//3) + 1, top_radius//6):
        y_coord = int(((int(top_radius*0.5))**2 - x**2)**(0.5))
        point = (side//2 + x, (side-(2*bottom_radius+2*middle_radius+top_radius))+y_coord)
        cv2.circle(img, point, top_radius//10, (0, 0, 0), -1)
    dist = (side-4*bottom_radius//3) - (side-2*bottom_radius-middle_radius)
    breaks = dist//(num_buttons-1)
    for x in range(num_buttons):
        cv2.circle(img, (side//2, (side-4*bottom_radius//3) - x*breaks), middle_radius//10, (0, 0, 0), -1)
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

@bot.slash_command(name = "snowman", description = "Do you wanna build a snowman?")
async def snowman(interaction: discord.Interaction):
    pass

@snowman.subcommand(name = "build", description = "Build a snowman")
async def snowman_build(interaction: discord.Interaction):
    button_view = BuildView()
    snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
    snowman_embed.add_field(name = "Bottom snowball radius", value = 150)
    snowman_embed.add_field(name = "Middle snowball radius", value = 112)
    snowman_embed.add_field(name = "Top snowball radius", value = 84)
    snowman_embed.add_field(name = "Arm length", value = 125)
    snowman_embed.add_field(name = "Number of buttons", value = 3)
    snowman_embed.add_field(name = "Primary hat colour", value = (0, 0, 0))
    snowman_embed.add_field(name = "Secondary hat colour", value = (255, 0, 0))
    snowman_embed.add_field(name = "Primary scarf colour", value = (255, 0, 0))
    snowman_embed.add_field(name = "Secondary scarf colour", value = (0, 0, 255))
    snowman_embed.add_field(name = "Background colour", value = (55, 100, 255))
    snowman_embed.set_footer(text = "Image dimensions: 1024 x 1024")
    await interaction.send(view = button_view, embed = snowman_embed, file = discord.File("./build-a-snowman/basic_snowman.png"), ephemeral = True)

@bot.slash_command(name = "snowball", description = "Do you wanna go out and play?")
async def snowball(interaction: discord.Interaction):
    pass

@snowball.subcommand(name = "load", description = "Load a snowball")
async def snowball_load(interaction: discord.Interaction):
    global snowball_data
    try:
        if not snowball_data[interaction.guild_id][interaction.user.id]["lastHit"]:
            if snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] < 2 and (int(str(time.time()).split(".")[0])-snowball_data[interaction.guild_id][interaction.user.id]["lastLoad"] >= 30 or not snowball_data[interaction.guild_id][interaction.user.id]["lastLoad"]):
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] += 1
                snowball_data[interaction.guild_id][interaction.user.id]["lastLoad"] = int(str(time.time()).split(".")[0])
                await interaction.send(f"Snowball loaded! You now have **{snowball_data[interaction.guild_id][interaction.user.id]['snowballs']}** snowballs!", ephemeral = True)
            elif snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] >= 2:
                await interaction.send("You cannot load more than 2 snowballs!", ephemeral = True)
            else:
                await interaction.send(f"You have recently loaded a snowball! Try again <t:{snowball_data[interaction.guild_id][interaction.user.id]['lastLoad']+30}:R>", ephemeral = True)
        else:
            if int(str(time.time()).split(".")[0]) - snowball_data[interaction.guild_id][interaction.user.id]["lastHit"] >= 30:
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] += 1
                snowball_data[interaction.guild_id][interaction.user.id]["lastLoad"] = int(str(time.time()).split(".")[0])
                snowball_data[interaction.guild_id][interaction.user.id]["lastHit"] = None
                await interaction.send(f"Snowball loaded! You now have **{snowball_data[interaction.guild_id][interaction.user.id]['snowballs']}** snowballs!", ephemeral = True)
            else:
                await interaction.send(f"You have recently been hit by a player! You can load a snowball <t:{snowball_data[interaction.guild_id][interaction.user.id]['lastHit']+30}:R>", ephemeral = True)
    except:
        if interaction.guild.id not in list(snowball_data.keys()):
            snowball_data[interaction.guild_id] = {}
        snowball_data[interaction.guild_id][interaction.user.id] = {"snowballs": 1, "lastLoad": int(str(time.time()).split(".")[0]), "lastHit": None}
        await interaction.send(f"Snowball loaded! You now have **{snowball_data[interaction.guild_id][interaction.user.id]['snowballs']}** snowballs!", ephemeral = True)

@snowball.subcommand(name = "throw", description = "Throw a snowball")
async def snowball_throw(interaction: discord.Interaction, user: discord.Member = discord.SlashOption(name = "user", description = "The user you want to throw the snowball at", required = True)):
    global snowball_data
    probability = [True, True, True, True, False, False, False, False, False, False]
    try:
        if snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] > 0:
            if not snowball_data[interaction.guild_id][interaction.user.id]["lastHit"]:
                shot = rd.choice(probability)
                if shot:
                    snowball_data[interaction.guild_id][user.id]["lastHit"] = int(str(time.time()).split(".")[0])
                    snowball_data[interaction.guild_id][user.id]["snowballs"] = 0
                    snowball_data[interaction.guild_id][user.id]["lastLoad"] = None
                    snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                    await interaction.send(f"Sucess! {interaction.user.mention} has managed to hit {user.mention} with a snowball!")
                else:
                    snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                    await interaction.send(f"Close shot! {interaction.user.mention} missed {user.mention} by a whisker!")
            else:
                await interaction.send(f"{user.mention} has recently been hit by a snowball! Try again <t:{snowball_data[interaction.guild_id][user.id]['lastHit']+30}:R>", ephemeral = True)
        else:
            await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1050412204312252486>", ephemeral = True)
    except:
        if interaction.guild_id not in list(snowball_data.keys()):
            snowball_data[interaction.guild_id] = {}
        if interaction.user.id not in list(snowball_data[interaction.guild_id].keys()):
            await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1050412204312252486>", ephemeral = True)
        else:
            snowball_data[interaction.guild_id][user.id] = {"snowballs": 0, "lastHit": None}
            shot = rd.choice(probability)
            if shot:
                snowball_data[interaction.guild_id][user.id]["lastHit"] = int(str(time.time()).split(".")[0])
                snowball_data[interaction.guild_id][user.id]["snowballs"] = 0
                snowball_data[interaction.guild_id][user.id]["lastLoad"] = None
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                await interaction.send(f"Sucess! {interaction.user.mention} has managed to hit {user.mention} with a snowball!")
            else:
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                await interaction.send(f"Close shot! {interaction.user.mention} missed {user.mention} by a whisker!")

bot.run(token)