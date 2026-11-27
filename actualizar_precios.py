# -*- coding: utf-8 -*-
"""
Actualiza productos.json con una lista de precios nueva de Milver/Rigolleau.

Como usarlo (no hace falta saber programar, solo copiar y pegar el comando):

    python actualizar_precios.py "Milver srl Lista de precios Rigolleau N°XXXX.xls"

Esto:
  1. Lee el Excel nuevo (misma estructura que el original: fila 7 en adelante,
     columnas Id Articulo, Nombre Articulo, Caracteristica, Dto. Adicional,
     Precio CON IVA).
  2. Cruza cada fila con los productos del catalogo (catalogo_base.json) usando
     el numero de 5 digitos que aparece en el nombre del articulo.
  3. Vuelve a escribir productos.json con los precios actualizados.
  4. Muestra en pantalla un resumen: cuantos productos quedaron con precio,
     cuales no, y que filas del Excel no se pudieron cruzar.

No hace falta tocar las fotos ni el catalogo_base.json: esos no cambian.
Si Rigolleau saca productos nuevos que no estaban en el catalogo original,
hay que pedir el PDF actualizado y re-extraerlo (avisar para hacerlo de nuevo).
"""
import sys
import os
import re
import json
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta

try:
    import xlrd
except ImportError:
    print("Falta la libreria 'xlrd'. Instalala con: pip install xlrd")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOGO_BASE = os.path.join(BASE_DIR, 'catalogo_base.json')
PRODUCTOS_JSON = os.path.join(BASE_DIR, 'productos.json')

CATEGORY_SYNONYMS = {
    'Copas': ['copa', 'copas', 'vino', 'trago', 'brindis'],
    'Copas pie bajo': ['copa', 'copas', 'agua', 'vino', 'trago'],
    'Vasos': ['vaso', 'vasos', 'trago', 'agua', 'gaseosa'],
    'Vasos color': ['vaso', 'vasos', 'color', 'trago'],
    'Cerveceros': ['cerveza', 'cervecero', 'cerveceros', 'birra', 'chopp'],
    'Chopps': ['cerveza', 'chop', 'chopp', 'chopps', 'birra', 'cervecero'],
    'Jarros y tazones': ['taza', 'tazon', 'jarro', 'cafe', 'mate', 'te', 'desayuno'],
    'Vajilla': ['plato', 'playo', 'hondo', 'postre', 'vajilla', 'bowl', 'ensaladera', 'compotera'],
    'Fuentes horno': ['horno', 'fuente', 'budinera', 'tartera'],
    'Fuentes horno con tapa': ['horno', 'fuente', 'budinera', 'tartera', 'tapa'],
    'Recipientes hermeticos': ['tupper', 'taper', 'vianda', 'freezer', 'hermetico', 'recipiente'],
    'Bowls y ensaladeras': ['bowl', 'ensaladera', 'compotera', 'ensalada'],
    'Jarras': ['jarra', 'agua', 'jugo'],
    'Decorados': ['decorado', 'diseno', 'regalo'],
}

NAME_SYNONYMS = [
    (r'POSTRE|MILKSHAKE|DEGUSTACION', ['postre', 'helado']),
    (r'CERVEZA|CHOPP|BAL[OÓ]N|PINTA|BRUSELAS|HAMBURGO|AMSTERDAM', ['cerveza', 'birra']),
    (r'CAFE|MOKA|KENYA|KANSAS|CADIZ|GALES|ENCUENTRO|AMANECER', ['cafe', 'te', 'mate', 'taza']),
    (r'HORNO|BUDINERA|TARTERA|FUENTE', ['horno', 'budinera']),
    (r'HERM[EÉ]TIC|RECIP', ['tupper', 'taper', 'vianda']),
    (r'PLAYO|HONDO|POSTRE GOURMET|VAJILLA', ['plato']),
    (r'ENSALADERA|BOWL|COMPOTERA', ['ensaladera', 'bowl']),
]


def strip_accents(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))


