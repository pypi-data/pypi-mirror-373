# Installation Instructions for txttoqti

## Requisitos Previos

Antes de instalar `txttoqti`, asegúrate de tener instalado Python 3.6 o superior en tu sistema. Puedes verificar tu versión de Python ejecutando el siguiente comando en tu terminal:

```bash
python --version
```

## Instalación

Para instalar el paquete `txttoqti`, puedes utilizar `pip`, el gestor de paquetes de Python. Abre tu terminal y ejecuta el siguiente comando:

```bash
pip install txttoqti
```

## Instalación desde el Código Fuente

Si deseas instalar `txttoqti` desde el código fuente, sigue estos pasos:

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu_usuario/txttoqti.git
   ```

2. Navega al directorio del proyecto:

   ```bash
   cd txttoqti
   ```

3. Instala el paquete utilizando `pip`:

   ```bash
   pip install .
   ```

## Dependencias

`txttoqti` no tiene dependencias externas, ya que utiliza solo la biblioteca estándar de Python. Sin embargo, si deseas contribuir al desarrollo del paquete, puedes instalar las dependencias de desarrollo listadas en `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

## Verificación de la Instalación

Para verificar que `txttoqti` se ha instalado correctamente, puedes ejecutar el siguiente comando en tu terminal:

```bash
python -c "import txttoqti; print(txttoqti.__version__)"
```

Esto debería mostrar la versión instalada del paquete.