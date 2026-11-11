// Static-site data layer: answers api() calls from the JSON files exported by scripts/build_static.py.
// /check/<generator>/<variant> exists for every variant at the cross-check settings (rendered by the Python at build
// time); rendering other parameters with Python (POST /render) needs the local server.
const files = new Map();
async function file(rel) {
  if (!files.has(rel)) files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  return files.get(rel);
}

export async function staticApi(path, body) {
  const clean = path.split('?')[0].replace(/^\/+/, '');
  if (body || clean === 'render') throw new Error('Rendering new parameters with the Python generators needs the local app (Python server).');
  return file(clean);
}
