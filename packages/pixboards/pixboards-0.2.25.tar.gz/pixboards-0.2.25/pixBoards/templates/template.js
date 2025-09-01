// function shuffleImages() {
//     var container = document.getElementById('masonry-container');
//     var items = container.getElementsByClassName('masonry-item');
//     for (var i = items.length - 1; i > 0; i--) {
//         var j = Math.floor(Math.random() * (i + 1));
//         container.insertBefore(items[j], items[i]);
//     }
// }

function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
}

document.addEventListener("DOMContentLoaded", function () {
    var input = document.getElementById("columnCountInput");
    var container = document.querySelector(".masonry-container");

    if (input && container) {
        input.addEventListener("input", function () {
            const count = parseInt(input.value, 10);
            if (count >= 1) {
                container.style.columnCount = count;
            }
        });
    }
});

function goToPage(page) {
    const base = window.location.pathname.replace(/_\d+\.html$/, '');
    window.location.href = `${base}_${page}.html`;
}

document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("toggleLayout");
  const gallery = document.querySelector(".masonry-container") || document.querySelector(".justified-container");

  if (!gallery || !toggleButton) return;

  toggleButton.addEventListener("click", () => {
    const isMasonry = gallery.classList.contains("masonry-container");
    const newClass = isMasonry ? "justified-container" : "masonry-container";
    const oldClass = isMasonry ? "masonry-container" : "justified-container";

    gallery.classList.remove(oldClass);
    gallery.classList.add(newClass);

    toggleButton.textContent = isMasonry ? "Switch to Masonry" : "Switch to Justified";

    // update all children
    const items = gallery.querySelectorAll("div");
    items.forEach(item => {
      item.classList.toggle("masonry-item", !isMasonry);
      item.classList.toggle("justified-item", isMasonry);
    });
  });
});
