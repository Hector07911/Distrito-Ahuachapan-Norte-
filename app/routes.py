from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import os
from app.models import Empresa, Contacto, Inspeccion, EmpresaCerrada, HistorialPago, Role, Usuario, Rubro
from app import db
from sqlalchemy import func
from datetime import datetime
from app.services.excel_reader import leer_excel, listar_hojas
from app.services.excel_importer import importar_excel_completo
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint("main", __name__)

# --- HELPER FUNCTIONS ---
def parse_combined_contact(raw_value):
    """
    Intenta separar email y teléfono de un valor combinado.
    Retorna: (email, telefono)
    """
    if not raw_value:
        return None, None
    
    email = None
    telefono = None
    
    # Si contiene @, probablemente es email
    if '@' in raw_value:
        email = raw_value.strip()
    else:
        # Asumimos que es teléfono
        telefono = raw_value.strip()
    
    return email, telefono

# --- RUTAS DE AUTENTICACIÓN ---

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- CONFIGURACIÓN INICIAL (AYUDA A CREAR USUARIO) ---
def setup_initial_admin():
    """Crea roles y admin por defecto si no existen"""
    try:
        # 1. Crear Roles
        admin_role = Role.query.filter_by(nombre='ADMIN').first()
        if not admin_role:
            admin_role = Role(nombre='ADMIN')
            db.session.add(admin_role)
        
        user_role = Role.query.filter_by(nombre='USER').first()
        if not user_role:
            user_role = Role(nombre='USER')
            db.session.add(user_role)
            
        db.session.commit() # Commit intermedio para tener IDs de roles
        
        # 2. Crear Usuario Admin
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = Usuario(username='admin', role=admin_role)
            admin_user.set_password('admin2026') # CONTRASEÑA SOLICITADA
            db.session.add(admin_user)
            db.session.commit()
            print(">>> USUARIO ADMIN CREADO (pass: admin2026) <<<")
            
    except Exception as e:
        print(f"Error en setup inicial: {e}")
        db.session.rollback()

# --- RUTAS PROTEGIDAS ---

@main.route('/')
@login_required
def index():
    # Ejecutamos el setup aquí por seguridad, la primera vez que se entra
    setup_initial_admin()
    
    try:
        # 1. Conteos Generales
        total_padrón = db.session.query(Empresa).count()
        total_activas = db.session.query(Empresa).filter(Empresa.estado_actual == 'ACTIVO').count()
        total_tramites = db.session.query(Empresa).filter(Empresa.estado_actual.in_(['SOLICITUD', 'EN TRAMITE'])).count()
        total_inspecciones = db.session.query(Inspeccion).count()
        total_cerradas = db.session.query(EmpresaCerrada).count()
        
        # 2. Categorización Dinámica por Rubros (Solo para negocios ACTIVOS)
        rubros_stats = []
        all_rubros = Rubro.query.order_by(Rubro.nombre).all()
        
        for r in all_rubros:
            count = db.session.query(Empresa).filter(
                Empresa.estado_actual == 'ACTIVO',
                Empresa.rubro_id == r.id
            ).count()
            rubros_stats.append({
                'id': r.id,
                'nombre': r.nombre,
                'icono': r.icono,
                'color': r.color,
                'count': count,
                'categoria': r.categoria,
                'descripcion': r.descripcion
            })

        # Conteos de empresas activas sin rubro asignado
        total_con_rubro = sum(s['count'] for s in rubros_stats)
        cat_otros = max(0, total_activas - total_con_rubro)

        # 3. Proyección (Scalar para evitar errores si no hay datos)
        proyeccion_2026 = db.session.query(func.sum(HistorialPago.monto_mensual))\
                            .filter(HistorialPago.anio == 2026).scalar() or 0
        
        return render_template(
            "index.html",
            total_padron=total_padrón,
            total_activas=total_activas,
            total_tramites=total_tramites,
            total_inspecciones=total_inspecciones,
            total_cerradas=total_cerradas,
            rubros_stats=rubros_stats,
            cat_otros=cat_otros,
            proyeccion_2026=proyeccion_2026
        )

    except Exception as e:
        db.session.rollback() # Limpia la tubería si hubo Broken Pipe
        print(f"Error crítico en Dashboard: {e}")
        # Retornamos valores seguros para que el usuario no vea una página de error
        return render_template(
            'index.html', 
            total_padron=0, 
            total_activas=0, 
            total_tramites=0, 
            total_inspecciones=0, 
            total_cerradas=0, 
            rubros_stats=[], 
            cat_otros=0, 
            proyeccion_2026=0
        )

