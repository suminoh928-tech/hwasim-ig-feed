// 화심주조 미라온·개화 페이지(/miraon.html, /gaehwa.html)에 스마트스토어 판매 제품을 그린다.
// 페이지 아래 '전체 제품 보기' 검은 칸(.hsj-more) 안, 링크 위에 들어간다. 제품이 없으면 아무것도 그리지 않는다.
(function () {
  var BASE = 'https://suminoh928-tech.github.io/hwasim-ig-feed/';
  var m = location.pathname.match(/^\/(?:pang\/html\/)?(miraon|gaehwa)\.html$/);
  if (!m) return;
  var brand = m[1];
  var en = /^en\./.test(location.hostname);
  var TITLE = en
    ? { miraon: 'Miraon on Naver Smart Store', gaehwa: 'Gaehwa on Naver Smart Store' }
    : { miraon: '스마트스토어의 미라온', gaehwa: '스마트스토어의 개화' };
  var NOTE = en ? 'Each opens its Smart Store page' : '누르면 스마트스토어 상품 페이지로 이동합니다';
  var SOLDOUT = en ? 'Sold out' : '품절';

  var CSS =
    '.hsj-store{max-width:960px;margin:0 auto;padding:0 0 64px;box-sizing:border-box;text-align:center;}' +
    '.hsj-store h4{color:#fff;font-size:24px;font-weight:400;margin:0 0 10px;letter-spacing:.02em;}' +
    '.hsj-store .hsj-store__note{color:#DB9D87;font-size:13px;margin:0 0 28px;}' +
    '.hsj-store__grid{display:flex;flex-wrap:wrap;justify-content:center;gap:24px;}' +
    '.hsj-store__item{display:block;width:calc((100% - 48px)/3);text-decoration:none!important;border:0!important;}' +
    '.hsj-store__img{position:relative;aspect-ratio:1/1;overflow:hidden;background:#fff;}' +
    '.hsj-store__badge{position:absolute;top:10px;left:10px;padding:4px 9px;background:rgba(34,12,0,.82);color:#fff;font-size:12px;line-height:1;letter-spacing:.04em;}' +
    '.hsj-store__img img{width:100%;height:100%;object-fit:cover;display:block;transition:opacity .3s;}' +
    '.hsj-store__item:hover img{opacity:.8;}' +
    '.hsj-store__name{color:#fff;font-size:14px;line-height:1.5;margin:12px 0 0;text-align:left;' +
    'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:keep-all;}' +
    '@media screen and (max-width:767px){.hsj-store{padding-bottom:48px;}.hsj-store h4{font-size:20px;}' +
    '.hsj-store__grid{gap:16px 12px;}.hsj-store__item{width:calc((100% - 12px)/2);}.hsj-store__name{font-size:13px;}}';

  function render(items) {
    var anchor = document.querySelector('.hsj-more');
    if (!anchor || !items || !items.length) return;
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    var box = document.createElement('section');
    box.className = 'hsj-store';
    var h = document.createElement('h4');
    h.textContent = TITLE[brand];
    var note = document.createElement('p');
    note.className = 'hsj-store__note';
    note.textContent = NOTE;
    var grid = document.createElement('div');
    grid.className = 'hsj-store__grid';
    items.forEach(function (p) {
      var a = document.createElement('a');
      a.className = 'hsj-store__item';
      a.href = p.link;
      a.target = '_blank';
      a.rel = 'noopener';
      var frame = document.createElement('div');
      frame.className = 'hsj-store__img';
      var img = document.createElement('img');
      img.src = BASE + p.image;
      var label = (en && p.name_en) || p.name;
      img.alt = label;
      img.loading = 'lazy';
      frame.appendChild(img);
      if (p.soldout) {
        var badge = document.createElement('span');
        badge.className = 'hsj-store__badge';
        badge.textContent = SOLDOUT;
        frame.appendChild(badge);
      }
      var name = document.createElement('p');
      name.className = 'hsj-store__name';
      name.textContent = label;
      a.appendChild(frame);
      a.appendChild(name);
      grid.appendChild(a);
    });
    box.appendChild(h);
    box.appendChild(note);
    box.appendChild(grid);
    anchor.insertBefore(box, anchor.firstChild);
  }

  function load() {
    fetch(BASE + 'store.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (d) { render(d[brand]); })
      .catch(function () { /* 실패하면 기존 구매 버튼만 보인다 */ });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
