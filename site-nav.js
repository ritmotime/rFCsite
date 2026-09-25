(function () {
  'use strict';
  var nav = window.RFC_NAV || [];
  var pages = [], files = {};
  nav.forEach(function (category) {
    category.pages.forEach(function (page) {
      page.category = category.id;
      pages.push(page); files[page.file] = page.id;
    });
  });
  function resolve(value) {
    value = decodeURIComponent((value || '').replace(/^#(?:page-)?/, ''));
    value = files[value] || value;
    return pages.find(function (page) { return page.id === value; });
  }
  function activate(page, push, anchor) {
    page = page || pages[0];
    var panel = document.getElementById('page-' + page.id);
    if (!panel) { window.location.href = page.file + (anchor ? '#' + anchor : ''); return; }
    document.querySelectorAll('.rfc-page-panel').forEach(function (item) { item.hidden = item !== panel; });
    document.querySelectorAll('[data-category]').forEach(function (item) {
      var selected = item.getAttribute('data-category') === page.category;
      item.classList.toggle('active', selected);
      if (selected) item.setAttribute('aria-current', 'true'); else item.removeAttribute('aria-current');
    });
    var category = nav.find(function (item) { return item.id === page.category; });
    var sub = document.getElementById('subnav'); sub.textContent = ''; sub.hidden = category.pages.length < 2;
    category.pages.forEach(function (item) {
      var link = document.createElement('a'); link.href = item.file; link.textContent = item.title;
      if (item.id === page.id) { link.className = 'active'; link.setAttribute('aria-current', 'page'); }
      sub.appendChild(link);
    });
    document.title = page.title + ' · ritmoForceCurve™';
    if (push) history.pushState({page:page.id}, '', '#' + page.id + (anchor ? '/' + anchor : ''));
    if (anchor) {
      var target = document.getElementById(anchor);
      if (target && panel.contains(target)) target.scrollIntoView();
    } else if (push) { window.scrollTo({top:0,behavior:'auto'}); }
  }
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[href]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.target === '_blank') return;
    var href = link.getAttribute('href');
    if (!href || /^(?:[a-z]+:|\/\/|#)/i.test(href)) return;
    var file = href.split(/[?#]/)[0], page = resolve(file);
    if (!page || !document.getElementById('page-' + page.id)) return;
    event.preventDefault(); activate(page, true, href.indexOf('#') >= 0 ? href.split('#').slice(1).join('#') : '');
  });
  function restore() {
    var parts = window.location.hash.slice(1).split('/');
    var page = resolve(parts[0]);
    if (!page && nav.some(function(cat){return cat.id === parts[0];})) {
      var cat = nav.find(function(item){return item.id === parts[0];}); page = resolve(cat.pages[0].id);
    }
    if (!page && parts[0]) return; // Leave ordinary in-page anchors in the current panel.
    activate(page, false, parts[1] || '');
  }
  window.addEventListener('popstate', restore);
  window.addEventListener('hashchange', restore);
  restore();
})();
