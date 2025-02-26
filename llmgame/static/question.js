// handle the user's selection of an option
$('.option-card').click(function () {
    let selOption = $(this).data('option-name');
    //console.log(selOption);
    customConfirm("Are you sure you want to submit this answer?", selOption)
        .then((confirmed) => {
            if (confirmed) {
                // User confirmed, proceed with the AJAX request
                $.ajax({
                    url: '/check_answer',
                    method: 'POST',
                    data: {
                        selected_option: selOption
                    },
                    success: function (response) {
                        // Show feedback
                        document.getElementById('feedback').innerHTML = response.feedback;
                        // Show correct answer
                        document.getElementById(response.answer).style.backgroundColor = "#68f068";
                        // Show/hide Next button
                        if (response.feedback.startsWith("Correct")) {
                            document.getElementById('next-button').style.display = "block";
                        }
                        else {
                            document.getElementById('next-button').style.display = "none";
                            // Show wrong answer
                            document.getElementById(selOption).style.backgroundColor = "#f06868";
                        }

                        // Disable options
                        const optionCards = document.querySelectorAll('.option-card');
                        optionCards.forEach(otherCard => {
                            // Disable jQuery click events
                            $(otherCard).off('click');
                            if (otherCard !== this) {
                                otherCard.disabled = true;
                                otherCard.classList.add('disabled');
                            }
                            // Prevent hover effect
                            otherCard.style.pointerEvents = 'none';
                        });

                        // Disable lifelines
                        const lifelines = document.querySelectorAll('.lifeline-item');
                        lifelines.forEach(otherLifeline => {
                            // Disable jQuery click events
                            $(otherLifeline).off('click');
                            if (otherLifeline !== this) {
                                otherLifeline.disabled = true;
                                otherLifeline.classList.add('disabled');
                            }
                            // Prevent hover effect
                            otherLifeline.style.pointerEvents = 'none';
                        });
                    }
                });
            }
        }
    );
});

function customConfirm(message, selectedOption) {
    const overlay = document.createElement('div');
    overlay.classList.add('confirm-overlay');

    const dialog = document.createElement('div');
    dialog.classList.add('confirm-dialog');

    const optionText = document.createElement('p');
    optionText.innerHTML = `Selected Option: <b>${selectedOption}</b>`; 

    const messageText = document.createElement('p');
    messageText.textContent = message;
    messageText.style.textAlign = 'center';

    const buttonsContainer = document.createElement('div');
    buttonsContainer.classList.add('buttons-container');

    const confirmButton = document.createElement('button');
    confirmButton.textContent = "Confirm";
    confirmButton.classList.add('confirm-button');

    const cancelButton = document.createElement('button');
    cancelButton.textContent = "Cancel";
    cancelButton.classList.add('cancel-button');

    buttonsContainer.appendChild(confirmButton);
    buttonsContainer.appendChild(cancelButton);

    dialog.appendChild(optionText);
    dialog.appendChild(document.createElement('br'));
    dialog.appendChild(messageText);
    dialog.appendChild(buttonsContainer);
    overlay.appendChild(dialog);

    document.body.appendChild(overlay);

    return new Promise((resolve) => {
        confirmButton.addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(true);
        });

        cancelButton.addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(false);
        });
    });
}

function customReveal(message, answer) {
    const overlay = document.createElement('div');
    overlay.classList.add('confirm-overlay');

    const dialog = document.createElement('div');
    dialog.classList.add('confirm-dialog');

    const optionText = document.createElement('p');
    optionText.innerHTML = `The correct answer was: <b>${answer}</b>`; 

    const messageText = document.createElement('p');
    messageText.textContent = message;
    messageText.style.textAlign = 'center';

    const buttonsContainer = document.createElement('div');
    buttonsContainer.classList.add('buttons-container');

    const confirmButton = document.createElement('button');
    confirmButton.textContent = "New";
    confirmButton.classList.add('confirm-button');

    buttonsContainer.appendChild(confirmButton);

    dialog.appendChild(optionText);
    dialog.appendChild(document.createElement('br'));
    dialog.appendChild(messageText);
    dialog.appendChild(buttonsContainer);
    overlay.appendChild(dialog);

    document.body.appendChild(overlay);

    return new Promise((resolve) => {
        confirmButton.addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(true);
        });
    });
}

function customAskHost() {
    const overlay = document.createElement('div');
    overlay.classList.add('confirm-overlay');

    const dialog = document.createElement('div');
    dialog.classList.add('confirm-dialog');
    dialog.style.textAlign = 'center';
    dialog.style.maxWidth = '40%'

    const optionText = document.createElement('p');
    optionText.innerHTML = `You have asked the host...`; 

    const messageText = document.createElement('p');
    messageText.id = 'message-text';
    messageText.textContent = "";
    messageText.style.fontWeight = 'bold';

    const buttonsContainer = document.createElement('div');
    buttonsContainer.classList.add('buttons-container');
    buttonsContainer.style.justifyContent = 'center';

    const loader = document.createElement('div');
    loader.id = 'loader-dialog';
    loader.classList.add('loader');

    const confirmButton = document.createElement('button');
    confirmButton.id = 'ok-button';
    confirmButton.textContent = "OK";
    confirmButton.classList.add('confirm-button');
    confirmButton.style.display = 'none';

    buttonsContainer.appendChild(confirmButton);

    dialog.appendChild(optionText);
    dialog.appendChild(document.createElement('br'));
    dialog.appendChild(messageText);
    dialog.appendChild(loader);
    dialog.appendChild(buttonsContainer);
    overlay.appendChild(dialog);

    document.body.appendChild(overlay);

    // show loader
    loader.style.display = 'block';
    $.ajax({
        url: '/lifeline/ask_host',
        method: 'POST',
        data: {
        },
        success: function (response) {
            // Hide loader
            document.getElementById('loader-dialog').style.display = 'none';

            // Show message
            document.getElementById('message-text').textContent = response.hint;

            // show OK button
            document.getElementById('ok-button').style.display = 'block';
        }
    });

    return new Promise((resolve) => {
        confirmButton.addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(true);
        });
    });
}


// Function to update current question
function setCurrentQuestion(targetQuestionItem) {
    // Remove 'current' class from all items
    questionItems.forEach(item => {
        item.classList.remove('current');
    });

    // Add 'current' class to clicked item
    if (targetQuestionItem != undefined) {
        targetQuestionItem.classList.add('current');
    }
}

// Function to update lifeline in UI:
// if a lifeline has been used, 
// a cross appears and they can't be clicked again
function setUsedLifelines(lifelines, flags)
{
    for (let index = 0; index < lifelines.length; ++index) {
        // lifeline has been used
        if (flags[index] == 0 ) {
            var lifelineImg = lifelines[index].querySelector('.lifeline-img');
            var lifelineCross = lifelines[index].querySelector('.lifeline-cross');

            lifelineCross.style.display = 'block';
            lifelineImg.style.pointerEvents = 'none';
        }
    }
}