@main.route("/empresas")
@login_required
def empresas():
    try:
        filtro = request.args.get('filtro', '').strip().lower()
        
        # 1. Usamos db.session.query para mayor estabilidad en la conexión
        query = db.session.query(Empresa)

        # 2. Aplicar filtros de categoría
        if filtro.isdigit():
            # Filtro por Rubro ID
            query = query.filter(Empresa.rubro_id == int(filtro), Empresa.estado_actual == 'ACTIVO')
            rubro_obj = Rubro.query.get(int(filtro))
            titulo = f"Rubro: {rubro_obj.nombre}" if rubro_obj else "Rubro no encontrado"
        elif filtro == 'tienda':
            query = query.filter(
                (Empresa.nombre_negocio.ilike('%TIENDA%')) | 
                (Empresa.nombre_negocio.ilike('%ABARROTES%'))
            ).filter(Empresa.estado_actual == 'ACTIVO')
            titulo = "Listado de Tiendas"
        elif filtro == 'restaurante':
            query = query.filter(
                (Empresa.nombre_negocio.ilike('%RESTAURANTE%')) | 
                (Empresa.nombre_negocio.ilike('%COMEDOR%'))
            ).filter(Empresa.estado_actual == 'ACTIVO')
            titulo = "Listado de Restaurantes"
        elif filtro == 'otro':
            query = query.filter(
                Empresa.rubro_id == None,
                ~Empresa.nombre_negocio.ilike('%TIENDA%'),
                ~Empresa.nombre_negocio.ilike('%ABARROTES%'),
                ~Empresa.nombre_negocio.ilike('%RESTAURANTE%'),
                ~Empresa.nombre_negocio.ilike('%COMEDOR%'),
                Empresa.estado_actual == 'ACTIVO'
            )
            titulo = "Otros Negocios"
        else:
            # Por defecto: Solo activas
            query = query.filter(Empresa.estado_actual == 'ACTIVO')
            titulo = "Listado de Activas"

        # 3. Ejecutar la consulta con ordenamiento y CARGA ANTICIPADA (Eager Loading)
        # Esto evita el error de TIMEOUT en Render al traer contactos en una sola consulta
        from sqlalchemy.orm import joinedload
        empresas_list = query.options(joinedload(Empresa.contactos)).order_by(Empresa.nombre_negocio.asc()).all()
        
        return render_template(
            "empresas.html",
            empresas=empresas_list,
            titulo=titulo,
            subtitulo="Negocios vigentes en el municipio",
            filtro_predeterminado=filtro
        )

    except Exception as e:
        # ¡ESTO ES LO MÁS IMPORTANTE! 
        # Si MySQL falla, liberamos la sesión para que no se trabe el sistema
        db.session.rollback()
        print(f"Error en ruta empresas: {e}")
        flash("Error de conexión con la base de datos. Reintentando...", "error")
        return render_template(
            "empresas.html", 
            empresas=[], 
            titulo="Error", 
            subtitulo="No se pudieron cargar los datos",
            filtro_predeterminado=""
        )

