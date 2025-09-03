# Cisco DNA Center Ansible Collection - Copilot Instructions

## 📋 Lista de Instrucciones Generales

### 1. Análisis Inicial
- [x] **Comprender el problema**: Lee y analiza completamente el requerimiento
- [x] **Definir el alcance**: Establece qué se debe implementar o resolver en el contexto de Cisco DNA Center

### 2. Planificación del Código
- [x] **Descomponer el problema**: Divide en tareas más pequeñas y manejables
- [x] **Identificar archivos necesarios**: Determina qué módulos, playbooks o roles crear/modificar
- [x] **Definir la arquitectura**: Planifica la estructura de módulos Ansible y workflows
- [x] **Considerar patrones Ansible**: Aplica mejores prácticas de Ansible y patrones de collections

### 3. Implementación
- [x] **Seguir convenciones**: Utiliza el estilo de código existente del proyecto
- [x] **Escribir código limpio**: Aplica principios de código legible y mantenible, usar `ansible-lint` para validación
- [x] **Implementar funcionalidad básica**: Comienza con la funcionalidad core de DNA Center
- [x] **Agregar validaciones**: Incluye manejo de errores y validaciones de parámetros
- [x] **Documentar el código**: Añade documentación YAML apropiada en módulos y comentarios cuando sea necesario en inglés

### 4. Testing y Validación
- [x] **Pruebas**: Usa la estructura `tests/` para escribir pruebas unitarias y de integración necesarias para validar la funcionalidad
- [x] **Validación con ansible-lint**: Ejecuta `ansible-lint` para verificar mejores prácticas
- [x] **Validación con yamllint**: Ejecuta `yamllint` para verificar sintaxis YAML

### 5. Optimización y Refinamiento
- [x] **Refactorizar si es necesario**: Mejora la estructura del código
- [x] **Optimizar rendimiento**: Identifica y corrige cuellos de botella en operaciones DNA Center
- [x] **Revisar seguridad**: Verifica manejo seguro de credenciales y datos sensibles
- [x] **Actualizar documentación**: Mantén la documentación sincronizada

## 🔧 Resolución de Problemas - Checklist

### Análisis del Error
1. **Leer el mensaje de error completo de Ansible**
2. **Identificar el módulo/playbook donde ocurre**
3. **Entender el contexto de la operación DNA Center**
4. **Revisar logs de conexión con DNA Center**

### Estrategias de Debug
1. **Revisar cambios recientes en módulos**
2. **Consultar documentación de DNA Center API**
3. **Verificar compatibilidad de versiones (DNA Center vs Collection)**
4. **Buscar soluciones en issues de GitHub del proyecto**

### Proceso de Solución
1. **Implementar fix mínimo**: La solución más simple primero
2. **Probar la solución**: Verificar que resuelve el problema con DNA Center
3. **Verificar efectos secundarios**: Asegurar que no rompe otras funcionalidades
4. **Documentar la solución**: Explicar qué causó el problema y cómo se resolvió

## 🎯 Mejores Prácticas

