docker compose exec -e ENABLE_EXCHANGE_RATES=true -w /app app php -d error_reporting=~E_DEPRECATED artisan route:list --json --no-ansi --no-interaction
