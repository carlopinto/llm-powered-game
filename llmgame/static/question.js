
$('.option-card').click(function() {
    let selOption = $(this).data('option-name');
    //console.log(selOption);
    $.ajax({
        url: '/check_answer', 
        method: 'POST',     
        data: { 
            selected_option: selOption
        }, 
        success: function(response) { 
            // Show feedback
            document.getElementById('feedback').innerHTML = response.feedback;
            // Show correct answer
            document.getElementById(response.answer).style.backgroundColor = "#68f068";
            // Show/hide Next button
            if(response.feedback.startsWith("Correct")){
                document.getElementById('next-button').style.display = "block";
            }
            else{
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
});