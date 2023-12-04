import dotenv
dotenv.load_dotenv()

# load in default active host
import data.hosts

from bot import main

main()