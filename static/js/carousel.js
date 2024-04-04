function pauseOrResumeCarousel(carouselId) {
    // console.log(carouselId)
    let carouselElement = $(carouselId);

    // Проверяем, установлена ли пауза на карусели
    if (carouselElement.attr('data-bs-pause') === 'true') {
        // Если пауза установлена, снимаем её и меняем значение атрибута data-bs-pause на 'false'
        carouselElement.attr('data-bs-pause', 'false');
        carouselElement.carousel('cycle');
    } else {
        // Если пауза не установлена, ставим паузу и меняем значение атрибута data-bs-pause на 'true'
        carouselElement.attr('data-bs-pause', 'true');
        carouselElement.carousel('pause');
    }
}

// Функция для перезапуска карусели с начала
function restartCarousel(carouselId) {
    // console.log(carouselId)
    $(carouselId).carousel(0).carousel('pause').carousel('cycle');
}

// Привязка событий к кнопкам
$('#toolsPanel').on('click', '.pauseOrResumeCarousel', function() {
    let carouselId = $(this).data('target');
    // console.log(carouselId)
    pauseOrResumeCarousel(carouselId);
});

$('#toolsPanel').on('click', '.restartCarousel', function() {
    let carouselId = $(this).data('target');
    // console.log(carouselId)
    restartCarousel(carouselId);
});

$('#toolsPanel').on('click', '.closeCarousel', function() {
    let carouselId = this.id.split('_')[0];
    closeCarousel(carouselId);
});

$('#toolsPanel').on('input', '.form-range', function() {
    let sliderId = this.id;
    let carouselId = sliderId.split('_')[0];
    let newInterval = parseInt($(this).val());

    $('#' + carouselId + '_intervalLabel').text((newInterval / 100) + 's');

    // Изменяем data-bs-interval для карусели
    $('#' + carouselId + '_carousel').attr('data-bs-interval', newInterval);

    // Отключаем инициализированную карусель
    $('#' + carouselId + '_carousel').carousel('dispose');

    $('#' + carouselId + '_carousel').carousel();
});

function closeCarousel(carouselId) {
    let carouselContainer = $("#" + carouselId + "_carouselContainer");
    carouselContainer.remove();
    if ($("#toolsPanel").children().length === 0)
        $('#toolsPanel').attr('hidden', true);
}

// Функция вызывается, когда последний слайд карусели становится активным
function onLastSlide(carouselId) {
    // console.log(carouselId)
    let carouselElement = $('#' + carouselId);
    let interval = carouselElement.data('bs-interval');

    carouselElement.attr('data-bs-pause', 'true');

    setTimeout(function() {
        carouselElement.trigger('carouselCompleted', [carouselId]);
    }, interval);
}

// Подписка на событие 'slid.bs.carousel' для всех каруселей
$('#toolsPanel').on('slide.bs.carousel', '.carousel', function() {
    let $this = $(this); // $this теперь указывает на карусель, от которой пришло событие
    let lastItemIndex = $this.find('.carousel-item').length - 1;
    let currentActiveIndex = $this.find('.carousel-item.active').index();

    if (currentActiveIndex === lastItemIndex) {
        $this.carousel('pause');
        onLastSlide($this.attr('id'));
        // console.log('Reached last slide of ' + $this.attr('id'));
    }

    let carouselId = $this.attr('id');
    let soundModeSwitch = $('#' + carouselId.split('_')[0] + '_soundModeSwitch');
    if (soundModeSwitch.is(':checked')) {
        // Воспроизводим звук
        let audio = new Audio('static/audio/click1.mp3');
        audio.play();
    }
});


$('#toolsPanel').on('slid.bs.carousel', '.carousel', function() {
    let $this = $(this);
    let currentActiveItem = $this.find('.carousel-item.active');
    let currentActiveItemAlt = currentActiveItem.find('img').attr('alt');

    $('#' + $this.attr('id').split('_')[0] + '_carouselOverlay').text(currentActiveItemAlt);
});


$('#toolsPanel').on('click', '.carousel-image', function() {
    var carouselId = $(this).closest('.carousel').attr('id');
    var overlay = $('#' + carouselId.split('_')[0] + '_carouselOverlay');
    var switchSelector = '#' + carouselId.split('_')[0] + '_textModeSwitch';

    overlay.css('visibility', 'visible');
    $(switchSelector).prop('checked', true);
});


$('#toolsPanel').on('click', '.carousel-overlay', function() {
    var carouselId = $(this).closest('.carousel').attr('id');
    var switchSelector = '#' + carouselId.split('_')[0] + '_textModeSwitch';

    $(this).css('visibility', 'hidden');
    $(switchSelector).prop('checked', false);
});


$('#toolsPanel').on('change', '.form-check-input', function() {
    var carouselId = $(this).attr('id').split('_')[0];
    var overlay = $('#' + carouselId + '_carouselOverlay');

    if ($(this).is(':checked')) {
        // Если переключатель активен, показываем наложение
        overlay.css('visibility', 'visible');
    } else {
        // Если переключатель неактивен, скрываем наложение
        overlay.css('visibility', 'hidden');
    }
});