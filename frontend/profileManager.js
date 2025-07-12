// profileManager.js
(function(){
  const selectEl = document.getElementById('profile-select');
  const modal    = document.getElementById('profile-modal');
  const form     = document.getElementById('profile-form');
  const cancelBtn= document.getElementById('cancel-btn');

  const profileManager = {
    profiles: [],
    currentId: 'guest',

    init() {
      this.load();
      this.bindEvents();
      // Ensure modal starts hidden
      this.hideModal();
      this.updateDropdown();
    },

    load() {
      const saved = localStorage.getItem('profiles');
      this.profiles = saved ? JSON.parse(saved) : [];
      const savedId = localStorage.getItem('currentProfileId');
      this.currentId = savedId || 'guest';
    },

    save() {
      localStorage.setItem('profiles', JSON.stringify(this.profiles));
    },

    saveCurrentId() {
      localStorage.setItem('currentProfileId', this.currentId);
    },

    bindEvents() {
      selectEl.addEventListener('change', e => this.onSelectChange(e));
      cancelBtn.addEventListener('click', () => this.onCancel());
      form.addEventListener('submit', e => this.onFormSubmit(e));
    },

    updateDropdown() {
      selectEl.innerHTML = '<option value="guest">Guest</option>';
      this.profiles.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.name;
        selectEl.appendChild(opt);
      });
      const createOpt = document.createElement('option');
      createOpt.value = 'create';
      createOpt.textContent = 'Create New Profile...';
      selectEl.appendChild(createOpt);
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

    onFormSubmit(e) {
      e.preventDefault();
      const data = new FormData(form);
      const newProfile = {
        id: Date.now().toString(),
        name:           data.get('name'),
        age:            data.get('age'),
        blood_group:    data.get('blood_group'),
        pre_cond:       data.get('pre_cond')
      };
      this.profiles.push(newProfile);
      this.save();
      this.currentId = newProfile.id;
      this.saveCurrentId();
      this.updateDropdown();
      this.hideModal();
    },

    getCurrentProfile() {
      if (this.currentId === 'guest') {
        return { id: 'guest', name: 'Guest', age: '', blood_group: '', pre_cond: '' };
      }
      return this.profiles.find(p => p.id === this.currentId)
             || { id: 'guest', name: 'Guest', age: '', blood_group: '', pre_cond: '' };
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
  document.addEventListener('DOMContentLoaded', () => profileManager.init());
})();
