document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#rsvp form');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            name: this.querySelector('input[placeholder="Ваше имя"]').value,
            guests: this.querySelector('input[placeholder="Количество гостей"]').value,
            wishes: this.querySelector('textarea').value
        };

        try {
            const response = await fetch('http://localhost:5000/send-rsvp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                alert('Спасибо! Ваше подтверждение отправлено.');
                form.reset();
            } else {
                alert('Произошла ошибка при отправке.');
            }
        } catch (error) {
            alert('Ошибка соединения с сервером.');
        }
    });
});

function addGuest() {
    const container = document.getElementById('guestsContainer');
    const currentGuests = container.querySelectorAll('.guest-input').length;
    
    // Проверяем количество гостей (максимум 5)
    if (currentGuests >= 5) {
        alert('Максимальное количество гостей - 5');
        return;
    }
    
    const guestDiv = document.createElement('div');
    guestDiv.className = 'guest-input';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'guests[]';
    input.placeholder = 'Имя гостя';
    input.required = true;
    input.pattern = '^[А-Яа-яЁё]+ [А-Яа-яЁё]+$';
    input.title = 'Введите имя и фамилию через пробел';
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = '✕';
    removeButton.onclick = function() {
        container.removeChild(guestDiv);
        // После удаления гостя проверяем, нужно ли показать кнопку добавления
        const addGuestButton = document.querySelector('button[onclick="addGuest()"]');
        if (container.querySelectorAll('.guest-input').length < 5) {
            addGuestButton.style.display = 'block';
        }
    };
    
    guestDiv.appendChild(input);
    guestDiv.appendChild(removeButton);
    container.appendChild(guestDiv);
    
    // Скрываем кнопку добавления, если достигнут лимит
    if (currentGuests + 1 >= 5) {
        document.querySelector('button[onclick="addGuest()"]').style.display = 'none';
    }
}

function submitForm(event) {
    event.preventDefault();
    
    const form = document.getElementById('rsvpForm');
    const inputs = form.querySelectorAll('input[name="guests[]"]');
    const guests = Array.from(inputs).map(input => input.value);
    
    fetch('http://127.0.0.1:5000/send-rsvp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ guests: guests })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Спасибо! Ваше подтверждение отправлено.');
            inputs.forEach(input => {
                input.value = '';
            });
        } else {
            alert('Произошла ошибка при отправке формы.');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке формы.');
    });
} 