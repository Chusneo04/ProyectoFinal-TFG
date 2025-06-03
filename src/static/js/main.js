const usuario_existe = document.getElementById('usuario_existe');

if (usuario_existe) {
  setTimeout(() => {
    usuario_existe.style.opacity = '0'
  }, 2500);
}

if (window.location.search){

  let nuevaUrl = window.location.origin + window.location.pathname

  window.history.replaceState({}, document.title, nuevaUrl)

}