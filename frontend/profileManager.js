(async function(){
  const selectEl     = document.getElementById('profile-select');
  const modal        = document.getElementById('profile-modal');
  const form         = document.getElementById('profile-form');
  const cancelBtn    = document.getElementById('cancel-btn');
  const editBtn      = document.getElementById('edit-profile-btn');
  const deleteBtn    = document.getElementById('delete-profile-btn');

  // --- Crypto helpers ---
  async function deriveKey(passphrase, salt) {
    const base = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(passphrase),
      'PBKDF2',
      false,
      ['deriveKey']
    );
    return crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt, iterations: 200_000, hash: 'SHA-256' },
      base,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt','decrypt']
    );
  }

  async function encryptData(key, obj) {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encoded = new TextEncoder().encode(JSON.stringify(obj));
    const cipher = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      encoded
    );
    return { iv: Array.from(iv), data: Array.from(new Uint8Array(cipher)) };
  }

  async function decryptData(key, encrypted) {
    const iv = new Uint8Array(encrypted.iv);
    const data = new Uint8Array(encrypted.data);
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      data
    );
    return JSON.parse(new TextDecoder().decode(decrypted));
  }

  // --- Profile Manager ---
  const profileManager = {
    profiles: [],
    currentId: 'guest',
    key: null,
    salt: null,
    guestMode: false,
    editingId: null,   // ← track edit mode

    async init() {
      // 1) Load or generate persistent salt
      const saltStored = localStorage.getItem('profiles_salt');
      if (saltStored) {
        this.salt = new Uint8Array(JSON.parse(saltStored));
      } else {
        this.salt = crypto.getRandomValues(new Uint8Array(16));
        localStorage.setItem('profiles_salt', JSON.stringify(Array.from(this.salt)));
      }

      // 2) Unlock or create
      const encBlob = localStorage.getItem('profiles_encrypted');
      if (saltStored && encBlob) {
        let unlocked = false;
        while (!unlocked) {
          const pass = prompt('Enter your profiles passphrase:');
          if (pass === null) {
            this.guestMode = true;
            this.profiles = [];
            break;
          }
          this.key = await deriveKey(pass, this.salt);
          try {
            this.profiles = await decryptData(this.key, JSON.parse(encBlob));
            unlocked = true;
          } catch {
            const retry = confirm(
              'Passphrase incorrect.\n\n' +
              'Press OK to retry, or Cancel to continue as guest.'
            );
            if (!retry) {
              this.guestMode = true;
              this.profiles = [];
              break;
            }
          }
        }
      } else {
        const pass = prompt('Create a passphrase to secure your profiles:');
        if (pass === null) throw new Error('Passphrase is required');
        this.key = await deriveKey(pass, this.salt);
        this.profiles = [];
      }

      // 3) Restore last-selected (or guest)
      this.currentId = this.guestMode
        ? 'guest'
        : (localStorage.getItem('currentProfileId') || 'guest');

      // 4) Build UI & bind events
      this.updateDropdown();
      this.bindEvents();
      this.updateButtons();
      this.hideModal();
    },

    // Encrypt & persist profiles
    async save() {
      if (this.guestMode) return;
      const encrypted = await encryptData(this.key, this.profiles);
      localStorage.setItem('profiles_encrypted', JSON.stringify(encrypted));
    },

    // Persist which profile is active
    saveCurrentId() {
      localStorage.setItem('currentProfileId', this.currentId);
    },

    bindEvents() {
      selectEl.addEventListener('change',    e => this.onSelectChange(e));
      cancelBtn.addEventListener('click',    () => this.onCancel());
      form.addEventListener('submit',        e => this.onFormSubmit(e));
      editBtn.addEventListener('click',      () => this.onEditProfile());
      deleteBtn.addEventListener('click',    () => this.onDeleteProfile());
    },

    updateDropdown() {
      selectEl.innerHTML = '';
      // Guest
      selectEl.appendChild(Object.assign(document.createElement('option'), {
        value: 'guest', textContent: 'Guest'
      }));
      // Profiles
      if (!this.guestMode) {
        this.profiles.forEach(p => {
          selectEl.appendChild(Object.assign(document.createElement('option'), {
            value: p.id, textContent: p.name
          }));
        });
        selectEl.appendChild(Object.assign(document.createElement('option'), {
          value: 'create', textContent: 'Create New Profile…'
        }));
      }
      selectEl.value = this.currentId;
    },

    updateButtons() {
      const isGuest = this.currentId === 'guest';
      editBtn.disabled   = isGuest;
      deleteBtn.disabled = isGuest;
    },

    onSelectChange(e) {
      const val = e.target.value;
      if (val === 'create') {
        form.reset();
        this.editingId = null;
        this.showModal();
      } else {
        this.currentId = val;
        this.saveCurrentId();
        this.hideModal();
      }
      this.updateButtons();
    },

    onCancel() {
      this.hideModal();
      selectEl.value = this.currentId;
    },

    async onFormSubmit(e) {
      e.preventDefault();
      const data = new FormData(form);
      let profile;
      if (this.editingId) {
        // --- update existing ---
        profile = this.profiles.find(p => p.id === this.editingId);
        profile.name         = data.get('name');
        profile.age          = data.get('age');
        profile.sex          = data.get('sex');
        profile.blood_group  = data.get('blood_group');
        profile.pre_cond     = data.get('pre_cond');
        this.editingId = null;
      } else {
        // --- create new ---
        profile = {
          id: Date.now().toString(),
          name:         data.get('name'),
          age:          data.get('age'),
          sex:          data.get('sex'),
          blood_group:  data.get('blood_group'),
          pre_cond:     data.get('pre_cond')
        };
        this.profiles.push(profile);
      }

      await this.save();
      this.currentId = profile.id;
      this.saveCurrentId();
      this.updateDropdown();
      this.updateButtons();
      this.hideModal();
    },

    onEditProfile() {
      if (this.currentId === 'guest') return;
      const p = this.profiles.find(x => x.id === this.currentId);
      this.editingId = p.id;
      form.elements['name'].value         = p.name;
      form.elements['age'].value          = p.age;
      form.elements['sex'].value          = p.sex;
      form.elements['blood_group'].value  = p.blood_group;
      form.elements['pre_cond'].value     = p.pre_cond;
      this.showModal();
    },

    async onDeleteProfile() {
      if (this.currentId === 'guest') return;
      if (!confirm('Really delete this profile?')) return;
      this.profiles = this.profiles.filter(p => p.id !== this.currentId);
      await this.save();
      this.currentId = 'guest';
      this.saveCurrentId();
      this.updateDropdown();
      this.updateButtons();
    },

    getCurrentProfile() {
      if (this.currentId === 'guest') {
        return { id:'guest', name:'Guest', age:'', sex:'', blood_group:'', pre_cond:'' };
      }
      return this.profiles.find(p => p.id === this.currentId)
          || { id:'guest', name:'Guest', age:'', sex:'', blood_group:'', pre_cond:'' };
    },

    showModal() {
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
    },

    hideModal() {
      modal.classList.add('hidden');
      modal.style.display = 'none';
    }
  };

  window.profileManager = profileManager;
  document.addEventListener('DOMContentLoaded', () => {
    profileManager.init().catch(err => console.error(err));
  });
})();
