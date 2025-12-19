# Orbital Parcel Ops 🚀📦

Sistema de seguimiento de paquetes interplanetarios basado en AWS Lambda, API Gateway y RDS PostgreSQL.

## Arquitectura

- **Backend:** Python 3.11 (Lambda)
- **API:** API Gateway REST
- **Base de Datos:** RDS PostgreSQL (free tier: db.t3.micro)
- **Infraestructura:** OpenTofu/Terraform
- **CI/CD:** GitHub Actions

## Estructura del Proyecto

```
orbital-parcel-ops/
├── infra/                  # OpenTofu (Terraform)
│   ├── main.tf            # Configuración principal
│   ├── lambda.tf          # Lambda function
│   ├── api_gateway.tf     # API Gateway
│   ├── rds.tf             # RDS PostgreSQL
│   ├── vpc.tf             # VPC, subnets, NAT
│   ├── variables.tf       # Variables
│   ├── outputs.tf         # Outputs
│   └── versions.tf        # Providers
│
├── backend/
│   ├── app/
│   │   ├── main.py        # Entrypoint Lambda
│   │   ├── db.py          # Conexión DB
│   │   ├── models.py      # Queries SQL
│   │   ├── handlers/      # Handlers CRUD
│   │   │   ├── packages.py
│   │   │   ├── scans.py
│   │   │   └── ops.py
│   │   └── utils.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/             # Tests unitarios
│
├── scripts/
│   ├── package_lambda.sh  # Empaquetar Lambda
│   ├── schema.sql         # Migraciones SQL
│   └── seed.py            # Seed de datos
│
├── Makefile
└── README.md
```

## Setup Local

### 1. Clonar repositorio

```bash
git clone <repo-url>
cd Orbital-Parcel-Ops
```

### 2. Crear entorno virtual Python

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Ejecutar tests

```bash
# Desde el directorio raíz
make test

# O directamente
cd backend
pytest -v
```

## Quick Start: Despliegue en AWS (5-15 min)

```bash
# 1. Configurar AWS
aws configure  # Ingresa access key, secret key, región (us-east-1)

# 2. Instalar OpenTofu
# En macOS: brew install opentofu
# En Linux: https://opentofu.org/docs/intro/install/
# En Windows: choco install opentofu

# 3. Empaquetar Lambda
make package

# 4. Desplegar infraestructura
cd infra

# Configurar variables
export TF_VAR_db_password="ChangeMe123!"  # Cambiar a contraseña fuerte

# Inicializar Terraform
tofu init

# Ver cambios (opcional)
tofu plan

# Aplicar (tarda ~10-15 min)
tofu apply

# Obtener URL de la API
API_URL=$(tofu output -raw api_url)
echo "API: $API_URL"

# 5. Ejecutar migraciones y seed
cd ..
DB_HOST=$(cd infra && tofu output -raw db_endpoint | cut -d: -f1)
export DATABASE_URL="postgresql://postgres:ChangeMe123!@$DB_HOST:5432/orbital_parcel_ops"

make migrate
make seed

# 6. Testear API
curl "$API_URL/health"
curl "$API_URL/packages" | python -m json.tool
```

### Detener costos: Destruir infraestructura

```bash
cd infra
tofu destroy  # Responder 'yes' para confirmar
```

---

## Despliegue en AWS (Detallade)

### Prerequisitos

- AWS CLI configurado (`aws configure`)
- OpenTofu o Terraform instalado
- Credenciales AWS con permisos para Lambda, RDS, VPC, API Gateway

### Costos estimados (capa gratuita)

**Free tier (primeros 12 meses):**
- Lambda: 1M invocaciones/mes + 400K GB-segundo gratis
- API Gateway: 1M llamadas/mes gratis
- RDS PostgreSQL db.t3.micro: 750 horas/mes gratis
- 20 GB almacenamiento RDS gratis

**Costos fuera de free tier:**
- NAT Gateway: ~$0.045/hora (~$32/mes) — **puedes comentar esto en `vpc.tf` si no necesitas internet desde Lambda**
- RDS después de 750 horas: ~$0.017/hora (~$12/mes para db.t3.micro)

### Paso 1: Empaquetar Lambda

```bash
make package
# O manualmente:
bash scripts/package_lambda.sh
```

Esto crea `backend/build/lambda.zip` con código y dependencias.

