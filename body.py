import disnake
from disnake.ext import tasks, commands
import json
from random import randint
import asyncio
from math import floor

from utils import chance

with open('TOKEN_HERE.txt', 'r+') as token_file:
    token = token_file.read()

# service variables #
global slash_inter, button_inter

slash_inter = disnake.ApplicationCommandInteraction

global bufer, acs


bufer = [0, False] ## 0 - привязан к серверу? | 1 - айди привязаного сервера |
acs = False ## текущий способ остановки работы бота на другом сервере. Постоянно ифает сообщение находится ли пользователь там где надо? ТРЕБУЕТСЯ ЗАМЕНА!


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
        eco = bot.get_cog('Economy')
        bufer = data['bufer']
        eco.import_bank(data['bank'])
    return bufer
##--загрузка--##


########################################################
########### РАБОТА С ФАЙЛАМИ ###########################
########################################################


@bot.event ## works when it ready
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try: ## проверяю на наличие файлика и обьявляю переменные
        importData()
        global bufer
        bufer = importData()
        print('Loading succesful.')
    except:
        print('No saves found')
    eco = bot.get_cog('Economy')
    save.start(bufer, bank=eco.get_bank())

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

#------------------economy class-----------------#
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    __bank = {} # "юзер" : деньги
    
    ## операции для ввода-вывода банка ##
    def import_bank(self, bank):
        self.__bank = bank

    def get_bank(self):
        return self.__bank
    ## операции для ввода-вывода банка ##
    
    
    async def withdraw_money(self, member, money): # вывод денег
        if (member not in self.__bank):
            return '404' # не найдено

        if (self.__bank[f'{member}'] < money):
            return '204' # не разрешено, денег нема
        else:
            self.__bank[f'{member}'] -= money

    async def give_money(self, member, money): # начисление денег
        if (member not in self.__bank):
            self.__bank[f'{member}'] = money
        else:
            self.__bank[f'{member}'] += money

bot.add_cog(Economy(bot))
#------------------economy class-----------------#

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    async def debug(self, ctx):
        if acs:
            await ctx.reply(f'{acs} {bufer[1]}, {bufer[0]}')



