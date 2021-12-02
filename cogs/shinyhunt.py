#Cog with commands to manage user's shiny hunt

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord import Color

import math

class shinyhunt(commands.Cog):

	server_ids = [760880935557398608]

	def __init__(self, client):
		self.client = client

	#User's shiny hunt details
	@cog_ext.cog_slash( name="my_shiny",
						guild_ids=server_ids,
						description="Set your shiny so Ki can mention you if it happens to spawn"
					  )
	async def my_shiny(self, ctx):

		#Check if user has data in database
		if(ctx.author.name not in self.client.data_base.db.child("users").get().val()):
			await ctx.send(f"<@{ctx.author.id}> you haven't registered with Ki yet! Register with /add_me")
			return

		#Get user data from database
		shiny_hunt = self.client.data_base.db.child("users").child(ctx.author.name).child("shiny").get().val()["pokemon"]
		streak = self.client.data_base.db.child("users").child(ctx.author.name).child("shiny").get().val()["streak"]
		percentage = ((1 + math.log(1 + streak/30)) / 4096)*100

		#Embed decorations
		shiny_embed = discord.Embed()
		shiny_embed.title = "Shiny Hunt"
		shiny_embed.color = 0x00FFFF

		shiny_embed.add_field(name="Streak", value=streak, inline=True)
		shiny_embed.add_field(name="Percent Chance", value=str(percentage)+"%", inline=True)

		if(shiny_hunt == "None"):
			shiny_embed.description = "Ki isn't checking for the pokemon you are hunting!"
			button_text = "Set It"
		else:
			shiny_embed.description = f"Ki will mention you if a **{shiny_hunt}** spawns"
			URL = self.client.data_base.storage.child(f"Images/{shiny_hunt}/pokemon.png").get_url(token=None)
			shiny_embed.set_thumbnail(url=URL)
			button_text = "Change It Or Update My Streak"

		await ctx.send(embed=shiny_embed, components=[
                                    		create_actionrow(
                                        		create_button(style=ButtonStyle.green, label=button_text, custom_id="get_shiny")
                                        	)
                                    	  ])

	#Get the shiny hunt data from the user
	@cog_ext.cog_component()
	async def get_shiny(self, ctx):

		#Checks if message is from user
		def check(m):
			return m.author.id == ctx.author.id

		#Checks if message is from PokeTwo
		def checkP2(m):
			return m.author.id == self.client.poketwo_id

		while True:
			await ctx.send(f"<@{ctx.author.id}> do ?sh")
			message = await self.client.wait_for('message', check=check)

			if("?sh" in message.content):
				break

		#Get shiny hunt data from embed sent by PokeTwo
		shiny_message = await self.client.wait_for('message', check=checkP2)
		fields = shiny_message.embeds[0].to_dict()["fields"]
		shiny_hunt_data = {}

		for field in fields:
			if(field["name"] == "Currently Hunting"):
				shiny_hunt_data["pokemon"] = field["value"]
			elif(field["name"] == "Chain"):
				shiny_hunt_data["streak"] = int(field["value"])

		#Store data in database
		self.client.data_base.db.child("users").child(ctx.author.name).child("shiny").update(shiny_hunt_data)
		await ctx.send(f"<@{ctx.author.id}> your shiny hunt data is set.")

	#Returns users and their shiny hunt pokemon
	async def get_shinies(self, ctx):

		shinies = []
		users = self.client.data_base.db.child("users").get().val()

		for user, data in users.items():
			user_shiny_data = {}
			if(user == "Morty"):
				continue

			user_shiny_data["name"] = user
			user_shiny_data["pokemon"] = data["shiny"]["pokemon"]
			shinies.append(user_shiny_data)

		return(shinies)

	#Updates shiny hunt streak by one
	async def update_streak(self, name):
		streak = self.client.data_base.db.child("users").child(name).child("shiny").get().val()["streak"]
		self.client.data_base.db.child("users").child(name).child("shiny").update({"streak": int(streak)+1})

def setup(client):
	client.add_cog(shinyhunt(client))