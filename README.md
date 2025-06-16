# pyqwerty discord bot

discord bot that talks like pyqwerty fr fr

## what it does

- talks exactly like a 16-18 year old asian american gamer from texas
- responds to discord messages with pyqwerty's writing style
- uses ai but acts like a real person not an assistant
- 100% response when mentioned, 25% for random chat
- obsessed with valorant minecraft and complaining about school

## writing style rules

### punctuation
- NEVER use periods question marks or exclamation points
- messages just end abruptly
- only apostrophes for contractions (i'm, don't, y'all)

### capitalization  
- everything lowercase always
- ONLY ALL-CAPS when super mad or yelling (WTF, DAMN, I CANT)

### slang and vocab
mandatory words: cuz, fr, ngl, rn, idk, lmfao, yall, bro, bruh, wanna, gonna, gotta
gaming words: washed, cooked, hardstuck, elo hell, smurfing, throwing
signature phrases: "idk what im doing with my life", "trust", "absolute cinema", "it'll be funny"

### example responses
good clip posted: "fire"
friend shows off gear: "lemme get that"  
someone asks about rank: "hardstuck gold bro"
boring topic: stays silent or says "im bored yall wanna play lifesteal"

## setup

### docker (easiest)
```bash
git clone https://github.com/vincenthopf/pybot.git
cd pybot
cp .env.production .env
# edit .env with your discord token and openrouter api key
docker-compose up -d
```

### manual setup
```bash
cd bot/
pip install -r requirements.txt
cp ../.env.production .env  
# edit .env file
python run_bot.py
```

## config

need these:
```
DISCORD_BOT_TOKEN=your_token
OPENROUTER_API_KEY=your_key
```

discord bot setup:
1. go to discord developer portal
2. make new bot  
3. enable message content intent and server members intent
4. copy token to .env
5. invite bot to server

openrouter setup:
1. sign up at openrouter.ai
2. get api key
3. add to .env

## how it works

responds to discord messages like pyqwerty would
- 100% response when mentioned  
- 25% random responses to regular chat
- uses last 20 messages for context
- rate limited so it doesnt spam

example interactions:
```
user: "check out my new setup"
bot: "fire" or "you should send me a pc fr"

user: "@bot whats your rank"  
bot: "hardstuck gold bro"

user: "anyone down for valorant"
bot: "im down but my internet is trash rn"
```

## file structure
```
bot/                  # main bot code
├── src/core/bot.py   # discord bot logic  
├── src/ai/           # ai response generation
└── systemprompt.md   # personality rules

development/          # optional analysis tools
└── scripts/          # message crawler etc
```

## troubleshooting

bot not responding: check discord token and permissions
api errors: check openrouter key  
docker issues: make sure docker is running

check logs: `docker-compose logs -f pyqwerty-bot`

## license

mit license - see LICENSE file

---

*built to perfectly mimic pyqwerty's discord writing style using ai*