class UserCommands(commands.Cog):
    eco = bot.get_cog('Economy') # получаю класс экономики
    # bank = self.eco.get_bank() - получение банка из функции внутри класса выглядит так
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description='Посмотреть в свой кошелек')
    async def wallet(self, slash_inter):
        if acs and self.eco is not None:
            bank = self.eco.get_bank()
            if slash_inter.author.mention not in bank:
                await slash_inter.send("*/Oohh, I think I don't have wallet/*", ephemeral = True)
            else:
                await slash_inter.send(f"*/you looking in your wallet and see {bank[f'{slash_inter.author.mention}']} dcoins/*", ephemeral = True)

    @commands.slash_command(description='Попытай удачу ограбить банк.')
    async def rob_bank(self, slash_inter):
        if (acs):
            bank = self.eco.get_bank()
            rand = randint(500, 1000)
            await slash_inter.send(f"{slash_inter.author.mention} started a bank robbery!!!")
            await asyncio.sleep(5)
            if (chance(20)):
                try:
                    moni = floor(bank[f'{slash_inter.author.mention}'] * 0.2 + rand) # округляю(20% от денег игрока + рандомное колво денег в банке)
                    await self.eco.give_money(slash_inter.author.mention, moni) # перевожу денег игроку на счет
                except Exception: # если у игрона не будет кошеля, то выйдет ошибка которая здесь поймается и игроку насчет начислет только колво денег в банке
                    moni = rand
                    await self.eco.give_money(slash_inter.author.mention, moni)
                await slash_inter.edit_original_response(f"Yoo {slash_inter.author} succesfully rob a bank for {moni} dcoins!!!")
            
            else:
                try:
                    moni = floor(bank[f'{slash_inter.author.mention}'] * 0.7) # отбираем 70 процентов денег игрока
                    res = await self.eco.withdraw_money(slash_inter.author.mention, moni)

                    if (res == '204'): # если каким то чудом денег вдруг не хватило то тебя отпускают
                        await slash_inter.edit_original_response(f"Ouch, {slash_inter.author} has been caught by cops, but you don't have enough money to pay fine, so they just let you free XD")
                    else:  
                        await slash_inter.edit_original_response(f'Ouch, {slash_inter.author} has been caught by cops, and payed fine for {moni} dcoins')
                except Exception: # если нет кошелька то ты просто убегаешь (ИРОНИЯ АХХАХА)
                    await slash_inter.edit_original_response(f'Ouch, {slash_inter.author} has been caught by cops, but managed to run away')

    @commands.slash_command(description='Попытай удачу ограбить кого-то.')
    async def rob(self, slash_inter, member: disnake.Member):
        if (acs):
            await slash_inter.send(f"{slash_inter.author.mention} get this personal and wants to rob {member}.")
            await asyncio.sleep(3)
            bank = self.eco.get_bank() # обьявляю банк
            if (chance(30)): # шансы 
                try: # проверка на ошибку
                    pred_bank = bank[f'{member.mention}'] # кошелек жертвы
                    moni = floor(pred_bank * 0.1) # 10% от денег жертвы 
                    await self.eco.withdraw_money(member.mention, moni) # перевожу на счет грабителю
                    await self.eco.give_money(slash_inter.author.mention, moni) # снимаю со счета жертвы
                    await slash_inter.edit_original_response(f"You succesfully rob {member} and take {moni} dcoins with you.") #
                except Exception:
                    await slash_inter.edit_original_response(f"You found {member} wallet empty, lol")
            else:
                try:
                    thief_bank = bank[f'{slash_inter.author.mention}']
                    moni = floor(thief_bank * 0.5)
                    await self.eco.withdraw_money(slash_inter.author.mention, moni)
                    await self.eco.give_money(member.mention, moni)
                    await slash_inter.edit_original_response(f"{member} caught you and take {moni} dcoins from you")
                except Exception:
                    await slash_inter.edit_original_response(f"{slash_inter.author.mention} was caughted by {member} and bonked.")
                
    @commands.slash_command(description='Передать деньги кому-то.')
    async def give_money(self, slash_inter, memb: disnake.Member, money:int):
        await slash_inter.send(f'Money transmission in process...')
        await asyncio.sleep(1)
        if (acs):
            if (slash_inter.author.mention == memb.mention):
                await slash_inter.edit_original_response(f"You really think that im so dumb?")
            else:
                bank = self.eco.get_bank()
                try:
                    comission = floor(money * 0.9) # комиссия 10% сволочи
                    res = await self.eco.withdraw_money(slash_inter.author.mention, money)
                    if (res == '204'):
                        await slash_inter.edit_original_response(f"Operation terminated. You don't have enough money")
                    else:
                        await self.eco.give_money(memb.mention, comission)
                        await slash_inter.edit_original_response(f'Operation succes.')
                except Exception:
                    await slash_inter.edit_original_response(f"Something went wrong. Please check arguments.")
    
    @commands.slash_command(description='Получить аватар пользователя') ## аватарка чек
    async def avatar(slash_inter, member : disnake.Member=None):
        try:
            userAvatar = member.avatar
            await slash_inter.send(userAvatar, ephemeral=True)
        except Exception:
            await slash_inter.send('Something went wrong :(', ephemeral=True)

#----------------------classes------------------------#

#------------tasks------------------#

@tasks.loop(minutes=1.0) ## цикл сохранения переменных в файл
async def save(bufer, bank):
    try:
        exportData(bufer, bank)
    except Exception:
        pass

@tasks.loop(hours=24) # луп для получения зарплаты, и оплаты ролей и тд
async def payday():
    pass

#------------tasks------------------#


bot.add_cog(AdminCommands(bot))
bot.add_cog(UserCommands(bot))
bot.run(token)