// Dashboard logic — vanilla JS, no frameworks.
const $ = (s, r=document) => r.querySelector(s);
const list = $('#todo-list');
const form = $('#todo-form');
const input = $('#todo-input');
const prioritySel = $('#todo-priority');
const empty = $('#empty');
const filters = document.querySelectorAll('.chip');

let todos = [];
let filter = 'all';

async function api(path, opts={}){
  const res = await fetch(path, {
    headers:{'Content-Type':'application/json'},
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if(res.status===401){ window.location='/login'; return; }
  if(!res.ok) throw new Error('Request failed');
  return res.status===204 ? null : res.json();
}

function render(){
  const filtered = todos.filter(t =>
    filter==='all' ? true : filter==='done' ? t.completed : !t.completed
  );
  list.innerHTML='';
  filtered.forEach(t=>{
    const li = document.createElement('li');
    li.className = 'todo' + (t.completed?' done':'');
    li.dataset.id = t.id;
    li.innerHTML = `
      <button class="todo__check" aria-label="Toggle">✓</button>
      <span class="todo__title"></span>
      <span class="todo__pri pri-${t.priority}">${t.priority}</span>
      <button class="todo__del" aria-label="Delete">✕</button>`;
    li.querySelector('.todo__title').textContent = t.title;
    li.querySelector('.todo__check').addEventListener('click', ()=>toggle(t));
    li.querySelector('.todo__del').addEventListener('click', ()=>remove(t, li));
    list.appendChild(li);
  });
  empty.classList.toggle('hidden', filtered.length>0);
  updateStats();
}

function updateStats(){
  $('#stat-total').textContent = todos.length;
  $('#stat-done').textContent  = todos.filter(t=>t.completed).length;
  $('#stat-open').textContent  = todos.filter(t=>!t.completed).length;
}

async function load(){
  todos = await api('/api/todos') || [];
  render();
}

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const title = input.value.trim();
  if(!title) return;
  const created = await api('/api/todos',{method:'POST',body:{title,priority:prioritySel.value}});
  todos.unshift(created);
  input.value='';
  render();
});

async function toggle(t){
  const updated = await api(`/api/todos/${t.id}`,{method:'PATCH',body:{completed:!t.completed}});
  Object.assign(t, updated);
  render();
}

async function remove(t, li){
  li.classList.add('removing');
  await new Promise(r=>setTimeout(r,260));
  await api(`/api/todos/${t.id}`,{method:'DELETE'});
  todos = todos.filter(x=>x.id!==t.id);
  render();
}

filters.forEach(c => c.addEventListener('click', ()=>{
  filters.forEach(x=>x.classList.remove('chip--active'));
  c.classList.add('chip--active');
  filter = c.dataset.filter;
  render();
}));

load();
