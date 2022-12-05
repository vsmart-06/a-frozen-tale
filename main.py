import nextcord as discord
from nextcord.ext import commands
import asyncio
import dotenv
import os

dotenv.load_dotenv()

bot = commands.Bot()
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print("Do you want to build a snowman?")

class BuildCircles(discord.ui.Modal):
    def __init__(self):
        super().__init__("Build a snowman!", timeout = None)
        self.bottom_radius_value = None
        self.middle_radius_value = None
        self.top_radius_value = None

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
        
        if not (self.bottom_radius_value >= self.middle_radius_value >= self.top_radius_value):
            await interaction.send("The radii of your snowballs have to be lesser than or equal to the radius of the snowball beneath them!", ephemeral = True)
        
        else:
            snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
            snowman_embed.add_field(name = "Bottom snowball radius", value = self.bottom_radius_value)
            snowman_embed.add_field(name = "Middle snowball radius", value = self.middle_radius_value)
            snowman_embed.add_field(name = "Top snowball radius", value = self.top_radius_value)
            return await interaction.send(embed = snowman_embed, ephemeral = True)

    def getValues(self):
        if self.bottom_radius_value:
            return self.bottom_radius_value, self.middle_radius_value, self.top_radius_value

class BuildDetails(discord.ui.Modal):
    def __init__(self):
        super().__init__("Build a snowman!", timeout = None)
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

        self.hat_colour = discord.ui.TextInput(
            label = "Colour of the hat",
            style = discord.TextInputStyle.short,
            placeholder = "Enter the hex code for the colour of the hat (Ex: 000000 for black)",
            required = False
        )
        self.add_item(self.hat_colour)
    
    async def callback(self, interaction: discord.Interaction):
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
        
        if self.hat_colour.value:
            try:
                self.hat_colour_value = self.hat_colour.value
                if len(self.hat_colour_value) != 6:
                    await interaction.send("You have to enter a 6 symbol hex code for the colour!", ephemeral = True)
                    return
                for x in self.hat_colour_value:
                    if not(x.isnumeric() or x in "abcdef"):
                        await interaction.send("Invalid hex code", ephemeral = True)
                        return
            except:
                await interaction.send("You have to enter a 6 symbol hex code for the colour!", ephemeral = True)
                return
        else:
            self.hat_colour_value = "000000"
        
        rgb_old = [self.hat_colour_value[:2], self.hat_colour_value[2:4], self.hat_colour_value[4:]]
        rgb = []
        for x in rgb_old:
            rgb.append(int(x, 16))
        
        rgb = tuple(rgb)
        
        snowman_embed = discord.Embed(title = "Your snowman!", colour = discord.Colour.blue())
        snowman_embed.add_field(name = "Arm length", value = self.arm_length_value)
        snowman_embed.add_field(name = "Number of buttons", value = self.num_buttons_value)
        snowman_embed.add_field(name = "Hat colour", value = str(rgb))
        return await interaction.send(embed = snowman_embed, ephemeral = True)
    
    def getValues(self):
        return self.arm_length_value, self.num_buttons_value, self.hat_colour_value

class DropdownCustomize(discord.ui.Select):
    def __init__(self, original_interaction: discord.Interaction):
        self.original_interaction = original_interaction
        options = [
            discord.SelectOption(label = "Snowballs", description = "Customize the radii of the snowballs!", emoji = "❄"),
            discord.SelectOption(label = "Details", description = "Customize the other aesthetics of your snowman!", emoji = "🎨")
        ]
        super().__init__(placeholder = "Select a customization option", min_values = 1, max_values = 1, options = options)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Snowballs":
            await interaction.response.send_modal(BuildCircles())
            await self.original_interaction.response.edit_message(view = DropdownCustomize(self.original_interaction))
        elif self.values[0] == "Details":
            await interaction.response.send_modal(BuildDetails())
            await self.original_interaction.response.edit_message(view = DropdownCustomize(self.original_interaction))

class ButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label = "❄ Snowballs", style = discord.ButtonStyle.blurple)
    async def snowballs(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        return await interaction.response.send_modal(BuildCircles())
    
    @discord.ui.button(label = "🎨 Details", style = discord.ButtonStyle.blurple)
    async def details(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        return await interaction.response.send_modal(BuildDetails())
    

@bot.slash_command(name = "build", description = "Build a snowman")
async def build(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(DropdownCustomize(interaction))
    await interaction.send(view = view, ephemeral = True)

bot.run(token)