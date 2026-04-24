# Proyecto TDA2005 con modulo bluetooth
Proyecto universitario enfocado en el diseño, simulación y construcción de un amplificador de audio basado en un amplificador TDA2005, utilizado para alimentar un altavoz estero de 20W.

# Contenido del repositorio

El repositorio incluye los siguientes archivos relacionados con el proyecto:

- **math.m**

código de matlab para calcular valores de resistencias y capacitores de un transistor JFET para el acoplamiento de la señal

- **esquematico/**

La carpeta contiene imagenes del circuito en donde se puede ver cómo es que fue armado y las vias hechas

- **proteus.pdsprj**

Posee los archivos del software de Proteus donde se tiene el esquematico

- **esp32/esp32.ino**

Tiene el archivo de arduino con el código el cual se programó el integrado

- **informe proyecto 2.pdf**

Posee la información, datos y requisitos del proyecto y explicación acerca de cómo se realizó junto con explicación del código

- **presentación proyecto 2.pdf**

Diapositivas para la presentación del informe hacia el publico objetivo.

- **servidor externo/**

Esta carpeta posee los archivos del servidor que se propone usar para conectarse con la esp32 de forma remota para usar el proyecto a una mayor distancia que una conexión bluetooth

**Cómo construir el proyecto**

estando en la carpeta principal del proyecto:

```
cd '.\servidor externo\
pnpm install
pip install yt-dlp -U
choco install ffmpeg-full
pnpm run pm2:start
```

de otra forma, el proyecto está compilado en un .exe para que pueda correrse de forma immediata después de descargar el repositorio

## Objetivo del proyecto

Diseñar y construir un amplificador de audio estereo que pueda conectarse con bluetooth y wifi de tal forma que pueda ser controlado de forma cercana con bluetooth o lejana al conectarse a una red.
