#/bin/bash

docker stop fastapi_rtk-postgres
docker remove fastapi_rtk-postgres
docker run --name fastapi_rtk-postgres -e POSTGRES_PASSWORD=postgres -d -p 5433:5432 postgres:alpine
is_ready() {
    docker exec fastapi_rtk-postgres pg_isready -U postgres
}
until is_ready; do
    echo >&2 "Postgres is unavailable - sleeping"
    sleep 1
done

docker exec -it fastapi_rtk-postgres psql -U postgres -c "CREATE DATABASE fastapi_rtk;"
echo "Database fastapi_rtk created"
docker exec -it fastapi_rtk-postgres psql -U postgres -c "CREATE DATABASE fastapi_rtk_assets;"
echo "Database fastapi_rtk_assets created"

cmd_to_run="CREATE USER fastapi_rtk WITH PASSWORD 'fastapi_rtk'; GRANT ALL PRIVILEGES ON SCHEMA public TO fastapi_rtk;"
cmd_to_run_assets="GRANT ALL PRIVILEGES ON SCHEMA public TO fastapi_rtk;"

docker exec -it fastapi_rtk-postgres psql -U postgres -d fastapi_rtk -c "$cmd_to_run"
docker exec -it fastapi_rtk-postgres psql -U postgres -d fastapi_rtk_assets -c "$cmd_to_run_assets"

echo "User fastapi_rtk with password fastapi_rtk created"
echo "Postgres is running on port 5433"