### Paso 2: Configurar variables Terraform

Crea un archivo `infra/terraform.tfvars`:

```hcl
aws_region  = "us-east-1"
environment = "dev"
db_name     = "orbital_parcel_ops"
db_username = "postgres"
db_password = "TU_PASSWORD_SEGURO"  # Usa secretos en producción
```

**Importante:** No commitees `terraform.tfvars` con contraseñas. Usa variables de entorno:

```bash
export TF_VAR_db_password="tu_password_seguro"
```

### Paso 3: Inicializar Terraform

```bash
cd infra
tofu init  # O terraform init
```

### Paso 4: Planificar despliegue

```bash
tofu plan
```

Revisa los recursos que se van a crear (VPC, RDS, Lambda, API Gateway, etc.).

### Paso 5: Aplicar infraestructura

```bash
tofu apply
```

Confirma con `yes`. Esto tarda ~10-15 minutos (RDS tarda en crear).

### Paso 6: Obtener URL de la API

```bash
tofu output api_url
```

Ejemplo de salida: `https://abc123.execute-api.us-east-1.amazonaws.com/dev`

### Paso 7: Ejecutar migraciones

```bash
# Obtener endpoint de RDS
DB_HOST=$(tofu output -raw db_endpoint | cut -d: -f1)

# Conectar y ejecutar schema
export DATABASE_URL="postgresql://postgres:TU_PASSWORD@$DB_HOST:5432/orbital_parcel_ops"
make migrate
```

### Paso 8: Seed de datos (opcional)

```bash
make seed
```

## API Endpoints

Base URL: `https://<api-id>.execute-api.us-east-1.amazonaws.com/dev`

### Health Check

```bash
GET /health
```

Respuesta:
```json
{"status": "ok"}
```

### Packages

**Listar paquetes**
```bash
GET /packages?limit=50
```

**Obtener paquete**
```bash
GET /packages/{id}
```

**Crear paquete**
```bash
POST /packages
Content-Type: application/json

{
  "tracking_number": "PKG-001",
  "status": "pending",
  "origin": "New York, NY",
  "destination": "Los Angeles, CA",
  "weight_kg": 2.5
}
```

**Actualizar estado**
```bash
PUT /packages/{id}
Content-Type: application/json

{
  "status": "in_transit"
}
```

### Scans

**Listar scans**
```bash
GET /scans?limit=50
GET /scans?package_id=1
```

**Registrar scan**
```bash
POST /scans
Content-Type: application/json

{
  "package_id": 1,
  "location": "NYC Hub",
  "scan_type": "checkpoint"
}
```

## Comandos útiles

```bash
# Empaquetar Lambda
make package

# Ejecutar tests
make test

# Seed de datos
make seed

# Migraciones
make migrate

# Ver logs Lambda (requiere AWS CLI)
aws logs tail /aws/lambda/orbital-parcel-ops-api --follow

# Ver estado de Terraform
cd infra && tofu show

# Destruir infraestructura (¡cuidado!)
cd infra && tofu destroy
```

## OpenTofu

### Primer paso: Infraestructura base

1. Configurar AWS CLI con `access-key` y `secret-key`
2. Crear archivos Terraform base (Lambda, IAM, API Gateway)
3. Ejecutar `tofu plan` para visualizar cambios
4. Aplicar con `tofu apply`

### Recursos creados

- VPC con subnets públicas y privadas
- RDS PostgreSQL (db.t3.micro, free tier)
- Lambda function con VPC access
- API Gateway REST API
- Security Groups
- IAM Roles y policies
- Secrets Manager para credenciales DB
- CloudWatch Logs

## CI/CD

GitHub Actions workflow en `.github/workflows/ci.yml`:

- Ejecuta tests en cada push/PR
- Instala dependencias
- Corre pytest

Para añadir despliegue automático, añade:
- Secretos AWS en GitHub
- Step para empaquetar Lambda
- Step para `tofu apply`

## Desarrollo

### Añadir nuevos endpoints

1. Crear handler en `backend/app/handlers/`
2. Añadir ruta en `backend/app/main.py`
3. Añadir tests en `backend/tests/`
4. Ejecutar `make test`

### Modificar schema DB

1. Editar `scripts/schema.sql`
2. Ejecutar `make migrate`

## Troubleshooting

