# **Game Activity Bot**  

A Discord bot that tracks and announces when members start or stop playing games. Perfect for gaming communities to stay informed about who's playing what!  

---  

## **Features**  
- Detects when members start or stop playing a game.  
- Posts embedded messages with playtime details in a designated channel.  
- Configurable options for excluded games, notification cooldowns, and check intervals.  
- Uses a default game icon for thumbnail consistency.  

---  

## **Setup**  

### **Prerequisites**  
Before you begin, ensure you have the following:  
- **Python 3.8+**  
- A **Discord Bot Token**  
- The `pip` package manager  
- Basic knowledge of using a terminal  

### **Installation**  

1. **Clone the Repository**  
   ```bash  
   git clone https://github.com/Timmy053/Game-Activity-Logger-.git  
   cd Game-Activity-Logger--bot

2. Install Dependencies
Install the required Python libraries:

pip install -r requirements.txt


3. Set Up Environment Variables

Create a .env file in the root directory.

Copy the structure from .env.example and fill in your bot token and other configurations:

TOKEN=your_discord_bot_token_here  
GUILD_ID=your_guild_id_here  
CHANNEL_ID=your_channel_id_here  
CHECK_INTERVAL=5  
COOLDOWN=20  
EXCLUDED_ACTIVITIES=example_game1,example_game2



4. Run the Bot
Start the bot using:

python main.py


---

How It Works

1. The bot periodically checks the presence of members in the server.


2. When a member starts or stops a game, the bot sends a notification in the configured channel.


3. Notifications include:

Member name and mention

Game name

Total playtime (when ending)

A default game icon thumbnail





---

Contributing

We welcome contributions! If you'd like to add features or fix bugs, follow these steps:

1. Fork the repository


2. Create a new branch (feature-name)


3. Commit your changes


4. Open a pull request




---

License

This project is licensed under the MIT License.

