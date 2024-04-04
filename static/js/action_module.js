async function processAccordion(accordionId) {
        // console.log('Начало обработки всего аккордеона: ', accordionId);
        const accordionItems = $(`#${accordionId}_action`).find('.accordion-item');
        for (let accordionItem of accordionItems) {
            await processAccordionItem(accordionItem);
        }
        // console.log('Обработка всего аккордеона завершена: ', accordionId);
    }

async function processAccordionItem(accordionItem) {
    // console.log('Начало обработки аккордеона: ', accordionItem.id);
    $(accordionItem).find('.accordion-button').removeClass('collapsed');
    $(accordionItem).find('.accordion-collapse').addClass('show');

    const accordionButton = $(accordionItem).find('.accordion-button');
    const buttonText = accordionButton.text().trim();

    await playAudioAndWait(buttonText);
    await processAccordionBody(accordionItem);

    // Сворачиваем текущий элемент аккордеона
    $(accordionItem).find('.accordion-button').addClass('collapsed');
    $(accordionItem).find('.accordion-collapse').removeClass('show');
    // console.log('Модуль аккордеона завершен: ', accordionItem.id);
}

async function processAccordionBody(accordionItem) {
    // console.log('Начало обработки тела аккордеона');
    const components = $(accordionItem).find('.accordion-body').find('div[id*="Container"]');
    // console.log(components)
    for (let component of components) {
        // console.log(component);
        await processComponent(component);
    }
    // console.log('Тело аккордеона обработано');
}

function playAudioAndWait(text) {
    // console.log('Начало воспроизведения аудио для текста: ', text);
    return generateAudioURLFromText(text).then(audioUrl => {
        return new Promise(resolve => {
            let audio = new Audio(audioUrl);
            audio.play();
            audio.onended = () => {
                // console.log('Аудио завершено: ', text);
                resolve();
            };
        });
    });
}

function processComponent(component) {
    // console.log(component);
    return new Promise(resolve => {
        const componentId = component.id;
        // console.log('Начало обработки компонента: ', componentId);
        const $component = $(component);
        // console.log($component);
        if (componentId.includes('_carouselContainer')) {
            restartCarousel('#' + componentId.split('_')[0] + '_carousel');
            $component.on('carouselCompleted', () => resolve());
        } else if (componentId.includes('_timerContainer')) {
            // console.log('timer');
            startTimer(componentId.split('_')[0]);
            $component.on('timerStopped', () => resolve());
        } else if (componentId.includes('_metronomeContainer')) {
            startMetronome(componentId.split('_')[0]);
            $component.on('metronomeStopped', () => resolve());
        } else if (componentId.includes('_audioContainer')) {
            togglePlayPause(componentId.split('_')[0]);
            $component.on('audioEnded', () => resolve());
        } else if (componentId.includes('_textContainer')) {
            const textPlayButton = $component.find('.play-audio-button');
            if (textPlayButton) {
                textPlayButton.click();
                $component.on('audioTextEnded', () => resolve());
            } else {
                resolve(); // Если текста нет, завершаем обработку
            }
        } else {
            resolve(); // Для неизвестных типов компонентов завершаем обработку
        }
    });
}