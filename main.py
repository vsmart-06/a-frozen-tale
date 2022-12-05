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

class BuildSnowman(discord.ui.Modal):
    def __init__(self, rgb: tuple):
        super().__init__("Build a snowman!", timeout = None)
        self.rgb = rgb

        self.bottom_radius = discord.ui.TextInput(
            label = "Radius of the bottom snowball",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the radius of the bottom snowball",
            required = True
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
            required = True
        )
        self.add_item(self.arm_length)

        self.num_buttons = discord.ui.TextInput(
            label = "Number of buttons",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the number of buttons",
            required = True
        )
        self.add_item(self.num_buttons)

    async def callback(self, interaction: discord.Interaction):
        try:
            self.bottom_radius_value = abs(int(float(self.bottom_radius.value)))
        except:
            await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
            return
        try:
            self.middle_radius_value = abs(int(float(self.middle_radius.value)))
        except:
            if not self.middle_radius.value:
                self.middle_radius_value = int(0.75*self.bottom_radius_value)
            else:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        try:
            self.top_radius_value = abs(int(float(self.top_radius.value)))
        except:
            if not self.top_radius.value:
                self.top_radius_value = int(0.75*self.middle_radius_value)
            else:
                await interaction.send("The values of the radii have to be numbers!", ephemeral = True)
                return
        
        try:
            self.arm_length_value = abs(int(float(self.arm_length.value)))
        except:
            await interaction.send("The value of the arm length has to be a number", ephemeral = True)
            return
        
        try:
            self.num_buttons_value = abs(int(self.num_buttons.value))
        except:
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
            createImage(self.bottom_radius_value, self.middle_radius_value, self.top_radius_value, self.arm_length_value, self.num_buttons_value, self.rgb[::-1])
            return await interaction.send(embed = snowman_embed, ephemeral = True)

def createImage(rb, rm, rt, al, nb, hc):
    img = np.zeros((512, 512, 3), np.uint8)
    img[:,:] = (255, 100, 55)
    cv2.circle(img, (256, 255-rb), rb, (255, 255, 255), -1)
    cv2.circle(img, (256, 255-(2*rb+rm)), rm, (255, 255, 255), -1)
    cv2.circle(img, (256, 255-(2*rb+2*rm+rt)), rt, (255, 255, 255), -1)
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

@bot.slash_command(name = "build", description = "Build a snowman")
async def build(interaction: discord.Interaction, colour: str = discord.SlashOption(name = "colour", description = "Enter the colour of the hat", required = False)):

    if colour:
        try:
            if len(colour) != 6:
                await interaction.send("You have to enter a 6 symbol hex code for the colour!", ephemeral = True)
                return
            for x in colour:
                if not(x.isnumeric() or x in "abcdef"):
                    await interaction.send("Invalid hex code", ephemeral = True)
                    return
        except:
            await interaction.send("You have to enter a 6 symbol hex code for the colour!", ephemeral = True)
            return
    else:
        colour = "000000"

    rgb_old = [colour[:2], colour[2:4], colour[4:]]
    rgb = []
    for x in rgb_old:
        rgb.append(int(x, 16))
    
    rgb = tuple(rgb)

    await interaction.response.send_modal(BuildSnowman(rgb))

bot.run(token)