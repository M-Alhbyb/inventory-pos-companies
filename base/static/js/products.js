// Modal elements

function AddModalFunction() {
  const AddModal = document.getElementById("addProductModal");
  AddModal.classList.remove("hidden");
  AddModal.classList.add("flex");
  document.body.style.overflow = "hidden";
  const closeModalBtn = document.getElementById("closeAddProductModal");
  const cancelBtn = document.getElementById("cancelAddProduct");
  const form = document.getElementById("addProductForm");
  const errorMessage = document.getElementById("errorMessage");

  // Open modal

  // Close modal function
  function closeModal() {
    AddModal.classList.add("hidden");
    AddModal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Close modal events
  closeModalBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  AddModal.addEventListener("click", (e) => {
    if (e.target === AddModal) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !AddModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Form submission with AJAX
  form.addEventListener("submit", async (e) => {
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
        // Close modal and reload page to show new category
        closeModal();
        location.reload();
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء إضافة المنتج";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  });
}

// Edit Modal elements
async function EditModalFunction(productId) {
  const EditModal = document.getElementById("editProductModal");
  EditModal.classList.remove("hidden");
  EditModal.classList.add("flex");
  document.body.style.overflow = "hidden";
  const closeModalBtn = document.getElementById("closeEditProductModal");
  const cancelBtn = document.getElementById("cancelEditProduct");
  const form = document.getElementById("editProductForm");
  const errorMessage = document.getElementById("errorMessage");

  getData(productId);

  // Close modal function
  function closeModal() {
    EditModal.classList.add("hidden");
    EditModal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Close modal events
  closeModalBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  EditModal.addEventListener("click", (e) => {
    if (e.target === EditModal) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !EditModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Form submission with AJAX
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch(`/products/edit/${productId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        // Close modal and reload page to show new category
        closeModal();
        location.reload();
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء تعديل المنتج";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = `حدث خطأ في الاتصال بالخادم ${error}`;
      errorMessage.classList.remove("hidden");
    }
  });

  async function getData(productId) {
    try {
      const response = await fetch(`/products/edit/${productId}/`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();
      if (data.success) {
        const form = document.getElementById("editProductForm");
        form.name.value = data.name;

        for (let i = 0; i < form.category.options.length; i++) {
          if (form.category.options[i].value == data.category) {
            form.category.options[i].selected = true;
            break;
          }
        }
        form.price.value = data.price;
        form.stock.value = data.stock;
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء تعديل المنتج";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  }
}

// Delete Modal elements
function DeleteModalFunction(categoryId) {
  const DeleteModal = document.getElementById("deleteProductModal");
  DeleteModal.classList.remove("hidden");
  DeleteModal.classList.add("flex");
  document.body.style.overflow = "hidden";
  const closeModalBtn = document.getElementById("closeDeleteProductModal");
  const cancelBtn = document.getElementById("cancelDeleteProduct");
  const form = document.getElementById("deleteProductForm");
  const errorMessage = document.getElementById("errorMessage");

  // Get category data
  const formName = document.getElementById("deleteProductName");
  const productName = document.querySelector(
    ".product-name-" + categoryId
  ).textContent;
  formName.textContent = productName;
  // Close modal function
  function closeModal() {
    DeleteModal.classList.add("hidden");
    DeleteModal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Close modal events
  closeModalBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  DeleteModal.addEventListener("click", (e) => {
    if (e.target === DeleteModal) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !DeleteModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Form submission with AJAX
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    try {
      const response = await fetch(`/products/delete/${categoryId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        // Close modal and reload page to show new category
        closeModal();
        location.reload();
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء حذف المنتج";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  });
}
