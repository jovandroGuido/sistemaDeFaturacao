document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('toggleSidebar');
  if (toggle) {
    toggle.addEventListener('click', () => {
      document.querySelector('.sidebar').classList.toggle('collapsed');
    });
  }
  document.querySelectorAll('form.delete-form').forEach(form => {
    form.addEventListener('submit', event => {
      if (!confirm('Deseja realmente excluir este item?')) {
        event.preventDefault();
      }
    });
  });
});
