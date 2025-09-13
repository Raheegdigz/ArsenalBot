from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
print("DEBUG TOKEN:", TOKEN)
import discord
from discord.ext import commands
import json
import random
import asyncio
from datetime import datetime, timedelta
import os

# -------------------- INTENTS --------------------
intents = discord.Intents.default()
intents.members = True  # Required to fetch guild members

# -------------------- BOT --------------------
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=['!', '/'], intents=intents)

# Data storage files
# Data storage files (stored in local "data" folder next to main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, "player_data.json")
TACTICS_FILE = os.path.join(DATA_DIR, "tactics.json")
TRIALS_FILE = os.path.join(DATA_DIR, "trials.json")

# Role IDs (replace with actual role IDs)
ROLE_IDS = {
    'official_player': '1415854436487663648',
    'reserve': '1379986606185906202',
    'substitution': '1415854663088996453',
    'b_team': '1415854765782470727',
    'a_team': '1379986606185906200',
    'starting_7': '1379986606185906203',
    'potw': '1415854891758522561',
    '1_star': '1415855082011885628',
    '2_star': '1415855147568992266',
    '3_star': '1415855184478998599',
    '4_star': '1415855202971549777',
    '5_star': '1415855219774066871'
}

# Level requirements
LEVEL_REQUIREMENTS = {
    'Reserve': 0,
    'Substitution': 10,
    'B Team': 20,
    'A Team': 35,
    'Starting 7': 50
}

# Performance levels
PERFORMANCE_LEVELS = {
    (0, 2): "Horrible",
    (3, 4): "Poor", 
    (5, 6): "Average",
    (7, 8): "Good",
    (9, 10): "Excellent"
}

# Fun data
COUNTRIES = [
    ("🇧🇷", "Brazil"), ("🇦🇷", "Argentina"), ("🇫🇷", "France"), ("🇩🇪", "Germany"),
    ("🇪🇸", "Spain"), ("🇮🇹", "Italy"), ("🇳🇱", "Netherlands"), ("🏴󠁧󠁢󠁥󠁮󠁧󠁿", "England"),
    ("🇵🇹", "Portugal"), ("🇧🇪", "Belgium"), ("🇲🇽", "Mexico"), ("🇺🇸", "USA"),
    ("🇨🇴", "Colombia"), ("🇺🇾", "Uruguay"), ("🇨🇷", "Costa Rica"), ("🇪🇬", "Egypt")
]

FOOTBALL_PLAYERS = [
    "Lionel Messi", "Cristiano Ronaldo", "Neymar", "Kylian Mbappe", 
    "Erling Haaland", "Robert Lewandowski", "Kevin De Bruyne", "Mohamed Salah",
    "Virgil van Dijk", "Karim Benzema", "Luka Modric", "Sadio Mane",
    "Harry Kane", "Son Heung-min", "Bruno Fernandes", "Paul Pogba"
]

# 7-aside formations for tactics
FORMATIONS_7_ASIDE = [
    "2-3-1", "2-2-2", "3-2-1", "3-1-2", "1-3-2", "1-4-1", "2-4-0", "3-3-0",
    "1-2-3", "2-1-3", "1-5-0", "4-1-1", "1-1-4", "3-1-1-1", "2-2-1-1",
    "1-3-1-1", "2-1-2-1", "1-2-2-1", "3-0-3", "2-0-4", "1-0-5", "4-0-2",
    "0-4-2", "0-3-3", "0-2-4", "1-1-1-3", "2-1-1-2", "1-2-1-2", "1-1-2-2",
    "0-5-1", "0-6-0", "5-1-0", "4-2-0", "6-0-0", "1-4-0-1", "0-4-0-2",
    "2-3-0-1", "1-3-0-2", "3-2-0-1", "0-1-4-1", "0-2-3-1", "1-0-4-1",
    "2-0-3-1", "3-0-2-1", "4-0-1-1", "0-0-5-1", "0-1-5-0", "1-0-5-0"
]

FORMATIONS = FORMATIONS_7_ASIDE  # Use 7-a-side formations

TACTICS_STYLES = [
    "Tiki-Taka", "Counter Attack", "High Press", "Possession", "Direct",
    "Wing Play", "Through Balls", "Set Pieces", "Defensive", "Attacking"
]

# Initialize data files
def init_data_files():
    # Create a "data" folder inside the same directory as this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # Define your data file(s)
    player_data_file = os.path.join(data_dir, "player_data.json")

    # Create empty file(s) if they don't exist
    if not os.path.exists(player_data_file):
        with open(player_data_file, "w") as f:
            f.write("{}")  # empty JSON object
    
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(TACTICS_FILE):
        with open(TACTICS_FILE, 'w') as f:
            json.dump({
                'formation': '4-2-1',
                'style': 'Attacking',
                'instructions': 'Press high, quick passing, overlap runs'
            }, f)
    
    if not os.path.exists(TRIALS_FILE):
        with open(TRIALS_FILE, 'w') as f:
            json.dump({
                'active_trials': {},
                'active_training': {},
                'active_friendlies': {},
                'potw_players': [],
                'current_lineup': [],
                'suggestions': []
            }, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_tactics():
    with open(TACTICS_FILE, 'r') as f:
        return json.load(f)

def save_tactics(tactics):
    with open(TACTICS_FILE, 'w') as f:
        json.dump(tactics, f, indent=2)

def load_trials():
    with open(TRIALS_FILE, 'r') as f:
        return json.load(f)

def save_trials(trials):
    with open(TRIALS_FILE, 'w') as f:
        json.dump(trials, f, indent=2)

def get_player_data(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            'points': 0,
            'level': 'Reserve',
            'stars': 1,
            'strikes': 0,
            'rating': 0,
            'position': 'Not Set',
            'form': 50,
            'contract_years': 0,
            'stats': {
                'goals': 0, 'assists': 0, 'passes': 0, 'dribbles_completed': 0,
                'dribbles_failed': 0, 'shots_taken': 0, 'shots_on_target': 0,
                'potws': 0, 'key_passes': 0, 'tackles': 0, 'interceptions': 0,
                'hattricks': 0, 'appearances': 0, 'clean_sheets': 0, 'saves': 0,
                'yellow_cards': 0, 'red_cards': 0, 'penalties_scored': 0
            },
            'performance_ratings': [],
            'registered': False
        }
        save_data(data)
    return data[str(user_id)]

def update_player_data(user_id, player_data):
    data = load_data()
    data[str(user_id)] = player_data
    save_data(data)

def is_admin():
    def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def is_official_player():
    def predicate(ctx):
        try:
            official_role = discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['official_player']))
            return official_role in ctx.author.roles if official_role else False
        except:
            return False
    return commands.check(predicate)

def get_performance_level(rating):
    for (min_val, max_val), level in PERFORMANCE_LEVELS.items():
        if min_val <= rating <= max_val:
            return level
    return "Unknown"

@bot.event
async def on_ready():
    init_data_files()
    print(f'{bot.user} has connected to Discord!')
    print("Arsenal FC Bot is ready! 🔴")

# Enhanced Role IDs for the new features
STRIKE_ROLES = {
    1: '1383629910169354250',
    2: '1383629908093436075', 
    3: '1383629903047561348'
}

STAFF_ROLES = {
    'trial_staff': '1379986606202552372',
    'staff': '1379986606202552373',
    'senior_staff': '1383579074152235018',
    'head_of_staff': '1416127117292470282',
    'head_of_discipline': '1416127236112781454',
    'head_of_tactics': '1416127416736419881',
    'executive_coordinator': '1386314895037042698',
    'community_manager': '1383525202792812635',
    'overseer': '1416127785461874705'
}

SPECIAL_ROLES = {
    'captain': '1381337986477719642',
    'pending': '1393704607125078086',
    'loa': '1388705296758739107',
    'sotw': '1393028997478354954'
}

WAITING_ROOM_VC = '1379986608392110147'
TRIALS_CHANNEL = '1416121352884322415'

# Position options for trials
POSITIONS = [
    "Goalkeeper", "Centre-Back", "Left-Back", "Right-Back", 
    "Defensive Midfielder", "Central Midfielder", "Attacking Midfielder",
    "Left Winger", "Right Winger", "Striker", "Support Striker"
]

STAFF_LEVEL_NAMES = {
    'trial_staff': 'Trial Staff',
    'staff': 'Staff',
    'senior_staff': 'Senior Staff',
    'head_of_staff': 'Head Of Staff',
    'head_of_discipline': 'Head Of Discipline', 
    'head_of_tactics': 'Head Of Tactics',
    'executive_coordinator': 'Executive Coordinator',
    'community_manager': 'Community Manager',
    'overseer': 'Overseer'
}

# Match results data structure
def init_results_file():
    results_file = os.path.join(DATA_DIR, "results.json")
    if not os.path.exists(results_file):
        with open(results_file, 'w') as f:
            json.dump([], f)
    return results_file

def load_results():
    results_file = init_results_file()
    with open(results_file, 'r') as f:
        return json.load(f)

def save_results(results):
    results_file = init_results_file()
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

# FORMATIONS_7_ASIDE already defined above

# Remove the built-in help command to avoid conflict
bot.remove_command('help')

# HELP COMMANDS
@bot.command()
async def help(ctx):
    """Beautiful help command for players"""
    embed = discord.Embed(
        title="🔴 ARSENAL FC - PLAYER COMMANDS",
        description="**Welcome to the Official Arsenal FC Discord!**\n⚽ *Gunners Forever!* ⚽",
        color=0xDC143C
    )
    
    embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
    
    embed.add_field(
        name="📊 **PLAYER INFORMATION**",
        value="`!stats @user` - View comprehensive player statistics\n"
              "`!leaderboard` - Club points leaderboard\n"
              "`!roster` - Official team roster\n"
              "`!viewstrikes @user` - Check player's disciplinary record\n"
              "`!document @user` - View official player document",
        inline=False
    )
    
    embed.add_field(
        name="⚽ **FUN & GAMES** *(20+ Activities!)*",
        value="`!guesscountry` - Guess the flag game 🏁\n"
              "`!guessplayer` - Football player guessing game ⭐\n"
              "`!trivia` - Arsenal & football trivia 🧠\n"
              "`!joke` - Random football jokes 😂\n"
              "`!quote` - Inspirational football quotes 💭\n"
              "`!fact` - Amazing football facts 📚\n"
              "`!predict` - Match prediction generator 🔮\n"
              "`!celebration` - Random goal celebrations 🎉\n"
              "`!nickname` - Get your football nickname 📛\n"
              "`!formation` - Tactical formation suggestions ⚽\n"
              "**+ 10 More Fun Commands!**",
        inline=False
    )
    
    embed.add_field(
        name="🏆 **TEAM INTERACTION**",
        value="`!suggestion <text>` - Submit suggestions to management 💡\n"
              "`!motivation` - Get motivated for the match! 🔥\n"
              "`!chant` - Arsenal chants and songs 🎵\n"
              "`!lucky` - Lucky number generator 🍀",
        inline=False
    )
    
    # Only show official player commands if they have the role
    try:
        official_role = discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['official_player']))
        if official_role in ctx.author.roles:
            embed.add_field(
                name="🎖️ **OFFICIAL PLAYER COMMANDS**",
                value="`!currenttactics` - View current team tactics\n"
                      "`!trials` - Join active trials\n"
                      "`!training` - Join training sessions\n"
                      "`!friendly` - Join friendly matches",
                inline=False
            )
    except:
        pass
    
    embed.add_field(
        name="🔴 **ARSENAL FC VALUES**",
        value="• **Respect** - Show respect to all members\n"
              "• **Dedication** - Commitment to the club\n"
              "• **Excellence** - Strive for greatness\n"
              "• **Unity** - We are stronger together",
        inline=False
    )
    
    embed.set_footer(
        text="💡 Only administrators can access management commands | North London Forever! 🔴",
        icon_url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png"
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def bothelp(ctx):
    embed = discord.Embed(
        title="🏆 Arsenal FC Bot Commands",
        description="Welcome to Arsenal FC! Here are all available commands:",
        color=0xDC143C
    )
    
    embed.add_field(
        name="📊 Player Commands",
        value="`!stats <user>` - View player statistics\n"
              "`!leaderboard` - View points leaderboard\n"
              "`!roster` - View team roster\n"
              "`!currenttactics` - View current tactics (Official players)\n"
              "`!viewstrikes <user>` - View player strikes",
        inline=False
    )
    
    embed.add_field(
        name="⚽ Fun Commands (20+ Games!)",
        value="`!guesscountry` - Guess the country game\n"
              "`!guessplayer` - Guess the football player\n"
              "`!trivia` - Football trivia questions\n"
              "`!joke` - Random football joke\n"
              "`!quote` - Inspirational quote\n"
              "`!fact` - Football fact\n"
              "`!predict` - Match prediction generator\n"
              "`!celebration` - Random celebration\n"
              "`!nickname` - Get a football nickname\n"
              "`!formation` - Random formation suggestion\n"
              "**Plus 10+ more fun commands!**",
        inline=False
    )
    
    embed.add_field(
        name="💭 Team Interaction",
        value="`!suggestion <text>` - Make a suggestion (Official players)\n"
              "`!motivation` - Get motivated\n"
              "`!chant` - Arsenal chant\n"
              "`!lucky` - Lucky number generator",
        inline=False
    )
    
    embed.set_footer(text="💡 Tip: Official players have access to additional commands! Use !adminhelp if you're an admin. Use !bothelp for main commands.")
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def managerhelp(ctx):
    embed = discord.Embed(
        title="🛡️ ARSENAL FC - ADMIN CONTROL PANEL",
        description="**Complete Management System - 40+ Commands**\n🔴 *Administrative Excellence* 🔴",
        color=0xFF0000
    )
    
    embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
    
    embed.add_field(
        name="👥 Player Management (8 commands)",
        value="`!register <user>` - Register a new player\n"
              "`!release <user> <reason>` - Release a player\n"
              "`!promotelevel <user> <level>` - Promote player\n"
              "`!demotelevel <user> <level>` - Demote player\n"
              "`!addpoints <user> <points>` - Add points\n"
              "`!removepoints <user> <points>` - Remove points\n"
              "`!stars <user> <number>` - Set star rating (1-5)\n"
              "`!rating <user> <rating>` - Set player rating (0-100)",
        inline=False
    )
    
    embed.add_field(
        name="📋 Match & Training (6 commands)",
        value="`!trials <max_entries>` - Start trials\n"
              "`!training <max_entries>` - Start training\n"
              "`!friendly <max_entries>` - Start friendly\n"
              "`!lineup <7 users>` - Set match lineup\n"
              "`!leaguematchdone` - Mark league match complete\n"
              "`!analysis <user> <rating> <text>` - Player analysis",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Awards & Discipline (4 commands)",
        value="`!potw <user>` - Add Player of the Week\n"
              "`!totw` - View Team of the Week\n"
              "`!strike <user> <reason>` - Give strike\n"
              "`!officecall <user> <reason>` - Office call",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Management Tools (7 commands)",
        value="`!tactics` - Manage tactics (Interactive UI)\n"
              "`!say <message>` - Bot announcement\n"
              "`!announcelm <text>` - League match announcement\n"
              "`!document <user>` - Player document/report\n"
              "`!allstats` - View all stat commands\n"
              "`!info <user>` - Detailed player info\n"
              "`!suggestions` - View all player suggestions",
        inline=False
    )
    
    embed.set_footer(
        text="🛡️ Arsenal FC Management System | Use responsibly for club excellence!",
        icon_url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png"
    )
    
    await ctx.send(embed=embed)

# REGISTRATION SYSTEM
class RegistrationView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=300)
        self.user = user
        self.position = None
        
    @discord.ui.select(
        placeholder="Choose your main position...",
        options=[
            discord.SelectOption(label="Goalkeeper", value="Goalkeeper", emoji="🥅"),
            discord.SelectOption(label="Defender", value="Defender", emoji="🛡️"),
            discord.SelectOption(label="Midfielder", value="Midfielder", emoji="⚽"),
            discord.SelectOption(label="Forward", value="Forward", emoji="🎯"),
            discord.SelectOption(label="Winger", value="Winger", emoji="🏃"),
        ]
    )
    async def position_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.position = select.values[0]
        
        contract_embed = discord.Embed(
            title="📋 ARSENAL FC - OFFICIAL CONTRACT",
            description="**PROFESSIONAL FOOTBALL PLAYER AGREEMENT**",
            color=0xDC143C
        )
        
        years = random.choice([2, 3, 4])
        
        contract_embed.add_field(
            name="📝 CONTRACT DETAILS",
            value=f"**Position:** {self.position}\n"
                  f"**Contract Length:** {years} years\n"
                  f"**Starting Level:** Reserve\n"
                  f"**Club:** Arsenal FC",
            inline=False
        )
        
        contract_embed.add_field(
            name="📋 PLAYER EXPECTATIONS",
            value="• **Training Attendance:** Mandatory participation in all scheduled training sessions\n"
                  "• **Match Availability:** Be available for matches and friendlies\n"
                  "• **Jersey Number:** Change your in-game shirt number to your assigned number\n"
                  "• **Media Participation:** You may appear in TikToks, YouTube videos, and streams\n"
                  "• **Professional Conduct:** Maintain high standards on and off the pitch\n"
                  "• **Team Commitment:** Show dedication and loyalty to Arsenal FC",
            inline=False
        )
        
        contract_embed.add_field(
            name="🎯 PROGRESSION SYSTEM",
            value="• Start as Reserve (0 points)\n"
                  "• Progress through: Substitution (10pts) → B Team (20pts) → A Team (35pts) → Starting 7 (50pts)\n"
                  "• Earn points through training, matches, and good performance\n"
                  "• Maintain professional standards to avoid strikes",
            inline=False
        )
        
        contract_embed.set_footer(text="By accepting, you agree to all terms and conditions above.")
        
        view = ContractResponseView(self.user, self.position, years)
        await interaction.response.edit_message(embed=contract_embed, view=view)

