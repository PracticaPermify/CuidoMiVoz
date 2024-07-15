'use strict';

window.chrome = window.chrome || {};

{
  chrome.runtime = chrome.runtime || {};
  chrome.runtime.getURL = chrome.runtime.getURL || ((path) => {
    return 'https://' + pwa.cdn + '/gh/' + pwa.repo + '/' + pwa.name + '@' + pwa.version + path;
  });
}

{
  chrome.downloads = chrome.downloads || {
    show() {},
    erase() {},
    cache: new Set(),
    search(e, callback) {
      callback([{
        "id": 0,
        "state": "complete"
      }]);
    },
    onChanged: {
      addListener(callback) {
        chrome.downloads.cache.add(callback);
      },
      removeListener(callback) {
        chrome.downloads.cache.delete(callback);
      }
    },
    download(options, callback) {
      const a = document.createElement('a');
      a.download = options.filename;
      a.href = options.url;
      a.click();
      //
      callback(0);
      //
      window.setTimeout(() => {
        for (const item of chrome.downloads.cache)  {
          item({
            "id": 0,
            "state": {
              "current": "complete"
            }
          });
        }
      }, 300);
    }
  };
}

{
  const storage = {
    'cache': [],
    'name': 'db',
    'version': 2,
    ready() {
      return new Promise((resolve, reject) => {
        storage.cache.push({resolve, reject});
      });
    },
    set(o, c) {
      const db = request.result;
      const tx = db.transaction(storage.name, 'readwrite');
      tx.addEventListener('complete', () => c());
      const store = tx.objectStore(storage.name);
      Object.entries(o).forEach(([name, value]) => store.put({name, value}));
    },
    remove(arr, c) {
      const db = request.result;
      const tx = db.transaction(storage.name, 'readwrite');
      tx.addEventListener('complete', () => c());
      const store = tx.objectStore(storage.name);
      for (const key of Array.isArray(arr) ? arr : [arr]) {
        store.delete(key);
      }
    },
    keys() {
      return new Promise(resolve => {
        const db = request.result;
        const tx = db.transaction(storage.name);
        tx.addEventListener('complete', () => resolve(keys.result || []));
        const store = tx.objectStore(storage.name);
        const index = store.index('name');
        const keys = index.getAllKeys();
      });
    },
    async get(o, c) {
      const keys = o ? Object.keys(o) : await storage.keys();
      const db = request.result;
      const tx = db.transaction(storage.name);
      const prefs = {};
      tx.addEventListener('complete', () => c(prefs));
      const store = tx.objectStore(storage.name);
      //
      for (const key of keys) {
        const request = store.get(key);
        request.onsuccess = e => {
          prefs[key] = e.target.result ? e.target.result.value : o[key];
        };
      }
    }
  };

  const request = indexedDB.open('storage', storage.version);

  request.onsuccess = () => {
    storage.ready = () => Promise.resolve();
    for (const {resolve} of storage.cache) {
      resolve();
    }
  };

  request.onupgradeneeded = e => {
    const db = e.target.result;
    db.createObjectStore(storage.name, {
      'keyPath': 'name'
    }).createIndex('name', 'name', {
      'unique': true
    });
  };
  
  chrome.storage = chrome.storage || {
    'local': {
      get(o, c = () => {}) {
        storage.ready().then(() => storage.get(o, c));
      },
      set(o, c = () => {}) {
        storage.ready().then(() => storage.set(o, c));
      },
      remove(o, c = () => {}) {
        storage.ready().then(() => storage.remove(o, c));
      }
    }
  };
}
