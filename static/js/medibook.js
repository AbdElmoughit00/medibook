document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-copy-text]').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copyText);
        const old = btn.textContent;
        btn.textContent = 'Copié ✓';
        setTimeout(() => btn.textContent = old, 1200);
      } catch (e) {}
    });
  });

  const specialtySelect = document.getElementById('specialtySelect');
  const specialtyCards = document.querySelectorAll('.specialty-choice-v2');
  const doctorCards = document.getElementById('doctorCards');
  const doctorInput = document.getElementById('doctorInput');
  const dateInput = document.getElementById('dateInput');
  const timeInput = document.getElementById('timeInput');
  const slotsSection = document.getElementById('slotsSection');
  const slotsContainer = document.getElementById('slotsContainer');
  const reasonSection = document.getElementById('reasonSection');
  const submitBtn = document.getElementById('submitBtn');
  const summaryBox = document.getElementById('bookingSummary');
  const summaryText = document.getElementById('summaryText');
  const noDoctorsMsg = document.getElementById('noDoctorsMsg');
  const noSlotsMsg = document.getElementById('noSlotsMsg');
  const doctorCount = document.getElementById('doctorCount');
  const summaryDoctor = document.getElementById('summaryDoctor');
  const summarySlot = document.getElementById('summarySlot');

  if (!specialtySelect || !doctorCards || !window.MEDIBOOK_URLS) return;

  let selectedDoctorName = '';

  const setStep = (id, active) => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('active', active);
  };

  const initials = (name) => {
    const parts = name.trim().split(/\s+/).slice(0, 2);
    return parts.map(p => p[0] || '').join('').toUpperCase() || 'DR';
  };

  const resetSlotChoice = () => {
    dateInput.value = '';
    timeInput.value = '';
    slotsContainer.innerHTML = '';
    slotsSection.classList.add('d-none');
    reasonSection.classList.add('d-none');
    summaryBox.classList.add('d-none');
    submitBtn.disabled = true;
    if (summarySlot) summarySlot.textContent = 'Non sélectionné';
    setStep('stepSlot', false);
    setStep('stepReason', false);
  };

  const renderDoctors = (doctors) => {
    doctorCards.innerHTML = '';
    doctorInput.value = '';
    selectedDoctorName = '';
    if (summaryDoctor) summaryDoctor.textContent = 'Non sélectionné';
    resetSlotChoice();

    noDoctorsMsg.classList.toggle('d-none', doctors.length > 0);
    doctorCount.textContent = `${doctors.length} médecin${doctors.length > 1 ? 's' : ''}`;

    doctors.forEach(doctor => {
      const col = document.createElement('div');
      col.className = 'col-md-6 doctor-card-wrapper';
      const badges = doctor.specialties.map(sp => `<span class="badge badge-soft">${sp}</span>`).join('');
      col.innerHTML = `
        <button type="button" class="choice-card doctor-choice w-100 text-start" data-doctor-id="${doctor.id}">
          <div class="d-flex align-items-start gap-3">
            <div class="doctor-avatar small-avatar">${initials(doctor.name)}</div>
            <div class="flex-grow-1">
              <h5 class="mb-1">Dr. ${doctor.name}</h5>
              <div class="d-flex flex-wrap gap-1 mb-2">${badges}</div>
              <p class="small text-muted mb-1">📍 ${doctor.address}</p>
              <p class="small text-muted mb-0">⏱ ${doctor.experience} ans d'expérience</p>
            </div>
          </div>
        </button>`;
      doctorCards.appendChild(col);
    });
  };

  const loadDoctors = async () => {
    const specialty = specialtySelect.value;
    const url = specialty ? `${window.MEDIBOOK_URLS.doctors}?specialty=${specialty}` : window.MEDIBOOK_URLS.doctors;
    doctorCards.innerHTML = '<div class="col-12"><div class="loading-card">Chargement des médecins...</div></div>';
    try {
      const response = await fetch(url);
      const data = await response.json();
      renderDoctors(data.doctors || []);
    } catch (e) {
      doctorCards.innerHTML = '<div class="col-12"><div class="alert alert-danger">Impossible de charger les médecins.</div></div>';
    }
  };

  const loadSlots = async (doctorId) => {
    resetSlotChoice();
    slotsSection.classList.remove('d-none');
    slotsContainer.innerHTML = '<div class="loading-card">Chargement des créneaux...</div>';
    try {
      const response = await fetch(`${window.MEDIBOOK_URLS.slots}?doctor=${doctorId}`);
      const data = await response.json();
      const groups = data.slots_by_date || [];
      noSlotsMsg.classList.toggle('d-none', groups.length > 0);
      slotsContainer.innerHTML = '';

      groups.forEach(group => {
        const box = document.createElement('div');
        box.className = 'slot-day-card';
        box.innerHTML = `<p class="fw-bold mb-2">📅 ${group.label}</p><div class="slot-choice d-flex flex-wrap gap-2"></div>`;
        const list = box.querySelector('.slot-choice');
        group.slots.forEach(slot => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'btn btn-sm btn-outline-success slot-btn';
          btn.textContent = slot;
          btn.dataset.date = group.date;
          btn.dataset.time = slot;
          list.appendChild(btn);
        });
        slotsContainer.appendChild(box);
      });
    } catch (e) {
      slotsContainer.innerHTML = '<div class="alert alert-danger">Impossible de charger les créneaux.</div>';
    }
  };

  specialtyCards.forEach(card => {
    card.addEventListener('click', () => {
      specialtyCards.forEach(el => el.classList.remove('selected'));
      card.classList.add('selected');
      specialtySelect.value = card.dataset.specialtyId || '';
      setStep('stepSpecialty', true);
      setStep('stepDoctor', false);
      loadDoctors();
    });
  });

  specialtySelect.addEventListener('change', () => {
    setStep('stepSpecialty', true);
    setStep('stepDoctor', false);
    loadDoctors();
  });

  doctorCards.addEventListener('click', (event) => {
    const card = event.target.closest('.doctor-choice');
    if (!card) return;
    document.querySelectorAll('.doctor-choice').forEach(el => el.classList.remove('selected'));
    card.classList.add('selected');
    doctorInput.value = card.dataset.doctorId;
    selectedDoctorName = card.querySelector('h5')?.textContent || 'médecin sélectionné';
    if (summaryDoctor) summaryDoctor.textContent = selectedDoctorName;
    setStep('stepDoctor', true);
    loadSlots(card.dataset.doctorId);
  });

  slotsContainer.addEventListener('click', (event) => {
    const btn = event.target.closest('.slot-btn');
    if (!btn) return;
    document.querySelectorAll('.slot-btn').forEach(el => el.classList.remove('selected'));
    btn.classList.add('selected');
    dateInput.value = btn.dataset.date;
    timeInput.value = btn.dataset.time;
    reasonSection.classList.remove('d-none');
    const line = `${selectedDoctorName} — ${btn.dataset.date} à ${btn.dataset.time}`;
    summaryText.textContent = line;
    if (summarySlot) summarySlot.textContent = `${btn.dataset.date} à ${btn.dataset.time}`;
    summaryBox.classList.remove('d-none');
    submitBtn.disabled = false;
    setStep('stepSlot', true);
    setStep('stepReason', true);
  });
});
