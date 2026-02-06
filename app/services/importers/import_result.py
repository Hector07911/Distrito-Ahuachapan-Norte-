# app/services/importers/import_result.py

class ImportResult:
    """Clase para almacenar resultados de importación"""
    
    def __init__(self):
        self.ok = 0
        self.errors = []
    
    def add_ok(self):
        """Incrementa el contador de registros exitosos"""
        self.ok += 1
    
    def add_error(self, row_number, message):
        """Agrega un error a la lista"""
        self.errors.append({
            'row': row_number,
            'message': message
        })
    
    @property
    def success_count(self):
        """Alias para compatibilidad"""
        return self.ok
    
    @property
    def error_count(self):
        """Número de errores"""
        return len(self.errors)
    
    @property
    def has_errors(self):
        """Retorna True si hay errores"""
        return len(self.errors) > 0
    
    @property
    def is_success(self):
        """Retorna True si no hay errores"""
        return len(self.errors) == 0
    
    def get_errors_by_row(self):
        """Agrupa errores por número de fila"""
        errors_dict = {}
        for error in self.errors:
            row = error['row']
            if row not in errors_dict:
                errors_dict[row] = []
            errors_dict[row].append(error['message'])
        return errors_dict
    
    def to_dict(self):
        """Convierte el resultado a diccionario"""
        return {
            'success': self.ok,
            'errors': self.errors,
            'total_errors': len(self.errors),
            'has_errors': self.has_errors
        }
    
    def __str__(self):
        return f"ImportResult(ok={self.ok}, errors={len(self.errors)})"
    
    def __repr__(self):
        return self.__str__()