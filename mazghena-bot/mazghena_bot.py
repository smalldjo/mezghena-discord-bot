import discord
from discord.ext import commands
import logging
import requests
import html
from time import time,sleep
from random import choices
import json
from private import tokens
import data

arq_tags = ["dz","dza","ar","arq","arabic","derja"]
eng_tags = ["en","eng","english"]
formatted_langs_list = " ".join(arq_tags+eng_tags)
countries = data.COUNTRIES
trivia_categories_str = '9: General, 10: Books, 11: Film \n 12: Music, 13: Musicals & Theatres, 14: Television \n 15: Video Games, 16: Board Games, 17: Science & &Nature \n 18: Sc & Computers, 19: Mathematics, 20: Mythology \n 21: Sports, 22: Geography, 23: History \n 24: Politics, 25: Art, 26: Celebrities \n 27: Animals, 28: Vehicles, 29: Comics \n 30: Gadgets, 31: Anime & Manga, 32: Cartoon & Animations'
trivia_dfc_tags = ["easy", "medium", "hard"]


logging.basicConfig(level=logging.INFO)
prefix = '??'
description = 'Mazghana-Bot:'
bot = commands.Bot(command_prefix=prefix, description=description)

sessions_status = {}


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game= discord.Game(name=bot.command_prefix+'help'))


@bot.command(pass_context=True)
async def tr(context,lang:str='',word:str=''):
    """Translation"""
    if(lang =='' or word==''):
        await bot.say('```Use Correct Syntax please :``` \n **' + bot.command_prefix+'tr source_lang word**')
        return
    print("Translation request: Server: '"+ context.message.server.name+"'  server_id: '"+ context.message.server.id +"'  |||  User: '" + context.message.author.display_name + "' id: '"+ context.message.author.id + "'  |||  Word : "+word)
   
    
    if(lang not in  arq_tags+eng_tags ):
        await bot.say("```Wrong source language! ``` \n use: **"+formatted_langs_list+"**")
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
        await bot.say( message )
    else:
        message = "``` No translation available \n you can do a manual search at \n https://glosbe.com/fr/arq/ ```"
        await bot.say(message)
   
@bot.command(pass_context=True)
async def trivia(context,cat:str='',dfc:str=''):
    """ Play Trivia Game, type ??trivia for more help"""
    global sessions_status
    msg = context.message
    session_id = get_session_id(msg)
    status = sessions_status.get(session_id)
    if(status and status is True):
        await bot.say(' ```Trivia session is already on in this channel```')
        return

    if(cat == '' or int(cat)>32 or int(cat)<9 ):
        await bot.say('```Usage : \n {0}trivia category difficulty : start trivia \n {0}triviastop : stop trivia ```  \n  ```categories : \n {1} ``` \n ```difficulties : {2} ``` \n example : {0}trivia 9 easy  '.format(prefix,trivia_categories_str,trivia_dfc_tags))
        return
    if(dfc is ''):
        parameters = {"amount":10,"category":cat,"type":'multiple'}
    elif dfc not in trivia_dfc_tags:
        await bot.say('```wrong difficulty, leave empty for random \n difficulties : {} ```'.format(trivia_dfc_tags) )
        return
    else:
        parameters = {"amount":10,"category":cat,"type":'multiple',"difficulty":dfc} 
    
    Scores = {}
    TIMEOUT =  15
    sessions_status[session_id] = True

   
    try:
        r  = requests.get('https://opentdb.com/api.php', params=parameters)   
    except Exception as e:
        msg = '```API Error: \n {}```'.format(e)
        await bot.say(msg)
        print(msg)
        return
    else:
        data = r.json()
        if(data['response_code'] != 0):
            await bot.say('```Wrong request, response_code isn\'t 0```')
            return
        questions = data['results']
        i = 1
        for question in questions :
            if(not sessions_status[session_id]):
                break
            question_text = html.unescape(question['question'])
            incorrect_answers = question['incorrect_answers'] 
            answer = html.unescape(question["correct_answer"])

            await bot.say(':new: Question -{}-{} \n ``` {} \n {}s```'.format(i,question['difficulty'],question_text,TIMEOUT))
            i+=1
            time_started = time()
            now = time_started
            answered =False
            while (not answered) and (now- time_started < TIMEOUT) and sessions_status[session_id] :
                guess = await bot.wait_for_message(timeout = TIMEOUT-(now- time_started), check=message_isntfrom_bot)
                if guess is None:
                    break
                if guess.content.lower() == answer.lower():
                    answered = True
                    if question['difficulty'] == 'hard':
                        points = 3
                    if question['difficulty'] == 'medium':
                        points = 2
                    if question['difficulty'] == 'easy':
                        points = 1
                    prev_score = Scores.get(guess.author.name)
                    if prev_score :
                        Scores[guess.author.name] = prev_score + points
                    else:
                        Scores[guess.author.name] = points
                    await bot.say(':white_check_mark: ```You are right : **{}**, {} points!```'.format(guess.author.name,points))
                now = time()
            if not answered:
                await bot.say(':timer: ```Time is up, one point for me ! \n It is actually {}.```'.format(answer))
                prev_score = Scores.get('Mazghana-bot')
                if prev_score:
                    Scores['Mazghana-bot'] = prev_score + 1
                else:
                    Scores['Mazghana-bot'] = 1
            sleep(3)
        await bot.say('```Trivia ended, \n Scores: \n {} ```'.format(Scores))
        sessions_status[session_id] = False

