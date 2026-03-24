document.addEventListener('DOMContentLoaded', function() {
    const taskCards = document.querySelectorAll('.task-card');
    const dropZones = document.querySelectorAll('.task-drop-zone');

    taskCards.forEach(card => {
        card.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.dataset.taskId);
            this.classList.add('dragging');
        });

        card.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            dropZones.forEach(zone => zone.classList.remove('drag-over'));
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');

            const taskId = e.dataTransfer.getData('text/plain');
            const newListId = this.dataset.listId;

            // Calcular posicion
            const cards = this.querySelectorAll('.task-card');
            let position = cards.length;

            // Obtener CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                              document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];

            fetch('/api/move-task/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    task_id: parseInt(taskId),
                    new_list_id: parseInt(newListId),
                    position: position
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // Mover la tarjeta visualmente
                    const card = document.querySelector(`[data-task-id="${taskId}"]`);
                    if (card) {
                        this.appendChild(card);
                    }
                }
            })
            .catch(err => console.error('Error moviendo tarea:', err));
        });
    });
});
