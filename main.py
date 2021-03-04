from asyncio.transports import ReadTransport
from typing import Awaitable
import discord
import asyncio
import random
import time

DISCORD_BOT_TOKEN = "YOUR DISCORD BOT TOKEN"
DIVIDER = "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"
REACTIONS = ["🇦","🇧", "🇨", "🇩", "🇪", "🇫", "🇬"]
YES_NO = ["✅", "❌"]
COLUMN_COUNT = 7
ROW_COUNT = 6
EMPTY = ":black_circle:"


client = discord.Client(activity=discord.Game("$play vs to start the game"))


class Row():

    def __init__(self):
        self.a = EMPTY
        self.b = EMPTY
        self.c = EMPTY
        self.d = EMPTY
        self.e = EMPTY
        self.f = EMPTY
        self.g = EMPTY
        self.all_columns = [self.a, self.b, self.c, self.d, self.e, self.f, self.g]
        self.generate_empty_row()

    def generate_empty_row(self):
        self.row = ""
        for case in self.all_columns[:-1]:
            self.row += f" {case} ➖"
        self.row += f' {self.all_columns[-1]}'


def generate_grid():
    all_rows = []
    for _ in range(6):
        new_row = Row()
        all_rows.append(new_row)
    
    grid = ""
    for row in all_rows:
        grid += f"{row.row}\n{DIVIDER}\n"
    for letter in REACTIONS:
        if REACTIONS[-1] == letter:
            grid += f" {letter}"
        else:
            grid += f" {letter} ➖"


    return all_rows, grid

def update_grid(all_rows:list):
    all_rows = all_rows
    grid = ""
    for row in all_rows:
        new_row = ""
        for column in row.all_columns[:-1]:
            new_row += f" {column} ➖"
        new_row += f" {row.all_columns[-1]}"
        grid += f"{new_row}\n{DIVIDER}\n"
    for letter in REACTIONS:
        if REACTIONS[-1] == letter:
            grid += f" {letter}"
        else:
            grid += f" {letter} ➖"
    
    return grid

def check_win(all_rows:list, player_color):
    #horizontal
    for row in all_rows:
        for column in range(COLUMN_COUNT-3):
            if row.all_columns[column] == player_color and row.all_columns[column+1] == player_color and row.all_columns[column+2] == player_color and row.all_columns[column+3] == player_color:
                return True, player_color

    #vertical
    for column in range(COLUMN_COUNT):
        for row in range(ROW_COUNT-3):
            if all_rows[row].all_columns[column] == player_color and all_rows[row+1].all_columns[column] == player_color and all_rows[row+2].all_columns[column] == player_color and all_rows[row+3].all_columns[column] == player_color:
                return True, player_color

    #diag positive
    for row in range(ROW_COUNT-3):
        for column in range(len(all_rows[row].all_columns)-3):
            if all_rows[5-row].all_columns[column] == player_color and all_rows[5-row-1].all_columns[column+1] == player_color and all_rows[5-row-2].all_columns[column+2] == player_color and all_rows[5-row-3].all_columns[column+3] == player_color:
                return True, player_color
    
    #diag negative
    for row in range(ROW_COUNT-3):
        for column in range(len(all_rows[row].all_columns)-3):
            if all_rows[row].all_columns[column] == player_color and all_rows[row+1].all_columns[column+1] == player_color and all_rows[row+2].all_columns[column+2] == player_color and all_rows[row+3].all_columns[column+3] == player_color:
                return True, player_color

    return False, None
                    
