function fetch_status() {
    fetch('/myorderdata')
        .then(response => response.json())
        .then(function(data) {
            data.forEach(function(order) {
                var statusElement = document.getElementById("status" + order['order_id']);
                statusElement.innerHTML = order['status'];

                // Update the class of the parent card based on the status
                var cardElement = statusElement.closest('.card');
                cardElement.className = getCardClass(order['status']);
            });
        });
}

// Function to determine the card class based on the status
function getCardClass(status) {
    switch (status) {
        case 'Order received':
            return 'card text-bg-light mb-3';
        case 'In progress':
            return 'card text-bg-warning mb-3';
        case 'Delivered':
            return 'card text-bg-success mb-3';
        case 'Cancelled':
            return 'card text-bg-danger mb-3';
        default:
            return 'card mb-3'; // Default class if status is not recognized
    }
}
