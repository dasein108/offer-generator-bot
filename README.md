# SMM Offer Generator

Telegram bot to generate SMM offers by short description.

 - Bot based on telegram WebApp feature
 - Uses DeepL api to generate auto-translations for UI. 
 - Uses ChatGPT to generate offers

## Run

 - Create `.env` file and add 3 variables: 
	 - `OPEN_AI_API_KEY=...`
	 - `DEEPL_API_KEY=...`
	 - `TELEGRAM_BOT_TOKEN=...`
 -  To use Telegram WebApp you should obtain domain name and link it to Caddy `build/caddy/Caddyfile` **OR** deploy `static` folder content somewhere.
 - Launch `docker-compose up`

## Deploy

 - Tiny example of deploy script for Gitlab CI is attached  `.gitlab-ci.yml`
