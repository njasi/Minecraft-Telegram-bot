import dotenv
dotenv.load_dotenv()

# load in default active host
import minecraft.hosts

from bot import main

main()