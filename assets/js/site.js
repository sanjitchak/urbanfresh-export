(() => {
  const GOOGLE_SHEETS_ENDPOINT = 'https://script.google.com/macros/s/AKfycbxIdZtDFyn-_gj9eOL_12WW2hK-pon9Nbb5-fAKiMDG77aOH4AQppq-80cQ1hI0LUVh1A/exec';
  const phone = '919433569217';
  const body = document.body;
  const menu = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('[data-main-nav]');

  if (menu && nav) {
    const closeMenu = () => {
      body.classList.remove('nav-open');
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', 'Open navigation');
    };

    menu.addEventListener('click', () => {
      const open = body.classList.toggle('nav-open');
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });

    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }

  const year = document.querySelector('[data-year]');
  if (year) year.textContent = new Date().getFullYear();

  const whatsappFollowUp = document.querySelector('[data-whatsapp-follow-up]');
  if (whatsappFollowUp) {
    const genericMessage = 'Hello UrbanFresh, I submitted an international rice RFQ and would like to continue on WhatsApp.';
    let followUpUrl = `https://wa.me/${phone}?text=${encodeURIComponent(genericMessage)}`;

    try {
      const savedUrl = window.sessionStorage.getItem('urbanfresh_quote_whatsapp_url');
      if (savedUrl && savedUrl.startsWith(`https://wa.me/${phone}`)) followUpUrl = savedUrl;
      window.sessionStorage.removeItem('urbanfresh_quote_whatsapp_url');
    } catch (error) {
      // The generic WhatsApp message still works if browser storage is unavailable.
    }

    whatsappFollowUp.href = followUpUrl;
  }

  const form = document.querySelector('[data-quote-form]');
  if (!form) return;

  const status = form.querySelector('[data-form-status]');
  const submitButton = form.querySelector('button[type="submit"]');
  const defaultButtonText = submitButton.textContent;
  const requiredNames = ['name', 'phone', 'location', 'quantity'];

  const showStatus = (message, state) => {
    status.textContent = message;
    status.className = `form-status show ${state}`;
    status.focus({ preventScroll: true });
  };

  const makeLeadId = () => {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') return window.crypto.randomUUID();
    return `uf-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  };

  const whatsappUrl = (data) => {
    const lines = [
      'Hello UrbanFresh, I have submitted an international rice RFQ.',
      '',
      `Name or company: ${data.get('name')}`,
      `Phone: ${data.get('phone')}`,
      `Destination country / port: ${data.get('location')}`,
      `Buyer type: ${data.get('buyer_type') || 'Not specified'}`,
      `Rice: ${data.get('variety') || 'Please advise'}`,
      `Processing: ${data.get('processing') || 'Please advise'}`,
      `Quantity: ${data.get('quantity')}`,
      `Packaging: ${data.get('packaging') || 'Please advise'}`,
      `Target shipment window: ${data.get('timeline') || 'Not specified'}`,
      `Notes: ${data.get('message') || 'None'}`
    ];
    return `https://wa.me/${phone}?text=${encodeURIComponent(lines.join('\n'))}`;
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.className = 'form-status';

    const data = new FormData(form);
    const missingInput = requiredNames
      .map((name) => form.elements.namedItem(name))
      .find((input) => !String(data.get(input.name) || '').trim());

    if (missingInput) {
      missingInput.setAttribute('aria-invalid', 'true');
      showStatus('Please add your name, phone number, destination and approximate quantity.', 'error');
      missingInput.focus();
      return;
    }

    requiredNames.forEach((name) => form.elements.namedItem(name).removeAttribute('aria-invalid'));

    if (!GOOGLE_SHEETS_ENDPOINT) {
      showStatus('The quote form is being connected. Please send this request on WhatsApp for now.', 'error');
      const fallback = document.createElement('a');
      fallback.href = whatsappUrl(data);
      fallback.target = '_blank';
      fallback.rel = 'noopener';
      fallback.className = 'text-link status-link';
      fallback.textContent = 'Send on WhatsApp';
      status.append(document.createElement('br'), fallback);
      return;
    }

    data.set('lead_id', makeLeadId());
    data.set('source_page', window.location.href);
    const followUpUrl = whatsappUrl(data);
    submitButton.disabled = true;
    submitButton.textContent = 'Saving your request...';
    form.setAttribute('aria-busy', 'true');

    try {
      await fetch(GOOGLE_SHEETS_ENDPOINT, {
        method: 'POST',
        mode: 'no-cors',
        body: new URLSearchParams(data)
      });

      try {
        window.sessionStorage.setItem('urbanfresh_quote_whatsapp_url', followUpUrl);
      } catch (error) {
        // The thank-you page supplies a generic WhatsApp message as a fallback.
      }

      window.location.assign('thank-you.html');
    } catch (error) {
      showStatus('We could not save the request. Check your connection or send the details on WhatsApp.', 'error');
      const fallback = document.createElement('a');
      fallback.href = whatsappUrl(data);
      fallback.target = '_blank';
      fallback.rel = 'noopener';
      fallback.className = 'text-link status-link';
      fallback.textContent = 'Send on WhatsApp';
      status.append(document.createElement('br'), fallback);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = defaultButtonText;
      form.removeAttribute('aria-busy');
    }
  });
})();
