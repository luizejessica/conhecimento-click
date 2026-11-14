(function () {
  var modal = document.querySelector('[data-search-modal]');
  var ui = null;
  function openSearch(q) {
    if (!ui && window.PagefindUI) {
      ui = new PagefindUI({
        element: '#busca', showSubResults: true, showImages: false, resetStyles: false,
        translations: {
          placeholder: 'Buscar artigos…', clear_search: 'Limpar', load_more: 'Mais resultados',
          search_label: 'Buscar na central de ajuda', filters_label: 'Filtros',
          zero_results: 'Nenhum resultado para [SEARCH_TERM]',
          many_results: '[COUNT] resultados para [SEARCH_TERM]', one_result: '[COUNT] resultado para [SEARCH_TERM]',
          alt_search: 'Nenhum resultado para [SEARCH_TERM]. Mostrando resultados para [DIFFERENT_TERM]',
          search_suggestion: 'Nenhum resultado para [SEARCH_TERM]. Tente outra busca:', searching: 'Buscando [SEARCH_TERM]…'
        }
      });
    }
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    setTimeout(function () {
      var input = modal.querySelector('input');
      if (input) { if (q) { ui.triggerSearch(q); } input.focus(); input.select(); }
    }, 30);
  }
  function closeSearch() { modal.hidden = true; document.body.style.overflow = ''; }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-open-search]')) { e.preventDefault(); openSearch(); }
    else if (e.target.closest('[data-close-search]')) closeSearch();
    else if (!modal.hidden && e.target.closest('.pagefind-ui__result-link')) closeSearch();
  });
  document.addEventListener('keydown', function (e) {
    var tag = (e.target.tagName || '').toLowerCase();
    if (e.key === '/' && modal.hidden && tag !== 'input' && tag !== 'textarea') { e.preventDefault(); openSearch(); }
    else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openSearch(); }
    else if (e.key === 'Escape') { if (!modal.hidden) closeSearch(); else if (!lb.hidden) lb.hidden = true; }
  });
  var q = new URLSearchParams(location.search).get('q');
  if (q) openSearch(q);

  // tema
  var tbtn = document.querySelector('[data-theme-toggle]');
  tbtn && tbtn.addEventListener('click', function () {
    var root = document.documentElement;
    var dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('tema', root.dataset.theme); } catch (e) {}
  });

  // zoom de imagens
  var lb = document.querySelector('[data-lightbox]');
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a.zoom');
    if (a) { e.preventDefault(); lb.querySelector('img').src = a.getAttribute('href'); lb.hidden = false; }
    else if (e.target.closest('[data-lightbox]')) lb.hidden = true;
  });

  // rola o menu lateral até o item atual
  var act = document.querySelector('.sidebar a.active');
  if (act && act.scrollIntoView && window.innerWidth > 900) act.scrollIntoView({ block: 'center' });
  if (window.innerWidth <= 900) { var sd = document.querySelector('.side-mobile'); if (sd) sd.open = false; }
})();
