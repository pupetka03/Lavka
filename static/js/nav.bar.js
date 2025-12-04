
    document.addEventListener('DOMContentLoaded', function() {
        const mobilePostButton = document.getElementById('mobile-post-button');
        const desktopPostButton = document.querySelector('.post-button');
        
        if (mobilePostButton) {
            mobilePostButton.addEventListener('click', function() {
                // Тригер кліку на звичайну кнопку
                if (desktopPostButton) {
                    desktopPostButton.click();
                }
                // Або відкрий модальне вікно
                // openPostModal();
            });
        }
        
        // Пошук на мобільному
        const mobileSearchToggle = document.getElementById('mobile-search-toggle');
        const searchToggle = document.getElementById('search-toggle');
        
        if (mobileSearchToggle && searchToggle) {
            mobileSearchToggle.addEventListener('click', function(e) {
                e.preventDefault();
                searchToggle.click();
            });
        }
    });
