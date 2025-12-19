# Orbital Parcel Ops - Resumen de Despliegue

**Fecha:** 19 de diciembre de 2025  
**Proyecto:** Orbital Parcel Ops - Sistema de rastreo de paquetes en AWS Lambda + RDS

---

## 🎯 Características Clave

✅ **Lambda:** Python 3.11 + pg8000 (driver PostgreSQL pure Python, sin dependencias C)  
✅ **Base de Datos:** RDS PostgreSQL 15.8 (compatible con capa gratuita)  
✅ **API:** Endpoints RESTful para CRUD de paquetes y escaneos  
✅ **Seguridad:** RDS en subnet privada, Lambda en VPC, credenciales en Secrets Manager  
✅ **Datos:** 10 paquetes semilla + 15 escaneos pre-poblados  
✅ **Monitoreo:** CloudWatch Logs para Lambda  
✅ **Infrastructure as Code:** OpenTofu/Terraform  
✅ **CI/CD:** GitHub Actions (pruebas automáticas en cada push)

---

## 💰 Desglose de Costos (Capa Gratuita, 12 meses)

| Servicio | Capa Gratuita | Costo |
|----------|---------------|--------|
| Lambda | 1M solicitudes/mes + 400K GB-segundos | $0 |
| API Gateway | 1M llamadas/mes | $0 |
| RDS (db.t3.micro) | 750 horas/mes + 20GB almacenamiento | $0 |
| **Total** | | **$0/mes** ✅ |

**Nota:** NAT Gateway está comentado. Costaría +$32/mes si se habilitara.

---

## 🔗 Endpoints de la API

**URL Base:** `https://c35genorc3.execute-api.us-east-1.amazonaws.com/dev`

```bash
# Verificación de salud
GET /health → {"status": "ok"}

# Paquetes
GET    /packages              # Listar todos
GET    /packages/{id}         # Obtener uno
POST   /packages              # Crear
PUT    /packages/{id}         # Actualizar estado

# Escaneos
GET    /scans                 # Listar todos
GET    /scans?package_id=N    # Filtrar por paquete
POST   /scans                 # Crear
```

---

## 🔐 Estado de Seguridad

✅ **RDS:** Subnet privada, sin acceso público  
✅ **Lambda:** Habilitado en VPC, grupos de seguridad restringidos  
✅ **Secrets:** Credenciales de base de datos en AWS Secrets Manager  
✅ **API:** HTTPS obligatorio (API Gateway)  
✅ **Contraseña de BD:** Generada de forma segura  

---

## 📝 Decisiones Clave y Resolución de Problemas

### Problema: psycopg2 en Lambda

❌ **Intentos Fallidos:** `psycopg2-binary`, `psycopg2`, `psycopg[binary]`
- Error: `No module named 'psycopg2._psycopg'` / `no pq wrapper available`
- Causa raíz: Desajuste de compilación de extensiones C entre el SO local y Amazon Linux 2

✅ **Solución:** Migrar a **pg8000**
- Driver PostgreSQL en pure Python
- Sin dependencias C = compatible instantáneamente con Lambda
- Ligero (4.6MB vs 8.8MB+)
- Mismo patrón de API que psycopg2

**Implementación:**
```python
# backend/requirements.txt
pg8000>=1.29.0

# backend/app/db.py
import pg8000.dbapi
conn = pg8000.dbapi.connect(user=..., password=..., host=..., port=5432, database=...)
```

---

## 🚀 Cómo Desplegar (Para el Siguiente Desarrollador)

### Inicio Rápido (5-15 minutos)

```bash
# 1. Clonar y configurar
git clone <repo>
cd Orbital-Parcel-Ops
cd backend && pip install -r requirements.txt && cd ..

# 2. Configurar AWS
aws configure  # Región: us-east-1

# 3. Desplegar infraestructura
cd infra
export TF_VAR_db_password="MiContraseñaSegura123!"
tofu init
tofu apply  # ~10-15 minutos

# 4. Ejecutar migraciones
cd ..
export DATABASE_URL="postgresql://postgres:MiContraseñaSegura123!@HOST_RDS:5432/orbital_parcel_ops"
make migrate && make seed

# 5. Probar
curl https://APIID.execute-api.us-east-1.amazonaws.com/dev/health
```

**Consultar README.md para instrucciones detalladas.**

---

## 📋 Pruebas

Todas las pruebas pasan:
```bash
cd backend
pytest -v

# O desde la raíz
make test
```

La cobertura incluye:
- Endpoint de salud
- CRUD de paquetes
- Operaciones de escaneos
- Conectividad a la base de datos

---

## 📚 Documentación

- **README.md** - Guía completa de configuración y solución de problemas
- **infra/*.tf** - Infrastructure as Code (bien comentado)
- **backend/app/*.py** - Código de aplicación con docstrings
- **backend/tests/*.py** - Cobertura de pruebas

---

## ⚠️ Notas Importantes

1. **Formato de URL de Base de Datos:** `postgresql://usuario:contraseña@host:puerto/basededatos`
   - RDS solo es accesible desde Lambda en esta configuración
   - Para migraciones locales, establecer temporalmente `publicly_accessible = true` en `rds.tf`

2. **Gestión de Credenciales:**
   - NO confirmar `terraform.tfvars` con contraseñas
   - Usar variables de entorno: `export TF_VAR_db_password="..."`
   - O integración con AWS Secrets Manager

3. **Limpieza:**
   ```bash
   cd infra && tofu destroy  # Elimina todos los recursos de AWS
   ```

---

## 🔄 Próximos Pasos (Opcionales)

- [ ] Agregar límite de velocidad a API Gateway
- [ ] Implementar versionado de funciones Lambda
- [ ] Configurar alarmas de CloudWatch para errores
- [ ] Agregar DynamoDB para cacheo
- [ ] Implementar failover multi-región
- [ ] Agregar autenticación de API (API keys u OAuth)
- [ ] Configurar escaneo de seguridad automatizado

---

**Estado:** ✅ Listo para evaluación / demostración  
**Última Actualización:** 2025-12-19  
**Infraestructura:** AWS (OpenTofu/Terraform)  
**Backend:** Python 3.11  
**Base de Datos:** PostgreSQL 15.8
