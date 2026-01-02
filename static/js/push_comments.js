document.addEventListener("DOMContentLoaded", () => {
    // 1. Отримання CSRF токена
    const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
    const csrftoken = csrfTokenElement ? csrfTokenElement.content : '';
    
    if (!csrftoken) {
        console.error('CSRF token is missing!');
        return;
    }

    // 2. Елементи модального вікна
    const commentModal = document.getElementById('comment-modal');
    const commentModalClose = document.getElementById('comment-modal-close');
    const commentCancel = document.getElementById('comment-cancel');
    const commentForm = document.getElementById('comment-form');
    const commentPublicationSlug = document.getElementById('comment-publication-slug');
    const commentParentId = document.getElementById('comment-parent-id');
    const commentText = document.getElementById('comment-text');
    const commentModalTitle = document.getElementById('comment-modal-title');

    // 3. ЄДИНИЙ обробник для ВСІХ кнопок коментарів
    document.querySelectorAll('.comments-toggle-btn-origin, .comments-toggle-btn-parent').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            const slug = btn.dataset.slug;
            const parent = btn.dataset.parent || null;
            const isReply = btn.classList.contains('comments-toggle-btn-parent');
            
            // Заповнюємо форму
            commentPublicationSlug.value = slug;
            commentParentId.value = parent;
            commentText.value = '';
            
            // Змінюємо UI для відповіді
            if (isReply) {
                commentModalTitle.textContent = 'Pridať odpoveď';
                commentText.placeholder = '😎 Napíš svoju відповідь... 🎯';
            } else {
                commentModalTitle.textContent = 'Pridať komentár';
                commentText.placeholder = '😎 Napiš niečo fakt cool... 🎯';
            }
            
            // Показуємо модалку
            commentModal.classList.remove('hidden');
            commentText.focus();
        });
    });

    // 4. Закриття модалки (залишаємо як було)
    if (commentModalClose) {
        commentModalClose.addEventListener('click', () => {
            commentModal.classList.add('hidden');
            commentText.value = '';
            commentParentId.value = '';
        });
    }

    if (commentCancel) {
        commentCancel.addEventListener('click', () => {
            commentModal.classList.add('hidden');
            commentText.value = '';
            commentParentId.value = '';
        });
    }

    if (commentModal) {
        commentModal.addEventListener('click', (e) => {
            if (e.target === commentModal) {
                commentModal.classList.add('hidden');
                commentText.value = '';
                commentParentId.value = '';
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && commentModal && !commentModal.classList.contains('hidden')) {
            commentModal.classList.add('hidden');
            commentText.value = '';
            commentParentId.value = '';
        }
    });

    // 5. ЄДИНИЙ обробник відправки форми
    if (commentForm) {
        commentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const slug = commentPublicationSlug.value;
            const text = commentText.value.trim();
            const parent = commentParentId.value;
            
            if (!text) {
                alert('😎 Napiš niečo fakt cool... 🎯!');
                return;
            }
            
            // Формуємо URL залежно від наявності parent
            const url = parent ? `/create_c/${slug}/${parent}/` : `/create_c/${slug}/`;
            
            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ text: text })
                });
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    const error = await response.text();
                    alert('Chyba pri pridávaní komentára.');
                    console.error('Server error:', error);
                }
            } catch (error) {
                console.error('Network Error:', error);
                alert('Chyba pri pridávaní komentára. Перевірте з’єднання.');
            }
        });
    }
});