import { getCookie } from './question_likes.js';

const csrftoken = getCookie('csrftoken');
const likeButtons = document.querySelectorAll('button[data-answer-id]');

for (const button of likeButtons) {
    button.addEventListener('click', function () {

        const request = new Request(
            `/app/answer/${button.dataset.answerId}/like?value=${button.dataset.value}`,
            {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin' // Do not send CSRF token to another domain.
            }
        );

        fetch(request).then(response => response.json())
            .then(data => {
                const counter = document.querySelector(`span[data-answer-like-counter="${button.dataset.answerId}"]`);
                counter.innerHTML = data.rating;

                const likeBtn = document.querySelector(`button[data-answer-id="${button.dataset.answerId}"][data-value="1"]`);
                const dislikeBtn = document.querySelector(`button[data-answer-id="${button.dataset.answerId}"][data-value="-1"]`);

                if (data.state == '1') {
                    likeBtn.classList.add('active');
                    dislikeBtn.classList.remove('active');
                } else if (data.state == '-1') {
                    likeBtn.classList.remove('active');
                    dislikeBtn.classList.add('active');
                }
                else{
                    likeBtn.classList.remove('active');
                    dislikeBtn.classList.remove('active');
                }
            });
    });
}