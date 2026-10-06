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
  if (!pages.length) return;

  function decode(value) {
    try { return decodeURIComponent(value || ''); }
    catch (_) { return value || ''; }
  }
  function resolve(value) {
    value = decode((value || '').replace(/^#/, '').replace(/^page-/, ''));
    value = files[value] || value;
    return pages.find(function (page) { return page.id === value; });
  }
  function pageForAnchor(anchor) {
    var target = document.getElementById(decode(anchor));
    var panel = target && target.closest('.rfc-page-panel');
    return panel && resolve(panel.getAttribute('data-page'));
  }
  function route(value) {
    var parts = (value || '').replace(/^#/, '').split('/');
    var legacy = decode(parts.join('/'));
    if (legacy === 'ios' || legacy === 'android-recording/ios') {
      return {page:resolve('ios-alignment'), anchor:''};
    }
    var page = resolve(parts[0]);
    if (!page) {
      var category = nav.find(function (item) { return item.id === decode(parts[0]); });
      if (category) page = resolve(category.pages[0].id);
    }
    if (page) return {page:page, anchor:decode(parts.slice(1).join('/'))};
    // Old bookmarks and ordinary section links must also reveal their guide.
    page = pageForAnchor(parts.join('/'));
    return page ? {page:page, anchor:decode(parts.join('/'))} : null;
  }
  function activate(page, push, anchor) {
    page = page || pages[0];
    var panel = document.getElementById('page-' + page.id);
    if (!panel) { window.location.href = page.file + (anchor ? '#' + encodeURIComponent(anchor) : ''); return; }
    document.querySelectorAll('.rfc-page-panel').forEach(function (item) { item.hidden = item !== panel; });
    document.querySelectorAll('[data-category]').forEach(function (item) {
      var selected = item.getAttribute('data-category') === page.category;
      item.classList.toggle('active', selected);
      if (selected) item.setAttribute('aria-current', 'true'); else item.removeAttribute('aria-current');
    });
    var category = nav.find(function (item) { return item.id === page.category; });
    var sub = document.getElementById('subnav');
    if (sub) {
      sub.textContent = ''; sub.hidden = category.pages.length < 2;
      category.pages.forEach(function (item) {
        var link = document.createElement('a'); link.href = item.file; link.textContent = item.title;
        if (item.id === page.id) { link.className = 'active'; link.setAttribute('aria-current', 'page'); }
        sub.appendChild(link);
      });
    }
    document.title = page.title + ' · ritmoForceCurve™';
    if (push) {
      var hash = '#' + encodeURIComponent(page.id) + (anchor ? '/' + encodeURIComponent(anchor) : '');
      if (location.hash !== hash) history.pushState({page:page.id}, '', hash);
    }
    if (anchor) {
      var target = document.getElementById(anchor);
      if (target && panel.contains(target)) {
        var ancestor = target.parentElement;
        while (ancestor && ancestor !== panel) {
          if (ancestor.tagName === 'DETAILS') ancestor.open = true;
          ancestor = ancestor.parentElement;
        }
        target.scrollIntoView();
      }
    } else if (push) { window.scrollTo({top:0,behavior:'auto'}); }
  }
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[href]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
        link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
    var href = link.getAttribute('href');
    if (!href) return;
    if (href.charAt(0) === '#') {
      var match = route(href);
      if (!match) return; // Keep the skip link and unknown anchors native.
      event.preventDefault(); activate(match.page, true, match.anchor); return;
    }
    var url;
    try { url = new URL(href, document.baseURI); } catch (_) { return; }
    var directory = location.pathname.slice(0, location.pathname.lastIndexOf('/') + 1);
    if (url.origin !== location.origin || url.pathname.slice(0, url.pathname.lastIndexOf('/') + 1) !== directory) return;
    var file = decode(url.pathname.slice(url.pathname.lastIndexOf('/') + 1));
    var page = resolve(file);
    var anchor = decode(url.hash.slice(1));
    if (file === 'android_recording.html' && anchor === 'ios') {
      page = resolve('ios-alignment'); anchor = '';
    }
    if (file === 'index.html' || !file) {
      var indexRoute = route(url.hash);
      page = indexRoute ? indexRoute.page : pages[0];
      anchor = indexRoute ? indexRoute.anchor : '';
    }
    if (!page || !document.getElementById('page-' + page.id)) return;
    event.preventDefault(); activate(page, true, anchor);
  });
  function restore() {
    var match = route(window.location.hash);
    if (!match && window.location.hash) return;
    activate(match ? match.page : pages[0], false, match ? match.anchor : '');
  }
  window.addEventListener('popstate', restore);
  window.addEventListener('hashchange', restore);
  restore();
})();
