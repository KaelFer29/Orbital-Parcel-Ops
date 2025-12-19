.PHONY: build test package seed migrate

build:
	@echo "🔨 Building Lambda package..."
	@bash scripts/package_lambda.sh

test:
	@echo "🧪 Running tests..."
	cd backend && . .venv/bin/activate && pytest -v

package: build

seed:
	@echo "🌱 Seeding database..."
	cd backend && . .venv/bin/activate && python ../scripts/seed.py

migrate:
	@echo "📊 Running migrations..."
	@if [ -z "$$DATABASE_URL" ]; then echo "❌ DATABASE_URL not set"; exit 1; fi
	psql $$DATABASE_URL < scripts/schema.sql
