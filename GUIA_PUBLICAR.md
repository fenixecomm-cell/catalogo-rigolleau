# Cómo publicar el catálogo gratis (para que lo uses en el celular)

La carpeta tiene estos archivos, todos van juntos:

```
index.html
styles.css
app.js
productos.json
catalogo_base.json
fotos/   (139 fotos + 1 genérica "sin-foto.jpg")
```

La forma más simple, sin instalar nada, es **Netlify Drop**:

## Opción A: Netlify Drop (recomendada, 2 minutos)

1. Entrá a https://app.netlify.com/drop desde la computadora.
2. Arrastrá la carpeta `PUJA` completa (o seleccioná todos los archivos de
   adentro) y soltala en esa página.
3. En unos segundos te da un link (algo como `https://nombre-random.netlify.app`).
4. Ese link ya lo podés abrir desde el celular del vendedor y guardarlo como
   acceso directo en la pantalla de inicio.

Para actualizar más adelante (por ejemplo después de correr
`actualizar_precios.py`), volvés a arrastrar la carpeta a la misma página.

## Opción B: GitHub Pages (si ya tenés o querés tener cuenta de GitHub)

1. Creá un repositorio nuevo en GitHub (puede ser privado o público), por
   ejemplo `catalogo-rigolleau`.
2. Subí todos los archivos de la carpeta `PUJA` a ese repositorio (podés
   arrastrarlos desde la web de GitHub, con el botón "Add file" → "Upload files").
3. Andá a **Settings** → **Pages** del repositorio.
4. En "Branch" elegí `main` y la carpeta `/ (root)`, guardá.
5. GitHub te va a dar un link tipo `https://tu-usuario.github.io/catalogo-rigolleau/`.
   Puede tardar 1-2 minutos en estar activo.

Para actualizar: subís de nuevo el archivo `productos.json` (y las fotos si
agregaste productos nuevos) reemplazando el anterior.

## Cuando llegue una lista de precios nueva

No hace falta rehacer nada del catálogo ni de las fotos. Solo:

1. Guardá el Excel nuevo en esta misma carpeta (o anotá dónde quedó).
2. Abrí una terminal en esta carpeta y corré:

   ```
   python actualizar_precios.py "ruta del excel nuevo.xls"
   ```

3. Te va a mostrar en pantalla cuántos productos quedaron con precio y cuáles
   no (por si hay que avisarle algo a Milver).
4. Volvés a subir solo `productos.json` actualizado (Netlify: arrastrás la
   carpeta de nuevo; GitHub Pages: subís el archivo reemplazando el viejo).

Si en algún momento Rigolleau saca un catálogo PDF nuevo con productos que hoy
no existen, ahí sí hay que avisarme para volver a extraer fotos y fichas de ese
PDF (eso no lo hace este script, porque el script solo toca precios).