class ContractResponseView(discord.ui.View):
    def __init__(self, user, position, years):
        super().__init__(timeout=300)
        self.user = user
        self.position = position
        self.years = years
        
    @discord.ui.button(label="✅ Accept Contract", style=discord.ButtonStyle.success)
    async def accept_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        player_data = get_player_data(self.user.id)
        player_data['registered'] = True
        player_data['position'] = self.position
        player_data['contract_years'] = self.years
        player_data['level'] = 'Reserve'
        update_player_data(self.user.id, player_data)
        
        guild = interaction.guild
        if guild:
            member = guild.get_member(self.user.id)
            try:
                official_role = discord.utils.get(guild.roles, id=int(ROLE_IDS['official_player']))
                reserve_role = discord.utils.get(guild.roles, id=int(ROLE_IDS['reserve']))
                
                if member and official_role:
                    await member.add_roles(official_role)
                if member and reserve_role:
                    await member.add_roles(reserve_role)
            except:
                pass
        
        embed = discord.Embed(
            title="🎉 CONTRACT ACCEPTED!",
            description=f"Welcome to Arsenal FC, {self.user.mention}!",
            color=0x00FF00
        )
        embed.add_field(
            name="✅ Registration Complete",
            value=f"You are now an official Arsenal FC player!\n"
                  f"**Position:** {self.position}\n"
                  f"**Level:** Reserve\n"
                  f"**Contract:** {self.years} years",
            inline=False
        )
        embed.set_footer(text="Good luck and welcome to the team! 🔴")
        
        await interaction.response.edit_message(embed=embed, view=None)
        
    @discord.ui.button(label="❌ Decline Contract", style=discord.ButtonStyle.danger)
    async def decline_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 Contract Declined",
            description="You have declined the Arsenal FC contract.",
            color=0xFF0000
        )
        embed.add_field(
            name="Thank you for your time",
            value="Feel free to reconsider in the future!",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

@bot.command()
@is_admin()
async def register(ctx, member: discord.Member):
    """Register a new player"""
    embed = discord.Embed(
        title="🏆 ARSENAL FC INVITATION",
        description=f"Hello {member.mention}!\n\nYou have been invited to join Arsenal FC as a professional player!",
        color=0xDC143C
    )
    
    embed.add_field(
        name="📋 Next Steps",
        value="1. Choose your main position from the dropdown below\n"
              "2. Review the official contract\n"
              "3. Accept or decline the offer",
        inline=False
    )
    
    view = RegistrationView(member)
    
    try:
        await member.send(embed=embed, view=view)
        await ctx.send(f"✅ Registration invitation sent to {member.mention}")
    except discord.Forbidden:
        await ctx.send(f"❌ Could not send DM to {member.mention}. They may have DMs disabled.")

# POINTS SYSTEM
@bot.command()
@is_admin()
async def addpoints(ctx, member: discord.Member, points: int):
    """Add points to a player"""
    player_data = get_player_data(member.id)
    old_points = player_data['points']
    player_data['points'] += points
    
    old_level = player_data['level']
    new_level = None
    
    for level, requirement in sorted(LEVEL_REQUIREMENTS.items(), key=lambda x: x[1], reverse=True):
        if player_data['points'] >= requirement:
            new_level = level
            break
    
    if new_level and new_level != old_level:
        player_data['level'] = new_level
    
    if points > 0:
        player_data['form'] = min(100, player_data['form'] + 2)
    
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="📈 Points Added", color=0x00FF00)
    embed.add_field(
        name="Player Update",
        value=f"**Player:** {member.mention}\n"
              f"**Points Added:** +{points}\n"
              f"**Total Points:** {old_points} → {player_data['points']}\n"
              f"**Level:** {player_data['level']}",
        inline=False
    )
    
    if new_level != old_level:
        embed.add_field(name="🎉 Level Up!", value=f"{old_level} → **{new_level}**", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def removepoints(ctx, member: discord.Member, points: int):
    """Remove points from a player"""
    player_data = get_player_data(member.id)
    old_points = player_data['points']
    player_data['points'] = max(0, player_data['points'] - points)
    
    old_level = player_data['level']
    new_level = 'Reserve'
    
    for level, requirement in sorted(LEVEL_REQUIREMENTS.items(), key=lambda x: x[1], reverse=True):
        if player_data['points'] >= requirement:
            new_level = level
            break
    
    if new_level != old_level:
        player_data['level'] = new_level
    
    player_data['form'] = max(0, player_data['form'] - 5)
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="📉 Points Removed", color=0xFF0000)
    embed.add_field(
        name="Player Update",
        value=f"**Player:** {member.mention}\n"
              f"**Points Removed:** -{points}\n"
              f"**Total Points:** {old_points} → {player_data['points']}\n"
              f"**Level:** {player_data['level']}\n"
              f"**Form:** {player_data['form']}%",
        inline=False
    )
    
    if new_level != old_level:
        embed.add_field(name="📉 Level Down", value=f"{old_level} → **{new_level}**", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    """View points leaderboard"""
    data = load_data()
    if not data:
        await ctx.send("No players registered yet!")
        return
    
    players = [(user_id, player_data['points'], player_data['level']) 
               for user_id, player_data in data.items() 
               if player_data.get('registered', False)]
    
    players.sort(key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(title="🏆 Arsenal FC Leaderboard", color=0xDC143C)
    
    if not players:
        embed.description = "No registered players yet!"
    else:
        leaderboard_text = ""
        for i, (user_id, points, level) in enumerate(players[:10], 1):
            try:
                user = ctx.bot.get_user(int(user_id))
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔸"
                leaderboard_text += f"{emoji} **{i}.** {user.mention if user else 'Unknown'} - {points} pts ({level})\n"
            except:
                continue
        
        embed.description = leaderboard_text
    
    embed.set_footer(text="💡 Tip: Earn points by attending training and performing well!")
    await ctx.send(embed=embed)

# PLAYER MANAGEMENT
@bot.command()
@is_admin()
async def promotelevel(ctx, member: discord.Member, *, level):
    """Promote a player to a new level"""
    if level not in LEVEL_REQUIREMENTS:
        await ctx.send(f"❌ Invalid level. Valid levels: {', '.join(LEVEL_REQUIREMENTS.keys())}")
        return
    
    player_data = get_player_data(member.id)
    old_level = player_data['level']
    player_data['level'] = level
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⬆️ Player Promoted", color=0x00FF00)
    embed.add_field(
        name="Promotion Details",
        value=f"**Player:** {member.mention}\n"
              f"**Previous Level:** {old_level}\n"
              f"**New Level:** {level}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def demotelevel(ctx, member: discord.Member, *, level):
    """Demote a player to a lower level"""
    if level not in LEVEL_REQUIREMENTS:
        await ctx.send(f"❌ Invalid level. Valid levels: {', '.join(LEVEL_REQUIREMENTS.keys())}")
        return
    
    player_data = get_player_data(member.id)
    old_level = player_data['level']
    player_data['level'] = level
    player_data['form'] = max(0, player_data['form'] - 10)
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⬇️ Player Demoted", color=0xFF4500)
    embed.add_field(
        name="Demotion Details",
        value=f"**Player:** {member.mention}\n"
              f"**Previous Level:** {old_level}\n"
              f"**New Level:** {level}\n"
              f"**Form Impact:** -{10}%",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def stars(ctx, member: discord.Member, stars: int):
    """Set a player's star rating (1-5)"""
    if not 1 <= stars <= 5:
        await ctx.send("❌ Stars must be between 1 and 5!")
        return
    
    player_data = get_player_data(member.id)
    old_stars = player_data['stars']
    player_data['stars'] = stars
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⭐ Star Rating Updated", color=0xFFD700)
    embed.add_field(
        name="Rating Details",
        value=f"**Player:** {member.mention}\n"
              f"**Previous Stars:** {'⭐' * old_stars}\n"
              f"**New Stars:** {'⭐' * stars}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def rating(ctx, member: discord.Member, rating: int):
    """Set a player's overall rating (0-100)"""
    if not 0 <= rating <= 100:
        await ctx.send("❌ Rating must be between 0 and 100!")
        return
    
    player_data = get_player_data(member.id)
    old_rating = player_data['rating']
    player_data['rating'] = rating
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="📊 Player Rating Updated", color=0x4169E1)
    embed.add_field(
        name="Rating Details",
        value=f"**Player:** {member.mention}\n"
              f"**Previous Rating:** {old_rating}\n"
              f"**New Rating:** {rating}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def release(ctx, member: discord.Member, *, reason):
    """Release a player from the club"""
    player_data = get_player_data(member.id)
    player_data['registered'] = False
    player_data['level'] = 'Reserve'
    player_data['stars'] = 1
    update_player_data(member.id, player_data)
    
    # Remove roles
    try:
        roles_to_remove = [
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['official_player'])),
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['reserve'])),
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['substitution'])),
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['b_team'])),
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['a_team'])),
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['starting_7'])),
            discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['potw']))
        ]
        
        for role in roles_to_remove:
            if role and role in member.roles:
                await member.remove_roles(role)
    except:
        pass
    
    # Send DM to released player
    release_embed = discord.Embed(
        title="📋 Arsenal FC - Contract Termination",
        description="Your contract with Arsenal FC has been terminated.",
        color=0xFF0000
    )
    release_embed.add_field(
        name="Reason for Release",
        value=reason,
        inline=False
    )
    release_embed.add_field(
        name="Thank you",
        value="Thank you for your time with Arsenal FC. We wish you the best in your future endeavors.",
        inline=False
    )
    
    try:
        await member.send(embed=release_embed)
    except:
        pass
    
    embed = discord.Embed(title="📋 Player Released", color=0xFF0000)
    embed.add_field(
        name="Release Details",
        value=f"**Player:** {member.mention}\n"
              f"**Reason:** {reason}\n"
              f"**Status:** Released from club",
        inline=False
    )
    
    await ctx.send(embed=embed)

