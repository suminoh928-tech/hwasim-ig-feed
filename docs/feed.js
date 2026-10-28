// 화심주조 MEDIA 페이지(/pang/html/media.html)의 #hsj-ig-feed 자리에 인스타그램 최근 게시물을 그린다.
(function () {
  var BASE = 'https://suminoh928-tech.github.io/hwasim-ig-feed/';
  function render() {
    var box = document.getElementById('hsj-ig-feed');
    if (!box) return;
    var mobile = window.matchMedia('(max-width: 768px)').matches;
    box.style.display = 'grid';
    box.style.gridTemplateColumns = mobile ? 'repeat(2, minmax(0, 1fr))' : 'repeat(3, minmax(0, 1fr))';
    box.style.gap = mobile ? '8px' : '16px';
    fetch(BASE + 'feed.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        d.posts.forEach(function (p) {
          var a = document.createElement('a');
          a.href = p.link;
          a.target = '_blank';
          a.rel = 'noopener';
          a.style.cssText = 'display:block;aspect-ratio:1/1;overflow:hidden;background:#eee;';
          var img = document.createElement('img');
          img.src = BASE + p.image;
          img.alt = p.caption ? p.caption.split('\n')[0] : '화심주조 인스타그램 게시물';
          img.loading = 'lazy';
          img.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;transition:opacity .3s;';
          a.onmouseenter = function () { img.style.opacity = '0.75'; };
          a.onmouseleave = function () { img.style.opacity = '1'; };
          a.appendChild(img);
          box.appendChild(a);
        });
      })
      .catch(function () { /* 실패하면 아래 인스타그램 링크만 보인다 */ });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render);
  else render();
})();
