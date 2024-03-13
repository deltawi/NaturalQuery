docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d -v ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql postgres
