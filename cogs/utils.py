import discord
from discord.ext import commands
import asyncio
import requests
from googleapiclient.discovery import build
from twitter import Twitter,OAuth

from time import time
from math import fmod,floor

from tools.db import db_manager
from private import tokens

arq_tags = ["dz","dza","ar","arq","arabic","derja"]
eng_tags = ["en","eng","english"]
formatted_langs_list = " ".join(arq_tags+eng_tags)

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_VIDEO_BASIC_LINK = "https://www.youtube.com/watch?v="

ALGERIA_WOEID = 23424740


class utils:

    def __init__(self,bot):
        self.bot = bot
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=tokens.YOUTUBE_DATA_TOKEN)
        self.twitter = Twitter(auth=OAuth(tokens.TWITTER_ACCESS_KEY,tokens.TWITTER_ACCESS_SECRET,tokens.TWITTER_CONSUMER_KEY,tokens.TWITTER_CONSUMER_SECRET))

    @commands.command()
    async def translate(self,context,lang:str='',word:str=''):
        """Translation"""
        if(lang =='' or word==''):
            await context.send('```Use Correct Syntax please :``` \n **' + self.bot.command_prefix+'tr source_lang word**')
            return
        msg = context.message
        print("Translation request: Server: '{0}'  server_id: '{1}'  |||  User: '{2}' id: '{3}'  |||  Word :{4}".format(msg.guild.name,msg.guild.id,msg.author.display_name,msg.author.id,word))


        if(lang not in  arq_tags+eng_tags ):
            await context.send("```Wrong source language! ``` \n use: **"+formatted_langs_list+"**")
            return
        if(lang in eng_tags):
            source = "en"
            dest = "arq"
        else:
            source = "arq"
            dest = "en"

        #from source to french
        parameters = {"from":source,"dest":"fr","format":"json","phrase":word,"pretty":"true"}
        r  = requests.get('https://glosbe.com/gapi/translate', params=parameters)
        data = r.json()
        results = data['tuc']
        if( len(results)>0 and 'phrase' in results[0]):
            first_word = ((results[0])['phrase'])['text']
        #from French to dest
            parameters = {"from":"fr","dest":dest,"format":"json","phrase":first_word,"pretty":"true"}
            r  = requests.get('https://glosbe.com/gapi/translate', params=parameters)
            data = r.json()
            output = list()
            for translation in (data["tuc"])[0:4] :
                if( "phrase" in translation):
                    phrase = translation["phrase"];
                    output.append(phrase['text']);
            if(len(output) > 0):
                message = "```Translating '"+word+"' ``` \n"
                for tr in output:
                    message += "**"+tr+"** \n "
                message += "```more at : https://glosbe.com/fr/arq/"+first_word+"```"
            else:
                message = "``` No translation available \n you can do a manual search at \n https://glosbe.com/fr/arq/ ```"
            await context.send( message )
        else:
            message = "``` No translation available \n you can do a manual search at \n https://glosbe.com/fr/arq/ ```"
            await context.send(message)

    @commands.command()
    async def who(self,context,member:discord.Member=None):
        if not member:
            member = context.message.author
        if member.bot:
            if member == self.bot.user:
                await context.send("``` ana robot :robot: ```")
            else:
                await context.send("``` {} ? just a random useless bot... ```".format(member.display_name))
            return

        intro_channel_id = db_manager.get_introduction_channel(context.message.guild.id)
        if intro_channel_id and self.bot.get_channel(intro_channel_id):
            intro_channel = self.bot.get_channel(intro_channel_id)
            if intro_channel == context.message.channel:
                await context.send("only introduction are allowed in this channel, please use a diffrent one",delete_after=2)
                await context.message.delete()
                return
            intro = await intro_channel.history().find(lambda m:m.author==member)
            if intro:
                intro_embed = discord.Embed(title="Who is {} ?".format(member.display_name),description=member.top_role.name)
                intro_embed.add_field(name="Hash:",value=member,inline=False)
                intro_embed.add_field(name="Member since",value=" {0.day}/{0.month}/{0.year} ".format(member.joined_at),inline=False)
                intro_embed.set_thumbnail(url=member.avatar_url)
                intro_embed.add_field(name="Introduction:",value="``` {} ```".format(intro.content),inline=False)

                await context.send("",embed=intro_embed)
            else:
                await context.send("{} haven't introduced himself yet".format(member.display_name))
        else:
            await context.send("No introduction channel found on this server")


    @commands.command()
    async def trends(self,context, medium:str=''):
        results = self.youtube.videos().list( part='snippet,statistics',chart="mostPopular",maxResults=3,regionCode="DZ").execute()
        trends_embed = discord.Embed(title="Trending in Algeria")
        trends_embed.set_thumbnail(url=results["items"][0]["snippet"]["thumbnails"]["default"]["url"])
        i = 1
        for video in results["items"]:
            title = video["snippet"]["title"]
            link = "{}{}".format(YOUTUBE_VIDEO_BASIC_LINK,video["id"])
            channel = video["snippet"]["channelTitle"]
            views = self.format_numbers(video["statistics"]["viewCount"])
            likes = self.format_numbers(video["statistics"]["likeCount"])
            dislikes = self.format_numbers(video["statistics"]["dislikeCount"])
            trends_embed.add_field(name="#{}:".format(i),value="[{}]({}) \n :eye: : {} :thumbsup: : {} :thumbsdown: : {} \n ___".format(title,link,views,likes,dislikes),inline=False)
            i = i+1

        #twitter
        trends_embed.add_field(inline=False,name="Twitter Top Trends:",value="---------")
        twitter_trends = self.twitter.trends.place(_id = ALGERIA_WOEID )
        i = 1
        for trend in twitter_trends[0]["trends"][:3]:
            trends_embed.add_field(name="#{}".format(i),value='[{}]({})'.format(trend['name'],trend['url']))
            i = i+1
        await context.send("",embed= trends_embed)


    def format_numbers(self,number):
        number = int(number)
        if number >= 1000000:
            mil = number / 1000000
            return("{:.1f}M".format(mil) )
        if number>=1000 :
            k = number / 1000
            return("{:.1f}K".format(k))
        return(number)




def setup(bot):
  bot.add_cog(utils(bot))
