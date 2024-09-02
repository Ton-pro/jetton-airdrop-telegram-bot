# Jetton Airdrop Telegram Bot

**⚡️Important note: you are able to deploy advanced stable version of this bot in 10 minutes via https://t.me/ez_airdrop_bot**

__________________

To run a telegram bot, you will need any server with a Linux operating system and docker and docker-compose installed
Clone the repository
```
git clone https://github.com/Ton-pro/jetton-airdrop-telegram-bot.git
```
Go to the folder with the project
```
cd jetton-airdrop-telegram-bot
```
Copy .env file from the example
```
cp config/.env.example config/.env
```
Fill in the .env file
```
nano config/.env
```
Launch containers with a bot and a database
```
docker-compose up -d
```

### Additional info

For create self Jetton - https://minter.ton.org
Texts are edited in a _texts.json_ file

* **AIRDROP_START_DATE** - Start date in format '00:00 01.06.2024'
* **AIRDROP_END_DATE** - End date in format '00:00 01.08.2024' (not requered)
* **INITIAL_BALANCE** - Amount of jettons that are given when completing a subscription task (after start bot cannot be updated)
* **INITIAL_REFERRAL_TOKENS** - Amount of jettons for the first level of referrals
* **SECOND_LEVEL_REFERRAL_TOKENS** - Amount of jettons for the second level of referrals
* **CHANNELS_LIST** - Chat/channel name without @ comma separated (example: tonpro_for_builders,tonpro_me_chat) (after start bot cannot be updated)
* **AIRDROP_AMOUNT** - Amount of jettons which you want to give away (after start bot cannot be updated)
* **AIRDROP_MAX_COUNT_USERS** - Maximum number of participants (after start bot cannot be updated)
* **AIRDROP_JETTON_WALLET** and  **AIRDROP_JETTON_MASTER** - From https://tonviewer.com (example: https://tonviewer.com/EQDQrN8WA4gPzPhQSLu5u6866hTlaRxPP5TJwfZ2adjqzEZ3/jetton/EQDHHg9keNBZ1ghZ1HtWRYnqSEPXYFoLmBqE1dTN0q7JIjDq) (after start bot cannot be updated)
* **AIRDROP_JETTON_NAME** - Coin symbol (after start bot cannot be updated)
* **BOT_API_TOKEN** - From @BotFather
* **TONCENTER_API** - Key from @tonapibot
* **LINK** - Bot link without @ (example: jetton_airdrop_telegram_bot)
* **MNEMONICS** - mnemonic phrase from Jetton wallet holder

For stop containers
```
docker-compose down
```

For clear database
```
docker volume rm jetton-airdrop-telegram-bot_postgres_data
```