def bot_IA(all_r:list, player_color:str, bot_color:str):

    def check_best_move(all_r:list, player_color:str):
        best_pos = []
        valid_pos = []

        #HORIZONTAL
        for r in range(ROW_COUNT):
            for c in range(COLUMN_COUNT-1):
                if all_r[r].all_columns[c] == player_color and all_r[r].all_columns[c+1] == player_color:
                    if c > 0 and c < 5:
                        if all_r[r].all_columns[c+2] == player_color:
                            if all_r[r].all_columns[c-1] == EMPTY:
                                try:
                                    if all_r[r+1].all_columns[c-1] != EMPTY:
                                        best_pos.append(c-1)
                                except IndexError:
                                    best_pos.append(c-1)
                            
                            try:
                                if all_r[r].all_columns[c+3] == EMPTY:
                                    try:
                                        if all_r[r+1].all_columns[c+3] != EMPTY:
                                            best_pos.append(c+3)
                                    except IndexError:
                                        best_pos.append(c+3)
                            except IndexError:
                                pass

                        if all_r[r].all_columns[c+2] == EMPTY and all_r[r].all_columns[c-1] == EMPTY:
                            try:
                                if all_r[r+1].all_columns[c+2] != EMPTY and all_r[r+1].all_columns[c-1] != EMPTY:
                                    valid_pos.append(c-1)
                                    valid_pos.append(c+2)
                            except IndexError:
                                valid_pos.append(c-1)
                                valid_pos.append(c+2)

                    elif c == 0:
                        if all_r[r].all_columns[c+2] == player_color:
                            if all_r[r].all_columns[c+3] == EMPTY:
                                try:
                                    if all_r[r+1].all_columns[c+3] != EMPTY:
                                        best_pos.append(c+3)
                                except IndexError:
                                    best_pos.append(c+3)

                    if c < 4:
                        if all_r[r].all_columns[c+2] == EMPTY and all_r[r].all_columns[c+3] == player_color:
                            try:
                                if all_r[r+1].all_columns[c+2] != EMPTY:
                                    best_pos.append(c+2)
                            except IndexError:
                                best_pos.append(c+2)

                    if c > 1:
                        if all_r[r].all_columns[c-1] == EMPTY and all_r[r].all_columns[c-2] == player_color:
                            try:
                                if all_r[r+1].all_columns[c-1] != EMPTY:
                                    best_pos.append(c-1)
                            except IndexError:
                                best_pos.append(c-1)

        #VERTICAL
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT-2):
                if r > 0:
                    if all_r[r].all_columns[c] == player_color and all_r[r+1].all_columns[c] == player_color and all_r[r+2].all_columns[c] == player_color:
                        if all_r[r-1].all_columns[c] == EMPTY:
                            best_pos.append(c)

        #DIAG +
        for r in range(ROW_COUNT-1):
            for c in range(COLUMN_COUNT-1):
                if all_r[5-r].all_columns[c] == player_color and all_r[5-r-1].all_columns[c+1] == player_color:
                    if c in range(1, 5) and r in range(1, 4):
                        if all_r[5-r+1].all_columns[c-1] == EMPTY and all_r[5-r-2].all_columns[c+2] == player_color:
                            try:
                                if all_r[5-r+2].all_columns[c-1] != EMPTY:
                                    best_pos.append(c-1)
                            except IndexError:
                                best_pos.append(c-1)

                        elif all_r[5-r+1].all_columns[c-1] == player_color and all_r[5-r-2].all_columns[c+2] == EMPTY:
                            if all_r[5-r-1].all_columns[c+2] != EMPTY:
                                best_pos.append(c+2)
                    
                    elif c == 0 and r < 3:
                        if all_r[5-r-2].all_columns[c+2] == player_color and all_r[5-r-3].all_columns[c+3] == EMPTY:
                            if all_r[5-r-1].all_columns[c+2] != EMPTY:
                                best_pos.append(c+2)

                    elif c == 4 and r < 4:
                        if all_r[5-r-2].all_columns[c+2] == player_color and all_r[5-r-1].all_columns[c-1] == EMPTY:
                            try:
                                if all_r[5-r+2].all_columns[c-1] != EMPTY:
                                    best_pos.append(c-1)
                            except IndexError:
                                best_pos.append(c-1)

                    if r < 3 and c < 4:
                        if all_r[5-r-2].all_columns[c+2] == EMPTY and all_r[5-r-3].all_columns[c+3] == player_color:
                            if all_r[5-r-1].all_columns[c+2] != EMPTY:
                                best_pos.append(c+2)

                    if r > 1 and c > 2:
                        if all_r[5-r+1].all_columns[c-1] == EMPTY and all_r[5-r+2].all_columns[c-2] == player_color:
                            if all_r[5-r+2].all_columns[c-1] != EMPTY:
                                best_pos.append(c-1)

        #DIAG -
        for r in range(ROW_COUNT-1):
            for c in range(COLUMN_COUNT-1):
                if all_r[r].all_columns[c] == player_color and all_r[r+1].all_columns[c+1] == player_color:
                    if c < 5 and r < 3:
                        if all_r[r+2].all_columns[c+2] == player_color:
                            try:
                                if all_r[r+4].all_columns[c+3] != EMPTY and all_r[r+3].all_columns[c+3] == EMPTY:
                                    best_pos.append(c+3)
                            except IndexError:
                                pass
                    
                        if c > 0 and r > 0:
                            if all_r[r+2].all_columns[c+2] == player_color and all_r[r-1].all_columns[c-1] == EMPTY:
                                if all_r[r].all_columns[c-1] != EMPTY:
                                    best_pos.append(c-1)

                    if r > 1:
                        if all_r[r-1].all_columns[c-1] == EMPTY and all_r[r-2].all_columns[c-2] == player_color:
                            if all_r[r].all_columns[c-1] != EMPTY:
                                best_pos.append(c-2)
                    
                    if r < 3 and c < 4:
                        if all_r[r+2].all_columns[c+2] == EMPTY and all_r[r+3].all_columns[c+3] == player_color:
                            if all_r[r+3].all_columns[c+2] != EMPTY:
                                best_pos.append(c-2)

        return best_pos, valid_pos

    #------------------BOT CAN WIN -----------------
    
    best_move, valid_pos = check_best_move(all_r, bot_color)
    if best_move != []:
        bot_choice = random.choice(best_move)
        return bot_choice
    elif valid_pos != []:
        bot_choice = random.choice(valid_pos)
        return bot_choice

    #------------------ BLOCKING: ------------------

    best_move, valid_pos = check_best_move(all_r, player_color)
    if best_move != []:
        bot_choice = random.choice(best_move)
        return bot_choice
    elif valid_pos != []:
        bot_choice = random.choice(valid_pos)
        return bot_choice

    #------------------ ELSE CHECK IF 2 PIECES

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-1):
            if r > 0:
                if all_r[r].all_columns[c] == bot_color and all_r[r+1].all_columns[c] == bot_color:
                    if all_r[r-1].all_columns[c] == EMPTY:
                        return c

    #---------- ELSE RANDOM ----------------------


    else:
        print("random")
        best_col = random.randint(0,6)
        return best_col
    



