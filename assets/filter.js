(function(){
  var btns=[].slice.call(document.querySelectorAll('.filters .f'));
  var items=[].slice.call(document.querySelectorAll('#list .svc'));
  var q=document.getElementById('q'),count=document.getElementById('count'),empty=document.getElementById('empty');
  var active='all';
  function apply(){
    var term=(q.value||'').toLowerCase().trim(),n=0;
    items.forEach(function(li){
      var ok=active==='all'||(active==='bpd'?li.dataset.bpd==='1':li.dataset.types.split(' ').indexOf(active)>-1);
      if(ok&&term) ok=li.textContent.toLowerCase().indexOf(term)>-1;
      li.hidden=!ok; if(ok) n++;
    });
    count.textContent=n+(n===1?' service':' services');
    empty.hidden=n>0;
  }
  btns.forEach(function(b){b.addEventListener('click',function(){
    active=b.dataset.f;
    btns.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
    apply();
  });});
  q.addEventListener('input',apply);
  var h=location.hash.replace('#','');
  if(h){var b=btns.filter(function(x){return x.dataset.f===h;})[0]; if(b) b.click();}
})();
