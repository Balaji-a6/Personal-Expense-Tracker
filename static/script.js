document.addEventListener('DOMContentLoaded', () => {
    const expenseForm = document.querySelector('[data-expense-form]');
    if (expenseForm) {
        expenseForm.addEventListener('submit', (event) => {
            const title = expenseForm.querySelector('[name="title"]').value.trim();
            const amount = Number(expenseForm.querySelector('[name="amount"]').value);
            const expenseDate = expenseForm.querySelector('[name="date"]').value;
            const errorBox = document.getElementById('jsError');
            const errors = [];
            const today = new Date();
            const localToday = [
                today.getFullYear(),
                String(today.getMonth() + 1).padStart(2, '0'),
                String(today.getDate()).padStart(2, '0'),
            ].join('-');

            if (!title) errors.push('Expense title is required.');
            if (!Number.isFinite(amount) || amount <= 0) errors.push('Amount must be greater than zero.');
            if (!expenseDate) errors.push('Expense date is required.');
            else if (expenseDate > localToday) errors.push('Expense date cannot be in the future.');

            errorBox.replaceChildren();
            if (errors.length) {
                event.preventDefault();
                const list = document.createElement('ul');
                list.className = 'mb-0';
                errors.forEach((message) => {
                    const item = document.createElement('li');
                    item.textContent = message;
                    list.appendChild(item);
                });
                errorBox.appendChild(list);
                errorBox.classList.remove('d-none');
                errorBox.focus();
            } else {
                errorBox.classList.add('d-none');
            }
        });
    }

    const passwordForm = document.querySelector('[data-password-form]');
    if (passwordForm) {
        passwordForm.addEventListener('submit', (event) => {
            const password = passwordForm.querySelector('[name="password1"]').value;
            const confirmation = passwordForm.querySelector('[name="password2"]').value;
            const errorBox = document.getElementById('passwordError');
            if (password !== confirmation) {
                event.preventDefault();
                errorBox.textContent = 'The two passwords do not match.';
                errorBox.classList.remove('d-none');
                passwordForm.querySelector('[name="password2"]').focus();
            } else {
                errorBox.classList.add('d-none');
                errorBox.textContent = '';
            }
        });
    }
});