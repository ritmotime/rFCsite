/* Shared Ritmo Help embed. Appearance is managed in Chatling. */
(function () {
  'use strict';
  // The public example report can also be embedded in the main website.
  // Keep one helper in the surrounding page instead of another inside its frame.
  if (window.self !== window.top || document.getElementById('chtl-script')) return;

  window.chtlConfig = Object.assign({}, window.chtlConfig || {}, {
    chatbotId: '6638573337',
    displayType: 'floating'
  });
  var embed = document.createElement('script');
  embed.async = true;
  embed.dataset.id = '6638573337';
  embed.id = 'chtl-script';
  embed.type = 'text/javascript';
  embed.src = 'https://chatling.ai/js/embed.js';
  document.body.appendChild(embed);
})();
