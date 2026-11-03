(function () {
  "use strict";

  var list = document.getElementById("list");

  // Live-Updates: der Server schickt beim Verbinden den aktuellen Stand und
  // danach jede Aenderung. EventSource verbindet sich selbst neu.
  if (list && window.EventSource) {
    var source = new EventSource("/events");
    source.onmessage = function (event) {
      list.innerHTML = event.data;
      // htmx verarbeitet per innerHTML eingefuegtes Markup nicht von selbst;
      // ohne diesen Aufruf sind hx-patch/hx-delete an neuen Buttons wirkungslos.
      if (window.htmx) {
        window.htmx.process(list);
      }
    };
  }

  // Leerer Text kommt als 400 zurueck; den Ausschnitt trotzdem in die Liste tauschen,
  // damit der Hinweis sichtbar wird.
  document.body.addEventListener("htmx:beforeSwap", function (event) {
    if (event.detail.xhr && event.detail.xhr.status === 400) {
      event.detail.shouldSwap = true;
      event.detail.isError = false;
    }
  });

  // Kopieren per Delegation, weil die Buttons bei jedem Update neu entstehen.
  document.addEventListener("click", function (event) {
    var button = event.target.closest ? event.target.closest(".copy") : null;
    if (!button) {
      return;
    }
    var text = button.getAttribute("data-copy") || "";
    var done = function () {
      var previous = button.textContent;
      button.textContent = "Kopiert";
      window.setTimeout(function () {
        button.textContent = previous;
      }, 1200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, done);
    } else {
      var area = document.createElement("textarea");
      area.value = text;
      document.body.appendChild(area);
      area.select();
      try {
        document.execCommand("copy");
        done();
      } catch (error) {
        /* nichts weiter */
      }
      document.body.removeChild(area);
    }
  });

  // Dialog fuer "Alles leeren"
  var dialog = document.getElementById("clear-dialog");
  var openButton = document.getElementById("clear-open");
  var cancelButton = document.getElementById("clear-cancel");
  var clearForm = document.getElementById("clear-form");

  if (dialog && openButton) {
    openButton.addEventListener("click", function () {
      dialog.showModal();
    });
  }
  if (dialog && cancelButton) {
    cancelButton.addEventListener("click", function () {
      dialog.close();
    });
  }
  if (dialog && clearForm) {
    clearForm.addEventListener("htmx:afterRequest", function () {
      dialog.close();
      clearForm.reset();
    });
  }
})();
