FOOTBALL MATCH CONNECTOR BOT
TELEGRAM + STRANDS AGENT + MCP SERVER

OVERVIEW

The goal is to build a Telegram bot that connects soccer players who want to play with organizers creating matches.

Users interact with a Telegram bot using natural language. The bot uses a Strands agent to understand the request and call tools hosted in an MCP server. The MCP server manages the business logic and database operations.

Players can find games and join them. Organizers can create games and specify match details. When a player joins a match, the bot shares contact information so the player and organizer can coordinate directly.

No Telegram groups are required. Communication happens directly between players and organizers.

SYSTEM ARCHITECTURE

Telegram Bot
Webhook API
Strands Agent
MCP Server
Database

Flow:

User sends message to Telegram bot

Telegram sends webhook request to backend

Backend forwards message to Strands agent

Agent interprets intent

Agent calls MCP tools

MCP server interacts with database

Result is returned to agent

Agent sends response back to Telegram bot

Bot replies to user

The agent never accesses the database directly. All business operations happen through MCP tools.

USER TYPES

Player
A person looking for a soccer match.

Example messages:
"I want to play soccer tonight"
"Any games near me?"
"I'm a goalkeeper looking for a game"

Capabilities:

search games

join games

specify preferred position

Organizer
A person creating a soccer match.

Example messages:
"Create a 7v7 game tomorrow at 8pm in Chapinero"

Capabilities:

create games

specify positions needed

specify field details

receive player contacts

CORE FEATURES

Create Game

Organizer provides:

location
date
time
game_type (5v5, 7v7, 11v11)
grass_type (natural or artificial)
players_needed
positions_needed

Example game:

Location: Chapinero
Date: tomorrow
Time: 8pm
Game type: 7v7
Grass type: artificial
Players needed: 4
Positions: goalkeeper, defender

Bot confirms creation and stores the game in the database.

Find Games

Player asks for available matches.

Example message:
"I want to play soccer tonight"

Agent calls find_games tool.

Bot responds with list of available matches.

Example:

Game 1
7v7 – Chapinero – 8pm
Need: defender

Game 2
5v5 – Usaquén – 9pm
Need: any player

User replies with a number to join.

Join Game

Player selects a match.

Agent calls join_game tool.

Player is added to the game.

Bot sends the organizer contact information to the player.

Example response:

You're in.

Organizer contact: @juanfootball

Send them a message to coordinate the match.

The organizer also receives a notification.

Example organizer message:

A player joined your game.

Name: Esteban
Telegram: @esteban23
Position: defender

AGENT RESPONSIBILITIES

The Strands agent performs the following tasks:

Understand user intent
Extract relevant parameters
Decide which MCP tool to call
Format responses for Telegram users

Example flow:

User message:
"I want to play soccer tonight"

Agent identifies intent: find_match

Agent calls tool: find_games

Agent formats the response and sends game options.

MCP SERVER RESPONSIBILITIES

The MCP server exposes tools used by the agent.

Responsibilities:

validate inputs
execute business logic
interact with database
return structured results

The agent only orchestrates the tools.

MCP TOOLS

create_game

Purpose: create a soccer match.

Inputs:

organizer_id
organizer_username
location
date
time
game_type
grass_type
players_needed
positions_needed

Output:

game_id
status

find_games

Purpose: search available matches.

Inputs:

location
date
position (optional)

Output:

list of games including:

game_id
location
time
game_type
players_needed
positions_needed

join_game

Purpose: add a player to a match.

Inputs:

game_id
player_id
player_username
position

Output:

status
organizer_username

get_game_details

Purpose: retrieve match details.

Inputs:

game_id

Output:

location
date
time
game_type
grass_type
players_needed

DATABASE MODEL

Users table

id
telegram_id
username
name
preferred_position
skill_level
location
created_at

Games table

id
organizer_id
location
date
time
game_type
grass_type
players_needed
status
created_at

Game_players table

game_id
player_id
position
status
joined_at

Status values:

joined
confirmed
cancelled

TELEGRAM BOT RESPONSIBILITIES

The Telegram bot handles:

receiving messages from users
sending messages back to users
forwarding user messages to the Strands agent
returning the agent response to Telegram

Telegram automatically provides user identity information including:

telegram_id
username
first_name

No login system is required.

MCP SERVER STRUCTURE

Recommended directory layout:

mcp_server

tools
create_game
find_games
join_game
get_game_details

services
game_service
user_service

database
models
database_connection

server

Each tool should call a service layer, and services interact with the database.

EXAMPLE USER INTERACTION

User message:

I want to play soccer tonight

Bot response:

I found 2 games near you.

7v7 – Chapinero – 8pm – need defender

5v5 – Usaquén – 9pm – any player

Reply with the number of the game you want to join.

User response:

1

Bot response:

You're in.

Organizer contact: @juanfootball

Send them a message to coordinate the match.

Organizer notification:

A player joined your game.

Name: Esteban
Telegram: @esteban23
Position: defender

MVP SCOPE

For the first version implement only:

create_game
find_games
join_game

Skip advanced features for now.

Do not implement:

payments
ratings
field booking
skill matching algorithms

Focus only on connecting players with games.

FUTURE FEATURES

Player ratings after matches

Skill level matching

Automated game suggestions

Example:

"A match near you needs a goalkeeper tonight."

Weekly recurring matches

Example:

"I want to play every Tuesday."

Automatic team balancing

Field booking integrations

Push notifications for new matches nearby

PROJECT GOAL

Reduce the friction of finding amateur soccer matches.

The bot should allow a user to go from:

"I want to play soccer"

to

"Here is the organizer you can contact"

in less than 30 seconds.