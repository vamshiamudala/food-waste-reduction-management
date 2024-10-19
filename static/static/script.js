function toggleMenu() {
  const dropdown = document.getElementById("hamburgerDropdown");
  dropdown.classList.toggle("active");
}

const modal = document.getElementById("addItemModal");
const addItemBtn = document.getElementById("add-item-btn");
const closeBtn = document.getElementsByClassName("close")[0];
const cancelBtn = document.getElementsByClassName("btn-cancel")[0];

addItemBtn.onclick = function () {
  modal.style.display = "block";
};

closeBtn.onclick = function () {
  modal.style.display = "none";
};
cancelBtn.onclick = function () {
  modal.style.display = "none";
};

window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

function deleteItem(itemId) {
  fetch(`/deleteItem/${itemId}`, { method: "POST" }).then((response) =>
    window.location.reload()
  );
}

function postItem(itemId) {
  fetch(`/postItem/${itemId}`, { method: "POST" }).then((response) =>
    window.location.reload()
  );
}

function deleteLog(logId) {
  fetch(`/deleteWasteLog/${logId}`, { method: "POST" }).then((response) =>
    window.location.reload()
  );
}

function schedulePickup(postId, cardElement) {
  fetch(`/schedulePickup/${postId}`, {
    method: "POST",
  }).then((response) => {
    if (response.ok) {
      cardElement.remove();
      alert("Pickup scheduled successfully!");
    } else {
      alert("Failed to schedule pickup.");
    }
  });
}
