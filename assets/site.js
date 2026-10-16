(function () {
  // Keep the current tab visible in the scrolling tab bar on phones.
  var scroller = document.querySelector('.tabs ul');
  var current = document.querySelector('.tabs a[aria-current="page"]');
  if (scroller && current) {
    var item = current.parentNode;
    if (item.offsetLeft + item.offsetWidth > scroller.clientWidth) {
      scroller.scrollLeft = Math.max(0, item.offsetLeft - 16);
    }
  }

  // Copy buttons (email address, speaker bio).
  Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'), function (btn) {
    var target = document.getElementById(btn.getAttribute('data-copy'));
    if (!target) return;
    var original = btn.textContent;
    btn.addEventListener('click', function () {
      var text = (target.innerText || target.textContent).trim();
      function done(label) {
        btn.textContent = label;
        setTimeout(function () { btn.textContent = original; }, 2000);
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
