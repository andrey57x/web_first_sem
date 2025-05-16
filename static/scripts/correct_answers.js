import { getCookie } from './question_likes.js';

const csrftoken = getCookie('csrftoken');
const checkboxes = document.querySelectorAll('input[type=checkbox]');
for (const checkbox of checkboxes) {
    checkbox.addEventListener('change', function () {
        const request = new Request(
            `/app/answer/${checkbox.dataset.answerId}/correct?value=${checkbox.checked}`,
            {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin' // Do not send CSRF token to another domain.
            }
        );

        fetch(request)
    });
}