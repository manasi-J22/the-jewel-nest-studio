/* Login & registration form handlers */

function bindLogin() {
  const form = document.getElementById('login-form');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = form.email.value.trim();
    const password = form.password.value;
    const errEl = document.getElementById('form-error');
    errEl.textContent = '';
    try {
      const res = await api('/api/auth/login', {
        method: 'POST', body: { email, password },
      });
      toast('Welcome back', 'success');
      const dest = res.user.role === 'admin' ? 'admin.html' : 'index.html';
      setTimeout(() => { window.location.href = dest; }, 400);
    } catch (err) {
      errEl.textContent = err.message;
    }
  });
}

function bindRegister() {
  const form = document.getElementById('register-form');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('form-error');
    errEl.textContent = '';
    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const phone = form.phone.value.trim();
    const password = form.password.value;
    const confirm = form.confirm.value;
    if (password !== confirm) {
      errEl.textContent = 'Passwords do not match';
      return;
    }
    if (password.length < 6) {
      errEl.textContent = 'Password must be at least 6 characters';
      return;
    }
    try {
      await api('/api/auth/register', {
        method: 'POST', body: { name, email, password, phone },
      });
      toast('Account created', 'success');
      setTimeout(() => { window.location.href = 'index.html'; }, 400);
    } catch (err) {
      errEl.textContent = err.message;
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  bindLogin();
  bindRegister();
});
