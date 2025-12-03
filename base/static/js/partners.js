// Add Partner Modal
function AddModalFunction() {
  const modal = document.getElementById("addPartnerModal");
  const form = document.getElementById("addPartnerForm");
  const closeBtn = document.getElementById("closeAddPartnerModal");
  const cancelBtn = document.getElementById("cancelAddPartner");
  const errorMessage = document.getElementById("addErrorMessage");

  // Open modal
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";

  // Close modal function
  function closeModal() {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Event listeners
  closeBtn.onclick = closeModal;
  cancelBtn.onclick = closeModal;

  modal.onclick = (e) => {
    if (e.target === modal) closeModal();
  };

  // Form submission
  form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        closeModal();
        location.reload();
      } else {
        errorMessage.textContent = data.error || "حدث خطأ غير متوقع";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  };
}

// Edit Partner Modal
function EditModalFunction(partnerId) {
  const modal = document.getElementById("editPartnerModal");
  const form = document.getElementById("editPartnerForm");
  const closeBtn = document.getElementById("closeEditPartnerModal");
  const cancelBtn = document.getElementById("cancelEditPartner");
  const errorMessage = document.getElementById("editErrorMessage");

  // Open modal
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";

  // GET data
  async function getData() {
    const formData = new FormData(form);
    try {
      const response = await fetch(`/partners/edit/${partnerId}/`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        for (const [key, value] of Object.entries(data.fields)) {
          const input = document.getElementById(`id_edit-${key}`);
          if (input) {
            input.value = value;
          }
        }
      }
    } catch (error) {
      console.log(error);
    }
  }

  getData();

  // Close modal function
  function closeModal() {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Event listeners
  closeBtn.onclick = closeModal;
  cancelBtn.onclick = closeModal;

  modal.onclick = (e) => {
    if (e.target === modal) closeModal();
  };

  // Form submission
  form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const response = await fetch(`/partners/edit/${partnerId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        closeModal();
        location.reload();
      } else {
        errorMessage.textContent = data.error || "حدث خطأ غير متوقع";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  };
}

// Delete partner Modal
function DeleteModalFunction(partnerId) {
  const modal = document.getElementById("deletepartnerModal");
  const form = document.getElementById("deletepartnerForm");
  const closeBtn = document.getElementById("closeDeletepartnerModal");
  const cancelBtn = document.getElementById("cancelDeletepartner");
  const errorMessage = document.getElementById("deleteErrorMessage");
  const nameSpan = document.getElementById("deletepartnerName");

  // Get partner name
  const name = document
    .querySelector(`.partner-fullname-${partnerId}`)
    .textContent.trim();
  nameSpan.textContent = name;

  // Open modal
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";

  // Close modal function
  function closeModal() {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    document.body.style.overflow = "auto";
    errorMessage.classList.add("hidden");
  }

  // Event listeners
  closeBtn.onclick = closeModal;
  cancelBtn.onclick = closeModal;

  modal.onclick = (e) => {
    if (e.target === modal) closeModal();
  };

  // Form submission
  form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const response = await fetch(`/partners/delete/${partnerId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        closeModal();
        location.reload();
      } else {
        errorMessage.textContent = data.error || "حدث خطأ غير متوقع";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  };
}

function addProductField(products) {
  const container = document.getElementById("products-fields");
  const newField = document.createElement("div");
  newField.classList = "flex items-center flex-col gap-2";
  const selectField = document.createElement("select");
  selectField.name = "product";
  selectField.classList =
    "w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right";

  // Add default option
  const defaultOption = document.createElement("option");
  defaultOption.value = "skip";
  defaultOption.text = "اختر منتج";
  selectField.appendChild(defaultOption);

  // Add product options with stock information
  for (let i = 0; i < products.length; i++) {
    const option = document.createElement("option");
    option.value = products[i].id;
    if (products[i].id != "skip") {
      option.text = products[i].name + " - (متوفر: " + products[i].stock + ")";
    } else {
      option.text = "اختر منتج";
    }

    option.setAttribute("data-stock", products[i].stock);
    selectField.appendChild(option);
  }

  const quantityField = document.createElement("input");
  quantityField.type = "number";
  quantityField.min = 1;
  quantityField.required = false;
  quantityField.placeholder = "الكمية";
  quantityField.name = "quantity";
  quantityField.classList =
    "w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right";
  newField.appendChild(selectField);
  newField.appendChild(quantityField);
  container.appendChild(newField);
}

function addProductFieldModal(products) {
  const container = document.getElementById("modal-products-fields");
  const newField = document.createElement("div");
  newField.classList = "flex items-center flex-col gap-2";
  const selectField = document.createElement("select");
  selectField.name = "product";
  selectField.classList =
    "w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all text-right";

  // Add default option
  const defaultOption = document.createElement("option");
  defaultOption.value = "skip";
  defaultOption.text = "اختر منتج";
  selectField.appendChild(defaultOption);

  // Add product options with stock information
  for (let i = 0; i < products.length; i++) {
    const option = document.createElement("option");
    option.value = products[i].id;
    option.text = products[i].name + " - (متوفر: " + products[i].stock + ")";
    option.setAttribute("data-stock", products[i].stock);
    selectField.appendChild(option);
  }

  const quantityField = document.createElement("input");
  quantityField.type = "number";
  quantityField.min = 1;
  quantityField.required = true;
  quantityField.placeholder = "الكمية";
  quantityField.name = "quantity";
  quantityField.classList =
    "w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all text-right";
  newField.appendChild(selectField);
  newField.appendChild(quantityField);
  container.appendChild(newField);
}

function toggleDetails(transactionId) {
  const detailsRow = document.getElementById(`details-${transactionId}`);
  if (detailsRow.classList.contains("hidden")) {
    detailsRow.classList.remove("hidden");
  } else {
    detailsRow.classList.add("hidden");
  }
}

function addProductFieldModalRestore(products) {
  const container = document.getElementById("modal-products-fields-restore");
  const newField = document.createElement("div");
  newField.classList = "flex items-center flex-col gap-2";
  const selectField = document.createElement("select");
  selectField.name = "product";
  selectField.classList =
    "w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all text-right";
  for (let i = 0; i < products.length; i++) {
    const option = document.createElement("option");
    option.value = products[i].id;
    option.text = products[i].name;
    selectField.appendChild(option);
  }
  const quantityField = document.createElement("input");
  quantityField.type = "number";
  quantityField.min = 1;
  quantityField.required = true;
  quantityField.placeholder = "الكمية";
  quantityField.name = "quantity";
  quantityField.classList =
    "w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all text-right";
  newField.appendChild(selectField);
  newField.appendChild(quantityField);
  container.appendChild(newField);
}
// Give Product Modal Functions
function openGiveProductModal() {
  const modal = document.getElementById("giveProductModal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeGiveProductModal() {
  const modal = document.getElementById("giveProductModal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
  // Reset form
  const container = document.getElementById("modal-products-fields");
  const firstField = container.querySelector(".flex");
  container.innerHTML = "";
  container.appendChild(firstField);
}

// Restore Product Modal Functions
function openRestoreProductModal() {
  const modal = document.getElementById("restoreProductModal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeRestoreProductModal() {
  const modal = document.getElementById("restoreProductModal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
  // Reset form
  document.getElementById("modal-products-fields-restore").innerHTML = `
        <div class="flex items-center flex-col gap-2">
            <select name="product" class="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all text-right">
                <option value="skip">اختر منتج</option>
                ${document.querySelector('select[name="product"]').innerHTML}
            </select>
            <input type="number" name="quantity" class="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all text-right" placeholder="الكمية" min="1" required>
        </div>
    `;
}

// Take Payment Modal Functions
function openTakePaymentModal() {
  const modal = document.getElementById("takePaymentModal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeTakePaymentModal() {
  const modal = document.getElementById("takePaymentModal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
  // Reset form
  document.getElementById("payment-amount").value = "";
}

// Delete Transaction Modal Functions
function openDeleteTransactionModal(transactionId, transactionType) {
  const modal = document.getElementById("deleteTransactionModal");
  document.getElementById("deleteTransactionId").value = transactionId;
  document.getElementById("deleteTransactionType").textContent =
    transactionType;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeDeleteTransactionModal() {
  const modal = document.getElementById("deleteTransactionModal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "auto";
  // Hide error message
  document.getElementById("deleteErrorMessage").classList.add("hidden");
}

// Handle delete transaction form submission
document.addEventListener("DOMContentLoaded", function () {
  const deleteForm = document.getElementById("deleteTransactionForm");
  if (deleteForm) {
    deleteForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const transactionId = document.getElementById(
        "deleteTransactionId"
      ).value;
      const partnerId = window.location.pathname.split("/")[2]; // Extract partner ID from URL
      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
      ).value;

      fetch(`/partners/${partnerId}/transaction/${transactionId}/delete/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Reload page to show updated data
            window.location.reload();
          } else {
            // Show error message
            const errorDiv = document.getElementById("deleteErrorMessage");
            errorDiv.textContent = data.error || "حدث خطأ أثناء حذف المعاملة";
            errorDiv.classList.remove("hidden");
          }
        })
        .catch((error) => {
          const errorDiv = document.getElementById("deleteErrorMessage");
          errorDiv.textContent = "حدث خطأ في الاتصال بالخادم";
          errorDiv.classList.remove("hidden");
        });
    });
  }
});
