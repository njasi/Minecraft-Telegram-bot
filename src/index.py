import dotenv

# load env before anything
dotenv.load_dotenv()

# load in defaults and init
import data.hosts
from data.users import init_users

init_users()

# now import the bot and set up
from bot import main

main()
