import nextcord as discord
from nextcord.ext import commands
import cv2
import numpy as np
import time
import random as rd
import requests
from records import save_snowman, get_snowman, change_stats, get_stats, get_leaderboard, quest_update, get_quest
import os

bot = commands.Bot()
token = os.getenv("DISCORD_TOKEN")

snowball_data = {}

@bot.event
async def on_ready():
    print("Do you want to build a snowman?")
    await bot.change_presence(activity = discord.Activity(name = "Frozen", type = discord.ActivityType.watching))
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("Do you want to build a snowman?")

@bot.event
async def on_guild_join(guild: discord.Guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send(f"New server: {guild}")
    new_server = discord.Embed(title = "Overview", description = "Hey there!\n\nHere is an overview of the bot submitted by Vishnu#2973 for the SnowCodes bot jam 2022. Get ready to embark on a journey and rediscover your childhood, as we make the movie Frozen a reality!", colour = discord.Colour.blue())
    new_server.set_footer(text = "Help page 1/4")
    channel = guild.system_channel
    if channel != None:
        try:
            await channel.send(embed = new_server, view = HelpView())
        except discord.errors.Forbidden:
            pass

@bot.event
async def on_guild_remove(guild: discord.Guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send(f"Removed from: {guild}")

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
        
        if 2*sum([self.bottom_radius_value, self.middle_radius_value, self.top_radius_value]) > 950:
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
            return await interaction.response.edit_message(embed = snowman_embed, view = self.button_view, file = discord.File(f"./snowmen/{interaction.guild_id}_{interaction.user.id}.png"))
    
    def getValues(self):
        return [self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, ConvertToHex(self.rgb), ConvertToHex(self.rgb_sec), ConvertToHex(self.scarf), ConvertToHex(self.scarf_sec), ConvertToHex(self.bg)]

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
        return await interaction.response.edit_message(embed = snowman_embed, view = self.button_view, file = discord.File(f"./snowmen/{interaction.guild_id}_{interaction.user.id}.png"))
    
    def getValues(self):
        return [self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, ConvertToHex(self.rgb), ConvertToHex(self.rgb_sec), ConvertToHex(self.scarf), ConvertToHex(self.scarf_sec), ConvertToHex(self.bg)]

    def setValues(self, bottom_radius, middle_radius, top_radius, arm_length, num_buttons):
        self.bottom_radius_value = bottom_radius
        self.middle_radius_value = middle_radius
        self.top_radius_value = top_radius
        self.arm_length_value = arm_length
        self.num_buttons_value = num_buttons

class ColourModal(discord.ui.Modal):
    def __init__(self):
        super().__init__("Hex code to colour!", timeout = None)

        self.colour = discord.ui.TextInput(
            label = "Hex code",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code",
            required = True
        )
        self.add_item(self.colour)
    
    async def callback(self, interaction: discord.Interaction):
        self.colour_value = ConvertToRGB(self.colour.value)
        if self.colour_value == 0:
            await interaction.send("The hex code has to have 6 symbols!", ephemeral = True)
            return
        elif self.colour_value == 1:
            await interaction.send("Invalid hex code", ephemeral = True)
            return
        colour_embed = discord.Embed(title = "Hex code to colour", colour = discord.Colour.blue())
        colour_embed.add_field(name = "Hex code", value = self.colour.value)
        colour_embed.add_field(name = "RGB code", value = self.colour_value)
        colourBox(self.colour_value[::-1], interaction.guild_id, interaction.user.id)
        await interaction.response.edit_message(embed = colour_embed, file = discord.File(f"./colours/{interaction.guild_id}_{interaction.user.id}.png"))


class ColourView(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label = "Red", description = "Get the hex code for the colour red", emoji = "🔴"),
            discord.SelectOption(label = "Orange", description = "Get the hex code for the colour orange", emoji = "🟠"),
            discord.SelectOption(label = "Yellow", description = "Get the hex code for the colour yellow", emoji = "🟡"),
            discord.SelectOption(label = "Green", description = "Get the hex code for the colour green", emoji = "🟢"),
            discord.SelectOption(label = "Blue", description = "Get the hex code for the colour blue", emoji = "🔵"),
            discord.SelectOption(label = "Purple", description = "Get the hex code for the colour purple", emoji = "🟣"),
            discord.SelectOption(label = "Brown", description = "Get the hex code for the colour brown", emoji = "🟤"),
            discord.SelectOption(label = "Black", description = "Get the hex code for the colour black", emoji = "⚫"),
            discord.SelectOption(label = "White", description = "Get the hex code for the colour white", emoji = "⚪"),
            discord.SelectOption(label = "Choose", description = "View the colour for your chosen hex code", emoji = "🎨"),
            discord.SelectOption(label = "Random", description = "Get the hex code for a random colour", emoji = "🎲")
        ]
        super().__init__(placeholder = "Select a colour option", min_values = 1, max_values = 1, options = options)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Red":
            code = "ff0000"
        elif self.values[0] == "Orange":
            code = "ffa500"
        elif self.values[0] == "Yellow":
            code = "ffd800"
        elif self.values[0] == "Green":
            code = "44c022"
        elif self.values[0] == "Blue":
            code = "0081ff"
        elif self.values[0] == "Purple":
            code = "7b00ff"
        elif self.values[0] == "Brown":
            code = "964b00"
        elif self.values[0] == "Black":
            code = "000000"
        elif self.values[0] == "White":
            code = "ffffff"
        elif self.values[0] == "Choose":
            hex_modal = ColourModal()
            await interaction.response.send_modal(hex_modal)
            return
        elif self.values[0] == "Random":
            code = ConvertToHex((rd.randint(0, 255), rd.randint(0, 255), rd.randint(0, 255)))
        colour_embed = discord.Embed(title = "Hex code to colour", colour = discord.Colour.blue())
        colour_embed.add_field(name = "Hex code", value = code)
        colour_embed.add_field(name = "RGB code", value = ConvertToRGB(code))
        colourBox(ConvertToRGB(code)[::-1], interaction.guild_id, interaction.user.id)
        await interaction.response.edit_message(embed = colour_embed, file = discord.File(f"./colours/{interaction.guild_id}_{interaction.user.id}.png"))
        return

class BuildView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.modal_structure = BuildStructure(self)
        self.modal_design = BuildDesign(self)
    
    @discord.ui.button(label = "Build", style = discord.ButtonStyle.blurple, emoji = "🛠")
    async def structure(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_structure)
    
    @discord.ui.button(label = "Design", style = discord.ButtonStyle.blurple, emoji = "🖌")
    async def design(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_design)
    
    @discord.ui.button(label = "Colour picker", style = discord.ButtonStyle.blurple, emoji = "🎨")
    async def colours(self, button: discord.ui.Button, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(ColourView())
        await interaction.send(view = view, ephemeral = True)

    @discord.ui.button(label = "Favourite", style = discord.ButtonStyle.red, emoji = "🌟")
    async def favourite(self, button: discord.ui.Button, interaction: discord.Interaction):
        save_snowman(interaction.user.id, self.modal_structure.getValues())
        await interaction.response.edit_message(content = "**Snowman saved!**", view = None)

    @discord.ui.button(label = "Done", style = discord.ButtonStyle.green, emoji = "✅")
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
    cv2.line(img, arm_right_start, arm_right_end, (0, 75, 150), 5)
    cv2.line(img, arm_left_start, arm_left_end, (0, 75, 150), 5)
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
    if num_buttons > 1:
        breaks = dist//(num_buttons-1)
        for x in range(num_buttons):
            cv2.circle(img, (side//2, (side-4*bottom_radius//3) - x*breaks), middle_radius//10, (0, 0, 0), -1)
    elif num_buttons == 1:
        cv2.circle(img, (side//2, side-2*bottom_radius), middle_radius//10, (0, 0, 0), -1)
    cv2.imwrite(f"./snowmen/{guild_id}_{user}.png", img)

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

def ConvertToHex(colour: tuple):
    final = ""
    for x in colour:
        hexa = hex(x)[2:]
        hexa = "0"*(2-len(hexa))+hexa
        final += hexa
    return final

def colourBox(colour: tuple, guild_id: int, user: int):
    box = np.zeros((512, 1024, 3), np.uint8)
    box[:,:] = colour
    cv2.imwrite(f"./colours/{guild_id}_{user}.png", box)

@bot.slash_command(name = "snowman", description = "Do you want to build a snowman?")
async def snowman(interaction: discord.Interaction):
    pass

@snowman.subcommand(name = "build", description = "Build a snowman!")
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
    await interaction.send(view = button_view, embed = snowman_embed, file = discord.File("./basic_snowman.png"), ephemeral = True)

@snowman.subcommand(name = "favourite", description = "View your favourite snowman!")
async def snowman_favourite(interaction: discord.Interaction):
    fav_snowman = get_snowman(interaction.user.id)
    if fav_snowman:
        createImage(fav_snowman[0], fav_snowman[1], fav_snowman[2], fav_snowman[3], fav_snowman[4], ConvertToRGB(fav_snowman[5])[::-1], ConvertToRGB(fav_snowman[6])[::-1], ConvertToRGB(fav_snowman[7])[::-1], ConvertToRGB(fav_snowman[8])[::-1], ConvertToRGB(fav_snowman[9])[::-1], interaction.guild_id, interaction.user.id)
        snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
        snowman_embed.add_field(name = "Bottom snowball radius", value = fav_snowman[0])
        snowman_embed.add_field(name = "Middle snowball radius", value = fav_snowman[1])
        snowman_embed.add_field(name = "Top snowball radius", value = fav_snowman[2])
        snowman_embed.add_field(name = "Arm length", value = fav_snowman[3])
        snowman_embed.add_field(name = "Number of buttons", value = fav_snowman[4])
        snowman_embed.add_field(name = "Primary hat colour", value = ConvertToRGB(fav_snowman[5]))
        snowman_embed.add_field(name = "Secondary hat colour", value = ConvertToRGB(fav_snowman[6]))
        snowman_embed.add_field(name = "Primary scarf colour", value = ConvertToRGB(fav_snowman[7]))
        snowman_embed.add_field(name = "Secondary scarf colour", value = ConvertToRGB(fav_snowman[8]))
        snowman_embed.add_field(name = "Background colour", value = ConvertToRGB(fav_snowman[9]))
        snowman_embed.set_footer(text = "Image dimensions: 1024 x 1024")
        await interaction.send(embed = snowman_embed, file = discord.File(f"./snowmen/{interaction.guild_id}_{interaction.user.id}.png"))
    else:
        await interaction.send("You do not have a favourite snowman yet!", ephemeral = True)

@bot.slash_command(name = "snowball", description = "Do you want to go out and play?")
async def snowball(interaction: discord.Interaction):
    pass

@snowball.subcommand(name = "load", description = "Load a snowball!")
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

def createShooter(guild_id: int, user: int, loc: int = 1, game: bool = True, real_loc: int = 1):
    side = 512
    img = np.zeros((side, side, 3), np.uint8)
    img[:,:] = (255, 100, 55)

    if game:
        cv2.circle(img, (side//6, side//6), 5, (255, 255, 255), -1)
        cv2.circle(img, (side//6, side//6 + 15), 10, (255, 255, 255), -1)
        cv2.circle(img, (side//6, side//6 + 40), 15, (255, 255, 255), -1)
    else:
        if real_loc == 0:
            cv2.circle(img, (side//6, side//6 + 15), 20, (0, 0, 255), -1)
            cv2.circle(img, (side//6, side//6 + 15), 15, (255, 255, 255), -1)
            cv2.circle(img, (side//6, side//6 + 15), 10, (0, 0, 255), -1)
            cv2.circle(img, (side//6, side//6 + 15), 5, (255, 255, 255), -1)
        else:
            cv2.circle(img, (side//6, side//6), 5, (255, 255, 255), -1)
            cv2.circle(img, (side//6, side//6 + 15), 10, (255, 255, 255), -1)
            cv2.circle(img, (side//6, side//6 + 40), 15, (255, 255, 255), -1)

    if game:
        cv2.circle(img, (3*side//6, side//6), 5, (255, 255, 255), -1)
        cv2.circle(img, (3*side//6, side//6 + 15), 10, (255, 255, 255), -1)
        cv2.circle(img, (3*side//6, side//6 + 40), 15, (255, 255, 255), -1)
    else:
        if real_loc == 1:
            cv2.circle(img, (3*side//6, side//6 + 15), 20, (0, 0, 255), -1)
            cv2.circle(img, (3*side//6, side//6 + 15), 15, (255, 255, 255), -1)
            cv2.circle(img, (3*side//6, side//6 + 15), 10, (0, 0, 255), -1)
            cv2.circle(img, (3*side//6, side//6 + 15), 5, (255, 255, 255), -1)
        else:
            cv2.circle(img, (3*side//6, side//6), 5, (255, 255, 255), -1)
            cv2.circle(img, (3*side//6, side//6 + 15), 10, (255, 255, 255), -1)
            cv2.circle(img, (3*side//6, side//6 + 40), 15, (255, 255, 255), -1)

    if game:
        cv2.circle(img, (5*side//6, side//6), 5, (255, 255, 255), -1)
        cv2.circle(img, (5*side//6, side//6 + 15), 10, (255, 255, 255), -1)
        cv2.circle(img, (5*side//6, side//6 + 40), 15, (255, 255, 255), -1)
    else:
        if real_loc == 2:
            cv2.circle(img, (5*side//6, side//6 + 15), 20, (0, 0, 255), -1)
            cv2.circle(img, (5*side//6, side//6 + 15), 15, (255, 255, 255), -1)
            cv2.circle(img, (5*side//6, side//6 + 15), 10, (0, 0, 255), -1)
            cv2.circle(img, (5*side//6, side//6 + 15), 5, (255, 255, 255), -1)
        else:
            cv2.circle(img, (5*side//6, side//6), 5, (255, 255, 255), -1)
            cv2.circle(img, (5*side//6, side//6 + 15), 10, (255, 255, 255), -1)
            cv2.circle(img, (5*side//6, side//6 + 40), 15, (255, 255, 255), -1)

    if loc == 0:
        cv2.rectangle(img, (side//6 + 30, side), (side//6 - 30, side-70), (34, 192, 68), -1)
        cv2.rectangle(img, (side//6 + 10, side-70), (side//6 - 10, side-140), (34, 192, 68), -1)
        cv2.rectangle(img, (side//6 + 15, side), (side//6 - 15, side-50), (0, 0, 255), -1)
        cv2.rectangle(img, (side//6 + 5, side), (side//6 - 5, side-40), (0, 216, 255), -1)

    elif loc == 1:
        cv2.rectangle(img, (3*side//6 + 30, side), (3*side//6 - 30, side-70), (34, 192, 68), -1)
        cv2.rectangle(img, (3*side//6 + 10, side-70), (3*side//6 - 10, side-140), (34, 192, 68), -1)
        cv2.rectangle(img, (3*side//6 + 15, side), (3*side//6 - 15, side-50), (0, 0, 255), -1)
        cv2.rectangle(img, (3*side//6 + 5, side), (3*side//6 - 5, side-40), (0, 216, 255), -1)

    elif loc == 2:
        cv2.rectangle(img, (5*side//6 + 30, side), (5*side//6 - 30, side-70), (34, 192, 68), -1)
        cv2.rectangle(img, (5*side//6 + 10, side-70), (5*side//6 - 10, side-140), (34, 192, 68), -1)
        cv2.rectangle(img, (5*side//6 + 15, side), (5*side//6 - 15, side-50), (0, 0, 255), -1)
        cv2.rectangle(img, (5*side//6 + 5, side), (5*side//6 - 5, side-40), (0, 216, 255), -1)
        
    cv2.imwrite(f"./shooters/{guild_id}_{user}.png", img)

class ShootView(discord.ui.View):
    global snowball_data

    def __init__(self, target_loc: int, opponent: discord.User):
        super().__init__(timeout = None)
        self.loc = 1
        self.target_loc = target_loc
        self.opponent = opponent
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "◀")
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.loc -= 1
        if self.loc < 0:
            self.loc = 2
        createShooter(interaction.guild_id, interaction.user.id, self.loc, True, self.target_loc)
        await interaction.response.edit_message(file = discord.File(f"./shooters/{interaction.guild_id}_{interaction.user.id}.png"))
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "▶")
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.loc += 1
        if self.loc > 2:
            self.loc = 0
        createShooter(interaction.guild_id, interaction.user.id, self.loc, True, self.target_loc)
        await interaction.response.edit_message(file = discord.File(f"./shooters/{interaction.guild_id}_{interaction.user.id}.png"))
    
    @discord.ui.button(label = "Shoot", style = discord.ButtonStyle.red, emoji = "💥")
    async def shoot(self, button: discord.ui.Button, interaction: discord.Interaction):
        if snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] > 0:
            createShooter(interaction.guild_id, interaction.user.id, self.loc, False, self.target_loc)
            if self.loc == self.target_loc:
                snowball_data[interaction.guild_id][self.opponent.id]["lastHit"] = int(str(time.time()).split(".")[0])
                snowball_data[interaction.guild_id][self.opponent.id]["snowballs"] = 0
                snowball_data[interaction.guild_id][self.opponent.id]["lastLoad"] = None
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                await interaction.response.edit_message(content = "Correct target hit!", file = discord.File(f"./shooters/{interaction.guild_id}_{interaction.user.id}.png"), view = None)
                await interaction.send(f"Success! {interaction.user.mention} has managed to hit {self.opponent.mention} with a snowball!")
                change_stats(interaction.guild_id, interaction.user.id, 0)
                change_stats(interaction.guild_id, self.opponent.id, 2)
            else:
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                await interaction.response.edit_message(content = "Incorrect target hit!", file = discord.File(f"./shooters/{interaction.guild_id}_{interaction.user.id}.png"), view = None)
                await interaction.send(f"Close shot! {interaction.user.mention} missed {self.opponent.mention} by a whisker!")
                change_stats(interaction.guild_id, interaction.user.id, 1)
        else:
            await interaction.response.edit_message(view = None)
            await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1052915532417998898>", ephemeral = True)

@snowball.subcommand(name = "throw", description = "Throw a snowball!")
async def snowball_throw(interaction: discord.Interaction, user: discord.Member = discord.SlashOption(name = "user", description = "The user you want to throw the snowball at", required = True)):
    global snowball_data
    probability = [0, 1, 2]
    if user.bot:
        await interaction.send("You can't throw a snowball at a bot!", ephemeral = True)
        return
    if user == interaction.user:
        try:
            if snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] != 0:
                snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] -= 1
                await interaction.send(f"{interaction.user.mention} slipped and threw a snowball at themselves!")
            else:
                await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1052915532417998898>", ephemeral = True)
        except:
            if interaction.guild_id not in list(snowball_data.keys()):
                snowball_data[interaction.guild_id] = {}
            if interaction.user.id not in list(snowball_data[interaction.guild_id].keys()):
                await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1052915532417998898>", ephemeral = True)
        return
    try:
        if snowball_data[interaction.guild_id][interaction.user.id]["snowballs"] > 0:
            if not snowball_data[interaction.guild_id][user.id]["lastHit"]:
                shot = rd.choice(probability)
                await interaction.send(content = f"Shoot at a target to see if you will hit {user.mention}!", view = ShootView(shot, user), file = discord.File("./basic_shooter.png"), ephemeral = True)
            else:
                if int(str(time.time()).split(".")[0]) - snowball_data[interaction.guild_id][user.id]["lastHit"] >= 30:
                    await interaction.send(content = f"Shoot at a target to see if you will hit {user.mention}!", view = ShootView(shot, user), file = discord.File("./basic_shooter.png"), ephemeral = True)
                else:
                    await interaction.send(f"{user.mention} has recently been hit by a snowball! Try again <t:{snowball_data[interaction.guild_id][user.id]['lastHit']+30}:R>", ephemeral = True)
        else:
            await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1052915532417998898>", ephemeral = True)
    except:
        if interaction.guild_id not in list(snowball_data.keys()):
            snowball_data[interaction.guild_id] = {}
        if interaction.user.id not in list(snowball_data[interaction.guild_id].keys()):
            await interaction.send("You do not have any snowballs to throw! Load some with </snowball load:1052915532417998898>", ephemeral = True)
        else:
            snowball_data[interaction.guild_id][user.id] = {"snowballs": 0, "lastLoad": None, "lastHit": None}
            shot = rd.choice(probability)
            await interaction.send(content = f"Shoot at a target to see if you will hit {user.mention}!", view = ShootView(shot, user), file = discord.File("./basic_shooter.png"), ephemeral = True)

@snowball.subcommand(name = "leaderboard", description = "View your server's snowball leaderboard!")
async def snowball_leaderboard(interaction: discord.Interaction):
    leaderboard = get_leaderboard(interaction.guild_id)
    leaderboard_embed = discord.Embed(title = "Server leaderboard", colour = discord.Colour.blue())
    if leaderboard:
        names = ""
        for x in leaderboard:
            if x == leaderboard[0]:
                names += "🥇"
            elif x == leaderboard[1]:
                if x[1:] == leaderboard[0][1:]:
                    names += "🥇"
                else:
                    names += "🥈"
            elif x == leaderboard[2]:
                if x[1:] == leaderboard[0][1:]:
                    names += "🥇"
                elif x[1:] == leaderboard[1][1:]:
                    names += "🥈"
                else:
                    names += "🥉"
            else:
                if x[1:] == leaderboard[0][1:]:
                    names += "🥇"
                elif x[1:] == leaderboard[1][1:]:
                    names += "🥈"
                elif x[1:] == leaderboard[2][1:]:
                    names += "🥉"
                else:
                    names += "👏"
            names += f"<@!{x[0]}>: Hits: {x[1]} | Misses: {x[2]} | Knock Outs: {x[3]}\n"
        leaderboard_embed.description = names
    else:
        leaderboard_embed.description = "Nobody has played the snowball game in this server yet!"
    await interaction.send(embed = leaderboard_embed)

@snowball.subcommand(name = "profile", description = "View a user's snowball statistics")
async def snowball_profile(interaction: discord.Interaction, user: discord.Member = discord.SlashOption(name = "user", description = "The user who's profile you would like to view", required = False)):
    if not user:
        user = interaction.user
    else:
        if user.bot:
            await interaction.send("You cannot view the profile of a bot!", ephemeral = True)
            return
    user_stats = get_stats(interaction.guild.id, user.id)
    user_embed = discord.Embed(title = f"Statistics for {user.name} in {interaction.guild}", colour = discord.Colour.blue())
    if user_stats:
        user_embed.add_field(name = "Hits", value = user_stats[0])
        user_embed.add_field(name = "Misses", value = user_stats[1])
        user_embed.add_field(name = "Knock Outs", value = user_stats[2])
    else:
        user_embed.description = f"{user.mention} has no snowball statistics yet!"
    await interaction.send(embed = user_embed)

class QuestView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout = None)
        self.pos = 0
        self.user = user
    
    @discord.ui.button(label = "Move", style = discord.ButtonStyle.blurple, emoji = "🚶‍♂️")
    async def move(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.pos in [0, 1]:
            difficulty = "easy"
        elif self.pos in [2, 3]:
            difficulty = "medium"
        else:
            difficulty = "hard"
        question_data = requests.get(f"https://the-trivia-api.com/api/questions?limit=1&difficulty={difficulty}").json()[0]
        question = question_data["question"]
        options = question_data["incorrectAnswers"]
        options.append(question_data["correctAnswer"])
        rd.shuffle(options)
        question_embed = discord.Embed(title = "Trivia!", description = f"*Difficulty*: **{question_data['difficulty'].capitalize()}**", colour = discord.Colour.blue())
        question_embed.add_field(name = "Question", value = f"**{question}**", inline = False)
        question_embed.add_field(name = "Options", value = f'''1️⃣ *{str(options[0]).capitalize()}*
2️⃣ *{str(options[1]).capitalize()}*
3️⃣ *{str(options[2]).capitalize()}*
4️⃣ *{str(options[3]).capitalize()}*
''', inline = False)
        await interaction.response.edit_message(embed = question_embed, view = QuizView(options.index(question_data["correctAnswer"])+1, question_data["correctAnswer"], self.user, self))

class QuizView(discord.ui.View):
    def __init__(self, answer: int, correct: str, user: discord.User, view_orig: QuestView):
        super().__init__(timeout = None)
        self.answer = answer
        self.correct = correct
        self.user = user
        self.view_orig = view_orig
        self.castle = "⬛⬛🏰⬛⬛"
        self.normal = "⬛⬛⬜⬛⬛"
        self.people = "⬛⬛🧑‍🤝‍🧑⬛⬛"
        self.dead = "⬛⬛❌⬛⬛"
        self.complete = "⬛⬛🟨⬛⬛"
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "1️⃣")
    async def one(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.answer == 1:
            self.view_orig.pos += 1
            if self.view_orig.pos != 5:
                journey = f"{self.castle}\n"
                done = False
                for x in range(5):
                    if 5-x-1 == self.view_orig.pos:
                        journey += f"{self.people}\n"
                        done = True
                    elif done:
                        journey += f"{self.complete}\n"
                    else:
                        journey += f"{self.normal}\n"

                await interaction.response.edit_message(content = "Correct answer!\n"+journey, embed = None, view = self.view_orig)
            else:
                journey = f"{self.people}\n"
                for x in range(5):
                    journey += f"{self.complete}\n"
                await interaction.response.edit_message(content = "You have successfully reached the castle! Let's meet Elsa!\n"+journey, embed = None, view = None)
                quest_update(interaction.user.id, True)
        else:
            journey = f"{self.castle}\n"
            done = False
            for x in range(5):
                if 5-x-1 == self.view_orig.pos:
                    journey += f"{self.people}\n"
                    done = True
                elif done:
                    journey += f"{self.complete}\n"
                else:
                    journey += f"{self.dead}\n"
            await interaction.response.edit_message(content = f"Incorrect answer! The correct answer was `{self.correct}`! You failed to reach the castle!\n"+journey, view = None)
            quest_update(interaction.user.id, False)
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "2️⃣")
    async def two(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.answer == 2:
            self.view_orig.pos += 1
            if self.view_orig.pos != 5:
                journey = f"{self.castle}\n"
                done = False
                for x in range(5):
                    if 5-x-1 == self.view_orig.pos:
                        journey += f"{self.people}\n"
                        done = True
                    elif done:
                        journey += f"{self.complete}\n"
                    else:
                        journey += f"{self.normal}\n"

                await interaction.response.edit_message(content = "Correct answer!\n"+journey, embed = None, view = self.view_orig)
            else:
                journey = f"{self.people}\n"
                for x in range(5):
                    journey += f"{self.complete}\n"
                await interaction.response.edit_message(content = "You have successfully reached the castle! Let's meet Elsa!\n"+journey, embed = None, view = None)
                quest_update(interaction.user.id, True)
        else:
            journey = f"{self.castle}\n"
            done = False
            for x in range(5):
                if 5-x-1 == self.view_orig.pos:
                    journey += f"{self.people}\n"
                    done = True
                elif done:
                    journey += f"{self.complete}\n"
                else:
                    journey += f"{self.dead}\n"
            await interaction.response.edit_message(content = f"Incorrect answer! The correct answer was `{self.correct}`! You failed to reach the castle!\n"+journey, view = None)
            quest_update(interaction.user.id, False)
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "3️⃣")
    async def three(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.answer == 3:
            self.view_orig.pos += 1
            if self.view_orig.pos != 5:
                journey = f"{self.castle}\n"
                done = False
                for x in range(5):
                    if 5-x-1 == self.view_orig.pos:
                        journey += f"{self.people}\n"
                        done = True
                    elif done:
                        journey += f"{self.complete}\n"
                    else:
                        journey += f"{self.normal}\n"

                await interaction.response.edit_message(content = "Correct answer!\n"+journey, embed = None, view = self.view_orig)
            else:
                journey = f"{self.people}\n"
                for x in range(5):
                    journey += f"{self.complete}\n"
                await interaction.response.edit_message(content = "You have successfully reached the castle! Let's meet Elsa!\n"+journey, embed = None, view = None)
                quest_update(interaction.user.id, True)
        else:
            journey = f"{self.castle}\n"
            done = False
            for x in range(5):
                if 5-x-1 == self.view_orig.pos:
                    journey += f"{self.people}\n"
                    done = True
                elif done:
                    journey += f"{self.complete}\n"
                else:
                    journey += f"{self.dead}\n"
            await interaction.response.edit_message(content = f"Incorrect answer! The correct answer was `{self.correct}`! You failed to reach the castle!\n"+journey, view = None)
            quest_update(interaction.user.id, False)
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "4️⃣")
    async def four(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.answer == 4:
            self.view_orig.pos += 1
            if self.view_orig.pos != 5:
                journey = f"{self.castle}\n"
                done = False
                for x in range(5):
                    if 5-x-1 == self.view_orig.pos:
                        journey += f"{self.people}\n"
                        done = True
                    elif done:
                        journey += f"{self.complete}\n"
                    else:
                        journey += f"{self.normal}\n"

                await interaction.response.edit_message(content = "Correct answer!\n"+journey, embed = None, view = self.view_orig)
            else:
                journey = f"{self.people}\n"
                for x in range(5):
                    journey += f"{self.complete}\n"
                await interaction.response.edit_message(content = "You have successfully reached the castle! Let's meet Elsa!\n"+journey, embed = None, view = None)
                quest_update(interaction.user.id, True)
        else:
            journey = f"{self.castle}\n"
            done = False
            for x in range(5):
                if 5-x-1 == self.view_orig.pos:
                    journey += f"{self.people}\n"
                    done = True
                elif done:
                    journey += f"{self.complete}\n"
                else:
                    journey += f"{self.dead}\n"
            await interaction.response.edit_message(content = f"Incorrect answer! The correct answer was `{self.correct}`! You failed to reach the castle!\n"+journey, view = None)
            quest_update(interaction.user.id, False)

@bot.slash_command(name = "quest", description = "Let's get Elsa!")
async def quest(interaction: discord.Interaction):
    pass

@quest.subcommand(name = "new", description = "Begin your quest!")
async def quest_new(interaction: discord.Interaction):
    journey = '''⬛⬛🏰⬛⬛
⬛⬛⬜⬛⬛
⬛⬛⬜⬛⬛
⬛⬛⬜⬛⬛
⬛⬛⬜⬛⬛
⬛⬛🧑‍🤝‍🧑⬛⬛ 
'''
    await interaction.send("Begin your journey to get to Elsa!\n"+journey, view = QuestView(interaction.user))

@quest.subcommand(name = "profile", description = "View a user's quest statistics")
async def quest_profile(interaction: discord.Interaction, user: discord.Member = discord.SlashOption(name = "user", description = "The user who's profile you would like to view", required = False)):
    if not user:
        user = interaction.user
    else:
        if user.bot:
            await interaction.send("You cannot view the profile of a bot!", ephemeral = True)
            return
    stats = get_quest(user.id)
    stats_embed = discord.Embed(title = f"Quest statistics for {user.name}", colour = discord.Colour.blue())
    if stats:
        stats_embed.add_field(name = "Wins", value = stats[0])
        stats_embed.add_field(name = "Losses", value = stats[1])
    else:
        stats_embed.description = "The user has not done a quest yet!"
    await interaction.send(embed = stats_embed)

class SaveElsa(discord.ui.View):
    def __init__(self, grid: list, current_dir: str, user: discord.User):
        super().__init__(timeout = 30.0)
        self.interaction_original: discord.PartialInteractionMessage = None
        self.grid = grid
        self.current_dir = current_dir
        self.user = user
        self.value = True
        self.time_start = int(str(time.time()).split(".")[0])
        self.current_loc = [None, None]
        for x in range(len(self.grid)):
            t = False
            for y in range(len(self.grid)):
                if self.grid[x][y] == "anna":
                    self.current_loc = [x, y]
                    t = True
                    break
            if t:
                break
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "⬅")
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user != interaction.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.current_loc[1] == 0:
            await interaction.send("You can't move to the left here!", ephemeral = True)
            return
        if self.current_dir == "left" and int(str(time.time()).split(".")[0]) - self.time_start < 30:
            self.grid[self.current_loc[0]][self.current_loc[1]] = True
            self.current_loc[1] -= 1
            self.current_dir = self.grid[self.current_loc[0]][self.current_loc[1]]
            self.grid[self.current_loc[0]][self.current_loc[1]] = "anna"
            if self.current_dir == "end":
                await interaction.response.edit_message(content = "You have successfully saved Elsa in time!\n"+stringGrid(self.grid), view = None)
                self.value = False
            else:
                await interaction.response.edit_message(content = f"You have to save Elsa <t:{self.time_start+30}:R>!\n"+stringGrid(self.grid))
        
        elif int(str(time.time()).split(".")[0]) - self.time_start >= 30:
            await interaction.response.edit_message(content = "You were too slow and could not save Elsa in time! Hans is now the king of Arendelle!\n"+stringGrid(self.grid), view = None)
            self.value = False

        else:
            self.current_loc[1] -= 1
            self.current_dir = self.grid[self.current_loc[0]][self.current_loc[1]]
            self.grid[self.current_loc[0]][self.current_loc[1]] = False
            await interaction.response.edit_message(content = "You moved in the wrong direction! You failed to save Elsa!\n"+stringGrid(self.grid), view = None)
            self.value = False
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "⬆")
    async def up(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user != interaction.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.current_dir == "up" and int(str(time.time()).split(".")[0]) - self.time_start < 30:
            self.grid[self.current_loc[0]][self.current_loc[1]] = True
            self.current_loc[0] -= 1
            self.current_dir = self.grid[self.current_loc[0]][self.current_loc[1]]
            self.grid[self.current_loc[0]][self.current_loc[1]] = "anna"
            if self.current_dir == "end":
                await interaction.response.edit_message(content = "You have successfully saved Elsa in time!\n"+stringGrid(self.grid), view = None)
                self.value = False
            else:
                await interaction.response.edit_message(content = f"You have to save Elsa <t:{self.time_start+30}:R>!\n"+stringGrid(self.grid))
        
        elif int(str(time.time()).split(".")[0]) - self.time_start >= 30:
            await interaction.response.edit_message(content = "You were too slow and could not save Elsa in time! Hans is now the king of Arendelle!\n"+stringGrid(self.grid), view = None)
            self.value = False

        else:
            self.current_loc[0] -= 1
            self.current_dir = self.grid[self.current_loc[0]][self.current_loc[1]]
            self.grid[self.current_loc[0]][self.current_loc[1]] = False
            await interaction.response.edit_message(content = "You moved in the wrong direction! You failed to save Elsa!\n"+stringGrid(self.grid), view = None)
            self.value = False

    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "➡")
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user != interaction.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        if self.current_loc[1] == len(self.grid)-1:
            await interaction.send("You can't move to the right here!", ephemeral = True)
            return
        if self.current_dir == "right" and int(str(time.time()).split(".")[0]) - self.time_start < 30:
            self.grid[self.current_loc[0]][self.current_loc[1]] = True
            self.current_loc[1] += 1
            self.current_dir = self.grid[self.current_loc[0]][self.current_loc[1]]
            self.grid[self.current_loc[0]][self.current_loc[1]] = "anna"
            if self.current_dir == "end":
                await interaction.response.edit_message(content = "You have successfully saved Elsa in time!\n"+stringGrid(self.grid), view = None)
                self.value = False
            else:
                await interaction.response.edit_message(content = f"You have to save Elsa <t:{self.time_start+30}:R>!\n"+stringGrid(self.grid))

        elif int(str(time.time()).split(".")[0]) - self.time_start >= 30:
            await interaction.response.edit_message(content = "You were too slow and could not save Elsa in time! Hans is now the king of Arendelle!\n"+stringGrid(self.grid), view = None)
            self.value = False

        else:
            self.current_loc[1] += 1
            self.current_dir = self.grid[self.current_loc[0]][self.current_loc[1]]
            self.grid[self.current_loc[0]][self.current_loc[1]] = False
            await interaction.response.edit_message(content = "You moved in the wrong direction! You failed to save Elsa!\n"+stringGrid(self.grid), view = None)
            self.value = False
    
    async def on_timeout(self):
        if self.value:
            await self.interaction_original.edit(content = "You were too slow and could not save Elsa in time! Hans is now the king of Arendelle!\n"+stringGrid(self.grid), view = None)
            self.value = False

def createGrid():
    grid = []
    for x in range(10):
        grid.append([None, None, None, None, None, None, None, None, None, None])
    current = [0, rd.randint(0, 9)]
    grid[current[0]][current[1]] = "anna"
    dirs = [0, 1, 2]
    while True:
        dir = rd.choice(dirs)
        if dir == 0:
            if current[1] != 0:
                current[1] -= 1
                if not grid[current[0]][current[1]]:
                    if grid[current[0]][current[1]+1] != "anna":
                        grid[current[0]][current[1]+1] = "left"
                    else:
                        start_dir = "left"
                else:
                    current[1] += 1
        elif dir == 1:
            current[0] += 1
            if not grid[current[0]][current[1]]:
                if grid[current[0]-1][current[1]] != "anna":
                    grid[current[0]-1][current[1]] = "up"
                else:
                    start_dir = "up"
                if current[0] == 9:
                    grid[current[0]][current[1]] = "end"
                    break
            else:
                current[0] -= 1
        elif dir == 2:
            if current[1] != 9:
                current[1] += 1
                if not grid[current[0]][current[1]]:
                    if grid[current[0]][current[1]-1] != "anna":
                        grid[current[0]][current[1]-1] = "right"
                    else:
                        start_dir = "right"
                else:
                    current[1] -= 1
    grid = grid[::-1]
    return grid, start_dir

def stringGrid(grid: list):
    grid_string = ""
    for row in grid:
        for x in row:
            if x == None:
                grid_string += "⬜"
            elif x == "left":
                grid_string += "⬅"
            elif x == "right":
                grid_string += "➡"
            elif x == "up":
                grid_string += "⬆"
            elif x == "anna":
                grid_string += "🧍‍♀️"
            elif x == "end":
                grid_string += "⚔"
            elif x == True:
                grid_string += "🟨"
            elif x == False:
                grid_string += "❌"
        grid_string += "\n"
    return grid_string

@bot.slash_command(name = "save", description = "Go and save Elsa!")
async def save(interaction: discord.Interaction):
    pass

@save.subcommand(name = "elsa", description = "Save Elsa from Hans!")
async def elsa(interaction: discord.Interaction):
    grid, start_dir = createGrid()
    grid_string = stringGrid(grid)
    save_elsa = SaveElsa(grid, start_dir, interaction.user)
    msg = await interaction.send(f"Follow the arrows on the path to save Elsa from Hans!\nYou have to save Elsa <t:{int(str(time.time()).split('.')[0])+30}:R>\n"+grid_string, view = save_elsa)
    save_elsa.interaction_original = msg

class HelpView(discord.ui.View):
    def __init__(self, user: discord.User = None):
        super().__init__(timeout = None)
        self.user = user
        self.page = 1
        self.helps = [None, None, None, None]
        self.helps[0] = discord.Embed(title = "Overview", description = "Hey there!\n\nHere is an overview of the bot submitted by Vishnu#2973 for the SnowCodes bot jam 2022. Get ready to embark on a journey and rediscover your childhood, as we make the movie Frozen a reality! Let's begin!", colour = discord.Colour.blue())
        self.helps[0].set_footer(text = "Help page 1/4")
        self.helps[1] = discord.Embed(title = "Overview", description = "At the beginning of the movie Frozen, Anna asked Elsa to play with her through the iconic **Do you want to build a snowman?** song. Let's try to fulfill Anna's dream ourselves, even though she could not!", colour = discord.Colour.blue())
        self.helps[1].add_field(name = "Do you want to build a snowman?", value = "Although Anna didn't get to build a snowman with Elsa (apart from Olaf), what's stopping you? Use the command </snowman build:1052915529532330005> to build your own snowman! Preserve your snowman by clicking the **Favourite** button so that you can call it whenever you want with the command </snowman favourite:1052915529532330005>!\n\n**Note**: All details of the snowman can be edited individually or in a group without affecting the others", inline = False)
        self.helps[1].add_field(name = "Come on let's go and play!", value = "At the same time, Elsa also sadly refused to play with Anna, but you can still play with your friends! Use the commands </snowball load:1052915532417998898> and </snowball throw:1052915532417998898> to have a snowball fight with your friends in your server! Use the command </snowball leaderboard:1052915532417998898> to view your server leaderboard in the game! You can also view your own statistics with the command </snowball profile:1052915532417998898>!\n\nA few points to remember:\n- You can only load a maximum of 2 snowballs at a time\n- You have to wait for 30 seconds between loading snowballs\n- When you get hit by a snowball, you lose all your current snowballs and you have to wait for 30 seconds till you can load another one", inline = False)
        self.helps[1].set_footer(text = "Help page 2/4")
        self.helps[2] = discord.Embed(title = "Overview", description = "After Elsa's powers are revealed to everyone in Arendelle, Anna resolves to go on a mission to retrieve her sister. During the course of this journey, Anna, accompanied by Olaf, Kristoff, and Sven, faced many difficulties to reach her Elsa's castle.\n\nTo replicate the hardships of this journey, you will be tasked with answering a series of questions to defrost the path and reach the castle, and get Elsa back to Arendelle! Use the command </quest new:1052915525702930523> to begin your journey! View your quest statistics with the command </quest profile:1052915525702930523>!", colour = discord.Colour.blue())
        self.helps[2].set_footer(text = "Help page 3/4")
        self.helps[3] = discord.Embed(title = "Overview", description = "Once Anna reaches Elsa's palace, she attempts to convince Elsa to return to Arendelle. This was to no avail, as Elsa refused to return. In the argument that ensued, Elsa accidentally freezes Anna's heart, but then forces Anna, Kristoff, Olaf, and Sven to leave. As the movie carries on, we eventually land back in Arendelle, where Elsa and Hans are having an intense battle, and Hans lies to Elsa telling that she had killed Anna. This leaves Elsa devastated, and Hans raises his sword to kill her. However, Anna manages to run in and stop Hans's blade as she turns to ice. Elsa then starts crying and hugging Anna, and this act of true love manages to bring Anna back to life, and she manages to reel her powers in, and return Arendelle to normality.\n\nTo complete your frozen journey, you must now go on a path created to replicate Anna's journey to save Elsa. You must traverse the path within 30 seconds, otherwise you will be too late to save Elsa from Hans! Follow the arrows exactly to reach the two of them. Use the command </save elsa:1052915534150250636> to begin! The clock is ticking!", colour = discord.Colour.blue())
        self.helps[3].set_footer(text = "Help page 4/4")
        
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "◀")
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user and not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        self.page -= 1
        if self.page == 0:
            self.page = 4
        await interaction.response.edit_message(embed = self.helps[self.page-1])
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "▶")
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user and not interaction.user == self.user:
            await interaction.send("This is not for you!", ephemeral = True)
            return
        self.page += 1
        if self.page == 5:
            self.page = 1
        await interaction.response.edit_message(embed = self.helps[self.page-1])

@bot.slash_command(name = "invite", description = "Fetch the invite link for the bot")
async def invite(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label = "Invite me!", style = discord.ButtonStyle.url, url = "https://discord.com/api/oauth2/authorize?client_id=1052913789269450772&permissions=274878220352&scope=bot%20applications.commands"))
    await interaction.send(view = view)

@bot.slash_command(name = "help", description = "View the bot's help page")
async def help(interaction: discord.Interaction):
    help_embed = discord.Embed(title = "Overview", description = "Hey there!\n\nHere is an overview of the bot submitted by Vishnu#2973 for the SnowCodes bot jam 2022. Get ready to embark on a journey and rediscover your childhood, as we make the movie Frozen a reality!", colour = discord.Colour.blue())
    help_embed.set_footer(text = "Help page 1/4")
    await interaction.send(embed = help_embed, view = HelpView(interaction.user))  

bot.run(token)