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
  const gallery = document.getElementById("gallery");

  if (!gallery || !toggleButton) return;

  toggleButton.addEventListener("click", () => {
    const isMasonry = gallery.classList.contains("masonry-container");
    const newClass = isMasonry ? "justified-container" : "masonry-container";
    const oldClass = isMasonry ? "masonry-container" : "justified-container";

    gallery.classList.remove(oldClass);
    gallery.classList.add(newClass);

    toggleButton.textContent = isMasonry ? "Switch to Masonry" : "Switch to Justified";

    // update children classes
    const items = gallery.querySelectorAll("div");
    items.forEach(item => {
      item.classList.toggle("masonry-item", !isMasonry);
      item.classList.toggle("justified-item", isMasonry);
    });

    // run justification logic when switching
    if (!isMasonry) {
      justifyGallery(".justified-container");
    }
  });
});


function justifyGallery(containerSelector, rowHeight = 240, gap = 6) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  const items = [...container.children];
  let row = [];
  let rowWidth = 0;
  const containerWidth = container.clientWidth - gap; 

  items.forEach((item, i) => {
    const img = item.querySelector("img, video");
    if (!img) return;

    const aspectRatio = img.naturalWidth / img.naturalHeight;
    const itemWidth = rowHeight * aspectRatio;

    row.push({ item, width: itemWidth });
    rowWidth += itemWidth + gap;

    if (rowWidth >= containerWidth || i === items.length - 1) {
      // scale row to fit perfectly
      const scale = (containerWidth - gap * (row.length - 1)) / (rowWidth - gap);
      row.forEach(({ item, width }) => {
        item.style.flex = `0 0 ${width * scale}px`;
      });
      row = [];
      rowWidth = 0;
    }
  });
}

window.addEventListener("load", () => {
  justifyGallery(".justified-container");
});

window.addEventListener("resize", () => {
  justifyGallery(".justified-container");
});