def normalize(s):
    s = strip_accents(s).lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def leer_excel(path):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_index(0)
    filas = []
    for r in range(6, sh.nrows):
        id_art = sh.cell_value(r, 0)
        nombre = sh.cell_value(r, 1)
        caracteristica = sh.cell_value(r, 2)
        dto = sh.cell_value(r, 3)
        precio = sh.cell_value(r, 4)
        if not str(nombre).strip():
            continue
        m = re.search(r'\d{5}', str(nombre))
        filas.append({
            'row': r + 1,
            'id_articulo': str(id_art).strip(),
            'nombre': str(nombre).strip(),
            'caracteristica': str(caracteristica).strip(),
            'dto_adicional': str(dto).strip(),
            'precio_con_iva': precio,
            'codigo5': m.group(0) if m else None,
        })

    fecha_serial = sh.cell_value(2, 3)
    fecha_lista = None
    if isinstance(fecha_serial, (int, float)) and fecha_serial:
        fecha_lista = (datetime(1899, 12, 30) + timedelta(days=fecha_serial)).strftime('%d/%m/%Y')

    return filas, fecha_lista


def main():
    if len(sys.argv) < 2:
        print('Uso: python actualizar_precios.py "ruta/a/la lista de precios.xls"')
        sys.exit(1)

    xls_path = sys.argv[1]
    if not os.path.exists(xls_path):
        print(f'No encuentro el archivo: {xls_path}')
        sys.exit(1)

    productos_base = json.load(open(CATALOGO_BASE, encoding='utf-8'))
    filas, fecha_lista = leer_excel(xls_path)

    por_codigo5 = defaultdict(list)
    for fila in filas:
        if fila['codigo5']:
            por_codigo5[fila['codigo5']].append(fila)

    codigos5_catalogo = set(p['codigo5'] for p in productos_base)

    productos_out = []
    con_precio = 0
    sin_precio = []
    for p in productos_base:
        filas_precio = por_codigo5.get(p['codigo5'], [])
        variantes = [{
            'presentacion': f['caracteristica'],
            'descuento': f['dto_adicional'] if f['dto_adicional'] not in ('', ' ') else None,
            'precio_con_iva': f['precio_con_iva'],
        } for f in filas_precio]

        if variantes:
            con_precio += 1
        else:
            sin_precio.append(p)

        kw = set()
        kw.update(CATEGORY_SYNONYMS.get(p['categoria'], []))
        for pattern, syns in NAME_SYNONYMS:
            if re.search(pattern, p['nombre'], re.IGNORECASE):
                kw.update(syns)
        if p['capacidad_ml']:
            kw.add(f"{p['capacidad_ml']}ml")
            kw.add(f"{p['capacidad_ml']} ml")

        buscable = normalize(' '.join([
            p['nombre'], p['categoria'], p['codigo'], str(p.get('ean13') or ''), ' '.join(kw),
        ]))

        productos_out.append({
            'codigo': p['codigo'],
            'nombre': p['nombre'].strip().title(),
            'categoria': p['categoria'],
            'capacidad_ml': p['capacidad_ml'],
            'alto_mm': p['alto_mm'],
            'ancho_mm': p['ancho_mm'],
            'largo_mm': p['largo_mm'],
            'peso_gr': p['peso_gr'],
            'unid_caja': p['unid_caja'],
            'cajas_pallet': p['cajas_pallet'],
            'unid_pallet': p['unid_pallet'],
            'ean13': p['ean13'],
            'foto': f"fotos/{p['foto']}" if p['foto'] else None,
            'variantes': variantes,
            'buscable': buscable,
        })

    sin_catalogo = [f for five, fs in por_codigo5.items() if five not in codigos5_catalogo for f in fs]

    categorias = sorted(set(p['categoria'] for p in productos_out))
    out = {
        'fecha_lista_precios': fecha_lista,
        'categorias': categorias,
        'productos': productos_out,
    }
    with open(PRODUCTOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'Lista de precios: {fecha_lista}')
    print(f'Productos del catalogo: {len(productos_out)}')
    print(f'Productos con precio actualizado: {con_precio}')
    print(f'Productos SIN precio en esta lista: {len(sin_precio)}')
    for p in sin_precio:
        print('  -', p['codigo'], p['nombre'])
    print(f'Filas del Excel que no corresponden a ningun producto del catalogo: {len(sin_catalogo)}')
    for f in sin_catalogo:
        print('  -', f['nombre'], '(fila', f['row'], 'del Excel)')
    print(f'\nproductos.json actualizado en: {PRODUCTOS_JSON}')


if __name__ == '__main__':
    main()
