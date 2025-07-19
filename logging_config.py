import logging
import os
import sys
import traceback
from pathlib import Path
import bpy

class TypeAnimatorFormatter(logging.Formatter):
    """Formateador personalizado para logs de TypeAnimator con traceback detallado."""
    
    def format(self, record):
        # Formato base
        formatted = super().format(record)
        
        # Añadir traceback si hay excepción
        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)
        
        # Añadir información adicional para errores críticos
        if record.levelno >= logging.ERROR:
            formatted += f'\n[Context] Module: {record.module}, Function: {record.funcName}, Line: {record.lineno}'
        
        return formatted

def setup_logging(level=None, enable_file_logging=True, enable_console_logging=True):
    """
    Configura el sistema de logging para TypeAnimator.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Si habilitar logging a archivo
        enable_console_logging: Si habilitar logging a consola
    """
    logger = logging.getLogger('typeanimator')
    
    # Limpiar handlers existentes para evitar duplicados
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configurar nivel de logging
    if level is None:
        # Obtener nivel desde preferencias del addon
        try:
            prefs = bpy.context.preferences.addons.get('typeanimator', None)
            if prefs and hasattr(prefs.preferences, 'log_level'):
                level = prefs.preferences.log_level
            else:
                level = 'INFO'
        except:
            level = 'INFO'
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Crear formateador personalizado
    formatter = TypeAnimatorFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo
    if enable_file_logging:
        try:
            # Verificar si está habilitado en preferencias
            try:
                prefs = bpy.context.preferences.addons.get('typeanimator', None)
                if prefs and hasattr(prefs.preferences, 'enable_file_logging'):
                    enable_file_logging = prefs.preferences.enable_file_logging
            except:
                pass
                
            if enable_file_logging:
                tempdir = bpy.app.tempdir if hasattr(bpy.app, 'tempdir') and bpy.app.tempdir else os.path.expanduser('~')
                log_file = Path(tempdir) / "typeanimator.log"
                file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)  # Archivo siempre en DEBUG
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                logger.debug(f"File logging enabled: {log_file}")
        except Exception as e:
            print(f"Error configurando file handler: {e}")
    
    # Handler para consola
    if enable_console_logging:
        try:
            # Verificar si está habilitado en preferencias
            try:
                prefs = bpy.context.preferences.addons.get('typeanimator', None)
                if prefs and hasattr(prefs.preferences, 'enable_console_logging'):
                    enable_console_logging = prefs.preferences.enable_console_logging
            except:
                pass
                
            if enable_console_logging:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(log_level)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
                logger.debug(f"Console logging enabled with level: {level}")
        except Exception as e:
            print(f"Error configurando console handler: {e}")
    
    return logger

def update_logging_from_preferences():
    """
    Actualiza la configuración de logging basada en las preferencias del addon.
    Se llama cuando el usuario cambia las preferencias.
    """
    try:
        prefs = bpy.context.preferences.addons.get('typeanimator', None)
        if not prefs or not hasattr(prefs.preferences, 'log_level'):
            return
        
        # Obtener configuración actual
        level = prefs.preferences.log_level
        enable_file = prefs.preferences.enable_file_logging
        enable_console = prefs.preferences.enable_console_logging
        
        # Reconfigurar logging
        setup_logging(level, enable_file, enable_console)
        
        logger = logging.getLogger('typeanimator')
        logger.info(f"Logging configuration updated: level={level}, file={enable_file}, console={enable_console}")
        
    except Exception as e:
        print(f"Error updating logging from preferences: {e}")

def log_exception(logger, message="Error no controlado", include_traceback=True):
    """
    Función helper para loggear excepciones con traceback completo.
    
    Args:
        logger: Logger instance
        message: Mensaje descriptivo del error
        include_traceback: Si incluir traceback completo
    """
    if include_traceback:
        logger.error(f"{message}: {sys.exc_info()[1]}", exc_info=True)
    else:
        logger.error(f"{message}: {sys.exc_info()[1]}")

def log_function_call(logger, func_name, args=None, kwargs=None):
    """
    Función helper para loggear llamadas a funciones (solo en DEBUG).
    
    Args:
        logger: Logger instance
        func_name: Nombre de la función
        args: Argumentos posicionales
        kwargs: Argumentos de palabra clave
    """
    if logger.isEnabledFor(logging.DEBUG):
        args_str = str(args) if args else "()"
        kwargs_str = str(kwargs) if kwargs else "{}"
        logger.debug(f"Calling {func_name}{args_str} {kwargs_str}")

def log_performance(logger, operation, start_time, end_time=None):
    """
    Función helper para loggear métricas de performance.
    
    Args:
        logger: Logger instance
        operation: Nombre de la operación
        start_time: Tiempo de inicio (time.time())
        end_time: Tiempo de fin (time.time()), si None usa tiempo actual
    """
    import time
    if end_time is None:
        end_time = time.time()
    
    duration = end_time - start_time
    logger.debug(f"Performance: {operation} took {duration:.4f} seconds")

def get_log_level_from_preferences():
    """Obtiene el nivel de logging desde las preferencias del addon."""
    try:
        prefs = bpy.context.preferences.addons.get('typeanimator', None)
        if prefs and hasattr(prefs.preferences, 'log_level'):
            return prefs.preferences.log_level
    except:
        pass
    return 'INFO'

def set_log_level(level):
    """
    Cambia el nivel de logging dinámicamente.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger('typeanimator')
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Actualizar nivel del logger principal
    logger.setLevel(log_level)
    
    # Actualizar nivel de handlers de consola
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            handler.setLevel(log_level)
    
    logger.info(f"Log level changed to: {level}")

def clear_log_file():
    """Limpia el archivo de log."""
    try:
        tempdir = bpy.app.tempdir if hasattr(bpy.app, 'tempdir') and bpy.app.tempdir else os.path.expanduser('~')
        log_file = Path(tempdir) / "typeanimator.log"
        if log_file.exists():
            log_file.unlink()
            logger = logging.getLogger('typeanimator')
            logger.info("Log file cleared successfully")
            return True
    except Exception as e:
        print(f"Error clearing log file: {e}")
    return False

def get_log_file_path():
    """Obtiene la ruta del archivo de log."""
    try:
        tempdir = bpy.app.tempdir if hasattr(bpy.app, 'tempdir') and bpy.app.tempdir else os.path.expanduser('~')
        return Path(tempdir) / "typeanimator.log"
    except:
        return None

def open_log_file():
    """Abre el archivo de log en el editor del sistema."""
    try:
        log_file = get_log_file_path()
        if log_file and log_file.exists():
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(["notepad", str(log_file)], check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(log_file)], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(log_file)], check=True)
            
            logger = logging.getLogger('typeanimator')
            logger.info("Log file opened in system editor")
            return True
    except Exception as e:
        print(f"Error opening log file: {e}")
    return False

def get_log_statistics():
    """Obtiene estadísticas del archivo de log."""
    try:
        log_file = get_log_file_path()
        if log_file and log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            stats = {
                'total_lines': len(lines),
                'file_size': log_file.stat().st_size,
                'error_count': len([l for l in lines if 'ERROR' in l]),
                'warning_count': len([l for l in lines if 'WARNING' in l]),
                'info_count': len([l for l in lines if 'INFO' in l]),
                'debug_count': len([l for l in lines if 'DEBUG' in l]),
            }
            return stats
    except Exception as e:
        print(f"Error getting log statistics: {e}")
    return None
