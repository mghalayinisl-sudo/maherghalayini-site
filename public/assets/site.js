(function () {
  // Menu button on phones and tablets: opens and closes the list of tabs.
  var header = document.querySelector('.site-header');
  var btn = document.querySelector('.menu-btn');
  if (header && btn) {
    var label = btn.querySelector('.menu-label');
    var setOpen = function (open) {
      header.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (label) label.textContent = open ? 'Close' : 'Menu';
    };
    btn.addEventListener('click', function () {
      setOpen(!header.classList.contains('open'));
    });
    document.addEventListener('click', function (e) {
      if (header.classList.contains('open') && !header.contains(e.target)) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('open')) {
        setOpen(false);
        btn.focus();
      }
    });
    // Close the menu when returning to a page with the Back button.
    window.addEventListener('pageshow', function () { setOpen(false); });
  }

  // Copy buttons (email address, speaker bio).
  Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'), function (copyBtn) {
    var target = document.getElementById(copyBtn.getAttribute('data-copy'));
    if (!target) return;
    var original = copyBtn.textContent;
    copyBtn.addEventListener('click', function () {
      var text = (target.innerText || target.textContent).trim();
      function done(text) {
        copyBtn.textContent = text;
        setTimeout(function () { copyBtn.textContent = original; }, 2000);
      }
      function selectIt() {
        try {
          var range = document.createRange();
          range.selectNodeContents(target);
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          done('Selected');
        } catch (e) { done(original); }
      }
      try {
        navigator.clipboard.writeText(text).then(function () { done('Copied'); }, selectIt);
      } catch (e) { selectIt(); }
    });
  });
})();
