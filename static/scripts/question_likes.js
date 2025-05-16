export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
const likeButtons = document.querySelectorAll('button[data-question-id]');

for (const button of likeButtons) {
    button.addEventListener('click', function () {

        const request = new Request(
            `/app/question/${button.dataset.questionId}/like?value=${button.dataset.value}`,
            {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin' // Do not send CSRF token to another domain.
            }
        );

        fetch(request).then(response => response.json())
            .then(data => {
                const counter = document.querySelector(`span[data-question-like-counter="${button.dataset.questionId}"]`);
                counter.innerHTML = data.rating;

                const likeBtn = document.querySelector(`button[data-question-id="${button.dataset.questionId}"][data-value="1"]`);
                const dislikeBtn = document.querySelector(`button[data-question-id="${button.dataset.questionId}"][data-value="-1"]`);

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