# DISCIPLINE SYSTEM
@bot.command()
@is_admin()
async def playerstrike(ctx, member: discord.Member, *, reason):
    """Give a strike to a player"""
    player_data = get_player_data(member.id)
    player_data['strikes'] += 1
    strikes = player_data['strikes']
    
    # Auto-demote at 3 strikes
    demoted = False
    if strikes >= 3:
        current_levels = list(LEVEL_REQUIREMENTS.keys())
        current_index = current_levels.index(player_data['level'])
        if current_index > 0:
            player_data['level'] = current_levels[current_index - 1]
            demoted = True
        player_data['strikes'] = 0  # Reset strikes after demotion
        player_data['form'] = max(0, player_data['form'] - 15)
    else:
        player_data['form'] = max(0, player_data['form'] - 5)
    
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⚠️ Strike Issued", color=0xFF4500)
    embed.add_field(
        name="Strike Details",
        value=f"**Player:** {member.mention}\n"
              f"**Reason:** {reason}\n"
              f"**Total Strikes:** {strikes if not demoted else 0}/3\n"
              f"**Form Impact:** -{5 if not demoted else 15}%",
        inline=False
    )
    
    if demoted:
        embed.add_field(
            name="🔻 Automatic Demotion",
            value=f"Player demoted to **{player_data['level']}** due to 3 strikes.\nStrikes reset to 0.",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def viewstrikes(ctx, member: discord.Member):
    """View a player's current strikes"""
    player_data = get_player_data(member.id)
    strikes = player_data['strikes']
    
    embed = discord.Embed(title="⚠️ Player Strikes", color=0xFFD700)
    embed.add_field(
        name="Strike Information",
        value=f"**Player:** {member.mention}\n"
              f"**Current Strikes:** {strikes}/3\n"
              f"**Status:** {'⚠️ Warning Zone' if strikes >= 2 else '✅ Good Standing'}",
        inline=False
    )
    
    if strikes >= 2:
        embed.add_field(
            name="⚠️ Warning",
            value="One more strike will result in automatic demotion!",
            inline=False
        )
    
    await ctx.send(embed=embed)

# STATISTICS SYSTEM
@bot.command()
async def stats(ctx, member: discord.Member):
    """View a player's comprehensive statistics"""
    player_data = get_player_data(member.id)
    stats = player_data['stats']
    
    embed = discord.Embed(
        title=f"📊 {member.display_name}'s Statistics",
        color=0x4169E1
    )
    
    # Offensive stats
    embed.add_field(
        name="⚽ Offensive Stats",
        value=f"**Goals:** {stats['goals']}\n"
              f"**Assists:** {stats['assists']}\n"
              f"**Hat-tricks:** {stats['hattricks']}\n"
              f"**Shots Taken:** {stats['shots_taken']}\n"
              f"**Shots on Target:** {stats['shots_on_target']}\n"
              f"**Penalties Scored:** {stats['penalties_scored']}",
        inline=True
    )
    
    # Passing & Technical
    embed.add_field(
        name="🎯 Passing & Technical",
        value=f"**Passes:** {stats['passes']}\n"
              f"**Key Passes:** {stats['key_passes']}\n"
              f"**Dribbles Completed:** {stats['dribbles_completed']}\n"
              f"**Dribbles Failed:** {stats['dribbles_failed']}\n",
        inline=True
    )
    
    # Defensive stats
    embed.add_field(
        name="🛡️ Defensive Stats",
        value=f"**Tackles:** {stats['tackles']}\n"
              f"**Interceptions:** {stats['interceptions']}\n"
              f"**Clean Sheets:** {stats['clean_sheets']}\n"
              f"**Saves:** {stats['saves']}",
        inline=True
    )
    
    # Discipline & Appearances
    embed.add_field(
        name="📋 Record",
        value=f"**Appearances:** {stats['appearances']}\n"
              f"**POTWs:** {stats['potws']}\n"
              f"**Yellow Cards:** {stats['yellow_cards']}\n"
              f"**Red Cards:** {stats['red_cards']}",
        inline=True
    )
    
    # Calculate some advanced stats
    shot_accuracy = (stats['shots_on_target'] / stats['shots_taken'] * 100) if stats['shots_taken'] > 0 else 0
    dribble_success = (stats['dribbles_completed'] / (stats['dribbles_completed'] + stats['dribbles_failed']) * 100) if (stats['dribbles_completed'] + stats['dribbles_failed']) > 0 else 0
    
    embed.add_field(
        name="📈 Advanced Stats",
        value=f"**Shot Accuracy:** {shot_accuracy:.1f}%\n"
              f"**Dribble Success:** {dribble_success:.1f}%\n"
              f"**Goals per Appearance:** {stats['goals'] / stats['appearances']:.2f}" if stats['appearances'] > 0 else "**Goals per Appearance:** 0.00",
        inline=True
    )
    
    embed.set_footer(text=f"⭐ Rating: {player_data['rating']}/100 | Form: {player_data['form']}% | Level: {player_data['level']}")
    
    await ctx.send(embed=embed)

# ENHANCED STATISTICS SYSTEM (15+ Commands)
@bot.command()
@is_admin()
async def goals(ctx, member: discord.Member, amount: int):
    """Add goals to a player's stats"""
    player_data = get_player_data(member.id)
    old_goals = player_data['stats']['goals']
    player_data['stats']['goals'] += amount
    if amount > 0:
        player_data['form'] = min(100, player_data['form'] + 2)
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⚽ Goals Updated", color=0x00FF00)
    embed.add_field(
        name="Goal Scorer Stats",
        value=f"**Player:** {member.mention}\n"
              f"**Goals Added:** +{amount}\n"
              f"**Total Goals:** {old_goals} → {player_data['stats']['goals']}\n"
              f"**Form Boost:** +{2 if amount > 0 else 0}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def assists(ctx, member: discord.Member, amount: int):
    """Add assists to a player's stats"""
    player_data = get_player_data(member.id)
    old_assists = player_data['stats']['assists']
    player_data['stats']['assists'] += amount
    if amount > 0:
        player_data['form'] = min(100, player_data['form'] + 2)
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🎯 Assists Updated", color=0x32CD32)
    embed.add_field(
        name="Playmaker Stats",
        value=f"**Player:** {member.mention}\n"
              f"**Assists Added:** +{amount}\n"
              f"**Total Assists:** {old_assists} → {player_data['stats']['assists']}\n"
              f"**Form Boost:** +{2 if amount > 0 else 0}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def hattricks(ctx, member: discord.Member, amount: int):
    """Add hat-tricks to a player's stats"""
    player_data = get_player_data(member.id)
    old_hattricks = player_data['stats']['hattricks']
    player_data['stats']['hattricks'] += amount
    if amount > 0:
        player_data['form'] = min(100, player_data['form'] + 5)  # Major form boost
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🔥 Hat-tricks Updated", color=0xFFD700)
    embed.add_field(
        name="Elite Performance",
        value=f"**Player:** {member.mention}\n"
              f"**Hat-tricks Added:** +{amount}\n"
              f"**Total Hat-tricks:** {old_hattricks} → {player_data['stats']['hattricks']}\n"
              f"**Form Boost:** +{5 if amount > 0 else 0}% (Major boost!)",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def appearances(ctx, member: discord.Member, amount: int):
    """Add appearances to a player's stats"""
    player_data = get_player_data(member.id)
    old_appearances = player_data['stats']['appearances']
    player_data['stats']['appearances'] += amount
    if amount > 0:
        player_data['form'] = min(100, player_data['form'] + 1)
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="📋 Appearances Updated", color=0x4169E1)
    embed.add_field(
        name="Match Participation",
        value=f"**Player:** {member.mention}\n"
              f"**Appearances Added:** +{amount}\n"
              f"**Total Appearances:** {old_appearances} → {player_data['stats']['appearances']}\n"
              f"**Form Impact:** +{1 if amount > 0 else 0}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def shotstaken(ctx, member: discord.Member, amount: int):
    """Add shots taken to a player's stats"""
    player_data = get_player_data(member.id)
    old_shots = player_data['stats']['shots_taken']
    player_data['stats']['shots_taken'] += amount
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🎯 Shots Taken Updated", color=0xFF6347)
    embed.add_field(
        name="Shooting Stats",
        value=f"**Player:** {member.mention}\n"
              f"**Shots Added:** +{amount}\n"
              f"**Total Shots:** {old_shots} → {player_data['stats']['shots_taken']}",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def shotsontarget(ctx, member: discord.Member, amount: int):
    """Add shots on target to a player's stats"""
    player_data = get_player_data(member.id)
    old_shots_target = player_data['stats']['shots_on_target']
    player_data['stats']['shots_on_target'] += amount
    update_player_data(member.id, player_data)
    
    # Calculate accuracy
    accuracy = (player_data['stats']['shots_on_target'] / player_data['stats']['shots_taken'] * 100) if player_data['stats']['shots_taken'] > 0 else 0
    
    embed = discord.Embed(title="🎯 Shots on Target Updated", color=0x00CED1)
    embed.add_field(
        name="Shooting Accuracy",
        value=f"**Player:** {member.mention}\n"
              f"**Shots on Target Added:** +{amount}\n"
              f"**Total Shots on Target:** {old_shots_target} → {player_data['stats']['shots_on_target']}\n"
              f"**Shooting Accuracy:** {accuracy:.1f}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def penaltiesscored(ctx, member: discord.Member, amount: int):
    """Add penalties scored to a player's stats"""
    player_data = get_player_data(member.id)
    old_penalties = player_data['stats']['penalties_scored']
    player_data['stats']['penalties_scored'] += amount
    if amount > 0:
        player_data['form'] = min(100, player_data['form'] + 1)
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🥅 Penalties Scored Updated", color=0x8FBC8F)
    embed.add_field(
        name="Penalty Specialist",
        value=f"**Player:** {member.mention}\n"
              f"**Penalties Added:** +{amount}\n"
              f"**Total Penalties:** {old_penalties} → {player_data['stats']['penalties_scored']}\n"
              f"**Form Boost:** +{1 if amount > 0 else 0}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def passes(ctx, member: discord.Member, amount: int):
    """Add passes to a player's stats"""
    player_data = get_player_data(member.id)
    old_passes = player_data['stats']['passes']
    player_data['stats']['passes'] += amount
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⚽ Passes Updated", color=0x9370DB)
    embed.add_field(
        name="Passing Stats",
        value=f"**Player:** {member.mention}\n"
              f"**Passes Added:** +{amount}\n"
              f"**Total Passes:** {old_passes} → {player_data['stats']['passes']}",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def keypasses(ctx, member: discord.Member, amount: int):
    """Add key passes to a player's stats"""
    player_data = get_player_data(member.id)
    old_key_passes = player_data['stats']['key_passes']
    player_data['stats']['key_passes'] += amount
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🗝️ Key Passes Updated", color=0xDAA520)
    embed.add_field(
        name="Creative Passing",
        value=f"**Player:** {member.mention}\n"
              f"**Key Passes Added:** +{amount}\n"
              f"**Total Key Passes:** {old_key_passes} → {player_data['stats']['key_passes']}",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def dribblescompleted(ctx, member: discord.Member, amount: int):
    """Add completed dribbles to a player's stats"""
    player_data = get_player_data(member.id)
    old_dribbles = player_data['stats']['dribbles_completed']
    player_data['stats']['dribbles_completed'] += amount
    update_player_data(member.id, player_data)
    
    # Calculate dribble success rate
    total_dribbles = player_data['stats']['dribbles_completed'] + player_data['stats']['dribbles_failed']
    success_rate = (player_data['stats']['dribbles_completed'] / total_dribbles * 100) if total_dribbles > 0 else 0
    
    embed = discord.Embed(title="🏃 Dribbles Completed Updated", color=0xFF1493)
    embed.add_field(
        name="Dribbling Skills",
        value=f"**Player:** {member.mention}\n"
              f"**Dribbles Added:** +{amount}\n"
              f"**Total Completed:** {old_dribbles} → {player_data['stats']['dribbles_completed']}\n"
              f"**Success Rate:** {success_rate:.1f}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def dribblesfailed(ctx, member: discord.Member, amount: int):
    """Add failed dribbles to a player's stats"""
    player_data = get_player_data(member.id)
    old_failed = player_data['stats']['dribbles_failed']
    player_data['stats']['dribbles_failed'] += amount
    update_player_data(member.id, player_data)
    
    total_dribbles = player_data['stats']['dribbles_completed'] + player_data['stats']['dribbles_failed']
    success_rate = (player_data['stats']['dribbles_completed'] / total_dribbles * 100) if total_dribbles > 0 else 0
    
    embed = discord.Embed(title="💨 Dribbles Failed Updated", color=0xFF6347)
    embed.add_field(
        name="Dribbling Analysis",
        value=f"**Player:** {member.mention}\n"
              f"**Failed Dribbles Added:** +{amount}\n"
              f"**Total Failed:** {old_failed} → {player_data['stats']['dribbles_failed']}\n"
              f"**Success Rate:** {success_rate:.1f}%",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def tackles(ctx, member: discord.Member, amount: int):
    """Add tackles to a player's stats"""
    player_data = get_player_data(member.id)
    old_tackles = player_data['stats']['tackles']
    player_data['stats']['tackles'] += amount
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🛡️ Tackles Updated", color=0x2E8B57)
    embed.add_field(
        name="Defensive Stats",
        value=f"**Player:** {member.mention}\n"
              f"**Tackles Added:** +{amount}\n"
              f"**Total Tackles:** {old_tackles} → {player_data['stats']['tackles']}",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def interceptions(ctx, member: discord.Member, amount: int):
    """Add interceptions to a player's stats"""
    player_data = get_player_data(member.id)
    old_interceptions = player_data['stats']['interceptions']
    player_data['stats']['interceptions'] += amount
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🔍 Interceptions Updated", color=0x4682B4)
    embed.add_field(
        name="Ball Recovery",
        value=f"**Player:** {member.mention}\n"
              f"**Interceptions Added:** +{amount}\n"
              f"**Total Interceptions:** {old_interceptions} → {player_data['stats']['interceptions']}",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def cleansheets(ctx, member: discord.Member, amount: int):
    """Add clean sheets to a player's stats"""
    player_data = get_player_data(member.id)
    old_cleansheets = player_data['stats']['clean_sheets']
    player_data['stats']['clean_sheets'] += amount
    if amount > 0:
        player_data['form'] = min(100, player_data['form'] + 3)  # Goalkeeper/defender boost
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🥅 Clean Sheets Updated", color=0x00FF7F)
    embed.add_field(
        name="Defensive Excellence",
        value=f"**Player:** {member.mention}\n"
              f"**Clean Sheets Added:** +{amount}\n"
              f"**Total Clean Sheets:** {old_cleansheets} → {player_data['stats']['clean_sheets']}\n"
              f"**Form Boost:** +{3 if amount > 0 else 0}% (Major defensive boost!)",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def saves(ctx, member: discord.Member, amount: int):
    """Add saves to a player's stats"""
    player_data = get_player_data(member.id)
    old_saves = player_data['stats']['saves']
    player_data['stats']['saves'] += amount
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="🧤 Saves Updated", color=0xFFD700)
    embed.add_field(
        name="Goalkeeper Stats",
        value=f"**Player:** {member.mention}\n"
              f"**Saves Added:** +{amount}\n"
              f"**Total Saves:** {old_saves} → {player_data['stats']['saves']}",
        inline=False
    )
    await ctx.send(embed=embed)

# STAT REMOVAL SYSTEM
@bot.command()
@is_admin()
async def remove(ctx, stat_name: str, member: discord.Member, amount: int):
    """Remove any statistic from a player"""
    player_data = get_player_data(member.id)
    
    # Map common stat names to database keys
    stat_mapping = {
        'goals': 'goals',
        'assists': 'assists', 
        'hattricks': 'hattricks',
        'hatricks': 'hattricks',  # Common misspelling
        'shotstaken': 'shots_taken',
        'shotsontarget': 'shots_on_target',
        'penaltiesscored': 'penalties_scored',
        'passes': 'passes',
        'keypasses': 'key_passes',
        'dribblescompleted': 'dribbles_completed',
        'dribblesfailed': 'dribbles_failed',
        'tackles': 'tackles',
        'interceptions': 'interceptions',
        'cleansheets': 'clean_sheets',
        'saves': 'saves',
        'yellowcards': 'yellow_cards',
        'redcards': 'red_cards',
        'appearances': 'appearances',
        'potws': 'potws'
    }
    
    stat_key = stat_mapping.get(stat_name.lower())
    if not stat_key:
        embed = discord.Embed(title="❌ Invalid Statistic", color=0xFF0000)
        embed.add_field(
            name="Available Statistics",
            value="goals, assists, hattricks, shotstaken, shotsontarget, penaltiesscored, "
                  "passes, keypasses, dribblescompleted, dribblesfailed, tackles, "
                  "interceptions, cleansheets, saves, yellowcards, redcards, appearances, potws",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    old_value = player_data['stats'][stat_key]
    player_data['stats'][stat_key] = max(0, old_value - amount)
    
    # Form impact for removing positive stats
    form_change = 0
    if amount > 0 and stat_key in ['goals', 'assists', 'hattricks', 'cleansheets', 'penalties_scored']:
        form_change = -2 if stat_key == 'hattricks' else -1
        player_data['form'] = max(0, player_data['form'] + form_change)
    
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="📉 Statistic Removed", color=0xFF4500)
    embed.add_field(
        name="Statistics Update",
        value=f"**Player:** {member.mention}\n"
              f"**Statistic:** {stat_name.title()}\n" 
              f"**Amount Removed:** -{amount}\n"
              f"**Previous Total:** {old_value}\n"
              f"**New Total:** {player_data['stats'][stat_key]}\n"
              f"**Form Impact:** {form_change}%" if form_change != 0 else f"**Form Impact:** No change",
        inline=False
    )
    await ctx.send(embed=embed)
    
    # Auto-demotion at 3 strikes
    demoted = False
    if strikes >= 3:
        current_levels = list(LEVEL_REQUIREMENTS.keys())
        current_index = current_levels.index(player_data['level'])
        if current_index > 0:
            old_level = player_data['level']
            new_level = current_levels[current_index - 1]
            player_data['level'] = new_level
            demoted = True
            
            # Remove all level roles and add new one
            try:
                for level in current_levels:
                    level_role_id = ROLE_IDS.get(level.lower().replace(' ', '_'))
                    if level_role_id:
                        role = discord.utils.get(guild.roles, id=int(level_role_id))
                        if role and role in member.roles:
                            await member.remove_roles(role)
                
                new_role_id = ROLE_IDS.get(new_level.lower().replace(' ', '_'))
                if new_role_id:
                    new_role = discord.utils.get(guild.roles, id=int(new_role_id))
                    if new_role:
                        await member.add_roles(new_role)
            except:
                pass
        
        player_data['strikes'] = 0  # Reset after demotion
        player_data['form'] = max(0, player_data['form'] - 20)
    else:
        player_data['form'] = max(0, player_data['form'] - 10)
    
    update_player_data(member.id, player_data)
    
    embed = discord.Embed(title="⚠️ DISCIPLINARY ACTION", color=0xFF4500)
    embed.add_field(
        name="Strike Details",
        value=f"**Player:** {member.mention}\n"
              f"**Reason:** {reason}\n"
              f"**Strikes:** {strikes if not demoted else 0}/3\n"
              f"**Form Impact:** -{10 if not demoted else 20}%",
        inline=False
    )
    
    if demoted:
        embed.add_field(
            name="🔻 AUTOMATIC DEMOTION",
            value=f"**Previous Level:** {old_level}\n"
                  f"**New Level:** {new_level}\n"
                  f"**Status:** Strikes reset to 0",
            inline=False
        )
    
    embed.set_footer(text="Arsenal FC Disciplinary System")
    await ctx.send(embed=embed)

# STAFF HELP COMMAND
@bot.command()
async def staffhelp(ctx):
    """Professional staff moderation panel"""
    # Check if user has any staff role
    staff_roles = ['trial_staff', 'staff', 'senior_staff', 'head_of_staff', 'head_of_discipline', 
                   'head_of_tactics', 'executive_coordinator', 'community_manager', 'overseer']
    
    has_staff_role = False
    try:
        for role_key in staff_roles:
            role_id = STAFF_ROLES.get(role_key)
            if role_id:
                role = discord.utils.get(ctx.guild.roles, id=int(role_id))
                if role and role in ctx.author.roles:
                    has_staff_role = True
                    break
    except:
        pass
    
    if not has_staff_role and not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ This command is restricted to Arsenal FC staff members.")
        return
    
    embed = discord.Embed(
        title="🛡️ ARSENAL FC - STAFF CONTROL PANEL",
        description="**Professional Moderation & Management Tools**\n🔴 *Staff Excellence Initiative* 🔴",
        color=0x800080
    )
    
    embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
    
    embed.add_field(
        name="👥 **PLAYER MODERATION** (5 commands)",
        value="`!viewstrikes @user` - Check player disciplinary record\n"
              "`!warn @user <reason>` - Issue formal warning\n"
              "`!timeout @user <minutes> <reason>` - Temporary timeout\n"
              "`!mute @user <reason>` - Mute disruptive player\n"
              "`!unmute @user` - Remove mute from player",
        inline=False
    )
    
    embed.add_field(
        name="📋 **LEAVE MANAGEMENT** (3 commands)",
        value="`!loa <reason> <return_date>` - Request Leave of Absence\n"
              "`!staffschedule` - View staff schedules\n"
              "`!coverage @staff_member` - Request coverage",
        inline=False
    )
    
    embed.add_field(
        name="🏆 **AWARDS & RECOGNITION** (4 commands)",
        value="`!sotw @user <reason>` - Staff of the Week award\n"
              "`!commendation @user <reason>` - Staff commendation\n"
              "`!staffmotm @user` - Staff Member of the Month\n"
              "`!recognize @user <achievement>` - General recognition",
        inline=False
    )
    
    embed.add_field(
        name="📊 **REPORTING & ANALYTICS** (3 commands)",
        value="`!staffreport` - Generate activity report\n"
              "`!incidentreport <details>` - Report incidents\n"
              "`!staffstats` - View staff performance metrics",
        inline=False
    )
    
    embed.set_footer(
        text="🛡️ Staff Excellence | Use professional judgment in all decisions",
        icon_url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png"
    )
    
    await ctx.send(embed=embed)

# LEAVE OF ABSENCE SYSTEM
class LOAApprovalView(discord.ui.View):
    def __init__(self, user, reason, return_date):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.user = user
        self.reason = reason
        self.return_date = return_date
    
    @discord.ui.button(label="✅ Approve LOA", style=discord.ButtonStyle.success)
    async def approve_loa(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Add LOA role
        try:
            loa_role = discord.utils.get(interaction.guild.roles, id=int(SPECIAL_ROLES['loa']))
            if loa_role:
                await self.user.add_roles(loa_role)
        except:
            pass
        
        embed = discord.Embed(
            title="✅ LEAVE OF ABSENCE APPROVED",
            color=0x00FF00
        )
        embed.add_field(
            name="LOA Details",
            value=f"**Staff Member:** {self.user.mention}\n"
                  f"**Reason:** {self.reason}\n"
                  f"**Return Date:** {self.return_date}\n"
                  f"**Approved By:** {interaction.user.mention}\n"
                  f"**Status:** Active LOA",
            inline=False
        )
        
        # Send DM to staff member
        try:
            dm_embed = discord.Embed(
                title="✅ LEAVE OF ABSENCE APPROVED",
                description="Your Leave of Absence request has been approved.",
                color=0x00FF00
            )
            dm_embed.add_field(
                name="Details",
                value=f"**Return Date:** {self.return_date}\n"
                      f"**Reason:** {self.reason}\n"
                      f"**Notes:** Enjoy your time off. Contact management if plans change.",
                inline=False
            )
            await self.user.send(embed=dm_embed)
        except:
            pass
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="❌ Deny LOA", style=discord.ButtonStyle.danger)
    async def deny_loa(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ LEAVE OF ABSENCE DENIED",
            color=0xFF0000
        )
        embed.add_field(
            name="LOA Request Denied",
            value=f"**Staff Member:** {self.user.mention}\n"
                  f"**Denied By:** {interaction.user.mention}\n"
                  f"**Status:** Please discuss with management",
            inline=False
        )
        
        try:
            dm_embed = discord.Embed(
                title="❌ LEAVE OF ABSENCE DENIED",
                description="Your Leave of Absence request has been denied.",
                color=0xFF0000
            )
            dm_embed.add_field(
                name="Next Steps",
                value="Please contact senior management to discuss your request further.",
                inline=False
            )
            await self.user.send(embed=dm_embed)
        except:
            pass
        
        await interaction.response.edit_message(embed=embed, view=None)

@bot.command()
@is_admin()
async def demotestaff(ctx, member: discord.Member, from_role: str, *, reason):
    """Demote staff member"""
    role_key = from_role.lower().replace(' ', '_')
    
    try:
        # Remove the specified role
        old_role = discord.utils.get(ctx.guild.roles, id=int(STAFF_ROLES.get(role_key, '')))
        if old_role and old_role in member.roles:
            await member.remove_roles(old_role)
    except:
        pass
    
    # Send notification DM
    demo_embed = discord.Embed(
        title="📉 STAFF POSITION CHANGE - ARSENAL FC",
        description="Your staff position has been modified.",
        color=0xFF4500
    )
    
    demo_embed.add_field(
        name="📋 CHANGE DETAILS",
        value=f"**Previous Position:** {from_role.title()}\n"
              f"**Reason:** {reason}\n"
              f"**Effective:** Immediately\n"
              f"**Changed By:** Arsenal FC Management",
        inline=False
    )
    
    try:
        await member.send(embed=demo_embed)
        await ctx.send(f"📉 {member.mention} has been demoted from **{from_role.title()}**")
    except:
        await ctx.send(f"📉 {member.mention} has been demoted from **{from_role.title()}**")

@bot.command()
@is_admin()
async def allstats(ctx):
    """View all available stat commands for admins"""
    embed = discord.Embed(
        title="📊 All Statistics Commands",
        description="Complete list of statistical commands available to admins",
        color=0x4169E1
    )
    
    embed.add_field(
        name="⚽ Offensive Stats",
        value="`!goals <user> <number>`\n"
              "`!assists <user> <number>`\n"
              "`!hattricks <user> <number>`\n"
              "`!shotstaken <user> <number>`\n"
              "`!shotsontarget <user> <number>`\n"
              "`!penaltiesscored <user> <number>`",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Passing & Technical",
        value="`!passes <user> <number>`\n"
              "`!keypasses <user> <number>`\n"
              "`!dribblescompleted <user> <number>`\n"
              "`!dribblesfailed <user> <number>`",
        inline=True
    )
    
    embed.add_field(
        name="🛡️ Defensive Stats",
        value="`!tackles <user> <number>`\n"
              "`!interceptions <user> <number>`\n"
              "`!cleansheets <user> <number>`\n"
              "`!saves <user> <number>`",
        inline=True
    )
    
    embed.add_field(
        name="📋 Discipline & Awards",
        value="`!potws <user> <number>`\n"
              "`!yellowcards <user> <number>`\n"
              "`!redcards <user> <number>`",
        inline=True
    )
    
    embed.add_field(
        name="📝 Usage Guide",
        value="**Format:** `!statname @user amount`\n"
              "**Example:** `!goals @player 3`\n"
              "**Tip:** Use positive numbers to add, negative to subtract",
        inline=False
    )
    
    embed.set_footer(text="💡 These commands are admin-only and affect player statistics and form!")
    
    await ctx.send(embed=embed)

# PLAYER INFO AND DOCUMENTS
@bot.command()
@is_admin()
async def info(ctx, member: discord.Member):
    """View detailed player information (Admin only)"""
    player_data = get_player_data(member.id)
    stats = player_data['stats']
    
    embed = discord.Embed(
        title=f"📋 {member.display_name}'s Player Information",
        color=0x4169E1
    )
    
    # Basic info
    embed.add_field(
        name="👤 Basic Information",
        value=f"**Level:** {player_data['level']}\n"
              f"**Points:** {player_data['points']}\n"
              f"**Stars:** {'⭐' * player_data['stars']}\n"
              f"**Position:** {player_data['position']}\n"
              f"**Rating:** {player_data['rating']}/100\n"
              f"**Form:** {player_data['form']}%",
        inline=True
    )
    
    # Contract & discipline
    embed.add_field(
        name="📋 Contract & Discipline",
        value=f"**Contract:** {player_data['contract_years']} years\n"
              f"**Registered:** {'✅' if player_data['registered'] else '❌'}\n"
              f"**Strikes:** {player_data['strikes']}/3\n"
              f"**Appearances:** {stats['appearances']}",
        inline=True
    )
    
    # Performance ratings
    avg_performance = sum(player_data['performance_ratings']) / len(player_data['performance_ratings']) if player_data['performance_ratings'] else 0
    embed.add_field(
        name="📈 Performance",
        value=f"**Average Performance:** {avg_performance:.1f}/10\n"
              f"**Total Analyses:** {len(player_data['performance_ratings'])}\n"
              f"**Goals:** {stats['goals']}\n"
              f"**Assists:** {stats['assists']}",
        inline=True
    )
    
    embed.set_footer(text=f"Player ID: {member.id}")
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def document(ctx, member: discord.Member):
    """View comprehensive player document/report"""
    player_data = get_player_data(member.id)
    stats = player_data['stats']
    
    embed = discord.Embed(
        title=f"📋 {member.display_name}'s Document/Report",
        description="**OFFICIAL ARSENAL FC PLAYER REPORT**",
        color=0xDC143C
    )
    
    # Personal Details
    embed.add_field(
        name="👤 Personal Details",
        value=f"**Name:** {member.display_name}\n"
              f"**Position:** {player_data['position']}\n"
              f"**Contract Length:** {player_data['contract_years']} years\n"
              f"**Member Since:** {member.joined_at.strftime('%Y-%m-%d') if member.joined_at else 'Unknown'}",
        inline=True
    )
    
    # Current Status
    embed.add_field(
        name="📊 Current Status",
        value=f"**Level:** {player_data['level']}\n"
              f"**Points:** {player_data['points']}\n"
              f"**Star Rating:** {'⭐' * player_data['stars']}\n"
              f"**Overall Rating:** {player_data['rating']}/100\n"
              f"**Current Form:** {player_data['form']}%",
        inline=True
    )
    
    # Performance Record
    avg_performance = sum(player_data['performance_ratings']) / len(player_data['performance_ratings']) if player_data['performance_ratings'] else 0
    embed.add_field(
        name="🏆 Performance Record",
        value=f"**Appearances:** {stats['appearances']}\n"
              f"**Goals:** {stats['goals']}\n"
              f"**Assists:** {stats['assists']}\n"
              f"**Average Match Rating:** {avg_performance:.1f}/10\n"
              f"**Hat-tricks:** {stats['hattricks']}\n"
              f"**POTWs:** {stats['potws']}",
        inline=True
    )
    
    # Discipline Record
    embed.add_field(
        name="⚠️ Discipline Record",
        value=f"**Current Strikes:** {player_data['strikes']}/3\n"
              f"**Yellow Cards:** {stats['yellow_cards']}\n"
              f"**Red Cards:** {stats['red_cards']}\n"
              f"**Disciplinary Status:** {'⚠️ Warning' if player_data['strikes'] >= 2 else '✅ Good Standing'}",
        inline=True
    )
    
    # Technical Stats
    shot_accuracy = (stats['shots_on_target'] / stats['shots_taken'] * 100) if stats['shots_taken'] > 0 else 0
    dribble_success = (stats['dribbles_completed'] / (stats['dribbles_completed'] + stats['dribbles_failed']) * 100) if (stats['dribbles_completed'] + stats['dribbles_failed']) > 0 else 0
    
    embed.add_field(
        name="📈 Technical Analysis",
        value=f"**Shot Accuracy:** {shot_accuracy:.1f}%\n"
              f"**Dribble Success Rate:** {dribble_success:.1f}%\n"
              f"**Defensive Actions:** {stats['tackles'] + stats['interceptions']}\n"
              f"**Goals per Appearance:** {(stats['goals'] / stats['appearances']):.2f}" if stats['appearances'] > 0 else "**Goals per Appearance:** 0.00",
        inline=True
    )
    
    # Additional Notes
    form_status = "Excellent" if player_data['form'] >= 80 else "Good" if player_data['form'] >= 60 else "Average" if player_data['form'] >= 40 else "Poor"
    embed.add_field(
        name="📝 Additional Notes",
        value=f"**Form Status:** {form_status}\n"
              f"**Registered Status:** {'✅ Official Player' if player_data['registered'] else '❌ Not Registered'}\n"
              f"**Total Performance Reviews:** {len(player_data['performance_ratings'])}\n"
              f"**Clean Sheets:** {stats['clean_sheets']}",
        inline=True
    )
    
    embed.set_footer(text=f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Arsenal FC Management")
    
    await ctx.send(embed=embed)

# ROSTER MANAGEMENT
@bot.command()
async def roster(ctx):
    """View team roster organized by levels"""
    data = load_data()
    registered_players = {user_id: player_data for user_id, player_data in data.items() if player_data.get('registered', False)}
    
    if not registered_players:
        embed = discord.Embed(
            title="📋 Arsenal FC Roster",
            description="No players registered yet!",
            color=0xDC143C
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="📋 Arsenal FC Official Roster",
        description=f"**Total Players:** {len(registered_players)}",
        color=0xDC143C
    )
    
    # Group players by level
    levels = {}
    for user_id, player_data in registered_players.items():
        level = player_data['level']
        if level not in levels:
            levels[level] = []
        
        try:
            user = ctx.bot.get_user(int(user_id))
            if user:
                levels[level].append((user.display_name, player_data['points'], player_data['stars']))
        except:
            continue
    
    # Display each level
    for level in ['Starting 7', 'A Team', 'B Team', 'Substitution', 'Reserve']:
        if level in levels:
            players_text = ""
            for name, points, stars in sorted(levels[level], key=lambda x: x[1], reverse=True):
                stars_display = '⭐' * stars
                players_text += f"• **{name}** ({points} pts) {stars_display}\n"
            
            embed.add_field(
                name=f"🏆 {level} ({len(levels[level])} players)",
                value=players_text or "No players",
                inline=False
            )
    
    embed.set_footer(text="💡 Tip: Players are sorted by points within each level!")
    
    await ctx.send(embed=embed)

# LINEUP MANAGEMENT
@bot.command()
@is_admin()
async def lineup(ctx, p1: discord.Member, p2: discord.Member, p3: discord.Member, 
                p4: discord.Member, p5: discord.Member, p6: discord.Member, p7: discord.Member):
    """Set the starting lineup (7 players)"""
    lineup_players = [p1, p2, p3, p4, p5, p6, p7]
    
    trials = load_trials()
    trials['current_lineup'] = [p.id for p in lineup_players]
    save_trials(trials)
    
    embed = discord.Embed(
        title="⚽ Arsenal FC Starting Lineup",
        description="**Official Starting 7 for the next match**",
        color=0xDC143C
    )
    
    lineup_text = ""
    for i, player in enumerate(lineup_players, 1):
        player_data = get_player_data(player.id)
        lineup_text += f"**{i}.** {player.mention} ({player_data['position']}) - {player_data['level']}\n"
    
    embed.add_field(
        name="🏆 Starting XI",
        value=lineup_text,
        inline=False
    )
    
    embed.set_footer(text="Good luck team! 🔴")
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def leaguematchdone(ctx):
    """Mark league match as complete and update appearances"""
    trials = load_trials()
    current_lineup = trials.get('current_lineup', [])
    
    if not current_lineup:
        await ctx.send("❌ No lineup set! Use `!lineup` first.")
        return
    
    updated_players = []
    for user_id in current_lineup:
        player_data = get_player_data(user_id)
        player_data['stats']['appearances'] += 1
        update_player_data(user_id, player_data)
        
        user = ctx.bot.get_user(user_id)
        if user:
            updated_players.append(user.display_name)
    
    embed = discord.Embed(
        title="✅ League Match Complete",
        description=f"Appearances updated for {len(updated_players)} players",
        color=0x00FF00
    )
    
    embed.add_field(
        name="📊 Updated Players",
        value="\n".join(f"• {name}" for name in updated_players),
        inline=False
    )
    
    embed.set_footer(text="Match statistics recorded!")
    
    await ctx.send(embed=embed)

# PERFORMANCE ANALYSIS
@bot.command()
@is_admin()
async def analysis(ctx, member: discord.Member, rating: int, *, analysis_text):
    """Provide performance analysis for a player"""
    if not 0 <= rating <= 10:
        await ctx.send("❌ Performance rating must be between 0 and 10!")
        return
    
    player_data = get_player_data(member.id)
    player_data['performance_ratings'].append(rating)
    
    # Update form based on performance
    if rating >= 8:
        player_data['form'] = min(100, player_data['form'] + 5)
    elif rating >= 6:
        player_data['form'] = min(100, player_data['form'] + 2)
    elif rating <= 3:
        player_data['form'] = max(0, player_data['form'] - 5)
    
    update_player_data(member.id, player_data)
    
    performance_level = get_performance_level(rating)
    
    embed = discord.Embed(
        title="📊 Player Performance Analysis",
        color=0x00FF00 if rating >= 7 else 0xFFD700 if rating >= 5 else 0xFF4500
    )
    
    embed.add_field(
        name="👤 Player",
        value=member.mention,
        inline=True
    )
    
    embed.add_field(
        name="📈 Performance Rating",
        value=f"{rating}/10 - **{performance_level}**",
        inline=True
    )
    
    embed.add_field(
        name="📊 Form Impact",
        value=f"Current Form: {player_data['form']}%",
        inline=True
    )
    
    embed.add_field(
        name="📝 Manager's Analysis",
        value=analysis_text,
        inline=False
    )
    
    avg_rating = sum(player_data['performance_ratings']) / len(player_data['performance_ratings'])
    embed.add_field(
        name="📊 Season Average",
        value=f"{avg_rating:.1f}/10 ({len(player_data['performance_ratings'])} reviews)",
        inline=False
    )
    
    embed.set_footer(text="Analysis recorded in player's development file.")
    
    await ctx.send(embed=embed)

# TACTICS SYSTEM
class TacticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.select(
        placeholder="Choose formation...",
        options=[
            discord.SelectOption(label="4-3-3", value="4-3-3", emoji="⚽"),
            discord.SelectOption(label="4-4-2", value="4-4-2", emoji="⚽"),
            discord.SelectOption(label="3-5-2", value="3-5-2", emoji="⚽"),
            discord.SelectOption(label="4-2-3-1", value="4-2-3-1", emoji="⚽"),
            discord.SelectOption(label="3-4-3", value="3-4-3", emoji="⚽"),
            discord.SelectOption(label="5-3-2", value="5-3-2", emoji="⚽"),
        ]
    )
    async def formation_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.formation = select.values[0]
        await interaction.response.defer()
        
    @discord.ui.select(
        placeholder="Choose playing style...",
        options=[
            discord.SelectOption(label="Attacking", value="Attacking", emoji="⚡"),
            discord.SelectOption(label="Defensive", value="Defensive", emoji="🛡️"),
            discord.SelectOption(label="Possession", value="Possession", emoji="🎯"),
            discord.SelectOption(label="Counter Attack", value="Counter Attack", emoji="🏃"),
            discord.SelectOption(label="High Press", value="High Press", emoji="🔥"),
            discord.SelectOption(label="Tiki-Taka", value="Tiki-Taka", emoji="🎨"),
        ]
    )
    async def style_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.style = select.values[0]
        await interaction.response.defer()
        
    @discord.ui.button(label="💾 Save Tactics", style=discord.ButtonStyle.success)
    async def save_tactics(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not hasattr(self, 'formation') or not hasattr(self, 'style'):
            await interaction.response.send_message("❌ Please select both formation and style first!", ephemeral=True)
            return
            
        # Ask for instructions via modal
        modal = TacticsModal(self.formation, self.style)
        await interaction.response.send_modal(modal)

class TacticsModal(discord.ui.Modal):
    def __init__(self, formation, style):
        super().__init__(title="Tactical Instructions")
        self.formation = formation
        self.style = style
        
        self.instructions = discord.ui.TextInput(
            label="Tactical Instructions",
            placeholder="Enter detailed tactical instructions for the team...",
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        self.add_item(self.instructions)
    
    async def on_submit(self, interaction: discord.Interaction):
        tactics = {
            'formation': self.formation,
            'style': self.style,
            'instructions': self.instructions.value
        }
        save_tactics(tactics)
        
        embed = discord.Embed(
            title="✅ Tactics Updated",
            description="Team tactics have been successfully updated!",
            color=0x00FF00
        )
        
        embed.add_field(name="Formation", value=self.formation, inline=True)
        embed.add_field(name="Style", value=self.style, inline=True)
        embed.add_field(name="Instructions", value=self.instructions.value, inline=False)
        
        await interaction.response.send_message(embed=embed)

@bot.command()
@is_admin()
async def tactics(ctx):
    """Interactive tactics management"""
    embed = discord.Embed(
        title="⚙️ Arsenal FC Tactics Manager",
        description="Configure team formation, style, and instructions",
        color=0x4169E1
    )
    
    current_tactics = load_tactics()
    embed.add_field(
        name="📋 Current Tactics",
        value=f"**Formation:** {current_tactics['formation']}\n"
              f"**Style:** {current_tactics['style']}\n"
              f"**Instructions:** {current_tactics['instructions']}",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Instructions",
        value="1. Select formation from the dropdown\n"
              "2. Choose playing style\n"
              "3. Click 'Save Tactics' to add instructions",
        inline=False
    )
    
    view = TacticsView()
    await ctx.send(embed=embed, view=view)

@bot.command()
@is_official_player()
async def currenttactics(ctx):
    """View current team tactics (Official players only)"""
    tactics = load_tactics()
    
    embed = discord.Embed(
        title="⚽ Arsenal FC Current Tactics",
        description="**Official Team Strategy**",
        color=0xDC143C
    )
    
    embed.add_field(
        name="📐 Formation",
        value=tactics['formation'],
        inline=True
    )
    
    embed.add_field(
        name="🎯 Playing Style",
        value=tactics['style'],
        inline=True
    )
    
    embed.add_field(
        name="📋 Tactical Instructions",
        value=tactics['instructions'],
        inline=False
    )
    
    embed.set_footer(text="💡 Study these tactics and be ready for the match!")
    
    await ctx.send(embed=embed)

# EVENTS SYSTEM (Trials, Training, Friendlies)
class EventView(discord.ui.View):
    def __init__(self, event_type, max_entries, channel_id):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.event_type = event_type
        self.max_entries = max_entries
        self.channel_id = channel_id
        self.entries = []
        
    @discord.ui.button(label="🚀 Enter", style=discord.ButtonStyle.success)
    async def enter_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        if user.id in self.entries:
            await interaction.response.send_message("❌ You're already entered!", ephemeral=True)
            return
            
        if len(self.entries) >= self.max_entries:
            await interaction.response.send_message("❌ Event is full!", ephemeral=True)
            return
            
        self.entries.append(user.id)
        
        embed = discord.Embed(
            title=f"🏆 Arsenal FC {self.event_type.title()}",
            description=f"**Entries:** {len(self.entries)}/{self.max_entries}",
            color=0xDC143C
        )
        
        if self.entries:
            participants = []
            guild = interaction.guild
            for user_id in self.entries:
                member = guild.get_member(user_id)
                if member:
                    participants.append(member.display_name)
            
            embed.add_field(
                name="👥 Participants",
                value="\n".join(f"• {name}" for name in participants),
                inline=False
            )
        
        embed.set_footer(text=f"Click 'Enter' to join the {self.event_type}!")
        
        # Send DM to participant
        try:
            dm_embed = discord.Embed(
                title=f"🏆 {self.event_type.title()} Confirmation",
                description=f"You've successfully entered the Arsenal FC {self.event_type}!",
                color=0x00FF00
            )
            dm_embed.add_field(
                name="📅 Event Details",
                value=f"**Type:** {self.event_type.title()}\n"
                      f"**Max Participants:** {self.max_entries}\n"
                      f"**Your Position:** #{len(self.entries)}",
                inline=False
            )
            dm_embed.set_footer(text="Good luck! 🔴")
            
            await user.send(embed=dm_embed)
        except:
            pass  # DMs disabled
        
        await interaction.response.edit_message(embed=embed, view=self)

@bot.command()
@is_admin()
async def trials(ctx, max_entries: int):
    """Start a trials event"""
    if max_entries <= 0:
        await ctx.send("❌ Max entries must be greater than 0!")
        return
    
    embed = discord.Embed(
        title="🏆 Arsenal FC Trials",
        description=f"**Max Entries:** {max_entries}\n**Current Entries:** 0/{max_entries}",
        color=0xDC143C
    )
    
    embed.add_field(
        name="ℹ️ Information",
        value="This is your chance to join Arsenal FC!\n"
              "Show your skills and earn a spot on the team.\n"
              "Click 'Enter' to participate!",
        inline=False
    )
    
    embed.set_footer(text="💡 Participants will receive a DM confirmation!")
    
    view = EventView("trials", max_entries, ctx.channel.id)
    await ctx.send(embed=embed, view=view)

@bot.command()
@is_admin()
async def training(ctx, max_entries: int):
    """Start a training session"""
    if max_entries <= 0:
        await ctx.send("❌ Max entries must be greater than 0!")
        return
    
    embed = discord.Embed(
        title="⚽ Arsenal FC Training Session",
        description=f"**Max Entries:** {max_entries}\n**Current Entries:** 0/{max_entries}",
        color=0x4169E1
    )
    
    embed.add_field(
        name="🎯 Training Focus",
        value="Improve your skills, fitness, and team chemistry!\n"
              "Attendance may earn you points and improve your form.\n"
              "Click 'Enter' to join the session!",
        inline=False
    )
    
    embed.set_footer(text="💡 Regular training attendance is expected!")
    
    view = EventView("training", max_entries, ctx.channel.id)
    await ctx.send(embed=embed, view=view)

@bot.command()
@is_admin()
async def friendly(ctx, max_entries: int):
    """Start a friendly match"""
    if max_entries <= 0:
        await ctx.send("❌ Max entries must be greater than 0!")
        return
    
    embed = discord.Embed(
        title="🤝 Arsenal FC Friendly Match",
        description=f"**Max Entries:** {max_entries}\n**Current Entries:** 0/{max_entries}",
        color=0x00FF00
    )
    
    embed.add_field(
        name="⚽ Match Information",
        value="Friendly match to practice tactics and build team spirit!\n"
              "No pressure, just pure football fun.\n"
              "Click 'Enter' to participate!",
        inline=False
    )
    
    embed.set_footer(text="💡 Friendlies are great for team bonding!")
    
    view = EventView("friendly", max_entries, ctx.channel.id)
    await ctx.send(embed=embed, view=view)

# POTW SYSTEM
@bot.command()
@is_admin()
async def potw(ctx, member: discord.Member):
    """Add a Player of the Week"""
    trials = load_trials()
    potw_list = trials.get('potw_players', [])
    
    if member.id not in potw_list:
        potw_list.append(member.id)
        trials['potw_players'] = potw_list
        save_trials(trials)
        
        # Update player stats
        player_data = get_player_data(member.id)
        player_data['stats']['potws'] += 1
        player_data['form'] = min(100, player_data['form'] + 10)
        update_player_data(member.id, player_data)
        
        # Add POTW role
        try:
            potw_role = discord.utils.get(ctx.guild.roles, id=int(ROLE_IDS['potw']))
            if potw_role:
                await member.add_roles(potw_role)
        except:
            pass
        
        embed = discord.Embed(
            title="🏆 Player of the Week Added!",
            description=f"**{member.mention}** has been named Player of the Week!",
            color=0xFFD700
        )
        
        embed.add_field(
            name="🎉 Congratulations!",
            value=f"**Total POTWs:** {player_data['stats']['potws']}\n"
                  f"**Form Boost:** +10% (Current: {player_data['form']}%)",
            inline=False
        )
        
        embed.set_footer(text="Excellent performance! Keep it up! 🔴")
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {member.mention} is already in the Team of the Week!")

@bot.command()
async def totw(ctx):
    """View Team of the Week"""
    trials = load_trials()
    potw_list = trials.get('potw_players', [])
    
    if not potw_list:
        embed = discord.Embed(
            title="🏆 Team of the Week",
            description="No players selected yet this week!",
            color=0xFFD700
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="🏆 Arsenal FC Team of the Week",
        description="Outstanding performers this week!",
        color=0xFFD700
    )
    
    potw_text = ""
    for i, user_id in enumerate(potw_list, 1):
        try:
            user = ctx.bot.get_user(user_id)
            if user:
                player_data = get_player_data(user_id)
                potw_text += f"**{i}.** {user.mention} ({player_data['level']}) - {player_data['stats']['potws']} POTWs\n"
        except:
            continue
    
    embed.add_field(
        name="⭐ Players of the Week",
        value=potw_text or "No players found",
        inline=False
    )
    
    embed.set_footer(text="💡 These players showed exceptional performance!")
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def announcelm(ctx, *, message):
    """Announce league match results"""
    embed = discord.Embed(
        title="⚽ League Match Announcement",
        description=message,
        color=0x00FF00
    )
    
    embed.add_field(
        name="📊 Performance Reviews",
        value="Check the #performances channel to see how you performed in this match!",
        inline=False
    )
    
    embed.set_footer(text="Arsenal FC Management | Check your individual performance analysis!")
    
    await ctx.send(embed=embed)

@bot.command()
@is_official_player()
async def suggestion(ctx, *, suggestion_text):
    """Make a suggestion (Official players only)"""
    trials = load_trials()
    suggestions = trials.get('suggestions', [])
    
    suggestion_data = {
        'user_id': ctx.author.id,
        'user_name': ctx.author.display_name,
        'suggestion': suggestion_text,
        'timestamp': datetime.now().isoformat()
    }
    
    suggestions.append(suggestion_data)
    trials['suggestions'] = suggestions
    save_trials(trials)
    
    embed = discord.Embed(
        title="💡 Suggestion Submitted",
        description="Thank you for your suggestion!",
        color=0x4169E1
    )
    
    embed.add_field(
        name="📝 Your Suggestion",
        value=suggestion_text,
        inline=False
    )
    
    embed.set_footer(text="Your suggestion has been recorded and will be reviewed by management.")
    
    await ctx.send(embed=embed)

@bot.command()
@is_admin()
async def suggestions(ctx):
    """View all player suggestions (Admin only)"""
    trials = load_trials()
    suggestions = trials.get('suggestions', [])
    
    if not suggestions:
        embed = discord.Embed(
            title="💡 Player Suggestions",
            description="No suggestions submitted yet!",
            color=0x4169E1
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="💡 Player Suggestions",
        description=f"**Total Suggestions:** {len(suggestions)}",
        color=0x4169E1
    )
    
    for i, suggestion in enumerate(suggestions[-10:], 1):  # Show last 10
        embed.add_field(
            name=f"#{i} - {suggestion['user_name']}",
            value=suggestion['suggestion'][:100] + ("..." if len(suggestion['suggestion']) > 100 else ""),
            inline=False
        )
    
    embed.set_footer(text="💡 Showing most recent suggestions. Consider implementing these ideas!")
    
    await ctx.send(embed=embed)

# FUN COMMANDS (20+ Games)
@bot.command()
async def guesscountry(ctx):
    """Guess the country flag game"""
    flag, country = random.choice(COUNTRIES)
    
    embed = discord.Embed(
        title="🌍 Guess the Country!",
        description=f"What country does this flag represent?\n\n**{flag}**",
        color=0x4169E1
    )
    embed.set_footer(text="Type your answer in chat!")
    
    await ctx.send(embed=embed)
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.lower() == country.lower():
            await ctx.send(f"🎉 Correct! It was **{country}** {flag}")
        else:
            await ctx.send(f"❌ Wrong! The correct answer was **{country}** {flag}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The answer was **{country}** {flag}")

@bot.command()
async def guessplayer(ctx):
    """Guess the football player with multiple choice"""
    correct_player = random.choice(FOOTBALL_PLAYERS)
    wrong_players = random.sample([p for p in FOOTBALL_PLAYERS if p != correct_player], 3)
    options = [correct_player] + wrong_players
    random.shuffle(options)
    
    embed = discord.Embed(
        title="⚽ Guess the Football Player!",
        description="Who is this legendary football player?",
        color=0x00FF00
    )
    
    # Create a simple riddle based on the player
    riddles = {
        "Lionel Messi": "This Argentine wizard has won 7 Ballon d'Ors",
        "Cristiano Ronaldo": "This Portuguese superstar is known for his incredible athleticism",
        "Neymar": "This Brazilian is known for his flair and skill moves",
        "Kylian Mbappe": "This young French speedster won the World Cup in 2018"
    }
    
    riddle = riddles.get(correct_player, f"This player is one of the greatest of all time")
    embed.add_field(name="🔍 Clue", value=riddle, inline=False)
    
    options_text = ""
    for i, option in enumerate(options, 1):
        options_text += f"**{i}.** {option}\n"
    
    embed.add_field(name="📋 Options", value=options_text, inline=False)
    embed.set_footer(text="Type the number (1-4) of your choice!")
    
    await ctx.send(embed=embed)
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content in ['1', '2', '3', '4']
    
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        choice_index = int(msg.content) - 1
        chosen_player = options[choice_index]
        
        if chosen_player == correct_player:
            await ctx.send(f"🎉 Correct! It was **{correct_player}**!")
        else:
            await ctx.send(f"❌ Wrong! The correct answer was **{correct_player}**")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The answer was **{correct_player}**")

@bot.command()
async def trivia(ctx):
    """Football trivia questions"""
    trivia_questions = [
        ("Which country won the first FIFA World Cup?", "Uruguay", ["Brazil", "Argentina", "Uruguay", "Germany"]),
        ("How many players are on a football team during a match?", "11", ["10", "11", "12", "9"]),
        ("Which club is known as 'The Red Devils'?", "Manchester United", ["Liverpool", "Arsenal", "Manchester United", "Chelsea"]),
        ("Who is the all-time top scorer for Real Madrid?", "Cristiano Ronaldo", ["Raul", "Cristiano Ronaldo", "Karim Benzema", "Alfredo Di Stefano"]),
        ("Which country has won the most World Cups?", "Brazil", ["Brazil", "Germany", "Argentina", "Italy"]),
    ]
    
    question, correct, options = random.choice(trivia_questions)
    random.shuffle(options)
    
    embed = discord.Embed(
        title="🧠 Football Trivia",
        description=question,
        color=0xFFD700
    )
    
    options_text = ""
    for i, option in enumerate(options, 1):
        options_text += f"**{i}.** {option}\n"
    
    embed.add_field(name="📋 Options", value=options_text, inline=False)
    embed.set_footer(text="Type the number of your choice!")
    
    await ctx.send(embed=embed)
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content in ['1', '2', '3', '4']
    
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        choice_index = int(msg.content) - 1
        chosen_answer = options[choice_index]
        
        if chosen_answer == correct:
            await ctx.send(f"🎉 Correct! The answer is **{correct}**!")
        else:
            await ctx.send(f"❌ Wrong! The correct answer is **{correct}**")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The answer was **{correct}**")

@bot.command()
async def joke(ctx):
    """Random football joke"""
    jokes = [
        "Why don't football players ever get hot? Because they have so many fans! 😄",
        "What do you call a football player who doesn't tackle? A spectator! 🤣",
        "Why did the football player go to the bank? To get his quarter back! 💰",
        "What's the difference between a football player and time? The football player runs down the field, time runs out! ⏰",
        "Why don't football stadiums ever get cold? Because they're full of fans! 🌬️",
        "What do you call a sleeping football player? A napback! 😴",
        "Why did the football team go to the bakery? Because they needed a good roll! 🥖",
    ]
    
    joke = random.choice(jokes)
    
    embed = discord.Embed(
        title="😄 Football Joke",
        description=joke,
        color=0xFFD700
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def quote(ctx):
    """Inspirational football quote"""
    quotes = [
        "\"Football is the beautiful game.\" - Pelé ⚽",
        "\"Success is no accident. It is hard work, perseverance, learning, studying, sacrifice.\" - Pelé 🏆",
        "\"The ball is round, the game lasts ninety minutes, and everything else is just theory.\" - Sepp Herberger ⚽",
        "\"I learned all about life with a ball at my feet.\" - Ronaldinho 🎨",
        "\"Football is a simple game based on the giving and taking of passes.\" - Bill Shankly 🎯",
        "\"Some people think football is a matter of life and death. I assure you, it's much more serious than that.\" - Bill Shankly ❤️",
    ]
    
    quote = random.choice(quotes)
    
    embed = discord.Embed(
        title="💭 Inspirational Quote",
        description=quote,
        color=0x4169E1
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def fact(ctx):
    """Random football fact"""
    facts = [
        "⚽ The fastest goal ever scored was in 2.8 seconds!",
        "🏟️ The largest football stadium is Rungrado 1st of May Stadium with 114,000 capacity!",
        "🌍 Football is played by over 250 million people in over 200 countries!",
        "⚡ The fastest recorded shot was 131 mph by Ronny Heberson!",
        "👑 Pelé is the only player to win 3 World Cups!",
        "🥅 The crossbar height is exactly 8 feet (2.44 meters)!",
        "📺 The World Cup is the most watched sporting event in the world!",
    ]
    
    fact = random.choice(facts)
    
    embed = discord.Embed(
        title="🧠 Football Fact",
        description=fact,
        color=0x00FF00
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def predict(ctx):
    """Match prediction generator"""
    teams = ["Arsenal", "Liverpool", "Manchester City", "Chelsea", "Tottenham", "Manchester United"]
    team1 = random.choice(teams)
    team2 = random.choice([t for t in teams if t != team1])
    
    score1 = random.randint(0, 4)
    score2 = random.randint(0, 4)
    
    predictions = [
        f"🔮 **{team1} {score1}-{score2} {team2}**",
        f"🎯 Top scorer: {random.choice(FOOTBALL_PLAYERS)}",
        f"📊 Total goals: {score1 + score2}",
        f"🃏 Surprise factor: {'High' if random.random() > 0.5 else 'Low'}"
    ]
    
    embed = discord.Embed(
        title="🔮 Match Prediction",
        description="Here's what the crystal ball says...",
        color=0x9932CC
    )
    
    for prediction in predictions:
        embed.add_field(name="🎲", value=prediction, inline=False)
    
    embed.set_footer(text="⚠️ For entertainment purposes only!")
    
    await ctx.send(embed=embed)

@bot.command()
async def celebration(ctx):
    """Random celebration generator"""
    celebrations = [
        "🕺 The Classic Knee Slide!",
        "✈️ The Airplane Celebration!",
        "🤫 The 'Shhh' to the Crowd!",
        "❤️ The Heart Symbol!",
        "🙏 The Prayer Celebration!",
        "🎭 The Mask Celebration!",
        "🦅 The Eagle Spread!",
        "⚡ The Lightning Bolt!",
        "🎯 The Archer Shot!",
        "👑 The Crown Gesture!",
    ]
    
    celebration = random.choice(celebrations)
    
    embed = discord.Embed(
        title="🎉 Goal Celebration",
        description=f"Your signature celebration: **{celebration}**",
        color=0xFFD700
    )
    
    embed.set_footer(text="Score a goal and show off your moves!")
    
    await ctx.send(embed=embed)

@bot.command()
async def nickname(ctx):
    """Generate a football nickname"""
    prefixes = ["The", "El", "The Amazing", "Lightning", "Golden", "Iron", "The Great"]
    suffixes = ["Striker", "Wizard", "Maestro", "Rocket", "Bullet", "Magician", "Legend", "Beast"]
    
    nickname = f"{random.choice(prefixes)} {random.choice(suffixes)}"
    
    embed = discord.Embed(
        title="⚡ Your Football Nickname",
        description=f"**{ctx.author.display_name}** - aka **{nickname}**",
        color=0xFF4500
    )
    
    embed.set_footer(text="Wear it with pride on the pitch!")
    
    await ctx.send(embed=embed)

@bot.command()
async def formation(ctx):
    """Random formation suggestion"""
    formation = random.choice(FORMATIONS)
    style = random.choice(TACTICS_STYLES)
    
    tips = {
        "4-3-3": "Great for attacking with wide play",
        "4-4-2": "Balanced formation with solid midfield",
        "3-5-2": "Control the midfield with wing-backs",
        "4-2-3-1": "Perfect for creative attacking midfielder",
        "3-4-3": "High-intensity attacking football",
        "5-3-2": "Solid defensive structure"
    }
    
    embed = discord.Embed(
        title="📐 Formation Suggestion",
        description=f"**Formation:** {formation}\n**Style:** {style}",
        color=0x4169E1
    )
    
    embed.add_field(
        name="💡 Tip",
        value=tips.get(formation, "Adapt based on your team's strengths!"),
        inline=False
    )
    
    await ctx.send(embed=embed)

# Additional fun commands
@bot.command()
async def motivation(ctx):
    """Get motivated for the game"""
    motivations = [
        "🔥 Champions are made when nobody's watching!",
        "⚡ Every expert was once a beginner!",
        "🏆 Victory belongs to the most persevering!",
        "💪 Hard work beats talent when talent doesn't work hard!",
        "🎯 The harder the battle, the sweeter the victory!",
        "⭐ Believe you can and you're halfway there!",
    ]
    
    motivation = random.choice(motivations)
    
    embed = discord.Embed(
        title="💪 Motivation Boost",
        description=motivation,
        color=0xFF4500
    )
    
    embed.set_footer(text="Now get out there and show them what you're made of! 🔴")
    
    await ctx.send(embed=embed)

@bot.command()
async def chant(ctx):
    """Arsenal chant"""
    chants = [
        "🔴 **ARSENAL! ARSENAL! ARSENAL!** 🔴",
        "🎵 *North London Forever!* 🎵",
        "⚽ *We've got Özil, Mesut Özil!* ⚽",
        "🏆 *49 unbeaten, 49 unbeaten!* 🏆",
        "🔴 *Red Army! Red Army!* 🔴",
    ]
    
    chant = random.choice(chants)
    
    embed = discord.Embed(
        title="📣 Arsenal Chant",
        description=chant,
        color=0xDC143C
    )
    
    embed.set_footer(text="Sing it loud and proud! 🔴⚪")
    
    await ctx.send(embed=embed)

@bot.command()
async def lucky(ctx):
    """Lucky number generator"""
    lucky_number = random.randint(1, 99)
    
    embed = discord.Embed(
        title="🍀 Your Lucky Number",
        description=f"**{lucky_number}**",
        color=0x00FF00
    )
    
    embed.add_field(
        name="✨ Lucky Message",
        value="This number will bring you good fortune on the pitch!",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ERROR HANDLING
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="❌ Access Denied",
            description="You don't have permission to use this command.",
            color=0xFF0000
        )
        
        if "is_admin" in str(error):
            embed.add_field(
                name="Required Permission",
                value="Administrator only",
                inline=False
            )
        elif "is_official_player" in str(error):
            embed.add_field(
                name="Required Role",
                value="Official Player role required",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found! Make sure to mention a valid member.")
    
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
    
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument! Please check your command format.")
    
    else:
        print(f"Error: {error}")

# COMPREHENSIVE MATCH RESULT SYSTEM
class MatchResultView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.home_team = None
        self.away_team = None
        self.home_score = None
        self.away_score = None
        self.goal_scorers = {}
        self.assists = {}
        self.possession = None
        
    @discord.ui.select(
        placeholder="Select Home Team...",
        options=[
            discord.SelectOption(label="Arsenal FC", value="Arsenal FC", emoji="🔴"),
            discord.SelectOption(label="Manchester City", value="Manchester City", emoji="🔵"),
            discord.SelectOption(label="Liverpool FC", value="Liverpool FC", emoji="🔴"),
            discord.SelectOption(label="Chelsea FC", value="Chelsea FC", emoji="🔵"),
            discord.SelectOption(label="Manchester United", value="Manchester United", emoji="🔴"),
            discord.SelectOption(label="Tottenham", value="Tottenham", emoji="⚪"),
            discord.SelectOption(label="Newcastle United", value="Newcastle United", emoji="⚫"),
            discord.SelectOption(label="Brighton", value="Brighton", emoji="🔵"),
            discord.SelectOption(label="Aston Villa", value="Aston Villa", emoji="🟤"),
            discord.SelectOption(label="West Ham", value="West Ham", emoji="🟤"),
            discord.SelectOption(label="Custom Team", value="custom", emoji="⚽"),
        ]
    )
    async def home_team_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "custom":
            modal = CustomTeamModal(self, "home")
            await interaction.response.send_modal(modal)
        else:
            self.home_team = select.values[0]
            embed = discord.Embed(
                title="⚽ Match Result Setup",
                description=f"**Home Team:** {self.home_team}\n\nNow select the away team:",
                color=0x4169E1
            )
            await interaction.response.edit_message(embed=embed, view=AwayTeamView(self))

class CustomTeamModal(discord.ui.Modal):
    def __init__(self, parent_view, team_type):
        super().__init__(title=f"Enter {team_type.title()} Team Name")
        self.parent_view = parent_view
        self.team_type = team_type
        
    team_name = discord.ui.TextInput(
        label="Team Name",
        placeholder="Enter the team name...",
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.team_type == "home":
            self.parent_view.home_team = self.team_name.value
            embed = discord.Embed(
                title="⚽ Match Result Setup",
                description=f"**Home Team:** {self.parent_view.home_team}\n\nNow select the away team:",
                color=0x4169E1
            )
            await interaction.response.edit_message(embed=embed, view=AwayTeamView(self.parent_view))
        else:
            self.parent_view.away_team = self.team_name.value
            embed = discord.Embed(
                title="⚽ Match Result Setup",
                description=f"**Home Team:** {self.parent_view.home_team}\n"
                           f"**Away Team:** {self.parent_view.away_team}\n\n"
                           f"Now enter the final score:",
                color=0x4169E1
            )
            await interaction.response.edit_message(embed=embed, view=ScoreInputView(self.parent_view))

class AwayTeamView(discord.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=600)
        self.parent = parent
        
    @discord.ui.select(
        placeholder="Select Away Team...",
        options=[
            discord.SelectOption(label="Arsenal FC", value="Arsenal FC", emoji="🔴"),
            discord.SelectOption(label="Manchester City", value="Manchester City", emoji="🔵"),
            discord.SelectOption(label="Liverpool FC", value="Liverpool FC", emoji="🔴"),
            discord.SelectOption(label="Chelsea FC", value="Chelsea FC", emoji="🔵"),
            discord.SelectOption(label="Manchester United", value="Manchester United", emoji="🔴"),
            discord.SelectOption(label="Tottenham", value="Tottenham", emoji="⚪"),
            discord.SelectOption(label="Newcastle United", value="Newcastle United", emoji="⚫"),
            discord.SelectOption(label="Brighton", value="Brighton", emoji="🔵"),
            discord.SelectOption(label="Aston Villa", value="Aston Villa", emoji="🟤"),
            discord.SelectOption(label="West Ham", value="West Ham", emoji="🟤"),
            discord.SelectOption(label="Custom Team", value="custom", emoji="⚽"),
        ]
    )
    async def away_team_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "custom":
            modal = CustomTeamModal(self.parent, "away")
            await interaction.response.send_modal(modal)
        else:
            self.parent.away_team = select.values[0]
            embed = discord.Embed(
                title="⚽ Match Result Setup",
                description=f"**Home Team:** {self.parent.home_team}\n"
                           f"**Away Team:** {self.parent.away_team}\n\n"
                           f"Now enter the final score:",
                color=0x4169E1
            )
            await interaction.response.edit_message(embed=embed, view=ScoreInputView(self.parent))

class ScoreInputModal(discord.ui.Modal):
    def __init__(self, parent_view):
        super().__init__(title="Enter Match Score")
        self.parent_view = parent_view
        
    home_score = discord.ui.TextInput(
        label=f"Home Team Goals",
        placeholder="0",
        max_length=2
    )
    
    away_score = discord.ui.TextInput(
        label=f"Away Team Goals", 
        placeholder="0",
        max_length=2
    )
    
    possession = discord.ui.TextInput(
        label="Home Team Possession %",
        placeholder="50",
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.parent_view.home_score = int(self.home_score.value)
            self.parent_view.away_score = int(self.away_score.value)
            self.parent_view.possession = int(self.possession.value)
            
            embed = discord.Embed(
                title="⚽ Match Result Setup",
                description=f"**{self.parent_view.home_team}** {self.parent_view.home_score} - {self.parent_view.away_score} **{self.parent_view.away_team}**\n\n"
                           f"**Possession:** {self.parent_view.possession}% - {100-self.parent_view.possession}%\n\n"
                           f"Now add goal scorers and assists:",
                color=0x4169E1
            )
            await interaction.response.edit_message(embed=embed, view=GoalScorersView(self.parent_view))
            
        except ValueError:
            await interaction.response.send_message("❌ Please enter valid numbers for scores and possession!", ephemeral=True)

class ScoreInputView(discord.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=600)
        self.parent = parent
        
    @discord.ui.button(label="📝 Enter Score & Possession", style=discord.ButtonStyle.primary)
    async def enter_score(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ScoreInputModal(self.parent)
        await interaction.response.send_modal(modal)

class GoalScorersModal(discord.ui.Modal):
    def __init__(self, parent_view):
        super().__init__(title="Add Goal Scorers & Assists")
        self.parent_view = parent_view
        
    goal_scorers = discord.ui.TextInput(
        label="Goal Scorers (Format: Player 2, Player2 1)",
        placeholder="Example: Saka 2, Martinelli 1",
        style=discord.TextStyle.paragraph,
        required=False
    )
    
    assists = discord.ui.TextInput(
        label="Assists (Format: Player 1, Player2 2)", 
        placeholder="Example: Odegaard 1, Rice 1",
        style=discord.TextStyle.paragraph,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # Parse goal scorers
        if self.goal_scorers.value:
            for entry in self.goal_scorers.value.split(','):
                entry = entry.strip()
                if entry:
                    parts = entry.rsplit(' ', 1)
                    if len(parts) == 2:
                        player, goals = parts[0].strip(), parts[1].strip()
                        try:
                            self.parent_view.goal_scorers[player] = int(goals)
                        except ValueError:
                            pass
        
        # Parse assists
        if self.assists.value:
            for entry in self.assists.value.split(','):
                entry = entry.strip()
                if entry:
                    parts = entry.rsplit(' ', 1)
                    if len(parts) == 2:
                        player, assist_count = parts[0].strip(), parts[1].strip()
                        try:
                            self.parent_view.assists[player] = int(assist_count)
                        except ValueError:
                            pass
        
        # Generate final result
        await self.generate_final_result(interaction)
    
    async def generate_final_result(self, interaction):
        parent = self.parent_view
        
        # Determine match result
        if parent.home_score > parent.away_score:
            result_emoji = "🟢"
            result_text = "WIN"
            result_color = 0x00FF00
        elif parent.home_score < parent.away_score:
            result_emoji = "🔴"
            result_text = "LOSS"  
            result_color = 0xFF0000
        else:
            result_emoji = "🟡"
            result_text = "DRAW"
            result_color = 0xFFD700
        
        embed = discord.Embed(
            title=f"{result_emoji} MATCH RESULT - {result_text}",
            description=f"**{parent.home_team}** vs **{parent.away_team}**",
            color=result_color
        )
        
        embed.add_field(
            name="📊 Final Score",
            value=f"**{parent.home_team}** {parent.home_score} - {parent.away_score} **{parent.away_team}**",
            inline=False
        )
        
        embed.add_field(
            name="📈 Match Statistics", 
            value=f"**Possession:** {parent.possession}% - {100-parent.possession}%\n"
                  f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
                  f"**Time:** {datetime.now().strftime('%H:%M')} UTC",
            inline=True
        )
        
        if parent.goal_scorers:
            scorers_text = ""
            for player, goals in parent.goal_scorers.items():
                scorers_text += f"⚽ **{player}** ({goals})\n"
            embed.add_field(name="⚽ Goal Scorers", value=scorers_text, inline=True)
        
        if parent.assists:
            assists_text = ""
            for player, assist_count in parent.assists.items():
                assists_text += f"🎯 **{player}** ({assist_count})\n"  
            embed.add_field(name="🎯 Assists", value=assists_text, inline=True)
        
        embed.add_field(
            name="🏆 Match Details",
            value=f"**Competition:** Premier League\n"
                  f"**Venue:** {parent.home_team} Stadium\n"
                  f"**Attendance:** {random.randint(40000, 60000):,}\n"
                  f"**Referee:** Premier League Official",
            inline=False
        )
        
        embed.set_footer(text="Arsenal FC Match Result System | COYG! 🔴")
        embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
        
        await interaction.response.edit_message(embed=embed, view=None)

class GoalScorersView(discord.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=600)
        self.parent = parent
        
    @discord.ui.button(label="⚽ Add Goal Scorers & Assists", style=discord.ButtonStyle.success)
    async def add_scorers(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GoalScorersModal(self.parent)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✅ Finish Without Scorers", style=discord.ButtonStyle.secondary)
    async def finish_without_scorers(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GoalScorersModal(self.parent)
        await modal.generate_final_result(interaction)

@bot.command()
@is_admin()
async def result(ctx):
    """Create comprehensive match results"""
    embed = discord.Embed(
        title="⚽ ARSENAL FC - MATCH RESULT CREATOR",
        description="**Create a comprehensive match result**\n\nSelect the home team to get started:",
        color=0x4169E1
    )
    embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
    
    view = MatchResultView(ctx)
    await ctx.send(embed=embed, view=view)

# REMOVE INFO COMMAND (as requested)
# The !info command is removed as requested since !document exists

# Update document to show signing and release timestamps  
@bot.command()
@is_admin()
async def document_enhanced(ctx, member: discord.Member):
    """Enhanced player document with timestamps"""
    player_data = get_player_data(member.id)
    stats = player_data['stats']
    
    # Get signing and release dates
    signing_date = member.joined_at.strftime('%Y-%m-%d %H:%M') if member.joined_at else 'Unknown'
    release_date = "Active Player"
    if not player_data.get('registered', False):
        release_date = f"Released on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    embed = discord.Embed(
        title=f"📋 {member.display_name}'s Enhanced Document",
        description="**OFFICIAL ARSENAL FC PLAYER REPORT**\n*With Complete Timeline*",
        color=0xDC143C
    )
    
    embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
    
    # Personal Details with timestamps
    embed.add_field(
        name="👤 Personal & Contract Details",
        value=f"**Name:** {member.display_name}\n"
              f"**Position:** {player_data['position']}\n"
              f"**Contract Length:** {player_data['contract_years']} years\n"
              f"**Signed:** {signing_date}\n"
              f"**Status:** {release_date}",
        inline=False
    )
    
    # Current Status
    embed.add_field(
        name="📊 Current Status",
        value=f"**Level:** {player_data['level']}\n"
              f"**Points:** {player_data['points']}\n"
              f"**Star Rating:** {'⭐' * player_data['stars']}\n"
              f"**Overall Rating:** {player_data['rating']}/100\n"
              f"**Current Form:** {player_data['form']}%",
        inline=True
    )
    
    # Performance Record
    avg_performance = sum(player_data['performance_ratings']) / len(player_data['performance_ratings']) if player_data['performance_ratings'] else 0
    embed.add_field(
        name="🏆 Performance Record",
        value=f"**Appearances:** {stats['appearances']}\n"
              f"**Goals:** {stats['goals']}\n"
              f"**Assists:** {stats['assists']}\n"
              f"**Average Match Rating:** {avg_performance:.1f}/10\n"
              f"**Hat-tricks:** {stats['hattricks']}\n"
              f"**POTWs:** {stats['potws']}",
        inline=True
    )
    
    embed.add_field(
        name="⚠️ Discipline & Status",
        value=f"**Current Strikes:** {player_data['strikes']}/3\n"
              f"**Yellow Cards:** {stats['yellow_cards']}\n"
              f"**Red Cards:** {stats['red_cards']}\n"
              f"**Registration Status:** {'✅ Active' if player_data['registered'] else '❌ Released'}\n"
              f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        inline=False
    )
    
    embed.set_footer(text=f"Arsenal FC Official Document System | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    await ctx.send(embed=embed)

# NEW ENHANCED COMMANDS FOR ARSENAL FC BOT - MAJOR UPDATE

# TRIAL RESULTS SYSTEM
@bot.command()
@is_admin()
async def trialsresult(ctx, member: discord.Member):
    "Complete trial evaluation for a player"
    view = TrialResultView(member, ctx.author)
    
    embed = discord.Embed(
        title="📋 TRIAL EVALUATION SYSTEM",
        description=f"**Evaluating:** {member.display_name}\n**Evaluator:** {ctx.author.display_name}\n",
        color=0x4169E1
    )
    
    embed.add_field(
        name="🎯 Trial Assessment",
        value="Please complete the comprehensive evaluation below:\n"
              "• Select the player's position\n"
              "• Rate their performance (1-10)\n"
              "• Choose pass/fail result\n"
              "• Provide detailed feedback",
        inline=False
    )
    
    embed.set_footer(text="Complete evaluation will be sent to trials channel for review")

    await ctx.send(embed=embed, view=view)

class TrialResultView(discord.ui.View):
    def __init__(self, player, evaluator):
        super().__init__(timeout=600)
        self.player = player
        self.evaluator = evaluator
        self.position = None
        self.rating = None
        self.result = None
        self.feedback = None
        
    @discord.ui.select(
        placeholder="Choose player's position...",
        options=[
            discord.SelectOption(label="Goalkeeper", value="Goalkeeper", emoji="🥅"),
            discord.SelectOption(label="Defender", value="Defender", emoji="🛡️"),
            discord.SelectOption(label="Midfielder", value="Midfielder", emoji="⚽"),
            discord.SelectOption(label="Forward", value="Forward", emoji="🎯"),
            discord.SelectOption(label="Winger", value="Winger", emoji="🏃"),
        ]
    )
    async def select_position(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.position = select.values[0]
        await interaction.response.send_message(f"✅ Position set: {self.position}", ephemeral=True)
    
    @discord.ui.select(
        placeholder="Rate performance (1-10)...",
        options=[
            discord.SelectOption(label="1 - Very Poor", value="1"),
            discord.SelectOption(label="2 - Poor", value="2"),
            discord.SelectOption(label="3 - Below Average", value="3"),
            discord.SelectOption(label="4 - Below Average", value="4"),
            discord.SelectOption(label="5 - Average", value="5"),
            discord.SelectOption(label="6 - Above Average", value="6"),
            discord.SelectOption(label="7 - Good", value="7"),
            discord.SelectOption(label="8 - Very Good", value="8"),
            discord.SelectOption(label="9 - Excellent", value="9"),
            discord.SelectOption(label="10 - Outstanding", value="10"),
        ]
    )
    async def select_rating(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.rating = int(select.values[0])
        await interaction.response.send_message(f"✅ Rating set: {self.rating}/10", ephemeral=True)

    @discord.ui.button(label="✅ PASS", style=discord.ButtonStyle.success, row=2)
    async def pass_trial(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "PASSED"
        await interaction.response.send_message("✅ Trial result: PASSED", ephemeral=True)

    @discord.ui.button(label="❌ FAIL", style=discord.ButtonStyle.danger, row=2)
    async def fail_trial(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "FAILED"
        await interaction.response.send_message("❌ Trial result: FAILED", ephemeral=True)

    @discord.ui.button(label="📝 Add Feedback", style=discord.ButtonStyle.secondary, row=2)
    async def add_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TrialFeedbackModal(self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🚀 Submit Evaluation", style=discord.ButtonStyle.primary, row=3)
    async def submit_evaluation(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not all([self.position, self.rating, self.result]):
            await interaction.response.send_message("❌ Please complete all fields before submitting!", ephemeral=True)
            return
        
        # Send to trials channel
        trials_channel = interaction.guild.get_channel(int(TRIALS_CHANNEL))
        if trials_channel:
            result_embed = discord.Embed(
                title="📋 TRIAL EVALUATION COMPLETE",
                description=f"**Player:** {self.player.mention}\n**Evaluator:** {self.evaluator.mention}",
                color=0x00FF00 if self.result == "PASSED" else 0xFF0000
            )
            
            result_embed.add_field(
                name="📊 Evaluation Results",
                value=f"**Position:** {self.position}\n"
                      f"**Performance Rating:** {self.rating}/10 ({get_performance_level(self.rating)})\n"
                      f"**Trial Result:** {self.result}",
                inline=False
            )
            
            if self.feedback:
                result_embed.add_field(
                    name="💭 Evaluator Feedback",
                    value=self.feedback,
                    inline=False
                )
            
            result_embed.add_field(
                name="⏰ Evaluation Details",
                value=f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
                      f"**Time:** {datetime.now().strftime('%H:%M:%S')}\n"
                      f"**Evaluated by:** {self.evaluator.display_name}",
                inline=False
            )
            
            # If passed and has pending role, remove it and add appropriate level role
            if self.result == "PASSED":
                try:
                    pending_role = discord.utils.get(interaction.guild.roles, id=int(SPECIAL_ROLES['pending']))
                    if pending_role in self.player.roles:
                        await self.player.remove_roles(pending_role)
                        
                        # Add official player role and reserve role (default)
                        official_role = discord.utils.get(interaction.guild.roles, id=int(ROLE_IDS['official_player']))
                        reserve_role = discord.utils.get(interaction.guild.roles, id=int(ROLE_IDS['reserve']))
                        
                        if official_role:
                            await self.player.add_roles(official_role)
                        if reserve_role:
                            await self.player.add_roles(reserve_role)
                        
                        result_embed.add_field(
                            name="🎉 Player Status Updated",
                            value="• Removed pending role\n• Added official player role\n• Added reserve role",
                            inline=False
                        )
                        
                        # Update player data
                        player_data = get_player_data(self.player.id)
                        player_data['registered'] = True
                        player_data['position'] = self.position
                        player_data['level'] = 'Reserve'
                        player_data['signed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        update_player_data(self.player.id, player_data)
                        
                        # Send congratulatory DM
                        try:
                            congrats_embed = discord.Embed(
                                title="🎉 CONGRATULATIONS!",
                                description=f"You have successfully passed your trial for Arsenal FC!",
                                color=0x00FF00
                            )
                            congrats_embed.add_field(
                                name="✅ Trial Results",
                                value=f"**Position:** {self.position}\n"
                                      f"**Rating:** {self.rating}/10\n"
                                      f"**Status:** Official Player",
                                inline=False
                            )
                            congrats_embed.add_field(
                                name="🔴 Welcome to Arsenal FC!",
                                value="You are now an official member of the Arsenal FC squad. "
                                      "Continue working hard and you'll progress through the ranks!",
                                inline=False
                            )
                            await self.player.send(embed=congrats_embed)
                        except:
                            pass
                            
                except Exception as e:
                    result_embed.add_field(
                        name="⚠️ Role Update Error",
                        value=f"Could not update player roles automatically: {str(e)}",
                        inline=False
                    )
            
            await trials_channel.send(embed=result_embed)
        
        # Confirm submission
        await interaction.response.edit_message(
            content="✅ Trial evaluation submitted successfully!",
            embed=None,
            view=None
        )

class TrialFeedbackModal(discord.ui.Modal):
    def __init__(self, trial_view):
        super().__init__(title="Trial Feedback")
        self.trial_view = trial_view
        
    feedback = discord.ui.TextInput(
        label="Detailed Performance Feedback",
        style=discord.TextStyle.paragraph,
        placeholder="Provide detailed feedback on the player's performance during the trial...",
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.trial_view.feedback = self.feedback.value
        await interaction.response.send_message("✅ Feedback saved!", ephemeral=True)

# CAPTAIN APPOINTMENT SYSTEM
@bot.command()
@is_admin()
async def appoint_captain(ctx, member: discord.Member, *, reason):
    """Appoint official club captain"""
    view = CaptainConfirmView(member, reason, ctx.author)
    
    embed = discord.Embed(
        title="👑 CAPTAIN APPOINTMENT",
        description=f"**Appointing:** {member.display_name}\n**Appointed by:** {ctx.author.display_name}\n",
        color=0xFFD700
    )
    
    embed.add_field(
        name="📋 Captain Responsibilities",
        value="• Lead by example on and off the pitch\n"
              "• Represent the team in official matters\n"
              "• Motivate teammates during matches\n"
              "• Act as liaison between players and management\n"
              "• Uphold Arsenal FC values and standards",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Appointment Reason",
        value=reason,
        inline=False
    )

    embed.set_footer(text="Confirm appointment to proceed with captain role assignment")

    await ctx.send(embed=embed, view=view)

class CaptainConfirmView(discord.ui.View):
    def __init__(self, player, reason, appointer):
        super().__init__(timeout=300)
        self.player = player
        self.reason = reason
        self.appointer = appointer

    @discord.ui.button(label="👑 Confirm Appointment", style=discord.ButtonStyle.success)
    async def confirm_captain(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Add captain role
            captain_role = discord.utils.get(interaction.guild.roles, id=int(SPECIAL_ROLES['captain']))
            if captain_role:
                await self.player.add_roles(captain_role)
            
            # Send congratulatory DM
            captain_embed = discord.Embed(
                title="👑 CONGRATULATIONS, CAPTAIN!",
                description=f"You have been appointed as the official Captain of Arsenal FC!",
                color=0xFFD700
            )
            
            captain_embed.add_field(
                name="🎖️ Appointment Details",
                value=f"**Appointed by:** {self.appointer.display_name}\n"
                      f"**Reason:** {self.reason}\n"
                      f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
            
            captain_embed.add_field(
                name="👑 Captain's Oath",
                value="As Captain of Arsenal FC, you pledge to:\n"
                      "• Lead with integrity and passion\n"
                      "• Inspire your teammates to greatness\n"
                      "• Represent the club with honor\n"
                      "• Embody the Arsenal spirit on and off the pitch",
                inline=False
            )

            captain_embed.set_footer(text="Congratulations on this prestigious appointment! 🔴")

            try:
                await self.player.send(embed=captain_embed)
            except:
                pass
            
            # Update player data
            player_data = get_player_data(self.player.id)
            player_data['captain'] = True
            player_data['captain_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_player_data(self.player.id, player_data)
            
            # Success message
            success_embed = discord.Embed(
                title="👑 CAPTAIN APPOINTED!",
                description=f"{self.player.mention} is now the official Captain of Arsenal FC!",
                color=0x00FF00
            )
            
            success_embed.add_field(
                name="✅ Actions Completed",
                value="• Captain role assigned\n"
                      "• Congratulatory DM sent\n"
                      "• Player data updated\n"
                      "• Leadership status activated",
                inline=False
            )
            
            await interaction.response.edit_message(embed=success_embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error appointing captain: {str(e)}", ephemeral=True)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
    async def cancel_appointment(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Captain Appointment Cancelled",
            description="The captain appointment has been cancelled.",
            color=0xFF0000
        )
        await interaction.response.edit_message(embed=embed, view=None)

# STAFF OF THE WEEK COMMAND
@bot.command()
@is_admin()
async def sotw(ctx, member: discord.Member, *, reason):
    """Award Staff of the Week"""
    try:
        # Add SOTW role
        sotw_role = discord.utils.get(ctx.guild.roles, id=int(SPECIAL_ROLES['sotw']))
        if sotw_role:
            await member.add_roles(sotw_role)
        
        # Send congratulatory DM
        sotw_embed = discord.Embed(
            title="🌟 STAFF OF THE WEEK AWARD!",
            description="Congratulations! You have been selected as Staff of the Week!",
            color=0xFFD700
        )
        
        sotw_embed.add_field(
            name="🏆 Award Details",
            value=f"**Awarded by:** {ctx.author.display_name}\n"
                  f"**Reason:** {reason}\n"
                  f"**Week of:** {datetime.now().strftime('%Y-%m-%d')}",
            inline=False
        )
        
        sotw_embed.add_field(
            name="⭐ Recognition",
            value="Your exceptional dedication, professionalism, and contribution to Arsenal FC "
                  "has been recognized by the management team. Thank you for your outstanding service!",
            inline=False
        )

        sotw_embed.set_footer(text="Keep up the excellent work! 🔴")

        try:
            await member.send(embed=sotw_embed)
        except:
            pass
        
        # Public announcement
        announcement_embed = discord.Embed(
            title="🌟 STAFF OF THE WEEK ANNOUNCEMENT",
            description=f"**{member.display_name}** has been awarded Staff of the Week!",
            color=0xFFD700
        )
        
        announcement_embed.add_field(
            name="🏆 Achievement",
            value=f"**Reason:** {reason}\n"
                  f"**Awarded by:** {ctx.author.display_name}\n"
                  f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
            inline=False
        )

        announcement_embed.set_footer(text="Congratulations on this well-deserved recognition!")

        await ctx.send(embed=announcement_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error awarding SOTW: {str(e)}")

# FORM EDITING COMMAND
@bot.command()
@is_admin()
async def editform(ctx, member: discord.Member, percentage: int):
    """Edit a player's form percentage"""
    if not 0 <= percentage <= 100:
        await ctx.send("❌ Form percentage must be between 0 and 100!")
        return
    
    player_data = get_player_data(member.id)
    old_form = player_data['form']
    player_data['form'] = percentage
    update_player_data(member.id, player_data)

    embed = discord.Embed(title="📊 Player Form Updated", color=0x4169E1)
    embed.add_field(
        name="Form Adjustment",
        value=f"**Player:** {member.mention}\n"
              f"**Previous Form:** {old_form}%\n"
              f"**New Form:** {percentage}%\n"
              f"**Change:** {'+' if percentage > old_form else ''}{percentage - old_form}%",
        inline=False
    )
    
    # Add form status
    if percentage >= 80:
        form_status = "🔥 Excellent Form"
    elif percentage >= 60:
        form_status = "✅ Good Form"
    elif percentage >= 40:
        form_status = "⚠️ Average Form"
    elif percentage >= 20:
        form_status = "📉 Poor Form"
    else:
        form_status = "❌ Very Poor Form"

    embed.add_field(name="Form Status", value=form_status, inline=False)

    await ctx.send(embed=embed)

# REMOVE STARS COMMAND  
@bot.command()
@is_admin()
async def removestars(ctx, member: discord.Member):
    """Remove star rating from a player"""
    player_data = get_player_data(member.id)
    old_stars = player_data['stars']
    player_data['stars'] = 1  # Reset to 1 star
    update_player_data(member.id, player_data)

    embed = discord.Embed(title="⭐ Star Rating Removed", color=0xFF4500)
    embed.add_field(
        name="Rating Reset",
        value=f"**Player:** {member.mention}\n"
              f"**Previous Stars:** {'⭐' * old_stars}\n"
              f"**New Stars:** ⭐ (Reset to 1)\n"
              f"**Action:** Star rating reset",
        inline=False
    )
    
    await ctx.send(embed=embed)

# =================== ENHANCED OFFICE CALL ===================
@bot.command()
@is_admin()

async def officecall(ctx, member: discord.Member=None, *, reason: str=None):
    """Enhanced office call with waiting room invite and robust error handling.

    Usage:
    !officecall @user reason for office call
    """
    if member is None or reason is None:
        await ctx.send(f"❌ Usage: `!officecall @user <reason>` — please mention a user and give a reason, {ctx.author.mention}.")
        return

    # Public embed (always posted)
    public_embed = discord.Embed(
        title="📞 OFFICE CALL",
        description=f"{member.mention} has been called to the manager's office.",
        color=0xFF4500,
        timestamp=datetime.utcnow()
    )
    public_embed.add_field(name="Called by", value=ctx.author.mention, inline=True)
    public_embed.add_field(name="Reason", value=reason, inline=False)
    public_embed.set_footer(text="Arsenal FC Management System")

    # DM embed
    dm_embed = discord.Embed(
        title="📞 OFFICE CALL — You have been called",
        description="You have received an office call from the management team.",
        color=0xFF4500,
        timestamp=datetime.utcnow()
    )
    dm_embed.add_field(name="Called by", value=ctx.author.display_name, inline=True)
    dm_embed.add_field(name="Reason", value=reason, inline=False)
    dm_embed.add_field(name="Instructions", value="Please join the waiting room voice channel or contact management.", inline=False)
    dm_embed.set_footer(text="If you cannot be reached here, management will attempt to contact you in-channel.")

    # Attempt DM first (but we will always post public notice)
    dm_sent = False
    try:
        try:
            await member.send(embed=dm_embed)
            dm_sent = True
        except discord.Forbidden:
            # DM closed or blocked
            dm_sent = False
        except Exception as e:
            # Unexpected DM error - log and continue
            dm_sent = False

        # Always post the public office call in the channel
        await ctx.send(embed=public_embed)

        # Follow-up admin notification
        if dm_sent:
            info = f"✅ Office call DM sent to {member.mention}."
        else:
            info = f"⚠️ Could not DM {member.mention}. Posted office call publicly instead. They may have DMs disabled."

        admin_embed = discord.Embed(title="📣 Office Call Result", description=info, color=0x00FF00, timestamp=datetime.utcnow())
        await ctx.send(embed=admin_embed)

    except discord.Forbidden:
        await ctx.send(f"❌ I do not have permission to post office calls here, {ctx.author.mention}.")
    except Exception as e:
        await ctx.send(f"❌ An unexpected error occurred while sending the office call: `{e}`")


# =================== OFFICE CALL BUTTON VIEW ===================
class OfficeCallView(discord.ui.View):
    def __init__(self, reason, admin):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.reason = reason
        self.admin = admin

    @discord.ui.button(label="🎧 Join Waiting Room", style=discord.ButtonStyle.primary)
    async def join_waiting_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not WAITING_ROOM_VC:
                await interaction.response.send_message("❌ Waiting room VC ID not configured.", ephemeral=True)
                return

            waiting_room_link = f"https://discord.com/channels/{interaction.guild_id}/{WAITING_ROOM_VC}"
            embed = discord.Embed(
                title="🎧 WAITING ROOM ACCESS",
                description="Please join the waiting room voice channel now.",
                color=0x0099FF
            )
            
            embed.add_field(
                name="📱 Voice Channel Link",
                value=f"[Click here to join the waiting room]({waiting_room_link})",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Next Steps",
                value="1. Join the voice channel using the link above\n"
                      "2. Wait for a management member to move you\n"
                      "3. Be respectful and professional\n"
                      "4. State your name clearly when asked",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error processing button click: {e}", ephemeral=True)

# BOT TOKEN - Replace with environment variable
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN environment variable is required!")
    else:
        # ===================  NEW COMPREHENSIVE FEATURES UPDATE ===================
    
    # Updated forms for main.py (already have 7-aside formations above)
     FORMATIONS_7_ASIDE = [
        "2-3-0-1", "1-3-0-2", "3-1-0-2", "2-2-0-2", "1-2-1-2",
        "0-4-2", "1-1-2-2", "2-1-0-3", "1-0-4-1", "0-2-3-1",
        "4-0-2", "3-2-0-1", "2-0-3-1", "1-0-5", "0-1-4-1"
    ]

    # =================== TRIAL RESULTS SYSTEM ===================
    class TrialResultView(discord.ui.View):
        def __init__(self, user):
            super().__init__(timeout=600)
            self.user = user
            self.position = None
            
        @discord.ui.select(
            placeholder="Select player position...",
            options=[
                discord.SelectOption(label="Goalkeeper", value="Goalkeeper", emoji="🥅"),
                discord.SelectOption(label="Defender", value="Defender", emoji="🛡️"),
                discord.SelectOption(label="Midfielder", value="Midfielder", emoji="⚽"),
                discord.SelectOption(label="Forward", value="Forward", emoji="🎯"),
                discord.SelectOption(label="Winger", value="Winger", emoji="🏃"),
            ]
        )
        async def position_select(self, interaction: discord.Interaction, select: discord.ui.Select):
            self.position = select.values[0]
            
            rating_view = TrialRatingView(self.user, self.position)
            embed = discord.Embed(
                title="📊 Trial Rating",
                description=f"Rate {self.user.mention}'s performance in the **{self.position}** position",
                color=0x4169E1
            )
            await interaction.response.edit_message(embed=embed, view=rating_view)

    class TrialRatingView(discord.ui.View):
        def __init__(self, user, position):
            super().__init__(timeout=600)
            self.user = user
            self.position = position
            
        @discord.ui.select(
            placeholder="Rate their performance (1-10)...",
            options=[
                discord.SelectOption(label="1 - Terrible", value="1", emoji="❌"),
                discord.SelectOption(label="2 - Very Poor", value="2", emoji="🔻"),
                discord.SelectOption(label="3 - Poor", value="3", emoji="⬇️"),
                discord.SelectOption(label="4 - Below Average", value="4", emoji="📉"),
                discord.SelectOption(label="5 - Average", value="5", emoji="➖"),
                discord.SelectOption(label="6 - Decent", value="6", emoji="📊"),
                discord.SelectOption(label="7 - Good", value="7", emoji="⬆️"),
                discord.SelectOption(label="8 - Very Good", value="8", emoji="🔝"),
                discord.SelectOption(label="9 - Excellent", value="9", emoji="✨"),
                discord.SelectOption(label="10 - Outstanding", value="10", emoji="🌟"),
            ]
        )
        async def rating_select(self, interaction: discord.Interaction, select: discord.ui.Select):
            rating = int(select.values[0])
            
            pass_fail_view = TrialPassFailView(self.user, self.position, rating)
            embed = discord.Embed(
                title="✅/❌ Trial Result",
                description=f"Did {self.user.mention} pass the trial?\n**Position:** {self.position}\n**Rating:** {rating}/10",
                color=0xFFD700
            )
            await interaction.response.edit_message(embed=embed, view=pass_fail_view)

    class TrialPassFailView(discord.ui.View):
        def __init__(self, user, position, rating):
            super().__init__(timeout=600)
            self.user = user
            self.position = position
            self.rating = rating
            
        @discord.ui.button(label="✅ PASSED", style=discord.ButtonStyle.success)
        async def trial_passed(self, interaction: discord.Interaction, button: discord.ui.Button):
            feedback_modal = TrialFeedbackModal(self.user, self.position, self.rating, True)
            await interaction.response.send_modal(feedback_modal)
            
        @discord.ui.button(label="❌ FAILED", style=discord.ButtonStyle.danger)
        async def trial_failed(self, interaction: discord.Interaction, button: discord.ui.Button):
            feedback_modal = TrialFeedbackModal(self.user, self.position, self.rating, False)
            await interaction.response.send_modal(feedback_modal)

    class TrialFeedbackModal(discord.ui.Modal):
        def __init__(self, user, position, rating, passed):
            super().__init__(title="Trial Feedback")
            self.user = user
            self.position = position
            self.rating = rating
            self.passed = passed
            
            self.feedback = discord.ui.TextInput(
                label="Overall Performance Feedback",
                placeholder="Provide detailed feedback on their trial performance...",
                style=discord.TextStyle.long,
                max_length=1000,
                required=True
            )
            self.add_item(self.feedback)
            
        async def on_submit(self, interaction: discord.Interaction):
            # Send to trials channel
            channel = interaction.client.get_channel(int(TRIALS_CHANNEL))
            if channel:
                result_embed = discord.Embed(
                    title="🏆 TRIAL RESULT SUBMITTED",
                    description=f"**Player:** {self.user.mention}\n**Evaluated by:** {interaction.user.mention}",
                    color=0x00FF00 if self.passed else 0xFF0000
                )
                
                result_embed.add_field(
                    name="📊 Trial Details",
                    value=f"**Position:** {self.position}\n"
                          f"**Rating:** {self.rating}/10\n"
                          f"**Result:** {'✅ PASSED' if self.passed else '❌ FAILED'}",
                    inline=False
                )
                
                result_embed.add_field(
                    name="💭 Manager Feedback",
                    value=self.feedback.value,
                    inline=False
                )
                
                result_embed.set_footer(text=f"Trial completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                await channel.send(embed=result_embed)
            
            # If passed, remove pending role
            if self.passed:
                try:
                    guild = interaction.guild
                    member = guild.get_member(self.user.id)
                    pending_role = discord.utils.get(guild.roles, id=int(SPECIAL_ROLES['pending']))
                    if member and pending_role and pending_role in member.roles:
                        await member.remove_roles(pending_role)
                except:
                    pass
            
            await interaction.response.send_message("✅ Trial result submitted successfully!", ephemeral=True)

    # =================== ENHANCED STRIKE SYSTEM ===================
    @bot.command()
    @is_admin()
    async def addstrike(ctx, member: discord.Member, *, reason):
        # Duplicate function removed
        player_data = get_player_data(member.id)
        player_data['strikes'] += 1
        strikes = player_data['strikes']
        
        # Add appropriate strike role
        try:
            guild = ctx.guild
            
            # Remove previous strike roles
            for i in range(1, 4):
                old_role = discord.utils.get(guild.roles, id=int(STRIKE_ROLES[i]))
                if old_role and old_role in member.roles:
                    await member.remove_roles(old_role)
            
            # Add new strike role if not at max
            if strikes <= 3:
                new_role = discord.utils.get(guild.roles, id=int(STRIKE_ROLES[strikes]))
                if new_role:
                    await member.add_roles(new_role)
        except:
            pass
        
        # Auto-demote at 3 strikes
        demoted = False
        if strikes >= 3:
            current_levels = list(LEVEL_REQUIREMENTS.keys())
            current_index = current_levels.index(player_data['level'])
            if current_index > 0:
                player_data['level'] = current_levels[current_index - 1]
                demoted = True
            player_data['strikes'] = 0  # Reset strikes after demotion
            player_data['form'] = max(0, player_data['form'] - 20)
        else:
            player_data['form'] = max(0, player_data['form'] - 8)
        
        update_player_data(member.id, player_data)
        
        embed = discord.Embed(title="⚠️ STRIKE ISSUED", color=0xFF4500)
        embed.add_field(
            name="🚨 Disciplinary Action",
            value=f"**Player:** {member.mention}\n"
                  f"**Reason:** {reason}\n"
                  f"**Strike Level:** {strikes if not demoted else 'Reset after demotion'}\n"
                  f"**Form Impact:** -{8 if not demoted else 20}%",
            inline=False
        )
        
        if strikes <= 3 and not demoted:
            embed.add_field(
                name=f"🔴 Strike {strikes} Role Added",
                value=f"Player now has Strike {strikes} role",
                inline=False
            )
        
        if demoted:
            embed.add_field(
                name="⬇️ AUTOMATIC DEMOTION",
                value=f"Player demoted to **{player_data['level']}** due to 3 strikes.\nStrikes reset and roles cleared.",
                inline=False
            )
        
        await ctx.send(embed=embed)

    # =================== CAPTAIN APPOINTMENT SYSTEM ===================
    class CaptainAppointmentView(discord.ui.View):
        def __init__(self, user, reason):
            super().__init__(timeout=300)
            self.user = user
            self.reason = reason
            
        @discord.ui.button(label="🏆 Confirm Captain Appointment", style=discord.ButtonStyle.success)
        async def confirm_captain(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Add captain role
            try:
                guild = interaction.guild
                member = guild.get_member(self.user.id)
                captain_role = discord.utils.get(guild.roles, id=int(SPECIAL_ROLES['captain']))
                
                if member and captain_role:
                    await member.add_roles(captain_role)
            except:
                pass
            
            # Send congratulations DM
            try:
                captain_embed = discord.Embed(
                    title="🏆 CAPTAIN APPOINTMENT",
                    description=f"Congratulations {self.user.mention}!",
                    color=0xFFD700
                )
                
                captain_embed.add_field(
                    name="👑 You are now the Official Captain!",
                    value=f"**Reason for Appointment:** {self.reason}\n\n"
                          "**Captain Responsibilities:**\n"
                          "• Lead by example on and off the pitch\n"
                          "• Motivate and guide teammates\n"
                          "• Represent the club with honor",
                    inline=False
                )
                
                await self.user.send(embed=captain_embed)
            except:
                pass
            
            # Confirmation message
            embed = discord.Embed(
                title="👑 CAPTAIN APPOINTED",
                description=f"{self.user.mention} is now the official team captain!",
                color=0xFFD700
            )
            
            await interaction.response.edit_message(embed=embed, view=None)

    @bot.command()
    @is_admin()
    async def captain(ctx, member: discord.Member, *, reason):
        """Appoint a team captain"""
        embed = discord.Embed(
            title="👑 CAPTAIN APPOINTMENT",
            description=f"Appointing {member.mention} as team captain",
            color=0xFFD700
        )
        
        embed.add_field(
            name="📋 Appointment Details",
            value=f"**Player:** {member.mention}\n"
                  f"**Reason:** {reason}\n"
                  f"**Appointed by:** {ctx.author.mention}",
            inline=False
        )
        
        view = CaptainAppointmentView(member, reason)
        await ctx.send(embed=embed, view=view)

    # =================== LOA SYSTEM ===================
    class LOAView(discord.ui.View):
        def __init__(self, user, reason, date):
            super().__init__(timeout=None)
            self.user = user
            self.reason = reason
            self.date = date
            
        @discord.ui.button(label="✅ Approve LOA", style=discord.ButtonStyle.success)
        async def approve_loa(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Add LOA role
            try:
                guild = interaction.guild
                member = guild.get_member(self.user.id)
                loa_role = discord.utils.get(guild.roles, id=int(SPECIAL_ROLES['loa']))
                
                if member and loa_role:
                    await member.add_roles(loa_role)
            except:
                pass
            
            embed = discord.Embed(
                title="✅ LOA APPROVED",
                description=f"Leave of Absence approved for {self.user.mention}",
                color=0x00FF00
            )
            
            await interaction.response.edit_message(embed=embed, view=None)

    @bot.command()
    async def loa(ctx, reason: str, *, date: str):
        """Request Leave of Absence"""
        # Check if user is staff
        user_roles = [role.id for role in ctx.author.roles]
        staff_role_ids = list(STAFF_ROLES.values())
        
        if not any(int(role_id) in user_roles for role_id in staff_role_ids):
            await ctx.send("❌ Only staff members can request LOA.")
            return
        
        # Send to management channel
        channel = bot.get_channel(int(TRIALS_CHANNEL))
        if channel:
            embed = discord.Embed(
                title="📝 LEAVE OF ABSENCE REQUEST",
                description=f"**Staff Member:** {ctx.author.mention}",
                color=0xFFD700
            )
            
            embed.add_field(
                name="📋 LOA Details",
                value=f"**Reason:** {reason}\n"
                      f"**Return Date:** {date}\n"
                      f"**Requested:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
            
            view = LOAView(ctx.author, reason, date)
            await channel.send(embed=embed, view=view)
        
        await ctx.send("✅ Your LOA request has been submitted to management for review.")

    # =================== STAFF PROMOTION/DEMOTION ===================
    @bot.command()
    @is_admin()
    async def promotestaff(ctx, member: discord.Member, stafflevel: str, *, reason):
        """Promote staff member"""
        if stafflevel.lower() not in STAFF_ROLES:
            await ctx.send(f"❌ Invalid staff level. Valid levels: {', '.join(STAFF_ROLES.keys())}")
            return
        
        # Send notification DM
        try:
            promotion_embed = discord.Embed(
                title="📊 STAFF PROMOTION",
                description=f"Your staff position has been upgraded!",
                color=0x00FF00
            )
            
            promotion_embed.add_field(
                name="📋 Promotion Details",
                value=f"**New Position:** {stafflevel.replace('_', ' ').title()}\n"
                      f"**Reason:** {reason}\n"
                      f"**Promoted by:** {ctx.author.mention}",
                inline=False
            )
            
            await member.send(embed=promotion_embed)
        except:
            pass
        
        embed = discord.Embed(
            title="✅ STAFF PROMOTION COMPLETED",
            description=f"{member.mention} has been promoted!",
            color=0x00FF00
        )
        
        await ctx.send(embed=embed)

    # =================== STAT REMOVAL COMMANDS ===================
    @bot.command()
    @is_admin()
    async def removegoals(ctx, member: discord.Member, amount: int):
        """Remove goals from a player's stats"""
        player_data = get_player_data(member.id)
        old_goals = player_data['stats']['goals']
        player_data['stats']['goals'] = max(0, player_data['stats']['goals'] - amount)
        update_player_data(member.id, player_data)
        
        embed = discord.Embed(title="🗑️ Goals Removed", color=0xFF6347)
        embed.add_field(
            name="Statistics Updated",
            value=f"**Player:** {member.mention}\n"
                  f"**Goals Removed:** -{amount}\n"
                  f"**Total Goals:** {old_goals} → {player_data['stats']['goals']}",
            inline=False
        )
        await ctx.send(embed=embed)

    @bot.command()
    @is_admin()
    async def removeassists(ctx, member: discord.Member, amount: int):
        """Remove assists from a player's stats"""
        player_data = get_player_data(member.id)
        old_assists = player_data['stats']['assists']
        player_data['stats']['assists'] = max(0, player_data['stats']['assists'] - amount)
        update_player_data(member.id, player_data)
        
        embed = discord.Embed(title="🗑️ Assists Removed", color=0xFF6347)
        embed.add_field(
            name="Statistics Updated",
            value=f"**Player:** {member.mention}\n"
                  f"**Assists Removed:** -{amount}\n"
                  f"**Total Assists:** {old_assists} → {player_data['stats']['assists']}",
            inline=False
        )
        await ctx.send(embed=embed)

    @bot.command()
    @is_admin()
    async def removeappearances(ctx, member: discord.Member, amount: int):
        """Remove appearances from a player's stats"""
        player_data = get_player_data(member.id)
        old_appearances = player_data['stats']['appearances']
        player_data['stats']['appearances'] = max(0, player_data['stats']['appearances'] - amount)
        update_player_data(member.id, player_data)
        
        embed = discord.Embed(title="🗑️ Appearances Removed", color=0xFF6347)
        embed.add_field(
            name="Match Record Updated",
            value=f"**Player:** {member.mention}\n"
                  f"**Appearances Removed:** -{amount}\n"
                  f"**Total Appearances:** {old_appearances} → {player_data['stats']['appearances']}",
            inline=False
        )
        await ctx.send(embed=embed)

    # =================== ENHANCED REGISTER WITH LEVEL ===================
    @bot.command()
    @is_admin()
    async def registerwithlevel(ctx, member: discord.Member, level: str = "Reserve"):
        """Register a new player with custom level"""
        if level not in LEVEL_REQUIREMENTS:
            await ctx.send(f"❌ Invalid level. Valid levels: {', '.join(LEVEL_REQUIREMENTS.keys())}")
            return
        
        embed = discord.Embed(
            title="🏆 ARSENAL FC ELITE INVITATION",
            description=f"Hello {member.mention}!\n\nYou have been invited to join Arsenal FC as a **{level}** level player!",
            color=0xDC143C
        )
        
        try:
            await member.send(embed=embed)
            await ctx.send(f"✅ Elite registration invitation sent to {member.mention} for **{level}** level")
        except discord.Forbidden:
            await ctx.send(f"❌ Could not send DM to {member.mention}. They may have DMs disabled.")

    # =================== SAY COMMAND ===================
    @bot.command()
    @is_admin()
    async def say(ctx, *, message):
        """Send a message as the bot"""
        await ctx.message.delete()
        
        embed = discord.Embed(
            title="📢 ARSENAL FC ANNOUNCEMENT",
            description=message,
            color=0xDC143C
        )
        
        embed.set_footer(text="Official Arsenal FC Management")
        embed.set_thumbnail(url="https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png")
        
        await ctx.send(embed=embed)

    # =================== COMPREHENSIVE RESULTS SYSTEM ===================
    class MatchResultsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=600)
            self.home_team = None
            self.away_team = None
            self.home_score = None
            self.away_score = None
            
        @discord.ui.button(label="⚽ Set Teams & Score", style=discord.ButtonStyle.primary)
        async def set_teams_score(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = TeamsScoreModal(self)
            await interaction.response.send_modal(modal)
            
        @discord.ui.button(label="📊 Generate Result", style=discord.ButtonStyle.secondary)
        async def generate_result(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.home_team or not self.away_team:
                await interaction.response.send_message("❌ Please set teams and score first!", ephemeral=True)
                return
            
            # Generate beautiful result
            result_embed = discord.Embed(
                title="⚽ MATCH RESULT",
                color=0x00FF00 if self.home_score > self.away_score else 0xFF0000 if self.home_score < self.away_score else 0xFFD700
            )
            
            result_embed.add_field(
                name="🏟️ Final Score",
                value=f"**{self.home_team}** {self.home_score} - {self.away_score} **{self.away_team}**",
                inline=False
            )
            
            result_embed.add_field(
                name="📅 Match Details",
                value=f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
                      f"**Time:** {datetime.now().strftime('%H:%M')}\n"
                      f"**Recorded by:** {interaction.user.mention}",
                inline=False
            )
            
            result_embed.set_footer(text="Arsenal FC Official Result")
            
            await interaction.response.edit_message(embed=result_embed, view=None)

    class TeamsScoreModal(discord.ui.Modal):
        def __init__(self, results_view):
            super().__init__(title="⚽ Teams & Score")
            self.results_view = results_view
            
            self.home_team = discord.ui.TextInput(
                label="Home Team",
                placeholder="Enter home team name...",
                required=True
            )
            
            self.away_team = discord.ui.TextInput(
                label="Away Team", 
                placeholder="Enter away team name...",
                required=True
            )
            
            self.home_score = discord.ui.TextInput(
                label="Home Team Score",
                placeholder="0",
                required=True,
                max_length=2
            )
            
            self.away_score = discord.ui.TextInput(
                label="Away Team Score",
                placeholder="0", 
                required=True,
                max_length=2
            )
            
            self.add_item(self.home_team)
            self.add_item(self.away_team)
            self.add_item(self.home_score)
            self.add_item(self.away_score)
            
        async def on_submit(self, interaction: discord.Interaction):
            self.results_view.home_team = self.home_team.value
            self.results_view.away_team = self.away_team.value
            self.results_view.home_score = int(self.home_score.value)
            self.results_view.away_score = int(self.away_score.value)
            
            # Update embed
            embed = discord.Embed(
                title="⚽ MATCH RESULT BUILDER",
                description="Building comprehensive match result...",
                color=0x00FF00
            )
            
            embed.add_field(
                name="🏟️ Match Details",
                value=f"**{self.results_view.home_team}** {self.results_view.home_score} - {self.results_view.away_score} **{self.results_view.away_team}**",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self.results_view)

    # =================== ENHANCED OFFICE CALL ===================
    class OfficeCallView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            
        @discord.ui.button(label="🎧 Join Waiting Room", style=discord.ButtonStyle.primary)
        async def join_waiting_room(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                guild = interaction.guild
                waiting_room = guild.get_channel(int(WAITING_ROOM_VC))
                
                if waiting_room and interaction.user.voice:
                    await interaction.user.move_to(waiting_room)
                    await interaction.response.send_message("✅ You've been moved to the waiting room!", ephemeral=True)
                elif not interaction.user.voice:
                    await interaction.response.send_message("❌ You must be in a voice channel first!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Could not find the waiting room!", ephemeral=True)
            except:
                await interaction.response.send_message("❌ Error moving you to the waiting room!", ephemeral=True)

                # Optional: check token is loaded
if not TOKEN:
    print("❌ Bot token is missing! Check your .env file.")
    exit()

# Event to confirm bot is online
@bot.event
async def on_ready():
    print(f"✅ Bot is online! Logged in as {bot.user} (ID: {bot.user.id})")

# Start bot


# ----------------- Head of Staff System & Commands -----------------
MY_USER_ID = 769543470158970880  # your user ID
HEAD_OF_STAFF_ROLE_ID = 1416127117292470282 # head of staff role ID

def is_headofstaff():
    def predicate(ctx):
        return ctx.author.id == HEAD_OF_STAFF_ROLE_ID or ctx.author.id == MY_USER_ID or any(role.id == HEAD_OF_STAFF_ROLE_ID for role in ctx.author.roles)
    return commands.check(predicate)
    def predicate(ctx):
        try:
            # Check by role name
            role_name = STAFF_LEVEL_NAMES.get('head_of_staff', 'Head Of Staff')
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            
            # Check if user has the role by name OR by ID
            has_name_role = role in ctx.author.roles if role else False
            has_id_role = any(r.id ==HEAD_OF_STAFF_ROLE_ID  for r in ctx.author.roles)
            
            # Return True if user has either
            return has_name_role or has_id_role
        except:
            return False
    return commands.check(predicate)

@bot.command(name="headofstaff")
@is_headofstaff()
async def headofstaff(ctx):
    """Show Head of Staff command suite UI"""
    embed = discord.Embed(title="🛡️ Head of Staff Console", color=0x1ABC9C, timestamp=datetime.utcnow())
    embed.description = "Commands available to Head of Staff — use responsibly."
    embed.add_field(name="Recognition", value="`!sotw @user <reason>`\n`!commendation @user <reason>`\n`!staffmotm @user`\n`!recognize @user <achievement>`", inline=False)
    embed.add_field(name="Management", value="`!promote @user <level>`\n`!demote <level>`\n`!staffschedule`\n`!coverage @user`", inline=False)
    embed.add_field(name="Discipline", value="`!strike @user <reason>`\n`!removestrike @user`\n`!warn @user <reason>`\n`!note @user <note>`", inline=False)
    embed.add_field(name="Admin Tools", value="`!stafftraining @user <topic>`\n`!traininglist`\n`!setgoal @user <goal>`\n`!goalstatus @user`", inline=False)
    embed.set_footer(text="Head of Staff — trusted leadership tools")
    await ctx.send(embed=embed)

# Basic implementations of requested commands (safely)
@bot.command()
@is_headofstaff()
async def staffschedule(ctx):
    """View staff schedules (placeholder)."""
    # Attempt to load a schedules JSON if exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    sched_file = os.path.join(data_dir, "staff_schedules.json")
    if os.path.exists(sched_file):
        try:
            with open(sched_file,'r',encoding='utf-8') as f:
                schedules = json.load(f)
            # Simple text output
            lines = []
            for k,v in schedules.items():
                lines.append(f"**{k}**: {v}")
            await ctx.send("\n".join(lines) if lines else "No schedules found.")
            return
        except Exception as e:
            await ctx.send(f"❌ Error reading schedules: {e}")
            return
    await ctx.send("No staff schedules configured. Use `!training` or add schedules in data/staff_schedules.json")

@bot.command()
@is_headofstaff()
async def coverage(ctx, member: discord.Member=None):
    """Request coverage from staff for a member"""
    if member is None:
        await ctx.send("Usage: `!coverage @staff_member`")
        return
    await ctx.send(f"📢 Coverage requested for {member.mention} by {ctx.author.mention} — please react if available.")

@bot.command()
@is_headofstaff()
async def commendation(ctx, member: discord.Member=None, *, reason: str=None):
    if member is None or reason is None:
        await ctx.send("Usage: `!commendation @user <reason>`")
        return
    embed = discord.Embed(title="🌟 Commendation", description=f"{member.mention} has been commended!", color=0xFFD700, timestamp=datetime.utcnow())
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=f"By {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command()
@is_headofstaff()
async def staffmotm(ctx, member: discord.Member=None):
    if member is None:
        await ctx.send("Usage: `!staffmotm @user`")
        return
    await ctx.send(f"🏅 {member.mention} is nominated as Staff Member of the Month by {ctx.author.mention}.")

@bot.command()
@is_headofstaff()
async def recognize(ctx, member: discord.Member=None, *, achievement: str=None):
    if member is None or achievement is None:
        await ctx.send("Usage: `!recognize @user <achievement>`")
        return
    embed = discord.Embed(title="👏 Recognition", description=f"{member.mention} — {achievement}", color=0x00FF88, timestamp=datetime.utcnow())
    embed.set_footer(text=f"Nominated by {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command()
@is_headofstaff()
async def staffreport(ctx):
    await ctx.send("📄 Staff activity report generated (placeholder).")

@bot.command()
@is_headofstaff()
async def incidentreport(ctx, *, details: str=None):
    if details is None:
        await ctx.send("Usage: `!incidentreport <details>`")
        return
    await ctx.send(f"🚨 Incident reported: {details}\nReported by: {ctx.author.mention}")

@bot.command()
@is_headofstaff()
async def staffstats(ctx):
    await ctx.send("📊 Staff performance metrics (placeholder).")

@bot.command()
@is_headofstaff()
async def staffoftheweek(ctx, member: discord.Member=None, *, reason: str=None):
    if member is None or reason is None:
        await ctx.send("Usage: `!staffoftheweek @user <reason>`")
        return

    embed = discord.Embed(
        title="🏆 Staff of the Week",
        description=f"{member.mention} has been recognized for outstanding contributions!",
        color=0xFFD700,  # gold color
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(
        name="🎉 Congratulations!",
        value="You’ve been given **Staff of the Week** by the **Head of Staff**!",
        inline=False
    )
    embed.set_footer(text=f"Awarded by {ctx.author.display_name}")

    await ctx.send(embed=embed)

# Promote / Demote
@bot.command()
@is_headofstaff()
async def promote(ctx, member: discord.Member=None):
    if member is None:
        await ctx.send("Usage: `!promote @user`")
        return
    # attempt to find 'Staff' and 'Senior Staff' roles
    staff_role = discord.utils.get(ctx.guild.roles, name=STAFF_LEVEL_NAMES.get('staff','Staff'))
    senior_role = discord.utils.get(ctx.guild.roles, name=STAFF_LEVEL_NAMES.get('senior_staff','Senior Staff'))
    try:
        if staff_role and staff_role in member.roles and senior_role:
            await member.add_roles(senior_role)
            await ctx.send(f"✅ {member.mention} has been promoted to {senior_role.name}.")
        elif staff_role and staff_role not in member.roles and staff_role:
            await member.add_roles(staff_role)
            await ctx.send(f"✅ {member.mention} has been added to {staff_role.name}.")
        else:
            await ctx.send("Could not determine promotion target roles.")
    except Exception as e:
        await ctx.send(f"❌ Error promoting user: {e}")

@bot.command()
@is_headofstaff()
async def demote(ctx, member: discord.Member=None):
    if member is None:
        await ctx.send("Usage: `!demote @user`")
        return
    staff_role = discord.utils.get(ctx.guild.roles, name=STAFF_LEVEL_NAMES.get('staff','Staff'))
    senior_role = discord.utils.get(ctx.guild.roles, name=STAFF_LEVEL_NAMES.get('senior_staff','Senior Staff'))
    try:
        if senior_role and senior_role in member.roles:
            await member.remove_roles(senior_role)
            await ctx.send(f"✅ {member.mention} has been demoted from {senior_role.name}.")
        elif staff_role and staff_role in member.roles:
            await member.remove_roles(staff_role)
            await ctx.send(f"✅ {member.mention} has been removed from {staff_role.name}.")
        else:
            await ctx.send("No staff roles found to remove.")
    except Exception as e:
        await ctx.send(f"❌ Error demoting user: {e}")

# Discipline & staff management
@bot.command()
@is_headofstaff()
async def strike(ctx, member: discord.Member=None, *, reason: str=None):
    if member is None or reason is None:
        await ctx.send("Usage: `!strike @user <reason>`")
        return
    # store strike in data/strikes.json
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    strikes_file = os.path.join(data_dir, "strikes.json")
    strikes = {}
    if os.path.exists(strikes_file):
        try:
            with open(strikes_file,'r',encoding='utf-8') as f:
                strikes = json.load(f)
        except:
            strikes = {}
    user_id = str(member.id)
    strikes.setdefault(user_id, []).append({"by": ctx.author.id, "reason": reason, "time": datetime.utcnow().isoformat()})
    with open(strikes_file,'w',encoding='utf-8') as f:
        json.dump(strikes,f,indent=2)
    await ctx.send(f"✅ Strike recorded for {member.mention}. Total strikes: {len(strikes[user_id])}")

@bot.command()
@is_headofstaff()
async def removestrike(ctx, member: discord.Member=None):
    if member is None:
        await ctx.send("Usage: `!removestrike @user`")
        return
    strikes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "strikes.json")
    if not os.path.exists(strikes_file):
        await ctx.send("No strikes recorded.")
        return
    with open(strikes_file,'r',encoding='utf-8') as f:
        strikes = json.load(f)
    user_id = str(member.id)
    if user_id in strikes and strikes[user_id]:
        strikes[user_id].pop()
        with open(strikes_file,'w',encoding='utf-8') as f:
            json.dump(strikes,f,indent=2)
        await ctx.send(f"✅ Removed one strike for {member.mention}. Remaining: {len(strikes.get(user_id,[]))}")
    else:
        await ctx.send("No strikes to remove for that user.")

@bot.command()
@is_headofstaff()
async def setgoal(ctx, member: discord.Member=None, *, goal: str=None):
    if member is None or goal is None:
        await ctx.send("Usage: `!setgoal @user <goal>`")
        return
    goals_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "goals.json")
    goals = {}
    if os.path.exists(goals_file):
        try:
            with open(goals_file,'r',encoding='utf-8') as f:
                goals = json.load(f)
        except:
            goals = {}
    user_id = str(member.id)
    goals[user_id] = {"goal": goal, "set_by": ctx.author.id, "progress": 0, "time": datetime.utcnow().isoformat()}
    with open(goals_file,'w',encoding='utf-8') as f:
        json.dump(goals,f,indent=2)
    await ctx.send(f"✅ Goal set for {member.mention}: {goal}")

@bot.command()
@is_headofstaff()
async def goalstatus(ctx, member: discord.Member=None):
    if member is None:
        await ctx.send("Usage: `!goalstatus @user`")
        return
    goals_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "goals.json")
    if not os.path.exists(goals_file):
        await ctx.send("No goals set.")
        return
    with open(goals_file,'r',encoding='utf-8') as f:
        goals = json.load(f)
    user_id = str(member.id)
    g = goals.get(user_id)
    if not g:
        await ctx.send("No goal for that user.")
        return
    await ctx.send(f"Goal for {member.mention}: {g.get('goal')} (progress: {g.get('progress',0)}%)")

@bot.command()
@is_headofstaff()
async def stafftraining(ctx, member: discord.Member=None, *, topic: str=None):
    if member is None or topic is None:
        await ctx.send("Usage: `!stafftraining @user <topic>`")
        return
    training_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "trainings.json")
    trainings = {}
    if os.path.exists(training_file):
        try:
            with open(training_file,'r',encoding='utf-8') as f:
                trainings = json.load(f)
        except:
            trainings = {}
    trainings.setdefault(str(member.id), []).append({"topic": topic, "scheduled_by": ctx.author.id, "time": datetime.utcnow().isoformat()})
    with open(training_file,'w',encoding='utf-8') as f:
        json.dump(trainings,f,indent=2)
    await ctx.send(f"✅ Training scheduled for {member.mention}: {topic}")

@bot.command()
@is_headofstaff()
async def traininglist(ctx):
    training_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "trainings.json")
    if not os.path.exists(training_file):
        await ctx.send("No trainings scheduled.")
        return
    with open(training_file,'r',encoding='utf-8') as f:
        trainings = json.load(f)
    lines = []
    for uid, items in trainings.items():
        for it in items:
            lines.append(f"<@{uid}> — {it.get('topic')} (by <@{it.get('scheduled_by')}>)")
    await ctx.send("\n".join(lines) if lines else "No trainings found.")

@bot.command()
@is_headofstaff()
async def feedback(ctx, member: discord.Member=None, *, feedback_text: str=None):
    if member is None or feedback_text is None:
        await ctx.send("Usage: `!feedback @user <feedback>`")
        return
    # store private feedback
    fb_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "feedback.json")
    fb = {}
    if os.path.exists(fb_file):
        try:
            with open(fb_file,'r',encoding='utf-8') as f:
                fb = json.load(f)
        except:
            fb = {}
    fb.setdefault(str(member.id), []).append({"by": ctx.author.id, "text": feedback_text, "time": datetime.utcnow().isoformat()})
    with open(fb_file,'w',encoding='utf-8') as f:
        json.dump(fb,f,indent=2)
    await ctx.send(f"✅ Feedback recorded for {member.mention} (private).")

@bot.command()
@is_headofstaff()
async def warn(ctx, member: discord.Member=None, *, reason: str=None):
    if member is None or reason is None:
        await ctx.send("Usage: `!warn @user <reason>`")
        return
    await ctx.send(f"⚠️ Warning issued to {member.mention} by {ctx.author.mention}: {reason}")

@bot.command()
@is_headofstaff()
async def praise(ctx, member: discord.Member=None, *, reason: str=None):
    if member is None or reason is None:
        await ctx.send("Usage: `!praise @user <reason>`")
        return
    await ctx.send(f"👏 Praise for {member.mention}: {reason}")

@bot.command()
@is_headofstaff()
async def note(ctx, member: discord.Member=None, *, note_text: str=None):
    if member is None or note_text is None:
        await ctx.send("Usage: `!note @user <note>`")
        return
    notes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "notes.json")
    notes = {}
    if os.path.exists(notes_file):
        try:
            with open(notes_file,'r',encoding='utf-8') as f:
                notes = json.load(f)
        except:
            notes = {}
    notes.setdefault(str(member.id), []).append({"by": ctx.author.id, "note": note_text, "time": datetime.utcnow().isoformat()})
    with open(notes_file,'w',encoding='utf-8') as f:
        json.dump(notes,f,indent=2)
    await ctx.send(f"✅ Note added for {member.mention} (private).")

bot.run(TOKEN)
