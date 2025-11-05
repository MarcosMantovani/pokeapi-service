up:
	docker-compose -f docker-compose.yml stop && docker-compose -f docker-compose.yml up

watch:	
	docker-compose -f docker-compose.yml stop && docker-compose -f docker-compose.yml up -d && docker logs -f --since 5m pokeapi-service

watch-scheduler:	
	docker-compose -f docker-compose.yml stop && docker-compose -f docker-compose.yml up -d && docker logs -f --since 5m pokeapi-service

watch-evolution:	
	docker-compose -f docker-compose.yml stop && docker-compose -f docker-compose.yml up -d && docker logs -f --since 5m pokeapi-service

stop:
	docker-compose -f docker-compose.yml stop

down:
	docker-compose -f docker-compose.yml down -v	

build:
	docker-compose -f docker-compose.yml down && docker-compose -f docker-compose.yml up --build pokeapi-service pokeapi-scheduler && docker logs -f pokeapi-service

bash:
	docker exec -it pokeapi-service bash

bash-scheduler:
	docker exec -it pokeapi-scheduler bash

bash-evolution:
	docker exec -it pokeapi-evolution bash

deploy:
	docker compose -f docker-compose-prod.yml stop pokeapi-service pokeapi-scheduler && git pull && docker compose -f docker-compose-prod.yml up -d --build pokeapi-service pokeapi-scheduler

run:
	docker compose -f docker-compose-prod.yml stop pokeapi-service pokeapi-scheduler && docker compose -f docker-compose-prod.yml up -d pokeapi-service pokeapi-scheduler

scheduler-logs:
	docker logs -f --since 10m pokeapi-scheduler

service-logs:
	docker logs -f --since 10m pokeapi-service

evolution-logs:
	docker logs -f --since 10m pokeapi-evolution
