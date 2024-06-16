# Auto-BullBot-bot

Auto-BullBot-bot is a Python-based automation script for interacting with the BullApp bot on Telegram. The Auto-BullBot-bot is designed to automate several actions within the BullApp bot on Telegram. It can automatically claim rewards, collect daily bonuses, purchase boosters, and complete various tasks. This makes it an efficient tool for users who want to maximize their gains and streamline their interactions with the BullApp bot, ensuring they never miss out on potential rewards and benefits.

## Setup

1. **Clone the repository:**

   ```sh
   git clone [git@github.com:NailAmber/Auto-BullBot-bot.git](https://github.com/NailAmber/Auto-BullBot-bot.git)
   cd Auto-BullBot-bot 
   ```

2. **Create a virtual environment**:

    On Windows:

    ```sh

    python -m venv /path/to/new/virtual/environment
    ```  
Activate the virtual environment:

  On Windows:

  ```sh

  .\path\to\new\virtual\environment\Scripts\activate
  ```

Install the required packages:

```sh
pip install -r requirements.txt
```

### Configuration
1. Get api id and api hash from here https://my.telegram.org/auth
2. Put your Api in `/data/api_config.json`:
  ```json
    {
        "+PhoneNumber" : [Api_id, "Api_hash"]
    }
  ```

