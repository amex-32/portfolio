function esc(s){ return String(s).replace(/[&<>'"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c];}); }
// 2048 + classement

  // ===========================
  (function(){
    'use strict';

    // ---- DOM refs ----
    const boardEl   = document.getElementById('g2048-board');
    const scoreEl   = document.getElementById('g-score');
    const bestEl    = document.getElementById('g-best');
    const msgEl     = document.getElementById('g-msg');
    const newBtn    = document.getElementById('g-new');

    // ---- State ----
    const SIZE = 4;
    let board = []; // flat 16-element array
    let score = 0;
    let best  = 0; try { best = parseInt(localStorage.getItem('ak2048best')||'0',10) || 0; } catch(e) {}

    // ---- Tile colors ----
    const COLORS = {
      2:    {bg:'#f0f8ff',color:'#1a3050'},
      4:    {bg:'#d0e8ff',color:'#1a3050'},
      8:    {bg:'#88c8ff',color:'#0a2040'},
      16:   {bg:'#6699ff',color:'#fff'},
      32:   {bg:'#ffcc66',color:'#5a3000'},
      64:   {bg:'#ff9944',color:'#fff'},
      128:  {bg:'#ff7777',color:'#fff'},
      256:  {bg:'#ff55aa',color:'#fff'},
      512:  {bg:'#cc44ff',color:'#fff'},
      1024: {bg:'#7744ff',color:'#fff'},
      2048: {bg:'#ffd700',color:'#3a2000'},
    };

    function tileStyle(v){
      const c = COLORS[v] || {bg:'#4488ff',color:'#fff'};
      return `background:${c.bg};color:${c.color};`;
    }

    // ---- Board helpers ----
    function emptyBoard(){ return Array(SIZE*SIZE).fill(0); }

    function idx(r,c){ return r*SIZE+c; }

    function empties(b){ const e=[]; b.forEach((v,i)=>{ if(!v) e.push(i); }); return e; }

    function addRandom(b){
      const e = empties(b);
      if(!e.length) return b;
      const pos = e[Math.floor(Math.random()*e.length)];
      const nb = b.slice();
      nb[pos] = Math.random()<0.9?2:4;
      return nb;
    }

    // ---- Slide one row left, returns {row, gain, moved} ----
    function slideRow(row){
      let arr = row.filter(v=>v!==0);
      let gain = 0;
      for(let i=0;i<arr.length-1;i++){
        if(arr[i]===arr[i+1]){
          arr[i]*=2; gain+=arr[i]; arr.splice(i+1,1);
        }
      }
      while(arr.length<SIZE) arr.push(0);
      const moved = arr.some((v,i)=>v!==row[i]);
      return {row:arr, gain, moved};
    }

    // ---- Move in a direction ----
    function move(b, dir){
      let nb = b.slice();
      let totalGain = 0;
      let anyMoved  = false;

      // Transform board so we always slide left on rows
      if(dir==='left'||dir==='right'){
        for(let r=0;r<SIZE;r++){
          let row = nb.slice(r*SIZE,(r+1)*SIZE);
          if(dir==='right') row.reverse();
          const res = slideRow(row);
          if(res.moved) anyMoved=true;
          totalGain += res.gain;
          const outRow = dir==='right'?res.row.slice().reverse():res.row;
          for(let c=0;c<SIZE;c++) nb[idx(r,c)]=outRow[c];
        }
      } else {
        // up / down: work on columns
        for(let c=0;c<SIZE;c++){
          let col = [];
          for(let r=0;r<SIZE;r++) col.push(nb[idx(r,c)]);
          if(dir==='down') col.reverse();
          const res = slideRow(col);
          if(res.moved) anyMoved=true;
          totalGain += res.gain;
          const outCol = dir==='down'?res.row.slice().reverse():res.row;
          for(let r=0;r<SIZE;r++) nb[idx(r,c)]=outCol[r];
        }
      }
      return {nb, gain:totalGain, moved:anyMoved};
    }

    // ---- Game over / win checks ----
    function hasMove(b){
      if(empties(b).length) return true;
      for(let r=0;r<SIZE;r++){
        for(let c=0;c<SIZE;c++){
          const v = b[idx(r,c)];
          if(r+1<SIZE && b[idx(r+1,c)]===v) return true;
          if(c+1<SIZE && b[idx(r,c+1)]===v) return true;
        }
      }
      return false;
    }

    function hasWon(b){ return b.some(v=>v>=2048); }

    // ---- Render ----
    function render(b, mergedIdx){
      // Remove existing tiles (not the background cells)
      boardEl.querySelectorAll('.g2048-tile').forEach(el=>el.remove());

      // Get cell positions from background cells
      const cells = boardEl.querySelectorAll('.g2048-cell');

      b.forEach((v,i)=>{
        if(!v) return;
        const cellRect = cells[i].getBoundingClientRect();
        const boardRect = boardEl.getBoundingClientRect();

        const tile = document.createElement('div');
        tile.className = 'g2048-tile' + (mergedIdx && mergedIdx.has(i) ? ' merged' : '');
        tile.textContent = v;
        tile.style.cssText = `
        position:absolute;
        left:${cells[i].offsetLeft}px;
        top:${cells[i].offsetTop}px;
        width:${cells[i].offsetWidth}px;
        height:${cells[i].offsetHeight}px;
        line-height:${cells[i].offsetHeight}px;
        font-size:${v>=1000?14:v>=100?16:18}px;
        ${tileStyle(v)}
      `;
        boardEl.appendChild(tile);
      });
    }

    function updateScore(){
      scoreEl.textContent = score;
      if(score>best){ best=score; try { localStorage.setItem('ak2048best',best); } catch(e) {} }
      bestEl.textContent = best;
      if(score>0) window.dispatchEvent(new CustomEvent('ak-score',{detail:{game:'2048',score}}));
    }

    // ---- Game flow ----
    function newGame(){
      board = emptyBoard();
      board = addRandom(board);
      board = addRandom(board);
      score = 0;
      msgEl.textContent = '';
      updateScore();
      render(board, null);
    }

    function applyMove(dir){
      const {nb, gain, moved} = move(board, dir);
      if(!moved) return;

      // Track merged indices for animation
      const mergedSet = new Set();
      nb.forEach((v,i)=>{ if(v!==board[i] && v!==0) mergedSet.add(i); });

      board = addRandom(nb);
      score += gain;
      updateScore();
      render(board, mergedSet);

      if(hasWon(board) && !msgEl.textContent){
        msgEl.textContent = '2048 atteint ! Continuez…';
      } else if(!hasMove(board)){
        msgEl.textContent = 'Game over !';
      }
    }

    // ---- Input ----
    document.addEventListener('keydown', e=>{
      if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) return;
      e.preventDefault();
      applyMove(e.key.replace('Arrow','').toLowerCase());
    });

    // Touch swipe — prevent page scroll only when interacting with the board element
    let tx=null, ty=null;
    // boardEl is the actual tile container (id="g2048-board")
    // attach touch handlers to the board only so page scrolling outside remains normal
    // touchstart must be non-passive so we can prevent default on touchmove
    boardEl.addEventListener('touchstart', e=>{
      const t=e.touches[0]; tx=t.clientX; ty=t.clientY;
    }, {passive:false});
    // prevent page from scrolling when moving finger within the board
    boardEl.addEventListener('touchmove', e=>{
      if(tx===null) return; e.preventDefault(); // stops page scroll while interacting with the board
    }, {passive:false});
    boardEl.addEventListener('touchend', e=>{
      if(tx===null) return;
      const t=e.changedTouches[0];
      const dx=t.clientX-tx, dy=t.clientY-ty;
      if(Math.abs(dx)<20 && Math.abs(dy)<20){ tx=ty=null; return; }
      if(Math.abs(dx)>Math.abs(dy)) applyMove(dx>0?'right':'left');
      else applyMove(dy>0?'down':'up');
      tx=ty=null;
    });

    newBtn.addEventListener('click', newGame);

    // Make board position:relative for absolute tile placement
    boardEl.style.position = 'relative';

    // The tiles are placed from the cells' measured size, which is 0 while the 2048 tab is hidden (the page opens on another tab,
    // or the games script selects the tab after this one has run). Place them again whenever the board gets a size.
    if(window.ResizeObserver) new ResizeObserver(()=>{ if(boardEl.offsetWidth) render(board, null); }).observe(boardEl);

    // ---- Init ----
    newGame();

  })();
