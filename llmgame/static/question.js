// handle the user's selection of an option
$('.option-card').click(function () {
    let selOption = $(this).data('option-name');
    //console.log(selOption);
    customConfirm("Are you sure you want to submit this answer?")
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

                    }
                });
            }
        }
    );
});

function customConfirm(message) {
    const overlay = document.createElement('div');
    overlay.classList.add('confirm-overlay');

    const dialog = document.createElement('div');
    dialog.classList.add('confirm-dialog');

    const messageText = document.createElement('p');
    messageText.textContent = message;

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