### ⚠️ **IMPORTANTE: Problema de psycopg2 en Lambda**

**Problema:** Lambda puede fallar con error `No module named 'psycopg2._psycopg'` o `no pq wrapper available`.

**Causa:** `psycopg2` y `psycopg[binary]` requieren compilación de extensiones C que no están disponibles en el entorno de Lambda (Amazon Linux 2). El paquete compilado localmente en macOS/Linux no es compatible con Lambda.

**Solución:** Este proyecto usa **`pg8000`** en lugar de `psycopg2`:

```python
# backend/requirements.txt
pg8000>=1.29.0  # Pure Python PostgreSQL driver, sin dependencias C
```

- ✅ Compatible con Lambda sin compilación
- ✅ No necesita libpq
- ✅ Soporta conexión por DATABASE_URL
- ✅ API similar a psycopg2

Si necesitas migrar a otro driver:
- **No uses:** `psycopg2`, `psycopg2-binary`, `psycopg[binary]`
- **Sí usa:** `pg8000`, `pymysql` (para MySQL), o compila en Docker con imagen `python:3.11`

### Lambda no puede conectar a RDS

1. **Verificar security groups:**
   ```bash
   # Lambda SG debe permitir egress a RDS SG en puerto 5432
   aws ec2 describe-security-groups --group-ids sg-lambda sg-rds
   ```

2. **Verificar subnets:**
   - Lambda debe estar en subnets privadas
   - RDS debe estar en el mismo VPC
   - Si RDS está en subnet pública, asegurar que tiene public IP y `publicly_accessible=true` (solo para migraciones)

3. **Revisar logs Lambda:**
   ```bash
   aws logs tail /aws/lambda/orbital-parcel-ops-api --follow --since 5m
   ```

4. **Testear conexión manual:**
   ```bash
   export DATABASE_URL="postgresql://postgres:PASSWORD@RDS_HOST:5432/orbital_parcel_ops"
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

### Tests fallan con import errors

- Asegúrate de activar el virtualenv: `source backend/.venv/bin/activate`
- Verificar que `conftest.py` existe en `backend/tests/`
- Ejecutar desde el directorio raíz: `make test`

### NAT Gateway muy caro

Comenta el recurso `aws_nat_gateway` y `aws_eip` en `infra/vpc.tf` si no necesitas que Lambda acceda a internet. 

**Nota:** Sin NAT Gateway, Lambda no podrá:
- Hacer requests a APIs públicas
- Acceder a internet
- Actualizar paquetes en tiempo de ejecución

RDS seguirá siendo accesible sin NAT porque está en el mismo VPC.

### Costo estimado sin NAT

- Lambda: Gratis (1M invocaciones/mes)
- API Gateway: Gratis (1M llamadas/mes)
- RDS: Gratis (db.t3.micro, 750 horas/mes)
- **Total: ~$0 en free tier** ✅

## Despliegue Producción

### Seguridad

1. **No uses `terraform.tfvars` con secretos** — Usa variable de entorno:
   ```bash
   export TF_VAR_db_password="secure_password"
   tofu apply  # No incluye contraseña en archivos
   ```

2. **Almacena credenciales en AWS Secrets Manager:**
   ```hcl
   # infra/rds.tf ya lo hace
   resource "aws_secretsmanager_secret_version" "db_credentials" {
     secret_id = aws_secretsmanager_secret.db_credentials.id
     secret_string = jsonencode({
       username = var.db_username
       password = var.db_password
       ...
     })
   }
   ```

3. **Cierra RDS a internet:**
   ```hcl
   # infra/rds.tf - Producción
   publicly_accessible = false  # Solo acceso desde Lambda
   ```

4. **Usa HTTPS en API Gateway** (AWS lo maneja automáticamente)

### Backups

```hcl
# infra/rds.tf - ya configurado
backup_retention_period = 7  # 7 días de retención
backup_window = "03:00-04:00"  # Horario UTC
skip_final_snapshot = false  # Tomar snapshot antes de destruir
```

### Monitoreo

```bash
# Ver logs
aws logs tail /aws/lambda/orbital-parcel-ops-api --follow

# Ver métricas Lambda
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=orbital-parcel-ops-api \
  --start-time 2025-12-19T00:00:00Z \
  --end-time 2025-12-19T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

## License

MIT