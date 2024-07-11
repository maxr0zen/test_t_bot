document.getElementById('payment-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const messageDiv = document.getElementById('message');

    // Fixed amount for payment
    const amount = 2;
    messageDiv.textContent = `Вы успешно оплатили ${amount} рубля.`;
});