@client.event
async def on_ready():
    print(f'Ready with {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel = message.channel
    host = message.author
    host_color = ":blue_circle:"
    opponent_color = ":red_circle:"
    host_mention = f"<@!{host.id}>"

    if message.content.startswith("$play vs"):
        try:
            opponent = message.content.split(' ')[2]
            try:
                opponent_id = int(opponent.split("!")[1].split('>')[0])
                opponent_mention = f"<@!{opponent_id}>"
            except IndexError:
                opponent_id = int(opponent.split("@")[1].split('>')[0])
                opponent_mention = f"<@!{opponent_id}>"
        
        except (IndexError, ValueError):
            embed = discord.Embed(title="Sorry, you need to mention somebody.", description="**Try again.**")
            embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
            bot_msg = await channel.send(embed=embed)
            return


        if "@" not in opponent_mention:
            embed = discord.Embed(title="Sorry, invalid pseudo.", description="**Try again.**")
            embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
            bot_msg = await channel.send(embed=embed)

        elif opponent_mention == host_mention or opponent_mention == f"<@!{client.user.id}>":
            embed = discord.Embed(title="Sorry, you can't play against yourself or me.", description="**Try again.**")
            embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
            bot_msg = await channel.send(embed=embed)

        elif "<@" in opponent:

            #Ask opponent to accept the match
            def check_opponent_accept(reaction, user):
                return str(reaction) in YES_NO and user.id == opponent_id

            timeout_accept_match = 0
            while timeout_accept_match != 10:


                embed = discord.Embed(title="Puissance 4 Match Invitation", description=f"Accept with {YES_NO[0]}\nDecline with {YES_NO[1]}\n**You have {10-timeout_accept_match}secs to react.**")
                embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                if timeout_accept_match == 0:
                    bot_msg = await channel.send(embed=embed)  
                    for emoji in YES_NO:
                        await bot_msg.add_reaction(emoji)
                else:
                    await bot_msg.edit(embed=embed)


                try:
                    reaction, user = await client.wait_for("reaction_add", timeout=1, check=check_opponent_accept)
                
                    await bot_msg.clear_reactions()
                    if str(reaction) == YES_NO[0]:
                        embed = discord.Embed(title="Puissance 4 Match Invitation", description=f"{opponent_mention} accepted the invitation.\nMatch starts soon...")
                        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                        await bot_msg.edit(embed=embed)
                        break

                    else:
                        embed = discord.Embed(title="Puissance 4 Match Invitation", description=f"{opponent_mention} declined the invitation.")
                        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                        await bot_msg.edit(embed=embed)
                        return

                except asyncio.TimeoutError:
                    if timeout_accept_match == 9:
                        await bot_msg.clear_reactions()
                        embed = discord.Embed(title="Puissance 4 Match Invitation", description=f"{opponent_mention} took too much time to react, match declined.")
                        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                        await bot_msg.edit(embed=embed)  
                        return
                    else:
                        timeout_accept_match += 1




            all_rows, grid = generate_grid() 
            current_player = random.choice([host_mention, opponent_mention])
            next_color_player = ":blue_circle:" if (current_player == host_mention) else ":red_circle:"
            

        
            embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
            embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
            await bot_msg.edit(embed=embed)
            for emoji in REACTIONS:
                await bot_msg.add_reaction(emoji)


            def check_host(reaction, user):
                return str(reaction) in REACTIONS and user.id == host.id
            def check_opponent(reaction, user):
                return str(reaction) in REACTIONS and user.id == opponent_id


            embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
            embed.add_field(name=f"30secs to play.", value=f"Current Player : {current_player} {next_color_player}")
            embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
            await bot_msg.edit(embed=embed)

            game_end = False

        
            while not game_end:

                indications = ""

                try:
                    if current_player == host_mention:
                        reaction, user = await client.wait_for("reaction_add", timeout=30, check=check_host)
                        await bot_msg.remove_reaction(str(reaction), user)
                        column = REACTIONS.index(str(reaction))
                        current_player = opponent_mention
                        next_color_player = ":red_circle:"
                        color = host_color

                    elif current_player == opponent_mention:
                        reaction, user = await client.wait_for("reaction_add", timeout=30, check=check_opponent)
                        await bot_msg.remove_reaction(str(reaction), user)
                        column = REACTIONS.index(str(reaction))
                        current_player = host_mention
                        next_color_player = ":blue_circle:"
                        color = opponent_color
                    
                    i = -1
                    for row in all_rows:
                        if row.all_columns[column] == EMPTY:
                            i += 1

                        #If Column Full
                        if i==-1:
                            if current_player == host_mention:
                                current_player = opponent_mention
                                next_color_player = ":red_circle:"

                            else:
                                current_player = host_mention
                                next_color_player = ":blue_circle:"
                                
                            indications = "This column is full, please play again.\n"
                            break
                            

                        #If Column Empty or Else
                        if i == 5 or row.all_columns[column] != EMPTY:
                            all_rows[i].all_columns[column] = color
                    


                    grid = update_grid(all_rows)
                    embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                    if color == ":blue_circle:":
                        embed.add_field(name=f"{indications}30secs to play.", value=f"Current Player : {current_player} {next_color_player}")
                    else:
                        embed.add_field(name=f"{indications}30secs to play.", value=f"Current Player : {current_player} {next_color_player}")
                    embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                    await bot_msg.edit(embed=embed)


                    # Check Win
                    result, winner_color = check_win(all_rows, host_color)
                    if result == False and winner_color == None:
                        result, winner_color = check_win(all_rows, opponent_color)
                    
                    if result is True:
                        if winner_color == ":blue_circle:":
                            winner = host_mention
                        else:
                            winner = opponent_mention
                        await bot_msg.clear_reactions()
                        embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                        embed.add_field(name=f"Match Finish, Result :", value=f"🎉 {winner} has won ! 🎉")
                        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                        await bot_msg.edit(embed=embed)
                        return

                    #Check if grid is full
                    k = 0
                    for column in all_rows[0].all_columns:
                        if column == EMPTY:
                            break
                        else:
                            k+=1
                        if k==7:
                            await bot_msg.clear_reactions()
                            embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                            embed.add_field(name=f"Draw !", value=f"Grid is full, nobody has won. Play again !")
                            embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                            await bot_msg.edit(embed=embed)
                            game_end = True

                    
                    

                    
                except asyncio.TimeoutError:
                    await bot_msg.clear_reactions()
                    embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                    embed.add_field(name=f"Match has expired.", value=f"{current_player} took too much time to play.")
                    embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                    await bot_msg.edit(embed=embed)
                    game_end = True

    elif message.content.startswith("$play solo"):

        embed = discord.Embed(title="Puissance 4 Match", description=f"{host_mention} are you ready ?")
        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
        bot_msg = await channel.send(embed=embed)

        opponent_mention = f"<@!{client.user.id}>"
        current_player = random.choice([opponent_mention, host_mention])
        next_color_player = ":blue_circle:" if (current_player == host_mention) else ":red_circle:"


        all_rows, grid = generate_grid() 


    
        embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
        await bot_msg.edit(embed=embed)
        for emoji in REACTIONS:
            await bot_msg.add_reaction(emoji)

        def check_host(reaction, user):
            return str(reaction) in REACTIONS and user.id == host.id


        embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
        embed.add_field(name=f"30secs to play.", value=f"Current Player : {current_player} {next_color_player}")
        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
        await bot_msg.edit(embed=embed)

        game_end = False

    
        while not game_end:

            indications = ""
            try:
                if current_player == host_mention:
                    reaction, user = await client.wait_for("reaction_add", timeout=30, check=check_host)
                    await bot_msg.remove_reaction(str(reaction), user)
                    column = REACTIONS.index(str(reaction))
                    current_player = opponent_mention
                    next_color_player = ":red_circle:"
                    color = host_color

                elif current_player == opponent_mention:
                    time.sleep(0.5)
                    bot_choice = bot_IA(all_rows, host_color, opponent_color)
                    print(bot_choice)
                    column = bot_choice
                    current_player = host_mention
                    next_color_player = ":blue_circle:"
                    color = opponent_color
                
                i = -1
                for row in all_rows:
                    if row.all_columns[column] == EMPTY:
                        i += 1

                    #If Column Full
                    if i==-1:
                        if current_player == host_mention:
                            current_player = opponent_mention
                            next_color_player = ":red_circle:"

                        else:
                            current_player = host_mention
                            next_color_player = ":blue_circle:"
                            
                        indications = "This column is full, please play again.\n"
                        break
                        

                    #If Column Empty or Else
                    if i == 5 or row.all_columns[column] != EMPTY:
                        all_rows[i].all_columns[column] = color
                


                grid = update_grid(all_rows)
                embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                if color == ":blue_circle:":
                    embed.add_field(name=f"{indications}30secs to play.", value=f"Current Player : {current_player} {next_color_player}")
                else:
                    embed.add_field(name=f"{indications}30secs to play.", value=f"Current Player : {current_player} {next_color_player}")
                embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                await bot_msg.edit(embed=embed)


                # Check Win
                result, winner_color = check_win(all_rows, host_color)
                if result == False and winner_color == None:
                    result, winner_color = check_win(all_rows, opponent_color)
                
                if result is True:
                    if winner_color == ":blue_circle:":
                        winner = host_mention
                    else:
                        winner = opponent_mention
                    await bot_msg.clear_reactions()
                    embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                    embed.add_field(name=f"Match Finish, Result :", value=f"🎉 {winner} has won ! 🎉")
                    embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                    await bot_msg.edit(embed=embed)
                    return

                #Check if grid is full
                k = 0
                for column in all_rows[0].all_columns:
                    if column == EMPTY:
                        break
                    else:
                        k+=1
                    if k==7:
                        await bot_msg.clear_reactions()
                        embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                        embed.add_field(name=f"Draw !", value=f"Grid is full, nobody has won. Play again !")
                        embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                        await bot_msg.edit(embed=embed)
                        game_end = True

                
                

                
            except asyncio.TimeoutError:
                await bot_msg.clear_reactions()
                embed = discord.Embed(title="----------- Puissance 4 Match ! -----------", description=grid)
                embed.add_field(name=f"Match has expired.", value=f"{current_player} took too much time to play.")
                embed.set_footer(text=f"Host : {host}", icon_url=host.avatar_url)
                await bot_msg.edit(embed=embed)
                game_end = True

client.run(DISCORD_BOT_TOKEN)
