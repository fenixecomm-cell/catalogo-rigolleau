let DATA = { productos: [], categorias: [], fecha_lista_precios: '' };
let categoriaActiva = 'Todas';
let textoBusqueda = '';

const $ = (sel) => document.querySelector(sel);

function normalizar(s) {
  if (!s) return '';
  return s
    .toString()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function singularizar(palabra) {
  if (palabra.length > 3 && palabra.endsWith('es')) return palabra.slice(0, -2);
  if (palabra.length > 3 && palabra.endsWith('s')) return palabra.slice(0, -1);
  return palabra;
}

function coincideProducto(producto, palabrasBusqueda) {
  const base = producto.buscable;
  return palabrasBusqueda.every((palabra) => {
    if (base.includes(palabra)) return true;
    const singular = singularizar(palabra);
    if (singular !== palabra && base.includes(singular)) return true;
    return false;
  });
}

function formatearPrecio(valor) {
  if (valor === null || valor === undefined) return '-';
  return valor.toLocaleString('es-AR', { style: 'currency', currency: 'ARS', minimumFractionDigits: 2 });
}

function precioPrincipal(producto) {
  if (!producto.variantes || producto.variantes.length === 0) return null;
  return producto.variantes[0];
}

function render() {
  const grilla = $('#grilla');
  const sinResultados = $('#sin-resultados');
  const contador = $('#contador');

  const palabras = normalizar(textoBusqueda).split(' ').filter(Boolean);

  const filtrados = DATA.productos.filter((p) => {
    const pasaCategoria = categoriaActiva === 'Todas' || p.categoria === categoriaActiva;
    if (!pasaCategoria) return false;
    if (palabras.length === 0) return true;
    return coincideProducto(p, palabras);
  });

  contador.textContent = `${filtrados.length} producto${filtrados.length === 1 ? '' : 's'}`;
  grilla.innerHTML = '';
  sinResultados.hidden = filtrados.length !== 0;

  const frag = document.createDocumentFragment();
  filtrados.forEach((p) => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'tarjeta';
    card.setAttribute('data-codigo', p.codigo);

    const variante = precioPrincipal(p);
    const precioHtml = variante
      ? `<p class="precio">${formatearPrecio(variante.precio_con_iva)} <span style="font-weight:400;color:#5b6472;font-size:0.72em;">(${variante.presentacion || 'unid.'})</span></p>`
      : `<p class="precio sin-precio">Sin precio cargado</p>`;

    card.innerHTML = `
      <img src="${p.foto || 'fotos/sin-foto.jpg'}" alt="${p.nombre}" loading="lazy"
           onerror="this.onerror=null;this.src='fotos/sin-foto.jpg';">
      <div class="cuerpo">
        <p class="nombre">${p.nombre}</p>
        <p class="meta">${p.codigo}${p.capacidad_ml ? ' · ' + p.capacidad_ml + ' ml' : ''}</p>
        ${precioHtml}
      </div>`;
    card.addEventListener('click', () => abrirModal(p));
    frag.appendChild(card);
  });
  grilla.appendChild(frag);
}

function renderCategorias() {
  const cont = $('#categorias');
  cont.innerHTML = '';
  const todas = ['Todas', ...DATA.categorias];
  todas.forEach((cat) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chip' + (cat === categoriaActiva ? ' activo' : '');
    btn.textContent = cat;
    btn.addEventListener('click', () => {
      categoriaActiva = cat;
      document.querySelectorAll('.chip').forEach((c) => c.classList.remove('activo'));
      btn.classList.add('activo');
      render();
    });
    cont.appendChild(btn);
  });
}

function filaFicha(etiqueta, valor) {
  if (valor === null || valor === undefined || valor === '') return '';
  return `<tr><td>${etiqueta}</td><td>${valor}</td></tr>`;
}

function abrirModal(p) {
  $('#modal-img').src = p.foto || 'fotos/sin-foto.jpg';
  $('#modal-img').onerror = function () { this.onerror = null; this.src = 'fotos/sin-foto.jpg'; };
  $('#modal-img').alt = p.nombre;
  $('#modal-categoria').textContent = p.categoria;
  $('#modal-nombre').textContent = p.nombre;
  $('#modal-codigo').textContent = `Código: ${p.codigo}${p.ean13 ? ' · EAN: ' + p.ean13 : ''}`;

  $('#modal-ficha').innerHTML = [
    filaFicha('Capacidad', p.capacidad_ml ? p.capacidad_ml + ' ml' : ''),
    filaFicha('Medidas (alto x ancho x largo)', (p.alto_mm && p.ancho_mm && p.largo_mm) ? `${p.alto_mm} x ${p.ancho_mm} x ${p.largo_mm} mm` : ''),
    filaFicha('Peso', p.peso_gr ? p.peso_gr + ' gr' : ''),
    filaFicha('Unidades por caja', p.unid_caja),
    filaFicha('Cajas por pallet', p.cajas_pallet),
    filaFicha('Unidades por pallet', p.unid_pallet),
  ].join('');

  const variantesBody = $('#modal-variantes');
  if (p.variantes && p.variantes.length > 0) {
    variantesBody.innerHTML = p.variantes.map((v) => `
      <tr>
        <td>${v.presentacion || 'Unidad'}${v.descuento ? ' · ' + v.descuento : ''}</td>
        <td class="precio-valor">${formatearPrecio(v.precio_con_iva)}</td>
      </tr>`).join('');
  } else {
    variantesBody.innerHTML = `<tr><td class="sin-precio-aviso" colspan="2">Todavía no tenemos precio cargado para este producto. Consultar con administración.</td></tr>`;
  }

  $('#modal').hidden = false;
  document.body.style.overflow = 'hidden';
}

function cerrarModal() {
  $('#modal').hidden = true;
  document.body.style.overflow = '';
}

function init() {
  fetch('productos.json')
    .then((r) => r.json())
    .then((data) => {
      DATA = data;
      $('#fecha-lista').textContent = data.fecha_lista_precios
        ? `Lista mayorista vigente: ${data.fecha_lista_precios}`
        : '';
      renderCategorias();
      render();
    })
    .catch((err) => {
      $('#grilla').innerHTML = '<p>No se pudo cargar productos.json. Revisá que el archivo esté en la misma carpeta.</p>';
      console.error(err);
    });

  $('#buscador-input').addEventListener('input', (e) => {
    textoBusqueda = e.target.value;
    render();
  });
  $('#limpiar-busqueda').addEventListener('click', () => {
    textoBusqueda = '';
    $('#buscador-input').value = '';
    render();
  });
  $('#cerrar-modal').addEventListener('click', cerrarModal);
  $('.modal-fondo').addEventListener('click', cerrarModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') cerrarModal();
  });
}

document.addEventListener('DOMContentLoaded', init);
