function toggleMenu() {
  const dropdown = document.getElementById("hamburgerDropdown");
  dropdown.classList.toggle("active"); // Toggle the 'active' class to show/hide the menu
}

// Modal handling
const modal = document.getElementById("addItemModal");
const addItemBtn = document.getElementById("add-item-btn");
const closeBtn = document.getElementsByClassName("close")[0];
const cancelBtn = document.getElementsByClassName("btn-cancel")[0];

// Open modal
addItemBtn.onclick = function () {
  modal.style.display = "block";
};

// Close modal
closeBtn.onclick = function () {
  modal.style.display = "none";
};
cancelBtn.onclick = function () {
  modal.style.display = "none";
};

// Close modal when clicking outside of the modal
window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// Optional: Function to delete an item (for later implementation)
function deleteItem(itemId) {
  // Send a delete request to the Flask route
  fetch(`/deleteItem/${itemId}`, { method: "POST" }).then((response) =>
    window.location.reload()
  );
}

function postItem(itemId) {
  fetch(`/postItem/${itemId}`, { method: "POST" }).then((response) =>
    window.location.reload()
  ); // Reload the page after posting
}

// Delete waste log function
function deleteLog(logId) {
  fetch(`/deleteWasteLog/${logId}`, { method: "POST" }).then((response) =>
    window.location.reload()
  ); // Reload the page after deletion
}

function schedulePickup(postId, cardElement) {
  fetch(`/schedulePickup/${postId}`, {
    method: "POST",
  }).then((response) => {
    if (response.ok) {
      // If pickup is successfully scheduled, remove the card from the page
      cardElement.remove();
      alert("Pickup scheduled successfully!");
    } else {
      alert("Failed to schedule pickup.");
    }
  });
}
