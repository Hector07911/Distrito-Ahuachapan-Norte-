# Sistema de Gestión Municipal de Empresas

## 🎯 Objetivo Principal

**Centralizar, ordenar y digitalizar la gestión de empresas municipales**, permitiendo a la administración llevar un control confiable y actualizado de los negocios que operan dentro del municipio.

## 📋 Problema Resuelto

### Situación Actual
- **Múltiples archivos de Excel** con información dispersa
- **Estructuras distintas** en cada archivo/hoja
- **Encabezados variables** (CODIGO DE EMPRESA vs CODIGO DE EXPENDIO vs CODIGO DE VIVERO)
- **Datos inconsistentes** (formatos de fecha, moneda, contacto)
- **Dificultad para seguimiento y fiscalización**
- **Procesos manuales** propensos a errores

### Ejemplos de Problemas Encontrados
1. **Contactos combinados**: `"sindybbarrera@gmail.com 7225-7730"`
2. **Códigos variables**: `"CAT-EM-450-2026"`, `"CAT-EX-001"`, `"CAT-V-001-2023"`
3. **Estados inconsistentes**: `"ACTIVO / ART. 3 NUMERAL 37 - ARBITRIOS"`, `"CERRADO"`
4. **Fechas en múltiples formatos**: `"06/01/2024"`, `"20/10/2025"`
5. **Valores monetarios**: `"$ 32,00"`, `"6.15"`, `"56,70"`

## 🏗️ Solución Implementada

### 1. Importador Universal
- **Un solo sistema** para todos los tipos de empresas
- **Mapeo flexible** de columnas con +100 variaciones
- **Detección inteligente** de campos combinados
- **Normalización automática** de datos

### 2. Tipos de Empresas Soportadas
- ✅ **EMPRESAS** - Empresas generales y negocios
- ✅ **EXPENDIOS** - Expendios y licencias comerciales
- ✅ **MERCADOS/PIEZAS** - Puestos en mercados municipales
- ✅ **VIVEROS** - Viveros y agricultura
- ✅ **ROTULOS/BANNERS** - Publicidad exterior
- ✅ **INSPECCIONES** - Control de inspecciones municipales
- ✅ **CERRADAS** - Empresas cerradas o suspendidas

### 3. Características Clave

#### 📊 Mapeo Inteligente de Columnas
```python
# Ejemplos de mapeo automático:
"CODIGO DE EMPRESA" → codigo
"CODIGO DE EXPENDIO" → codigo  
"PROPIETARIO / REPRESENTANTE LEGAL" → propietario
"TELEFONO / CORREO" → telefono + email
"EMPRESA / NEGOCIO" → nombre
```

#### 🔧 Procesamiento de Datos
- **Contactos combinados**: Extrae email y teléfono de campos unidos
- **Estados normalizados**: "ACTIVO / ART. 3..." → "ACTIVO"
- **Fechas múltiples**: Soporta DD/MM/YYYY, YYYY-MM-DD, etc.
- **Monedas**: Convierte "$ 32,00" → 32.00
- **Deduplicación**: Evita empresas duplicadas

#### 🛡️ Calidad de Datos
- **Validación flexible**: Requiere solo 1 campo identificador
- **Limpieza automática**: Elimina espacios, caracteres especiales
- **Normalización**: Estandariza formatos y valores
- **Corrección de errores**: Maneja datos concatenados de pandas

## 📈 Beneficios

### Para la Administración Municipal
- **Control centralizado** de todas las empresas
- **Información actualizada** y confiable
- **Procesos automatizados** que reducen errores
- **Facilidad de consulta** y generación de reportes
- **Mejor fiscalización** y seguimiento

### Para los Ciudadanos
- **Trámites más rápidos** con información precisa
- **Transparencia** en la gestión municipal
- **Servicios digitales** eficientes

## 🔄 Flujo de Trabajo

1. **Importación**: Cargar archivos Excel (cualquier estructura)
2. **Detección**: Identificación automática de tipo de hoja
3. **Mapeo**: Asignación inteligente de columnas
4. **Procesamiento**: Limpieza y normalización de datos
5. **Validación**: Verificación de calidad y deduplicación
6. **Almacenamiento**: Guardado en base de datos centralizada
7. **Reportes**: Generación de informes y estadísticas

## 🎯 Impacto Esperado

### Antes
- ❌ Archivos dispersos en Excel
- ❌ Datos inconsistentes y desactualizados
- ❌ Procesos manuales lentos
- ❌ Dificultad para fiscalizar
- ❌ Toma de decisiones con información incompleta

### Después
- ✅ Base de datos centralizada y actualizada
- ✅ Datos consistentes y normalizados
- ✅ Procesos automatizados eficientes
- ✅ Fiscalización simplificada
- ✅ Decisiones basadas en información completa

## 🚀 Próximos Pasos

1. **Capacitación** del personal municipal
2. **Integración** con otros sistemas municipales
3. **Módulo de reportes** avanzados
4. **Portal ciudadano** para consultas públicas
5. **Notificaciones automáticas** de vencimientos

---

**Este sistema representa una transformación digital fundamental para la gestión municipal, modernizando los procesos y mejorando el servicio a los ciudadanos.**
