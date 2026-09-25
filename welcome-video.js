(function () {
  'use strict';

  function initialize() {
    document.querySelectorAll('[data-rfc-video]').forEach(function (stage) {
      if (stage.dataset.rfcVideoReady) return;
      stage.dataset.rfcVideoReady = 'true';
      var video = stage.querySelector('video');
      var fullscreen = stage.querySelector('[data-rfc-fullscreen]');
      var status = stage.closest('figure').querySelector('[data-rfc-video-status]');
      var resumeTimer;
      var previousOverflow = '';
      if (!video || !fullscreen) return;

      video.controls = false;
      video.muted = true;
      video.defaultMuted = true;
      video.loop = true;
      video.playsInline = true;
      // The film already contains its slow motion. Preserve its original timing.
      fullscreen.hidden = false;

      function isVisible() {
        if (document.hidden || !stage.getClientRects().length) return false;
        var rect = stage.getBoundingClientRect();
        return rect.bottom > 0 && rect.top < window.innerHeight;
      }

      function play() {
        if (!isVisible() || video.error) return;
        var result;
        try { result = video.play(); } catch (error) { return; }
        if (result && typeof result.catch === 'function') {
          result.then(function () {
            status.textContent = '';
          }).catch(function () {
            // Autoplay restrictions are retried on the next page interaction.
          });
        }
      }

      function isFullscreen() {
        return document.fullscreenElement === stage ||
          document.webkitFullscreenElement === stage ||
          stage.classList.contains('is-expanded');
      }

      function updateFullscreen() {
        var active = isFullscreen();
        fullscreen.setAttribute('aria-label', active ? 'Exit full screen' : 'View video full screen');
        fullscreen.title = active ? 'Exit full screen' : 'View video full screen';
        fullscreen.querySelector('span').textContent = active ? 'Exit full screen' : 'Full screen';
        play();
      }

      function expandFallback() {
        previousOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        stage.classList.add('is-expanded');
        updateFullscreen();
      }

      function enterFullscreen() {
        var request = stage.requestFullscreen || stage.webkitRequestFullscreen;
        if (request) {
          try {
            var result = request.call(stage);
            if (result && typeof result.catch === 'function') result.catch(expandFallback);
            return;
          } catch (error) { /* Expand in the page when element fullscreen is unavailable. */ }
        }
        expandFallback();
      }

      function exitFullscreen() {
        if (stage.classList.contains('is-expanded')) {
          stage.classList.remove('is-expanded');
          document.body.style.overflow = previousOverflow;
          updateFullscreen();
        } else {
          var exit = document.exitFullscreen || document.webkitExitFullscreen;
          if (exit) {
            var result = exit.call(document);
            if (result && typeof result.catch === 'function') result.catch(function () {});
          }
        }
      }

      fullscreen.addEventListener('click', function () {
        if (isFullscreen()) exitFullscreen(); else enterFullscreen();
        play();
      });
      document.addEventListener('pointerdown', function () { if (video.paused) play(); }, { passive: true });
      document.addEventListener('keydown', function () { if (video.paused) play(); });
      stage.addEventListener('contextmenu', function (event) { event.preventDefault(); });
      video.addEventListener('playing', function () { status.textContent = ''; });
      video.addEventListener('loadeddata', play);
      video.addEventListener('ended', play);
      video.addEventListener('pause', function () {
        clearTimeout(resumeTimer);
        if (isVisible()) resumeTimer = setTimeout(play, 150);
      });
      video.addEventListener('error', function () {
        status.textContent = 'The rowing video could not load. Refresh the page to try again.';
      });
      document.addEventListener('fullscreenchange', updateFullscreen);
      document.addEventListener('webkitfullscreenchange', updateFullscreen);
      document.addEventListener('visibilitychange', play);
      document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && stage.classList.contains('is-expanded')) exitFullscreen();
      });
      // Native autoplay may pause when another guide hides the welcome panel.
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          if (entries.some(function (entry) { return entry.isIntersecting; })) play();
        }).observe(stage);
      }
      window.addEventListener('pageshow', play);
      play();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
})();
