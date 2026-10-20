/**
 * Al Majid Mission School - Admin Panel Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Confirm Delete Actions
  const deleteForms = document.querySelectorAll('form[data-confirm]');
  deleteForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      const msg = form.getAttribute('data-confirm') || 'Are you sure you want to delete this record?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // Bulk Attendance: "Mark All Present" button
  const markAllPresentBtn = document.getElementById('markAllPresentBtn');
  if (markAllPresentBtn) {
    markAllPresentBtn.addEventListener('click', () => {
      const presentRadios = document.querySelectorAll('input[type="radio"][value="Present"]');
      presentRadios.forEach(radio => {
        radio.checked = true;
      });
    });
  }

  // Quick Filter Auto-submit for Class/Date dropdowns
  const autoSubmitSelects = document.querySelectorAll('.auto-submit-filter');
  autoSubmitSelects.forEach(select => {
    select.addEventListener('change', () => {
      select.closest('form').submit();
    });
  });
});