@main.route('/empresas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_empresa():
    if request.method == 'POST':
        try:
            nombre_input = request.form.get('nombre').upper() if request.form.get('nombre') else None
            
            # 1. VALIDACIÓN PREVENTIVA (El Candado)
            # Buscamos si ya existe el nombre para evitar el error de Duplicate Entry
            if nombre_input:
                existe = db.session.query(Empresa).filter_by(nombre_negocio=nombre_input).first()
                if existe:
                    flash(f'¡Atención! Ya existe un negocio registrado con el nombre "{nombre_input}".', 'warning')
                    return render_template('empresas_form.html', empresa=None, action='crear')

            # 2. CREACIÓN DE LA INSTANCIA
            estado_input = request.form.get('estado') or 'ACTIVO'
            empresa = Empresa(
                codigo=request.form.get('codigo'),
                nombre_negocio=nombre_input,
                propietario=request.form.get('propietario').upper() if request.form.get('propietario') else None,
                distrito=request.form.get('distrito') or 'ATIQUIZAYA',
                giro=request.form.get('giro').upper() if request.form.get('giro') else None,
                direccion=request.form.get('direccion'),
                nit=request.form.get('nit'),
                nrc=request.form.get('nrc'),
                estado_actual=estado_input,
                notas=request.form.get('notas'),
                rubro_id=request.form.get('rubro_id') if request.form.get('rubro_id') else None
            )
            
            fecha_str = request.form.get('fecha_registro')
            if fecha_str:
                try:
                    empresa.fecha_inscripcion = datetime.fromisoformat(fecha_str).date()
                except ValueError:
                    pass

            db.session.add(empresa)
            db.session.flush() # Para obtener ID

            # 3. LOGICA ESPECIFICA: Si nace privada de actividad, la registramos en cerradas
            estados_archivo = ['CERRADO', 'INACTIVO', 'SUSPENDIDO', 'CANCELADO']
            if estado_input in estados_archivo:
                cierre = EmpresaCerrada(
                    empresa_id=empresa.id,
                    fecha=datetime.now().date(),
                    razon=f"Registrada como {estado_input} inicialmente"
                )
                db.session.add(cierre)

            # 4. GUARDADO DE CONTACTOS
            tel_raw = request.form.get('telefono')
            if tel_raw:
                db.session.add(Contacto(empresa_id=empresa.id, tipo='TELEFONO', valor=tel_raw.strip()))
            
            email_raw = request.form.get('email')
            if email_raw:
                db.session.add(Contacto(empresa_id=empresa.id, tipo='EMAIL', valor=email_raw.strip()))

            # 5. GUARDADO DE PAGOS (Multi-año)
            anios = request.form.getlist('pago_anio[]')
            cuotas = request.form.getlist('pago_cuota[]')
            
            for anio, cuota in zip(anios, cuotas):
                if anio and cuota:
                    try:
                        db.session.add(HistorialPago(
                            empresa_id=empresa.id,
                            anio=int(anio),
                            monto_mensual=float(cuota)
                        ))
                    except ValueError:
                        continue

            db.session.commit()
            flash(f'✅ Empresa "{nombre_input}" registrada exitosamente en el padrón.', 'success')
            return redirect(url_for('main.empresas'))

        except Exception as e:
            db.session.rollback()
            print(f"Error al crear empresa: {e}")
            flash(f'❌ Error al guardar: {str(e)}. Verifique los datos e intente nuevamente.', 'error')
    
    rubros_list = Rubro.query.order_by(Rubro.nombre).all()
    return render_template('empresas_form.html', empresa=None, action='crear', rubros_list=rubros_list)

@main.route('/empresas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_empresa(id):
    empresa = db.session.query(Empresa).get_or_404(id)
    estado_viejo = empresa.estado_actual

    if request.method == 'POST':
        try:
            nuevo_nombre = request.form.get('nombre').upper() if request.form.get('nombre') else None
            
            # 1. VALIDACIÓN PREVENTIVA
            if nuevo_nombre and nuevo_nombre != empresa.nombre_negocio:
                existe = db.session.query(Empresa).filter(
                    Empresa.nombre_negocio == nuevo_nombre, 
                    Empresa.id != id
                ).first()
                if existe:
                    flash(f'Error: Ya existe otra empresa con el nombre "{nuevo_nombre}".', 'error')
                    return render_template('empresas_form.html', empresa=empresa, action='editar')

            # 2. ACTUALIZACIÓN DE CAMPOS
            empresa.codigo = request.form.get('codigo') or empresa.codigo
            empresa.nombre_negocio = nuevo_nombre or empresa.nombre_negocio
            empresa.propietario = request.form.get('propietario').upper() if request.form.get('propietario') else empresa.propietario
            empresa.distrito = request.form.get('distrito') or empresa.distrito
            empresa.giro = request.form.get('giro').upper() if request.form.get('giro') else empresa.giro
            empresa.direccion = request.form.get('direccion') or empresa.direccion
            empresa.nit = request.form.get('nit') or empresa.nit
            empresa.nrc = request.form.get('nrc') or empresa.nrc
            empresa.notas = request.form.get('notas') or empresa.notas
            empresa.rubro_id = request.form.get('rubro_id') if request.form.get('rubro_id') else None
            
            fecha_str = request.form.get('fecha_registro')
            if fecha_str:
                try:
                    empresa.fecha_inscripcion = datetime.fromisoformat(fecha_str).date()
                except ValueError:
                    pass

            nuevo_estado = request.form.get('estado') or empresa.estado_actual
            empresa.estado_actual = nuevo_estado
            
            # --- LÓGICA DE CIERRE/REACTIVACIÓN ---
            estados_archivo = ['CERRADO', 'INACTIVO', 'SUSPENDIDO', 'CANCELADO']
            
            # CASO A: Entra a estados de "Archivo" (Antes NO estaba, ahora SI)
            if nuevo_estado in estados_archivo and estado_viejo not in estados_archivo:
                ya_existe = EmpresaCerrada.query.filter_by(empresa_id=empresa.id).first()
                if not ya_existe:
                    cierre = EmpresaCerrada(
                        empresa_id=empresa.id,
                        fecha=datetime.now().date(),
                        razon=f"Estado cambiado a {nuevo_estado} por el usuario"
                    )
                    db.session.add(cierre)
                    
            # CASO B: Sale de estados de "Archivo" (Antes estaba, ahora NO)
            elif estado_viejo in estados_archivo and nuevo_estado not in estados_archivo:
                cierre = EmpresaCerrada.query.filter_by(empresa_id=empresa.id).first()
                if cierre:
                    db.session.delete(cierre)

            # 3. GESTIÓN DE CONTACTOS
            tel_input = request.form.get('telefono')
            if tel_input:
                contacto_tel = next((c for c in empresa.contactos if c.tipo == 'TELEFONO'), None)
                if contacto_tel:
                    contacto_tel.valor = tel_input.strip()
                else:
                    db.session.add(Contacto(empresa_id=empresa.id, tipo='TELEFONO', valor=tel_input.strip()))
            
            email_input = request.form.get('email')
            if email_input:
                contacto_email = next((c for c in empresa.contactos if c.tipo == 'EMAIL'), None)
                if contacto_email:
                    contacto_email.valor = email_input.strip()
                else:
                    db.session.add(Contacto(empresa_id=empresa.id, tipo='EMAIL', valor=email_input.strip()))

            # 4. GESTIÓN DE PAGOS (Sincronización Multi-año)
            anios_form = request.form.getlist('pago_anio[]')
            cuotas_form = request.form.getlist('pago_cuota[]')
            
            # Convertimos a tipos correctos y filtramos vacíos
            pagos_dict = {}
            for a, c in zip(anios_form, cuotas_form):
                if a and c:
                    try:
                        pagos_dict[int(a)] = float(c)
                    except ValueError:
                        continue

            # Sincronizamos: eliminamos los que no están en el form y actualizamos/agregamos los que sí
            # Eliminamos los que ya no vienen en el formulario
            for pago_existente in list(empresa.pagos):
                if pago_existente.anio not in pagos_dict:
                    db.session.delete(pago_existente)
                else:
                    # Actualizamos el monto si cambió
                    pago_existente.monto_mensual = pagos_dict.pop(pago_existente.anio)
            
            # Los que quedaron en pagos_dict son nuevos
            for anio, cuota in pagos_dict.items():
                db.session.add(HistorialPago(
                    empresa_id=empresa.id,
                    anio=anio,
                    monto_mensual=cuota
                ))

            db.session.commit()
            
            # Mensaje específico según la acción
            if nuevo_estado == 'CERRADO' and estado_viejo != 'CERRADO':
                flash(f'✅ Empresa "{empresa.nombre_negocio}" actualizada y marcada como CERRADA.', 'success')
            elif estado_viejo == 'CERRADO' and nuevo_estado != 'CERRADO':
                flash(f'✅ Empresa "{empresa.nombre_negocio}" reactivada exitosamente.', 'success')
            else:
                flash(f'✅ Empresa "{empresa.nombre_negocio}" actualizada correctamente.', 'success')
            return redirect(url_for('main.empresas'))

        except Exception as e:
            db.session.rollback()
            print(f"Error editando empresa {id}: {e}")
            flash(f'❌ Error al actualizar: {str(e)}', 'error')
    
    rubros_list = Rubro.query.order_by(Rubro.nombre).all()
    return render_template('empresas_form.html', empresa=empresa, action='editar', rubros_list=rubros_list)
# --- IMPORTACIÓN MASIVA ---

@main.route("/importar", methods=["GET", "POST"])
@login_required
def importar():
    if request.method == "POST":
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
            
        archivo = request.files["archivo"]
        if archivo.filename == '':
            flash('Nombre de archivo vacío', 'error')
            return redirect(request.url)

        # Asegurar que existe la carpeta
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        ruta = os.path.join("uploads", archivo.filename)
        archivo.save(ruta)
        session["excel_ruta"] = ruta

        excel = leer_excel(ruta)
        hojas = listar_hojas(excel)

        return render_template("importar_dashboard.html", hojas=hojas)

    return render_template("importar.html")

@main.route("/importar/procesar", methods=["POST"])
@login_required
def importar_procesar():
    ruta = session.get("excel_ruta")
    if not ruta:
        flash("No hay archivo pendiente de procesar", "error")
        return redirect(url_for("main.importar"))

    # Esta función ahora usa el Universal Importer que reparte en 3 tablas
    resultados, hojas_admin = importar_excel_completo(ruta, db.session)

    return render_template("resultado_importacion.html", resultados=resultados)

# --- BÚSQUEDA Y DETALLES ---

@main.route('/empresas/buscar', methods=['GET'])
@login_required
def buscar_empresas():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    # Búsqueda optimizada para los nuevos campos
    empresas = Empresa.query.filter(
        (Empresa.nombre_negocio.ilike(f'%{query}%')) |
        (Empresa.codigo.ilike(f'%{query}%')) |
        (Empresa.propietario.ilike(f'%{query}%'))
    ).limit(10).all()
    
    resultados = []
    for emp in empresas:
        # Buscamos el primer teléfono de la lista de contactos
        tel = next((c.valor for c in emp.contactos if c.tipo == 'TELEFONO'), "N/A")
        resultados.append({
            'id': emp.id,
            'codigo': emp.codigo,
            'nombre': emp.nombre_negocio,
            'telefono': tel,
            'estado': emp.estado_actual
        })
    return jsonify(resultados)

@main.route('/empresas/detalles/<int:id>')
@login_required
def detalles_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    # Al ser relacional, empresa.contactos y empresa.pagos ya están disponibles
    return render_template('empresa_detalles.html', empresa=empresa)

@main.route('/empresas/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_empresa(id):
    # SEGURIDAD: Solo ADMIN puede eliminar
    if current_user.role.nombre != 'ADMIN':
        flash('Acceso denegado. Solo administradores pueden eliminar registros.', 'error')
        return redirect(url_for('main.empresas'))

    try:
        empresa = Empresa.query.get_or_404(id)
        
        # Eliminar también de cerradas si existe
        cierre = EmpresaCerrada.query.filter_by(empresa_id=id).first()
        if cierre:
            db.session.delete(cierre)

        db.session.delete(empresa)
        db.session.commit()
        flash(f'🗑️ Empresa "{empresa.nombre_negocio}" eliminada permanentemente del sistema.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar: {str(e)}', 'error')
    return redirect(url_for('main.empresas'))

@main.route("/inspecciones")
@login_required
def inspecciones():
    # 1. Inspecciones técnicas ya realizadas
    inspecciones_list = Inspeccion.query.join(Empresa).order_by(Inspeccion.fecha.desc()).all()
    
    # 2. Empresas que están en proceso de trámites (SOLICITUD o EN TRAMITE)
    empresas_en_tramite = Empresa.query.filter(Empresa.estado_actual.in_(['SOLICITUD', 'EN TRAMITE'])).all()
    
    return render_template(
        "inspecciones.html",
        inspecciones_list=inspecciones_list,
        empresas_tramite=empresas_en_tramite,
        titulo="Trámites e Inspecciones",
        subtitulo="Seguimiento de nuevas solicitudes y visitas"
    )

@main.route('/inspecciones/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_inspeccion(id):
    # SEGURIDAD: Solo ADMIN puede eliminar
    if current_user.role.nombre != 'ADMIN':
        flash('Acceso denegado. Solo administradores pueden eliminar registros.', 'error')
        return redirect(url_for('main.inspecciones'))
        
    try:
        inspeccion = Inspeccion.query.get_or_404(id)
        empresa_nombre = inspeccion.empresa.nombre_negocio if inspeccion.empresa else 'Desconocida'
        db.session.delete(inspeccion)
        db.session.commit()
        flash(f'🗑️ Inspección de "{empresa_nombre}" eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar inspección: {str(e)}', 'error')
    return redirect(url_for('main.inspecciones'))

@main.route("/cerradas")
@login_required
def cerradas():
    try:
        # Traemos la pareja de objetos: (Empresa, EmpresaCerrada)
        cerradas_list = db.session.query(Empresa, EmpresaCerrada)\
            .join(EmpresaCerrada, Empresa.id == EmpresaCerrada.empresa_id)\
            .order_by(EmpresaCerrada.fecha.desc()).all()
        
        return render_template(
            "cerradas.html",
            cerradas_list=cerradas_list,
            titulo="Cerradas",
            subtitulo="Historial de bajas de empresas"
        )
    except Exception as e:
        db.session.rollback()
        print(f"Error en ruta cerradas: {e}")
        return render_template("cerradas.html", cerradas_list=[], titulo="Error")

@main.route('/empresa/<int:id>')
@login_required
def detalle_empresa(id):
    try:
        # 1. Usamos db.session.query para mayor estabilidad con XAMPP
        # get_or_404 sigue siendo válido, pero así manejamos el error nosotros
        empresa = db.session.query(Empresa).filter(Empresa.id == id).first()
        
        if not empresa:
            flash("Empresa no encontrada", "error")
            return redirect(url_for('main.empresas'))

        # 2. No necesitas hacer nada más aquí. 
        # Como ya definiste las relaciones en los modelos, 
        # empresa.contactos y empresa.pagos funcionarán en el HTML.

        return render_template('empresa_detalle.html', empresa=empresa)

    except Exception as e:
        # 3. Limpieza de seguridad si la conexión parpadea
        db.session.rollback()
        print(f"Error al cargar detalle de empresa {id}: {e}")
        flash("Error de conexión al cargar el expediente", "error")
        return redirect(url_for('main.empresas'))

# --- RUTAS DE RÚBRICAS ---

@main.route('/rubros')
@login_required
def rubros():
    rubros = Rubro.query.order_by(Rubro.nombre).all()
    return render_template('rubros.html', rubros=rubros)

@main.route('/rubro/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_rubro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        icono = request.form.get('icono', 'tag').strip()
        color = request.form.get('color', 'blue').strip()
        categoria = request.form.get('categoria', '').strip()
        
        if not nombre:
            flash('El nombre del rubro es obligatorio', 'error')
            return render_template('rubro_form.html')
        
        # Verificar que no exista
        existe = Rubro.query.filter_by(nombre=nombre).first()
        if existe:
            flash('Ya existe un rubro con ese nombre', 'error')
            return render_template('rubro_form.html')
        
        try:
            rubro = Rubro(
                nombre=nombre,
                descripcion=descripcion,
                icono=icono,
                color=color,
                categoria=categoria
            )
            db.session.add(rubro)
            db.session.commit()
            flash('Rubro creado exitosamente', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear rubro: {str(e)}', 'error')
    
    return render_template('rubro_form.html')

@main.route('/rubro/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_rubro(id):
    rubro = Rubro.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        icono = request.form.get('icono', 'tag').strip()
        color = request.form.get('color', 'blue').strip()
        categoria = request.form.get('categoria', '').strip()
        
        if not nombre:
            flash('El nombre del rubro es obligatorio', 'error')
            return render_template('rubro_form.html', rubro=rubro)
        
        # Verificar que no exista otro con el mismo nombre
        existe = Rubro.query.filter(Rubro.nombre == nombre, Rubro.id != id).first()
        if existe:
            flash('Ya existe otro rubro con ese nombre', 'error')
            return render_template('rubro_form.html', rubro=rubro)
        
        try:
            rubro.nombre = nombre
            rubro.descripcion = descripcion
            rubro.icono = icono
            rubro.color = color
            rubro.categoria = categoria
            db.session.commit()
            flash('Rubro actualizado exitosamente', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar rubro: {str(e)}', 'error')
    
    return render_template('rubro_form.html', rubro=rubro)

@main.route('/rubro/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_rubro(id):
    rubro = Rubro.query.get_or_404(id)
    
    # Verificar que no tenga empresas asociadas
    empresas_count = Empresa.query.filter_by(rubro_id=id).count()
    if empresas_count > 0:
        flash(f'No se puede eliminar el rubro porque tiene {empresas_count} empresas asociadas', 'error')
        return redirect(url_for('main.index'))
    
    try:
        db.session.delete(rubro)
        db.session.commit()
        flash('Rubro eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar rubro: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))