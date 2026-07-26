(function () {
    // Placeholder — replace with the real "how it works" video ID.
    var DEMO_VIDEO_ID = 'dQw4w9WgXcQ';

    var trigger = document.getElementById('how-it-works-trigger');
    var overlay = document.getElementById('how-it-works-overlay');
    var closeBtn = document.getElementById('how-it-works-close');
    var iframe = document.getElementById('how-it-works-iframe');

    if (!trigger || !overlay || !closeBtn || !iframe) return;

    function openModal(event) {
        event.preventDefault();
        iframe.src = 'https://www.youtube.com/embed/' + DEMO_VIDEO_ID + '?autoplay=1';
        overlay.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        overlay.classList.remove('is-open');
        iframe.src = 'about:blank'; // unload the iframe so playback actually stops
        document.body.style.overflow = '';
    }

    trigger.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);

    overlay.addEventListener('click', function (event) {
        if (event.target === overlay) closeModal();
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
    });
})();