@bot.command(pass_context=True)
async def triviastop(context):
    """  stops Trivia session in this channel """
    global sessions_status
    msg = context.message
    session_id = get_session_id(msg)
    status = sessions_status.get(session_id)
    if(not status or status is False):
        await bot.say('There is no Trivia Session here to stop...')
        return
    sessions_status[session_id] = False
    await bot.say('Stoping Trivia Session...')    


@bot.command(pass_context=True)
async def flags(context):
    """ Play the Flags Game """ 
    global sessions_status
    msg = context.message
    session_id = get_session_id(msg)
    status = sessions_status.get(session_id)
    Scores = {}
    if(status and status is True):
        await bot.say(' ```a Game session is already on in this channel```')
        return
    #try:
    #    data_file = open('countries.json','r')
    #except:
    #    print('countries.json couldn\'t be read')
    #    await bot.say('error, couldn\'t start game')
    #    return
   # else:
    data = json.loads(countries)
    questions = choices(data,k=10)
    sessions_status[session_id] =  True
    i = 1
    TIMEOUT = 15
    for question in questions:
        if(not sessions_status[session_id]):
            break
        answer = question['name']['common']
        code = question['cca2'].lower()
        flag_url = html.escape('https://github.com/hjnilsson/country-flags/blob/master/png250px/{}.png?raw=true'.format(code))
        parametres = {"url":flag_url,"access_token": tokens.BITLY_API_KEY}
        try:
            bitly_lookup_reponse = requests.get('https://api-ssl.bitly.com/v3/user/link_lookup',params = parametres)
        except Exception as e:
            print('bitly error: {}'.format(e))
            return
        else:
            json_reponse = bitly_lookup_reponse.json()
            if(json_reponse['status_txt'] != "OK" or json_reponse['data']['link_lookup'][0].get('error')): #not found ? shorten it
                print('link no found , shortening...')
                parametres = {"longUrl":flag_url,"access_token": tokens.BITLY_API_KEY}
                try:
                    bitly_shorten_reponse = requests.get('https://api-ssl.bitly.com/v3/shorten',params = parametres)
                except Exception as e:
                    print('can\'t shorten , bitly error: {}'.format(e))
                    return
                else:
                    json_reponse = bitly_shorten_reponse.json()
                    if(json_reponse['status_txt'] != "OK"):
                        print('can\t shorten url : response_status : {}'.format(json_reponse['status_txt']))
                        return
                    flag_short_url = json_reponse['data']['url']
                    print('link shortened')
            else: #found it ? get the previouslty shortened link
                flag_short_url = json_reponse['data']['link_lookup'][0]['aggregate_link']
                print('linked lookedup and found , no need to shorted')

        #flag_local_path = 'flags/{}.png'.format(code)
        #try:
        #    flag_file = open('flags/{}.png'.format(code),'rb')
        #except:
        #    urllib.request.urlretrieve(flag_url,flag_local_path)
        #    flag_file = open('flags/{}.png'.format(code),'rb')
            
        await bot.say(':new:  -{0}- what country has this flag? \n {1} '.format(i,flag_short_url))
        i+=1
        #await bot.send_file(msg.channel,flag_file)
        #flag_file.close()
        answered = False
        time_started = time()
        now = time_started
        while (not answered) and (now- time_started < TIMEOUT) and sessions_status[session_id] :
            guess = await bot.wait_for_message(timeout = TIMEOUT-(now- time_started), check=message_isntfrom_bot)
            if guess is None:
                break
            if guess.content.lower() == answer.lower() :
                answered = True
                prev_score = Scores.get(guess.author.name)
                if(prev_score):
                    Scores[guess.author.name] = prev_score + 1
                else:
                    Scores[guess.author.name] = 1
                await bot.say(':white_check_mark: ```You are right : **{}**, {} points!```'.format(guess.author.name,1))
            now =time()
        if(not answered):
            await bot.say(':timer: ```Time is up, one point for me ! \n It is actually {}.```'.format(answer))
            prev_score = Scores.get('Mazghana-bot')
            if(prev_score):
                Scores['Mazghana-bot'] = prev_score + 1
            else:
                Scores['Mazghana-bot'] = 1
        sleep(3)
    await bot.say('Game ended, Scores : \n {}'.format(Scores))
    sessions_status[session_id] = False
            
        
    
#helpers
def message_isntfrom_bot(msg):
    return not msg.author == bot.user
def get_session_id(msg):
    return (msg.server.id+msg.channel.id)
bot.run(tokens.DISCORD_API_KEY)