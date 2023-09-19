import wolframalpha
import discord
from discord import app_commands, ButtonStyle
from discord.interactions import Interaction
from discord.ui import Button, View
import time
import ast
import re


class MyView(View):
  def __init__(self, buttons, callback_func=None, callback_func_arg=None, **kwargs):
    super().__init__(**kwargs)
    self.func=callback_func
    self.arg=callback_func_arg
    if buttons!=None:
      for button in buttons:
        self.add_item(button)
        
    async def on_timeout(self):
        if self.func!=None:
            if self.arg!=None:
                await self.func(*self.arg)
            else:
                await self.func()
        else:
            return
    


class MyButton(Button):
    def __init__(self, callback=None, callback_arg=None, **kwargs):
        super().__init__(**kwargs)
        self.cb=callback
        self.cb_arg=callback_arg
        
    async def callback(self, interaction):
        if self.cb_arg:
            await self.cb(interaction, self.cb_arg)
        else:
            await self.cb(interaction)
    
    def disable(self):
        self.disabled=True


class wolframResponse:
  def __init__(self, api_key):
    self.key=api_key
    self.client=wolframalpha.Client(self.key)
    self.raw_response=None
  
  def __iter__(self):
     return iter(self.pod)
  
  def ask(self, question):
    self.raw_response=self.client.query(question)

    for key, value in self.raw_response.items():
      value=str(value)
      converters = (int, float, ast.literal_eval, lambda v: None if v=='' else (v.lower() == "true" if v.lower() in ["true", "false"] else v))
      for convert in converters:
        try:
          value=convert(value)
          break
        except:
          continue
     
      key = re.sub('^\W+', '', key)
      key = re.sub('\W+', '_', key)
      setattr(self, key, value)


    if not self.success or self.numpods==0:
       pass
    else:
      self.pod=[Pod(p) for p in self.pod]

class Pod:
  def __init__(self, pod):
    self.pod=pod
    for key, value in self.pod.items():
      value=str(value)
      converters = (int, float, ast.literal_eval, lambda v: None if v=='' else (v.lower() == "true" if v.lower() in ["true", "false"] else v))
      for convert in converters:
        try:
          value=convert(value)
          break
        except:
          continue
      
      key = re.sub('^\W+', '', key)
      key = re.sub('\W+', '_', key)
      setattr(self, key, value)

    self.subpod=[self.subpod] if isinstance(self.subpod, dict) else self.subpod
    self.subpod=[Subpod(p) for p in self.subpod]


  def __iter__(self):
     return iter(self.subpod)



class Subpod:
  def __init__(self, subpod):
    self.subpod=subpod
    for key, value in self.subpod.items():
      value=str(value)
      converters = (int, float, ast.literal_eval, lambda v: None if v=='' else (v.lower() == "true" if v.lower() in ["true", "false"] else v))
      for convert in converters:
        try:
          value=convert(value)
          break
        except:
          continue
      
      key = re.sub('^\W+', '', key)
      key = re.sub('\W+', '_', key)
      setattr(self, key, value)

  def __str__(self):
     return (f'[{self.img["@alt"]}]({self.img["@src"]})')


key='YOUR API KEY'
wolfram_client=wolframResponse(key)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def result_embed(*, res, p=None):
    if res.timedout!=None:
       timedoutpod=res.timedout.split(',')
       timedoutpod=[f'`{x}`' for x in timedoutpod]
       warn=f'The following fields of information has timed out: {" ".join(timedoutpod)}'
    else:
       warn=''
       
    
    question=res.inputstring
    embed=discord.Embed(title='Open in WolframAlpha', description=f'**{question}**\n' if p==None else f'**{p.title}**\n'+warn, url="https://www.wolframalpha.com/input?i="+question.replace('+','%2B').replace(' ',"+"))
    
    if not res.success:
       embed.add_field(name='Error', value='WolframAlpha failed to respond')
       return embed
    elif res.numpods==0:
       embed.add_field(name='Error', value='Nothing to display')
       return embed

    
    if p!=None:
       res=p
       for i, pod in enumerate(res):
          if i==0:
             embed.set_image(url=pod.img['@src'])
          embed.add_field(name='', value=str(pod))

    else:
       for pod in res:
          embed.add_field(name=f'{pod.title}\n' if pod.title != None else '', value='\n\n'.join([f'[{subpod.img["@alt"]}]({subpod.img["@src"]})' for subpod in pod])[:1024])
    return embed


@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

@tree.command(name='status',description='General status of the bot.')
async def status(interaction):
    t=time.monotonic()
    await interaction.response.send_message('Online!')
    await interaction.edit_original_response(content='Online! Ping: **'+str(round(time.monotonic()-t,3))+'** seconds')


@tree.command(name='query', description='Get query of your question from wolframalpha')
async def wolfram(interaction, question:str):
    
    async def detailedPod(interaction, arg):
      pod, client=arg
      buttons=[MyButton(style=ButtonStyle.green, label=pod.title, callback=detailedPod, callback_arg=[pod, client]) for pod in client.pod]

      await interaction.response.edit_message(
          content='',
          embed=result_embed(res=client, p=pod),
          view=MyView(buttons=buttons)
      )
       
    






    await interaction.response.defer()
    wolfram_client.ask(question)
    try:
      button=[MyButton(style=ButtonStyle.green, label=pod.title, callback=detailedPod, callback_arg=[pod, wolfram_client]) for pod in wolfram_client.pod]
    except Exception as e:
      button=None
      print(e)

    embed=result_embed(res=wolfram_client)

    while True:
      try:
        await interaction.followup.send(
            content='',
            embed=embed,
            view=MyView(buttons=button)
        )
        break
      except:
        embed.remove_field(len(embed.fields)-1)






client.run("YOUR DISCORD BOT TOKEN")
