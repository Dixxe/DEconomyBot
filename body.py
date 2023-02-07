import disnake
from disnake.ext import tasks, commands
import json

with open('TOKEN_HERE.txt', 'r+') as token_file:
    token = token_file.read()

# service variables #
global slash_inter, button_inter

slash_inter = disnake.ApplicationCommandInteraction

global bufer, acs, bank

bank = {} # "юзер" : деньги
bufer = [0, False] ## 0 - привязан к серверу? | 1 - айди привязаного сервера |
acs = False ##accses


intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

########################################################
########### РАБОТА С ФАЙЛАМИ ###########################
########################################################


##--сохранение--##
def exportData(bufer, bank):
    data = {'bufer': bufer,
            'bank': bank}
            
    with open('value.json', 'w') as save:
        json.dump(data, save)
##--сохранение--##

##--загрузка--##
def importData():
    with open('value.json', 'r') as save:
        data = json.load(save)
        bufer = data['bufer']
        bank = data['bank']
    return bufer, bank
##--загрузка--##


########################################################
########### РАБОТА С ФАЙЛАМИ ###########################
########################################################


@bot.event ## works when it ready
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try: ## проверяю на наличие файлика и обьявляю переменные
        importData()
        global bufer, bank
        bufer, bank = importData()
        print(f'Loading succesful. {importData()}')
    except:
        print('No saves found')

@bot.event
async def on_guild_join(guild):
    bufer[0] = guild.id
    bufer[1] = True
    print(f'I have joined on server! {guild} Hope all working!')
    save.start(bufer)

##################################################

@bot.event
async def on_message(message):
        if (message.author == bot.user): ## проверка чтобы не было цикла
            return

        if ((bufer[0] == message.author.guild.id)):
            global acs
            acs = True  
        else:
            acs = False
            
        print(acs)
        await bot.process_commands(message)

#----------------------classes------------------------#


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    async def debug(self, ctx):
        if acs:
            await ctx.reply(f'{acs} {bufer[1]}, {bufer[0]}')


    @commands.command()
    async def hello(self, ctx, *, member: disnake.Member = None):
        member = member or ctx.author
        if acs:
            await ctx.send(f'Hello {member.name}~')

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def wallet(slash_inter):
        if slash_inter.author not in bank:
            await slash_inter.send("Oohh, I think you don't have wallet")
        else:
            await slash_inter.send(f"*you looking in your wallet and see {bank[f'{slash_inter.author}']} dcoins")
#----------------------classes------------------------#

#------------tasks------------------#

@tasks.loop(minutes=1.0) ## цикл сохранения переменных в файл линия 180
async def save(bufer):
    try:
        exportData(bufer)
    except Exception:
        pass

#------------tasks------------------#


bot.add_cog(AdminCommands(bot))
bot.add_cog(UserCommands(bot))
bot.run(token)