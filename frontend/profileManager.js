(async function(){
  const selectEl   = document.getElementById('profile-select');
  const modal      = document.getElementById('profile-modal');
  const form       = document.getElementById('profile-form');
  const cancelBtn  = document.getElementById('cancel-btn');

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
    guestMode: false,     // ← flag indicating “continue as guest”

    async init() {
      // 1) Load or generate persistent salt
      const saltStored = localStorage.getItem('profiles_salt');
      if (saltStored) {
        this.salt = new Uint8Array(JSON.parse(saltStored));
      } else {
        this.salt = crypto.getRandomValues(new Uint8Array(16));
        localStorage.setItem('profiles_salt', JSON.stringify(Array.from(this.salt)));
      }

      // 2) Attempt to unlock existing data if it exists
      const encBlob = localStorage.getItem('profiles_encrypted');
      if (saltStored && encBlob) {
        let unlocked = false;
        while (!unlocked) {
          const pass = prompt('Enter your profiles passphrase:');
          if (pass === null) {
            // User chose Cancel → continue as guest
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
              'Press OK to retry entering your passphrase,\n' +
              'or Cancel to continue as guest.'
            );
            if (!retry) {
              this.guestMode = true;
              this.profiles = [];
              break;
            }
            // otherwise loop again
          }
        }
      } else {
        // First‐time user (no existing blob)
        const pass = prompt('Create a passphrase to secure your profiles:');
        if (pass === null) throw new Error('Passphrase is required');
        this.key = await deriveKey(pass, this.salt);
        this.profiles = [];
      }

      // 3) Restore last-selected profile (or guest if in guestMode)
      this.currentId = this.guestMode
        ? 'guest'
        : (localStorage.getItem('currentProfileId') || 'guest');

      // 4) Build UI & bind events
      this.updateDropdown();
      this.bindEvents();
      this.hideModal();
    },

    // Encrypt & persist profiles (no-op in guestMode)
    async save() {
      if (this.guestMode) return;
      const encrypted = await encryptData(this.key, this.profiles);
      localStorage.setItem('profiles_encrypted', JSON.stringify(encrypted));
    },

    // Persist the active profile ID
    saveCurrentId() {
      localStorage.setItem('currentProfileId', this.currentId);
    },

    bindEvents() {
      selectEl.addEventListener('change', e => this.onSelectChange(e));
      cancelBtn.addEventListener('click', () => this.onCancel());
      form.addEventListener('submit', e => this.onFormSubmit(e));
    },

    updateDropdown() {
      selectEl.innerHTML = '';
      // Always include Guest option
      const guestOpt = document.createElement('option');
      guestOpt.value = 'guest';
      guestOpt.textContent = 'Guest';
      selectEl.appendChild(guestOpt);

      if (!this.guestMode) {
        // List decrypted profiles only if unlocked
        this.profiles.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = p.name;
          selectEl.appendChild(opt);
        });
        // “Create New Profile…” option
        const createOpt = document.createElement('option');
        createOpt.value = 'create';
        createOpt.textContent = 'Create New Profile…';
        selectEl.appendChild(createOpt);
      }

      selectEl.value = this.currentId;
    },

    onSelectChange(e) {
      const val = e.target.value;
      if (val === 'create') {
        form.reset();
        this.showModal();
      } else {
        this.currentId = val;
        this.saveCurrentId();
        this.hideModal();
      }
    },

    onCancel() {
      this.hideModal();
      selectEl.value = this.currentId;
    },

    async onFormSubmit(e) {
      e.preventDefault();
      const data = new FormData(form);
      const newProfile = {
        id:      Date.now().toString(),
        name:    data.get('name'),
        age:     data.get('age'),
        sex:     data.get('sex'),
        blood_group :    data.get('blood_group'),
        pre_cond: data.get('pre_cond')
      };
      this.profiles.push(newProfile);
      await this.save();
      this.currentId = newProfile.id;
      this.saveCurrentId();
      this.updateDropdown();
      this.hideModal();
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
