# Jetton Airdrop Telegram Bot

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
cp confif/.env.example confif/.env
```
Fill in the .env file
```
nano .env
```
Launch containers with a bot and a database
```
docker-compose up -d
```