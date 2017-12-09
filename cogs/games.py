import discord
from discord.ext import commands
import asyncio
import requests
import html
from time import time
from random import choices
import json
import operator

from .data.flags import COUNTRIES as countries
from tools.db import db_manager
import Config


class games:
    #trivia_categories_str = '    9: General, 10: Books, 11: Film \n     12: Music, 13: Musicals & Theatres, 14: Television \n    15: Video Games, 16: Board Games, 17: Science & &Nature \n    18: Sc & Computers, 19: Mathematics, 20: Mythology \n    21: Sports, 22: Geography, 23: History \n    24: Politics, 25: Art, 26: Celebrities \n    27: Animals, 28: Vehicles, 29: Comics \n    30: Gadgets, 31: Anime & Manga, 32: Cartoon & Animations'
    #trivia_dfc_tags = ["easy", "medium", "hard"]

    def __init__(self,bot):
        self.bot = bot
        self.trivia_sessions = {}
        self.flags_sessions = {}

        
        self.flag_rounds = Config.flag_game_rounds
        self.flags_round_time = Config.flag_game_round_duration


    #@commands.command()
    #async def trivia(self,context,action:str='' ,cat:str='',dfc:str=''):
    #    """ Play Trivia Game, type ??trivia for more help"""
    #
    #    msg = context.message
    #    session_id = self.get_session_id(msg)
    #    channel_session_status = self.is_channel_session_on(session_id)
    #
    #
    #    if (not action.lower() == 'start') and (not action.lower() == 'stop'):
    #        await self.show_trivia_help_msg(context)
    #        return
    #    else:
    #        if action.lower() == 'start' and channel_session_status:
    #            await context.send(' ```A game session is already running on in this channel```')
    #            return
    #        if action.lower() == 'stop':
    #            if self.is_trivia_session_on(session_id):
    #                self.trivia_sessions[session_id] =False
    #                await context.send('``` Trivia Session stoped ```')
    #                return
    #            else:
    #                await context.send('``` No trivia Session is running in this channel  ```')
    #                return
    #
    #    if(cat == '' or int(cat)>32 or int(cat)<9 ):
    #        await self.show_trivia_help_msg(context)
    #        return
    #    if(dfc is ''):
    #        parameters = {"amount":10,"category":cat,"type":'multiple'}
    #    elif dfc not in self.trivia_dfc_tags:
    #        await context.send('```wrong difficulty, leave empty for random \n difficulties : {} ```'.format(self.trivia_dfc_tags) )
    #        return
    #    else:
    #        parameters = {"amount":10,"category":cat,"type":'multiple',"difficulty":dfc}
    #
    #    Scores = {}
    #    TIMEOUT =  15
    #    self.trivia_sessions[session_id] =True
    #
    #    try:
    #        r  = requests.get('https://opentdb.com/api.php', params=parameters)
    #    except Exception as e:
    #        err_msg = '```API Error: \n {}```'.format(e)
    #        await context.send(err_msg)
    #        print(err_msg)
    #        return
    #    else:
    #        data = r.json()
    #        if(data['response_code'] != 0):
    #            await context.send('```Wrong request, response_code isn\'t 0```')
    #            return
    #        questions = data['results']
    #        i = 1
    #        for question in questions :
    #            if(not self.is_trivia_session_on(session_id)):
    #                break
    #
    #
    #            question_text = html.unescape(question['question'])
    #            incorrect_answers = question['incorrect_answers']
    #            answer = html.unescape(question["correct_answer"])
    #
    #            await context.send(':new: Question -{}-{} \n ``` {} \n {}s```'.format(i,question['difficulty'],question_text,TIMEOUT))
    #            i+=1
    #            time_started = time()
    #            now = time_started
    #            answered =False
    #            while (not answered) and (now- time_started < TIMEOUT) and self.is_trivia_session_on(session_id) :
    #                try:
    #                    guess = await self.bot.wait_for("message",timeout = TIMEOUT-(now- time_started), check=lambda m: (not m.author == self.bot.user) and (m.channel == msg.channel) )
    #                except asyncio.TimeoutError:
    #                     break;
    #                else:
    #                    print ('debug_answer')
    #                    if guess.content.lower() == answer.lower():
    #                        answered = True
    #                        if question['difficulty'] == 'hard':
    #                            points = 3
    #                        if question['difficulty'] == 'medium':
    #                            points = 2
    #                        if question['difficulty'] == 'easy':
    #                            points = 1
    #                        prev_score = Scores.get(guess.author.display_name)
    #                        if prev_score :
    #                            Scores[guess.author.display_name] = prev_score + points
    #                        else:
    #                            Scores[guess.author.display_name] = points
    #                        await context.send(':white_check_mark: ```You are right : **{}**, {} points!```'.format(guess.author.display_name,points))
    #                    now = time()
    #            if not answered:
    #                await context.send(':timer: ```Time is up, one point for me ! \n It is actually {}.```'.format(answer))
    #                prev_score = Scores.get('Mazghana-bot')
    #                if prev_score:
    #                    Scores['Mazghana-bot'] = prev_score + 1
    #                else:
    #                    Scores['Mazghana-bot'] = 1
    #            await asyncio.sleep(3)
    #        await context.send('```Trivia ended, \n Scores: \n {} ```'.format(Scores))
    #        self.trivia_sessions[session_id] =False

    @commands.command()
    async def flags(self,context,action:str=''):
        """ Play the Flags Quiz Game """

        msg = context.message
        session_id = self.get_session_id(msg)
        channel_status = self.is_channel_session_on(session_id)

        if db_manager.get_introduction_channel(msg.guild.id) == msg.channel.id:
            context.send("Not allowed in introduction channel!",delete_after=2)
            return

        if (not action.lower() == 'start') and (not action.lower() == 'stop'):
            await context.send("```use: ```\n ```{0}flags action ```\n ```action: start/stop ```".format(self.bot.command_prefix))
            return
        else:
            if action.lower() == 'start' and channel_status:
                await context.send(' ```a Game session is already running on in this channel```')
                return
            if action.lower() == 'stop':
                if self.is_flags_session_on(session_id):
                    self.flags_sessions[session_id] = False
                    await context.send('``` Flags Session stoped ```')
                    return
                else:
                    await context.send('``` No Flags Session is running in the channel  ```')
                    return
        #starting

        #getting flags data & selecting a few for this session
        data = json.loads(countries)
        questions = choices(data,k=self.flag_rounds)




        #displaying starting msg
        start_msg  = discord.Embed(color=discord.Color.orange(),title="Flags Game")
        start_msg.set_thumbnail(url=self.bot.user.avatar_url)
        start_msg.add_field(name="How it works:",value="I post a flag, you try to guess the country it belongs to \n simple right ? \n whoever has more points after {} rounds wins".format(self.flag_rounds))
        start_msg.add_field(inline=False, name="prepare yoursleves",value="Game starting in 5s")
        await context.send("",embed=start_msg)


        #setting session status scores ...
        self.flags_sessions[session_id] =  True
        Scores = {}
        i = 1
        await asyncio.sleep(5)

        for question in questions:
            if(not self.is_flags_session_on(session_id)):
                break

            answered = False
            answer = question['name']['common']
            code = question['cca2'].lower()
            flag_url = html.escape('https://github.com/hjnilsson/country-flags/blob/master/png250px/{}.png?raw=true'.format(code))

            question_embed = discord.Embed(color=discord.Color.orange(),title="Flags Game",description="Round {}".format(i))
            question_embed.add_field(inline=False, name=":map:",value="Can you guess this country?")
            question_embed.set_image(url=flag_url)
            question_embed.set_footer(text="{}s".format(self.flags_round_time))
            await context.send("",embed=question_embed)


            try:
                guess = await self.bot.wait_for("message",timeout = self.flags_round_time, check=lambda m: (not m.author == self.bot.user) and (m.channel == msg.channel) and (m.content.lower() == answer.lower()) )
            except asyncio.TimeoutError:
                pass
            else:
                answered = True
                prev_score = Scores.get(guess.author)
                if guess.author in Scores:
                    Scores[guess.author] = Scores[guess.author] + 1
                else:
                    Scores[guess.author] = 1


                answer_embed = discord.Embed(color=discord.Color.green(),title="Flags Game",description="Round {}".format(i))
                answer_embed.set_thumbnail(url=flag_url)
                answer_embed.add_field(inline=False, name=" :white_check_mark: Correct!",value="{0} you are correct".format(guess.author.mention))
                answer_embed.add_field(inline=False, name="Answer:",value=answer)
                answer_embed.add_field(inline=False, name="Score",value="{} : {} ".format(guess.author.display_name,Scores[guess.author]))
                await context.send("",embed=answer_embed)

            if(not answered) and self.is_flags_session_on(session_id):
                no_answer_embed = discord.Embed(color=discord.Color.red(),title="Flags Game",description="Round {}".format(i))
                no_answer_embed.set_thumbnail(url=flag_url)
                no_answer_embed.add_field(inline=False, name=":timer: Time is up",value="No correct answer, i take this round!")
                no_answer_embed.add_field(inline=False, name="Answer:",value=answer)
                await context.send("",embed=no_answer_embed)

                #award this bot a point
                if self.bot.user in Scores:
                    Scores[self.bot.user] = Scores[self.bot.user] + 1
                else:
                    Scores[self.bot.user] = 1
            await asyncio.sleep(5)
            i+=1

        Scores_l = sorted(Scores.items(), key=operator.itemgetter(1),reverse=True)
        Winner = (Scores_l[0])[0]
        scores_s =""
        for k in Scores_l:
            scores_s  = scores_s + "**{}** : {} \n".format(k[0].display_name,k[1])

        end_game_embed = discord.Embed(color=discord.Color.purple(),title="Flags Game",description="Game Ended")
        end_game_embed.set_thumbnail(url=Winner.avatar_url)
        end_game_embed.add_field(inline=False, name="Winner is: ",value=" :tada: {} :tada: \n Congrats!".format(Winner.mention))
        end_game_embed.add_field(inline=False, name="Finale Scores:",value=scores_s)
        await context.send("",embed=end_game_embed)


        self.flags_sessions[session_id] = False



    #async def show_trivia_help_msg(self,ctx):
    #    await ctx.send('```Usage : \n \n {0}trivia action category difficulty \n \n action : stop/start   \n \n categories : \n \n {1}  \n \n difficulties : {2}  \n \n examples: \n \n {0}trivia start 9 \n \n {0}trivia start 9 easy \n \n {0}trivia stop ``` '.format(self.bot.command_prefix,self.trivia_categories_str,self.trivia_dfc_tags))

    def get_session_id(self,msg):
        return (msg.guild.id+msg.channel.id)

    def is_channel_session_on(self,id):
        return (self.trivia_sessions.get(id) or self.flags_sessions.get(id))

    def is_trivia_session_on(self,id):
        return (self.trivia_sessions.get(id))

    def is_flags_session_on(self,id):
        return (self.flags_sessions.get(id))


def setup(bot):
    bot.add_cog(games(bot))
