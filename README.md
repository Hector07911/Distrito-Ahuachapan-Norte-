# Sistema de Gestión Municipal de Empresas

## 🎯 Objetivo

**Centralizar, ordenar y digitalizar la gestión de empresas municipales**, permitiendo a la administración llevar un control confiable y actualizado de los negocios que operan dentro del municipio.

## 🏗️ Arquitectura del Sistema

### Estructura de Archivos
```
sistema_empresas_municipal/
├── app/
│   ├── __init__.py              # Configuración de Flask
│   ├── models.py                # Modelos de base de datos
│   ├── routes.py                # Rutas y controladores
│   ├── services/                # Lógica de negocio
│   │   ├── excel_importer.py    # Importación principal
│   │   ├── excel_reader.py      # Lectura de archivos
│   │   ├── sheet_classifier.py # Clasificación de hojas
│   │   └── importers/           # Importadores especializados
│   │       ├── universal_company_importer.py  # ⭐ Importador universal
│   │       ├── import_manager.py               # Gestor de importación
│   │       ├── cerradas_importer.py           # Empresas cerradas
│   │       ├── inspecciones_importer.py         # Inspecciones
│   │       └── import_result.py               # Resultados de importación
│   └── templates/               # Plantillas HTML
├── migrations/                  # Migraciones de base de datos
├── uploads/                     # Archivos subidos
├── config.py                    # Configuración
├── run.py                       # Ejecución de la aplicación
└── requirements.txt             # Dependencias
```

## 🚀 Características Principales

### 1. Importador Universal
- **Un solo sistema** para todos los tipos de empresas
- **Mapeo inteligente** con +100 variaciones de columnas
- **Procesamiento robusto** de datos inconsistentes
- **Detección automática** de tipos de hojas

### 2. Tipos de Empresas Soportadas
- ✅ **EMPRESAS** - Empresas generales y negocios
- ✅ **EXPENDIOS** - Expendios y licencias comerciales  
- ✅ **MERCADOS/PIEZAS** - Puestos en mercados municipales
- ✅ **VIVEROS** - Viveros y agricultura
- ✅ **ROTULOS/BANNERS** - Publicidad exterior
- ✅ **INSPECCIONES** - Control de inspecciones municipales
- ✅ **CERRADAS** - Empresas cerradas o suspendidas

### 3. CRUD Completo
- **Crear** nuevas empresas con formulario completo
- **Editar** información existente
- **Eliminar** con confirmación
- **Ver** detalles completos con historial

### 4. Corrección de Datos
- **Interfaz intuitiva** para corregir errores de importación
- **Validación en tiempo real**
- **Re-importación** de datos corregidos

### 5. Búsqueda y Filtros
- **Búsqueda AJAX** por código, nombre o RUC
- **Filtros** por estado y distrito
- **Resultados en tiempo real**

## 🛠️ Instalación y Configuración

### Requisitos
- Python 3.8+
- MySQL/MariaDB
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repositorio>
cd sistema_empresas_municipal
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
# Editar .env con tus credenciales
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=municipal_empresas
```

5. **Iniciar base de datos**
```bash
flask db upgrade
```

6. **Ejecutar aplicación**
```bash
python run.py
```

## 📊 Uso del Sistema

### Importación de Datos

1. **Subir archivo Excel**
   - Ir a `/importar`
   - Seleccionar archivo .xlsx o .csv
   - El sistema detecta automáticamente las hojas

2. **Revisar resultados**
   - Ver resumen de importación
   - Identificar errores si los hay

3. **Corregir errores**
   - Click en "Corregir errores"
   - Editar datos directamente en el formulario
   - Re-importar datos corregidos

### Gestión de Empresas

1. **Ver listado**
   - `/empresas` - Todas las empresas
   - `/empresas/activas` - Solo activas
   - `/empresas/cerradas` - Solo cerradas

2. **Buscar y filtrar**
   - Búsqueda por código, nombre o RUC
   - Filtros por estado y distrito

3. **CRUD completo**
   - Nueva empresa: `/empresas/nueva`
   - Editar: `/empresas/editar/{id}`
   - Detalles: `/empresas/detalles/{id}`
   - Eliminar: Confirmación y eliminación

## 🔧 Procesamiento de Datos

### Mapeo Inteligente
El sistema reconoce automáticamente:

| Campo Original | Campo Mapeado |
|---------------|---------------|
| "CODIGO DE EMPRESA" | codigo |
| "CODIGO DE EXPENDIO" | codigo |
| "PROPIETARIO / REPRESENTANTE LEGAL" | propietario |
| "TELEFONO / CORREO" | telefono + email |
| "EMPRESA / NEGOCIO" | nombre |

### Limpieza Automática
- **Contactos combinados**: `"email@dominio.com 7225-7730"` → email + teléfono
- **Estados**: `"ACTIVO / ART. 3 NUMERAL 37"` → `"ACTIVO"`
- **Fechas**: Múltiples formatos (DD/MM/YYYY, YYYY-MM-DD)
- **Monedas**: `"$ 32,00"` → `32.00`

## 🎨 Diseño y Experiencia

### Características UI/UX
- **Diseño moderno** con TailwindCSS
- **Responsive** para todos los dispositivos
- **Accesibilidad** con navegación por teclado
- **Feedback visual** con colores y estados
- **Confirmaciones** para acciones destructivas

### Flujo de Usuario
1. **Importación simple** → arrastrar y soltar archivo
2. **Resultados claros** → resumen visual con estadísticas
3. **Corrección fácil** → edición inline de errores
4. **Gestión completa** → CRUD con validaciones

## 📈 Beneficios

### Para la Administración
- ✅ **Control centralizado** de todas las empresas
- ✅ **Procesos automatizados** que reducen errores
- ✅ **Información actualizada** y confiable
- ✅ **Facilidad de consulta** y reportes

### Para los Ciudadanos
- ✅ **Trámites más rápidos** con información precisa
- ✅ **Transparencia** en la gestión municipal
- ✅ **Servicios digitales** eficientes

## 🔄 Mantenimiento

### Tareas Regulares
- **Backups** de base de datos
- **Actualización** de dependencias
- **Monitoreo** de errores de importación
- **Optimización** de consultas

### Soporte
- **Documentación** completa en `OBJETIVO_SISTEMA.md`
- **Logs** de importación para debugging
- **Validaciones** para prevenir errores

## 🚀 Desarrollo Futuro

### Próximas Características
- [ ] **Portal ciudadano** para consultas públicas
- [ ] **Reportes avanzados** con gráficos
- [ ] **Notificaciones** automáticas
- [ ] **API REST** para integraciones
- [ ] **Móvil** responsive mejorado

---

**Este sistema representa una transformación digital fundamental para la gestión municipal, modernizando los procesos y mejorando el servicio a los ciudadanos.**