### Código Ansible de Calidad
- Usar nombres descriptivos para tareas, variables y módulos
- Mantener playbooks pequeños y enfocados (principio de responsabilidad única)
- Evitar duplicación de código (DRY - Don't Repeat Yourself)
- Usar tags apropiados para organizar tareas
- Implementar manejo de errores con `rescue` y `always`
- Usar `ansible-vault` para datos sensibles

### Desarrollo de Módulos
- Seguir estructura estándar de módulos Ansible
- Implementar documentación YAML completa
- Usar `AnsibleModule` para validación de parámetros
- Implementar modo `check_mode` cuando sea posible
- Manejar idempotencia apropiadamente

### Gestión de Credenciales DNA Center
- Usar variables de entorno o ansible-vault para credenciales
- Implementar validación de conectividad
- Manejar timeouts y reintentos apropiadamente
- Documentar requisitos de autenticación

### Compatibilidad con DNA Center
- Verificar matriz de compatibilidad antes de implementar
- Documentar versiones soportadas
- Implementar verificación de versión cuando sea necesario

## 📚 Recursos Específicos del Proyecto

### Documentación
- Documentación oficial de Cisco DNA Center: https://developer.cisco.com/docs/dna-center/
- DNA Center SDK Python: https://github.com/cisco-en-programmability/dnacentersdk
- Ansible Collections: https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html
- Ansible Module Development: https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

### Herramientas
- **Linting**: ansible-lint, yamllint
- **Testing**: pytest, ansible-test
- **Debug**: ansible-playbook -vvv, pdb para módulos Python
- **Validation**: dnacentersdk para validar conectividad

### Comunidades
- Cisco DevNet Community
- Ansible Community
- GitHub Issues del proyecto
- Cisco DNA Center Developer Community

---

# 📁 Estructura del Proyecto DNA Center Ansible Collection

## 🏗️ Estructura Actual del Proyecto

```
dnacenter-ansible/                   # Proyecto principal de la collection
├── 📂 .github/                      # Configuración de GitHub
│   ├── workflows/                   # GitHub Actions workflows
│   └── copilot-instructions.md      # Este archivo
│
├── 📂 plugins/                      # Plugins de Ansible
│   ├── __init__.py
│   ├── README.md
│   ├── 📂 action/                   # Action plugins
│   ├── 📂 doc_fragments/            # Fragmentos de documentación reutilizables
│   ├── 📂 module_utils/             # Utilidades compartidas entre módulos
│   ├── 📂 modules/                  # Módulos principales de DNA Center
│   │   ├── __init__.py
│   │   ├── accesspoint_workflow_manager.py    # Gestión de Access Points
│   │   ├── application_policy_workflow_manager.py # Políticas de aplicación
│   │   ├── device_credential_workflow_manager.py  # Credenciales de dispositivos
│   │   ├── discovery_workflow_manager.py      # Descubrimiento de dispositivos
│   │   ├── inventory_workflow_manager.py      # Gestión de inventario
│   │   ├── network_settings_workflow_manager.py # Configuración de red
│   │   ├── pnp_workflow_manager.py           # Plug and Play
│   │   ├── provision_workflow_manager.py     # Aprovisionamiento
│   │   ├── sda_*.py                          # Software Defined Access
│   │   ├── wireless_*.py                     # Configuración inalámbrica
│   │   └── [900+ módulos específicos]        # Módulos por funcionalidad DNA Center
│   │
│   └── 📂 plugin_utils/             # Utilidades para plugins
│
├── 📂 playbooks/                    # Playbooks de ejemplo y workflows
│   ├── accesspoint_workflow_manager.yml      # Ejemplo Access Points
│   ├── application_policy_workflow_manager.yml # Ejemplo políticas
│   ├── device_provision_workflow.yml         # Ejemplo aprovisionamiento
│   ├── discovery_workflow_manager.yml        # Ejemplo descubrimiento
│   ├── inventory_workflow_manager.yml        # Ejemplo inventario
│   ├── network_settings_workflow_manager.yml # Ejemplo configuración red
│   ├── pnp_workflow_manager.yml              # Ejemplo PnP
│   ├── sda_*.yml                             # Ejemplos SDA
│   ├── wireless_*.yml                        # Ejemplos inalámbrico
│   ├── credentials.template                  # Template credenciales
│   ├── device_details.template               # Template detalles dispositivo
│   └── hosts                                 # Inventario de ejemplo
│
├── 📂 tests/                        # Suite de pruebas
│   ├── integration/                 # Tests de integración
│   ├── unit/                        # Tests unitarios
│   └── sanity/                      # Tests de sanidad
│
├── 📂 docs/                         # Documentación del proyecto
│   ├── conf.py                      # Configuración Sphinx
│   ├── index.rst                    # Documentación principal
│   ├── Makefile                     # Build documentación
│   ├── requirements.txt             # Dependencias docs
│   └── 📂 _gh_include/              # Archivos incluidos en GitHub
│
├── 📂 changelogs/                   # Registro de cambios
│   └── changelog.yaml               # Changelog en formato YAML
│
├── 📂 meta/                         # Metadatos de la collection
│   └── runtime.yml                  # Configuración de runtime
│
├── 📂 .vscode/                      # Configuración VS Code
│   ├── launch.json                  # Configuración debug
│   ├── settings.json                # Configuración workspace
│   └── tasks.json                   # Tareas automatizadas
│
├── 📄 galaxy.yml                    # Configuración Ansible Galaxy
├── 📄 README.md                     # Información principal
├── 📄 requirements.txt              # Dependencias Python (dnacentersdk)
├── 📄 test-requirements.txt         # Dependencias para testing
├── 📄 Pipfile                       # Configuración pipenv
├── 📄 .ansible-lint                 # Configuración ansible-lint
├── 📄 .yamllint.yml                 # Configuración yamllint
├── 📄 .gitignore                    # Archivos ignorados por git
├── 📄 Makefile                      # Comandos de automatización
├── 📄 run_tests.sh                  # Script ejecución tests
├── 📄 LICENSE                       # Licencia del proyecto
├── 📄 CODEOWNERS                    # Propietarios del código
└── 📄 issues.md                     # Documentación de issues conocidos
```

## 🎯 Funciones Principales de Cada Carpeta

### 📁 **plugins/modules/**
- **Propósito**: Módulos Ansible para interactuar con Cisco DNA Center API
- **Funciones**:
  - Operaciones CRUD sobre recursos DNA Center
  - Workflows automatizados para configuraciones complejas
  - Integración con dnacentersdk Python
  - Manejo de idempotencia y estado

### 📁 **plugins/module_utils/**
- **Propósito**: Utilidades compartidas entre módulos
- **Funciones**:
  - Funciones comunes de conexión DNA Center
  - Validadores de parámetros compartidos
  - Manejo de errores estandarizado
  - Transformaciones de datos comunes

### 📁 **playbooks/**
- **Propósito**: Ejemplos de uso y workflows completos
- **Funciones**:
  - Playbooks de demostración por funcionalidad
  - Templates de configuración
  - Workflows end-to-end
  - Ejemplos de mejores prácticas

### 📁 **tests/**
- **Propósito**: Suite completa de testing
- **Funciones**:
  - Tests unitarios para módulos
  - Tests de integración con DNA Center
  - Tests de sanidad para collection
  - Validación de documentación

### 📁 **docs/**
- **Propósito**: Documentación técnica y de usuario
- **Funciones**:
  - Documentación de API por módulo
  - Guías de instalación y uso
  - Ejemplos de configuración
  - Referencia de parámetros

## 📋 Convenciones Específicas del Proyecto

### Módulos Ansible
- **Nomenclatura**: `snake_case` para nombres de módulos
- **Organización**: Un módulo por endpoint o workflow DNA Center
- **Documentación**: YAML completo con examples y return values
- **Versionado**: Seguir semantic versioning en galaxy.yml

### Workflow Managers
- **Propósito**: Módulos que orquestan múltiples operaciones DNA Center
- **Nomenclatura**: `*_workflow_manager.py`
- **Funcionalidad**: Implementan workflows completos (ej: descubrimiento + credenciales + inventario)

### Playbooks de Ejemplo
- **Nomenclatura**: Mismo nombre que el módulo con extensión `.yml`
- **Estructura**: Incluir variables de ejemplo y documentación
- **Templates**: Archivos `.template` para configuraciones sensibles

### Tests
- **Nomenclatura**: `test_[módulo].py` para tests unitarios
- **Organización**: Misma estructura que plugins/modules/
- **Framework**: pytest y ansible-test

## 🔧 Herramientas Específicas del Proyecto

### Linting y Validación
- **ansible-lint**: Validación de mejores prácticas Ansible
- **yamllint**: Validación de sintaxis YAML
- **Configuraciones**: `.ansible-lint` y `.yamllint.yml`

### Testing
- **ansible-test**: Framework oficial de testing Ansible
- **pytest**: Para tests unitarios de módulos Python
- **Integration tests**: Con DNA Center simulado o sandbox

### Dependencias
- **Producción**: `dnacentersdk >= 2.7.2` en requirements.txt
- **Testing**: pytest, ansible-test en test-requirements.txt
- **Development**: pipenv para gestión de entorno

### Automatización
- **Makefile**: Comandos comunes de build y test
- **GitHub Actions**: CI/CD automatizado
- **Scripts**: `run_tests.sh` para ejecución local

## 📊 Matriz de Compatibilidad

### Versiones Soportadas
| DNA Center | Collection | dnacentersdk |
|------------|------------|--------------|
| 2.3.5.3    | 6.13.3     | 2.6.11       |
| 2.3.7.6    | 6.25.0     | 2.8.3        |
| 2.3.7.9    | 6.33.2     | 2.8.6        |
| 3.1.3.0    | ^6.36.0    | ^2.10.1      |

### Requisitos
- **Ansible**: >= 2.15
- **Python**: >= 3.9
- **dnacentersdk**: >= 2.7.2

## 🚀 Flujo de Desarrollo

### Para Nuevos Módulos
1. Identificar endpoint DNA Center API
2. Crear módulo en `plugins/modules/`
3. Implementar documentación YAML
4. Crear tests en `tests/`
5. Añadir playbook de ejemplo
6. Validar con ansible-lint y yamllint
7. Ejecutar tests de integración

### Para Workflow Managers
1. Identificar secuencia de operaciones
2. Diseñar parámetros de entrada
3. Implementar lógica de workflow
4. Manejar rollback en caso de error
5. Documentar dependencies entre pasos
6. Crear playbook de demostración completa

### Para Modificaciones
1. Verificar matriz de compatibilidad
2. Mantener backward compatibility
3. Actualizar documentación
4. Ejecutar suite completa de tests
5. Actualizar changelog.yaml
