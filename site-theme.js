/* Fixed public-site accent. Older saved colour choices no longer apply. */
(function () {
  'use strict';
  document.documentElement.setAttribute('data-rfc-accent', 'teal');
  try {
    var url = new URL(location.href);
    if (url.searchParams.has('accent')) {
      url.searchParams.delete('accent');
      history.replaceState(history.state, '', url.href);
    }
  } catch (_) { /* Local previews may not permit history updates. */ }
  function updateLinks() {
    document.querySelectorAll('a[href]').forEach(function (link) {
      try {
        var url = new URL(link.getAttribute('href'), document.baseURI);
        if (/^https?:$/.test(url.protocol) &&
            (url.hostname === 'ritmoforcecurve.com' || url.hostname.endsWith('.ritmoforcecurve.com')) &&
            url.origin !== location.origin) {
          url.searchParams.set('accent', 'teal');
          link.href = url.href;
        }
      } catch (_) { /* Leave downloads and non-web links alone. */ }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', updateLinks);
  else updateLinks();
})();
