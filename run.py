#Run this file to start the bot.
from music import *
from main import *

#Your token here:
with open ("token.txt", "r") as TokenFile:
    TOKEN = TokenFile.read()

if __name__ == '__main__':
    bot.run(TOKEN)