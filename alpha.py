import wolframalpha as alpha
import discord
from discord import Option
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True 
intents.presences = True
bot=discord.Bot(
    allowed_mentions=discord.AllowedMentions(
        users=False,         # Whether to ping individual user @mentions
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=False,         # Whether to ping role @mentions
        replied_user=False,  # Whether to ping on replies to messages
    ),
)
plot_type=['plots','implicit plot','polar plots','3d plot','diagram']


alphaClient = alpha.Client('YOUR API KEY')



@bot.event
async def on_ready():
  print('online')


@bot.slash_command(description='Returns result from WolframAlpha')
async def wolframalpha(ctx, input:Option(str,'Question for WolframAlpha')):
  rep=await ctx.respond('calculating...')
  plot_type=['plots','implicit plot','polar plots','surface plot','result','contour plot','3d plot']
  user = ctx.author
  pfp = user.avatar.url
  graph=True
  i=0
  embed=None
  field=0
  try:
    res = alphaClient.query(input)
  except:
    await rep.edit_original_message(content="Sorry, WolframAlpha did not respond.")
    return
  for pod in res.pods:
    for sub in pod.subpods:
      if (not str(sub.img.alt).lower() in plot_type):
          if i==0:
            embed=discord.Embed(title=input, url="https://www.wolframalpha.com/input?i="+input.replace('+','%2B').replace(' ',"+"), description=None, color=discord.Color.orange())
            embed.set_author(name=ctx.author.name, icon_url=pfp)
            embed.set_thumbnail(url=sub.img.src)
            i+=1
          else:
            if len(str(sub.plaintext))>=1024:
              val=str(sub.plaintext)[0:1020]+"..."
            else:
              val=str(sub.plaintext)
            if pod.title!='' and sub.plaintext!=None:
              embed.add_field(name=str(pod.title), value=val, inline=False)
              i+=1
              field+=1
            else:
              if sub.plaintext!=None:
                embed.add_field(name='_ _', value=val, inline=True)
                field+=1
      elif graph and str(sub.img.alt).lower() in plot_type:
          graph=False
          embed.set_image(url=str(sub.img.src))
          i+=1
  
  if graph:
    for pod in res.pods:
      for sub in pod.subpods:
        embed.set_image(url=sub.img.src)
        break
      break
  
  if field==0:
    for pod in res.pods:
      for sub in pod.subpods:
        if len(str(sub.plaintext))>=1024:
              val=str(sub.plaintext)[0:1020]+"..."
        else:
          val=str(sub.plaintext)
        embed.add_field(name=str(pod.title),value=val, inline=False)
        break
      break
  

  if embed==None:
    embed=discord.Embed(title="Failed to load your answer, view in wolframalpha", url="https://www.wolframalpha.com/input?i="+input.replace('+','%2B').replace(' ',"+"), color=discord.Color.orange())

  try:
    await rep.edit_original_message(content=None,embed=embed)
  except:
    await rep.edit_original_message(content=None,embed=discord.Embed(title="Failed to load your answer, view in wolframalpha", url="https://www.wolframalpha.com/input?i="+input.replace('+','%2B').replace(' ',"+"), color=discord.Color.orange()))

bot.run('YOUR DISCORD BOT TOKEN')
